"""
API REST para o frontend your-app-creator (Bio Console).

Rotas sob prefixo /api/v1, alinhadas a src/lib/api.ts do frontend.
"""

from __future__ import annotations

import logging
import os
import uuid
from collections import deque
from datetime import date, datetime, timezone
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from fastapi import BackgroundTasks, Body, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel, Field

# Garantir imports do pacote systems.*
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent
_SRC = _APP_DIR.parent
_REPO_ROOT = _APP_DIR.parent.parent
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

def refresh_bio_console_dotenv_from_files() -> None:
    """
    Re-lê AI-Biomimetica/.env e depois bio_console.env (se existir — este último sobrescreve o primeiro).

    Chamado no arranque e antes de cada TTS/status para que alterações à voz entrem em efeito
    sem obrigar a reiniciar o Uvicorn (útil no Windows com --reload).
    """
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    # override=True: valores do ficheiro prevalecem sobre variáveis de ambiente vazias/erradas no SO
    load_dotenv(_REPO_ROOT / ".env", override=True)
    load_dotenv(_REPO_ROOT / "bio_console.env", override=True)


# Cofre Obsidian e outras variáveis: também lidas pelo worker do Uvicorn (--reload no Windows).
refresh_bio_console_dotenv_from_files()


def _elevenlabs_voice_id_tail(voice_id: str) -> Optional[str]:
    v = (voice_id or "").strip()
    if not v:
        return None
    return v[-6:] if len(v) > 6 else v

from systems.sistemas.sistema_meta_learning_biomimetico import AutoEvolvingAISystem  # noqa: E402

from app.obsidian_vault import (  # noqa: E402
    chokmah_subdir,
    vault_root_from_env,
    write_note as obsidian_write_note,
)

try:
    import requests
    from requests.exceptions import ConnectionError as RequestsConnectionError
    from requests.exceptions import Timeout as RequestsTimeout
except ImportError:
    requests = None  # type: ignore
    RequestsConnectionError = type(None)  # type: ignore[misc, assignment]
    RequestsTimeout = type(None)  # type: ignore[misc, assignment]


API_PREFIX = "/api/v1"
VERSION = "0.2.14-bio-console"

_ELEVENLABS_TTS_MAX_CHARS = 8000

_elevenlabs_verify_warned: List[bool] = [False]


def _elevenlabs_requests_verify():
    """
    Redes com inspeção SSL (proxy corporativo) falham com CERTIFICATE_VERIFY_FAILED.
    Opções: ELEVENLABS_CA_BUNDLE=caminho.pem (recomendado) ou ELEVENLABS_SSL_VERIFY=false (só rede confiável).
    """
    flag = os.environ.get("ELEVENLABS_SSL_VERIFY", "").strip().lower()
    if flag in ("0", "false", "no", "off"):
        if not _elevenlabs_verify_warned[0]:
            logger.warning(
                "ElevenLabs: ELEVENLABS_SSL_VERIFY desactivado — inseguro fora de rede controlada; "
                "prefira ELEVENLABS_CA_BUNDLE com o PEM da CA interna."
            )
            _elevenlabs_verify_warned[0] = True
        return False
    bundle = os.environ.get("ELEVENLABS_CA_BUNDLE", "").strip()
    if bundle:
        p = Path(bundle).expanduser()
        if p.is_file():
            return str(p.resolve())
    return True


def _elevenlabs_voice_settings() -> Dict[str, Any]:
    """Prosódia ElevenLabs — menos monótona (stability mais baixo = mais variação emocional)."""

    def _f01(env_key: str, default: float) -> float:
        raw = os.environ.get(env_key, "").strip()
        if not raw:
            return default
        try:
            return max(0.0, min(1.0, float(raw)))
        except ValueError:
            return default

    def _speed() -> float:
        raw = os.environ.get("ELEVENLABS_SPEED", "").strip()
        default = 0.97
        if not raw:
            return default
        try:
            return max(0.5, min(1.35, float(raw)))
        except ValueError:
            return default

    return {
        # Defaults calibrados para soar menos "robô"; afinar via .env ou trocar ELEVENLABS_VOICE_ID.
        "stability": _f01("ELEVENLABS_STABILITY", 0.36),
        "similarity_boost": _f01("ELEVENLABS_SIMILARITY_BOOST", 0.78),
        "style": _f01("ELEVENLABS_STYLE", 0.32),
        "use_speaker_boost": os.environ.get("ELEVENLABS_USE_SPEAKER_BOOST", "true").strip().lower()
        not in ("0", "false", "no", "off"),
        "speed": _speed(),
    }


def _elevenlabs_tts_json_body(text: str) -> Dict[str, Any]:
    """Corpo JSON do POST ElevenLabs (model_id, voice_settings, language opcional)."""
    model_id = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2").strip()
    body: Dict[str, Any] = {
        "text": text.strip()[:_ELEVENLABS_TTS_MAX_CHARS],
        "model_id": model_id or "eleven_multilingual_v2",
        "voice_settings": _elevenlabs_voice_settings(),
    }
    lang = os.environ.get("ELEVENLABS_LANGUAGE_CODE", "").strip()
    if lang:
        body["language_code"] = lang[:16]
    return body


def _elevenlabs_tts_query_params() -> Dict[str, Any]:
    """Query string: qualidade de áudio e latência vs qualidade."""
    params: Dict[str, Any] = {}
    fmt = os.environ.get("ELEVENLABS_OUTPUT_FORMAT", "").strip()
    if fmt:
        params["output_format"] = fmt
    raw_lat = os.environ.get("ELEVENLABS_OPTIMIZE_STREAMING_LATENCY", "").strip()
    if raw_lat != "":
        try:
            params["optimize_streaming_latency"] = max(0, min(4, int(raw_lat)))
        except ValueError:
            params["optimize_streaming_latency"] = 0
    return params


# CORS: Vite com host "::" expõe o UI também pelo IP LAN (ex. http://192.168.1.3:8080).
_CORS_LAN_REGEX = (
    r"https?://("
    r"localhost|127\.0\.0\.1"
    r"|192\.168\.\d{1,3}\.\d{1,3}"
    r"|10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}"
    r"):\d+$"
)


def _cors_allow_origins() -> List[str]:
    origins = [
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://localhost:8080",
        "https://127.0.0.1:8080",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    extra = os.environ.get("BIO_CONSOLE_EXTRA_CORS_ORIGINS", "").strip()
    if extra:
        origins.extend(x.strip() for x in extra.split(",") if x.strip())
    return origins


class TaskRequestModel(BaseModel):
    task_type: str = "chat"
    text_length: int = 0
    context: Dict[str, Any] = Field(default_factory=dict)


class BrainSettingsModel(BaseModel):
    use_local_brain: bool = True
    local_brain_type: str = "ollama"
    ollama_model: str = "llama3.1:8b"
    ollama_base_url: str = "http://localhost:11434"


class ChatMessageModel(BaseModel):
    role: str
    content: str
    created_at: Optional[str] = None


class ChatRequestModel(BaseModel):
    message: str = ""
    messages: List[ChatMessageModel] = Field(default_factory=list)
    task_type: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    # agent: raciocínio explícito + episódios para evolução contínua; chat: conversa directa
    mode: str = "chat"
    session_id: Optional[str] = None


class ElevenLabsTTSRequestModel(BaseModel):
    """Texto para síntese; a chave da API vem só de ELEVENLABS_API_KEY (nunca do cliente)."""

    text: str = Field(..., min_length=1, max_length=_ELEVENLABS_TTS_MAX_CHARS)
    voice_id: Optional[str] = Field(
        default=None,
        description="Opcional; senão usa ELEVENLABS_VOICE_ID no servidor",
    )


_OBSIDIAN_BODY_MAX = 500_000


class ObsidianNoteWriteModel(BaseModel):
    """
    Grava Markdown sob `<cofre>/<OBSIDIAN_CHOKMAH_RELATIVE>/`.
    Caminho só com .md, sem .. (validação no servidor).
    """

    relative_path: str = Field(
        ...,
        description="Ex.: episodios/2026-04-10.md (relativo à pasta CHOKMAH)",
    )
    body: str = Field(..., min_length=1, max_length=_OBSIDIAN_BODY_MAX)
    title: Optional[str] = Field(default=None, max_length=500)
    tags: List[str] = Field(default_factory=list)
    append: bool = Field(
        default=False,
        description="Se true e o ficheiro existir, acrescenta secção com data UTC",
    )
    frontmatter_extra: Dict[str, Any] = Field(
        default_factory=dict,
        description="Campos YAML simples (str, int, float, bool)",
    )


_state: Dict[str, Any] = {
    "engine": None,
    "brain": BrainSettingsModel().model_dump(),
    "history": [],
    "agent_episodes": [],
}

# WhatsApp (Z-API): deduplicação de webhooks e histórico por chat (telefone ou grupo)
_zapi_seen_message_ids: deque[str] = deque(maxlen=4000)
_zapi_histories: Dict[str, List[Dict[str, str]]] = {}
_WHATSAPP_MSG_MAX = 3800


def _load_evolving_agent_system_prompt() -> str:
    path = _APP_DIR / "prompts" / "evolving_agent_system.txt"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return (
        "És um agente autónomo. Responde em português. Usa EXACTAMENTE os marcadores "
        "---RACIOCINIO--- e ---RESPOSTA--- na tua mensagem."
    )


def _load_chat_conversation_system_prompt() -> str:
    path = _APP_DIR / "prompts" / "chat_conversation_system.txt"
    if path.is_file():
        return path.read_text(encoding="utf-8").strip()
    return (
        "Conversas em português com memória do histórico. Tom natural, adequado para voz. "
        "Responde só com a tua mensagem."
    )


def _trim_chat_messages(messages: List[Dict[str, str]], max_messages: int) -> List[Dict[str, str]]:
    if max_messages <= 0 or len(messages) <= max_messages:
        return messages
    return messages[-max_messages:]


def _split_agent_output(raw: str) -> tuple[str, str]:
    if "---RACIOCINIO---" in raw and "---RESPOSTA---" in raw:
        try:
            mid = raw.split("---RACIOCINIO---", 1)[1]
            reasoning, answer = mid.split("---RESPOSTA---", 1)
            return reasoning.strip(), answer.strip()
        except (IndexError, ValueError):
            pass
    return "", raw.strip()


def _ollama_chat_request(
    base_url: str, model: str, ollama_messages: List[Dict[str, str]], timeout: int = 120
) -> Dict[str, Any]:
    if not requests:
        raise HTTPException(status_code=503, detail="requests não instalado")
    url = f"{base_url.rstrip('/')}/api/chat"
    r = requests.post(
        url,
        json={"model": model, "messages": ollama_messages, "stream": False},
        timeout=timeout,
    )
    if r.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail=f"Ollama HTTP {r.status_code}: {r.text[:500]}",
        )
    return r.json()


def _extract_message_content(data: Dict[str, Any]) -> str:
    msg = data.get("message") or {}
    content = msg.get("content") if isinstance(msg, dict) else None
    if not content:
        raise HTTPException(status_code=502, detail="Resposta Ollama sem message.content")
    return str(content)


def _log_agent_episode(
    body: ChatRequestModel, answer: str, reasoning: str
) -> Dict[str, Any]:
    eps: List[Dict[str, Any]] = _state.setdefault("agent_episodes", [])
    client_ctx = body.context if isinstance(body.context, dict) else {}
    meet_ch = client_ctx.get("meet_channel") if isinstance(client_ctx, dict) else None

    eps.insert(
        0,
        {
            "id": str(uuid.uuid4()),
            "session_id": body.session_id,
            "at": _utc_now(),
            "user_last": (body.message or "")[:600],
            "answer_preview": answer[:500],
            "reasoning_chars": len(reasoning),
            "task_type": body.task_type,
            "meet_channel": meet_ch,
        },
    )
    del eps[500:]

    evo_ctx: Dict[str, Any] = {
        "session_id": body.session_id,
        "mode": "agent",
        "reasoning_chars": len(reasoning),
        "episodes_logged": len(eps),
    }
    if client_ctx:
        evo_ctx["client"] = client_ctx

    task_data: Dict[str, Any] = {
        "task_type": body.task_type or "agent_chokmah",
        "text_length": len(answer),
        "context": evo_ctx,
    }
    bio: Dict[str, Any] = {}
    try:
        eng = get_engine()
        bio = eng.ingest_agent_biomimetic_episode(task_data, reasoning, answer)
    except Exception as ex:
        logger.debug("ingest_agent_biomimetic_episode: %s", ex)
        bio = {"error": str(ex)}
    return bio


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _last_user_text_for_log(body: ChatRequestModel) -> str:
    u = (body.message or "").strip()
    if u:
        return u
    for m in reversed(body.messages or []):
        if m.role == "user" and (m.content or "").strip():
            return m.content.strip()
    return ""


def _maybe_obsidian_log_chat(
    body: ChatRequestModel,
    answer: str,
    reasoning: Optional[str],
    mode: str,
) -> None:
    """
    Grava troca no cofre Obsidian (append diário em CHOKMAH/dialogos/).
    Desligar: OBSIDIAN_AUTO_LOG_CHAT=false
    """
    flag = os.environ.get("OBSIDIAN_AUTO_LOG_CHAT", "true").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return
    root = vault_root_from_env()
    if not root or not root.is_dir():
        return
    ans = (answer or "").strip()
    if not ans:
        return
    user_txt = _last_user_text_for_log(body)[:5000]
    ans_clip = ans[:12000]
    rel = f"dialogos/{date.today().isoformat()}.md"
    lines = [
        f"**Modo:** `{mode}`",
    ]
    if body.session_id:
        lines.append(f"**Sessão:** `{body.session_id}`")
    lines.extend(
        [
            "",
            "### Pergunta",
            user_txt or "_(sem texto na última mensagem)_",
            "",
            "### Resposta",
            ans_clip,
        ]
    )
    r = (reasoning or "").strip()
    if r:
        r = r[:10000]
        lines.extend(["", "### Raciocínio (agente)", "", "```", r, "```"])
    md_body = "\n".join(lines)
    extra: Optional[Dict[str, Any]] = None
    if body.session_id:
        extra = {"session_id": str(body.session_id)[:120]}
    try:
        obsidian_write_note(
            vault=root,
            relative_md=rel,
            title=None,
            body=md_body,
            tags=["chokmah", "dialogo", "bio-console"],
            append=True,
            frontmatter_extra=extra,
        )
    except Exception as ex:
        logger.debug("Obsidian auto-log chat: %s", ex)


def _default_chokmah_welcome(agent_name: str) -> str:
    return f"Olá. Sou {agent_name}, o teu agente cognitivo, como posso lhe ajudar?"


def _maybe_obsidian_log_agent_event(
    *,
    kind: str,
    detail: str,
    agent_name: str,
) -> None:
    """Eventos do agente (abertura, etc.) em CHOKMAH/agent/eventos-AAAA-MM-DD.md."""
    flag = os.environ.get("OBSIDIAN_LOG_AGENT_EVENTS", "true").strip().lower()
    if flag in ("0", "false", "no", "off"):
        return
    root = vault_root_from_env()
    if not root or not root.is_dir():
        return
    rel = f"agent/eventos-{date.today().isoformat()}.md"
    md_body = "\n".join(
        [
            f"**Tipo:** `{kind}`",
            f"**Agente:** {agent_name}",
            f"**UTC:** {_utc_now()}",
            "",
            detail.strip()[:4000],
        ]
    )
    try:
        obsidian_write_note(
            vault=root,
            relative_md=rel,
            title=None,
            body=md_body,
            tags=["chokmah", "agente", "evento"],
            append=True,
            frontmatter_extra={"event_kind": kind[:80]},
        )
    except Exception as ex:
        logger.debug("Obsidian agent event: %s", ex)


def _get_brain() -> BrainSettingsModel:
    return BrainSettingsModel(**_state["brain"])


def _build_engine() -> AutoEvolvingAISystem:
    b = _get_brain()
    os.environ["OLLAMA_MODEL"] = b.ollama_model
    os.environ["OLLAMA_BASE_URL"] = b.ollama_base_url.rstrip("/")
    return AutoEvolvingAISystem(
        use_local_brain=b.use_local_brain,
        local_brain_type=b.local_brain_type,
    )


def get_engine() -> AutoEvolvingAISystem:
    if _state["engine"] is None:
        _state["engine"] = _build_engine()
        logger.info("AutoEvolvingAISystem inicializado para Bio Console API")
    return _state["engine"]


def reset_engine() -> None:
    _state["engine"] = None


def _ollama_unreachable_message(exc: BaseException, base_url: str) -> str:
    """Mensagem curta para o frontend quando Ollama não responde."""
    text = str(exc).lower()
    if (
        "10061" in str(exc)
        or "connection refused" in text
        or "failed to establish" in text
        or "actively refused" in text
    ):
        return (
            f"Ollama não está a correr (ou recusou a ligação) em {base_url}. "
            "No Windows: abra a aplicação Ollama ou execute na consola `ollama serve`; "
            "confirme `http://localhost:11434/api/tags` no browser. "
            "Instale o modelo com `ollama pull llama3.1:8b` (ou o nome em Configurações)."
        )
    if requests and isinstance(exc, RequestsTimeout):
        return "Ollama demorou demais a responder. Tente novamente ou use um modelo menor."
    if requests and isinstance(exc, RequestsConnectionError):
        return (
            f"Não foi possível ligar ao Ollama em {base_url}. "
            "Verifique se o serviço está ativo e se o URL nas Configurações está correto."
        )
    return f"Erro ao contactar Ollama: {exc}"


def _ollama_tags_reachable(base_url: str) -> bool:
    try:
        import requests
    except ImportError:
        return False
    try:
        r = requests.get(f"{base_url.rstrip('/')}/api/tags", timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def _normalize_recommendation(raw: Dict[str, Any], task: TaskRequestModel) -> Dict[str, Any]:
    params = raw.get("parameters") or {}
    if not isinstance(params, dict):
        params = {}
    out = {
        "provider": str(raw.get("provider", "local")),
        "parameters": {
            "temperature": float(params.get("temperature", 0.7)),
            "max_tokens": int(params.get("max_tokens", max(64, task.text_length * 2))),
            "top_p": float(params.get("top_p", 0.9)),
        },
        "strategy": str(raw.get("strategy", "balanced")),
        "confidence": float(raw.get("confidence", 0.75)),
        "reasoning": str(raw.get("reasoning", "")),
        "brain_type": raw.get("brain_type"),
        "model_used": raw.get("model_used"),
        "hybrid_metadata": raw.get("hybrid_metadata"),
        "metadata": {"source": "AI-Biomimetica", **(raw.get("metadata") or {})},
    }
    if raw.get("error"):
        out["error"] = str(raw["error"])
    return out


def _zapi_send_configured() -> bool:
    return bool(
        os.environ.get("ZAPI_INSTANCE_ID", "").strip()
        and os.environ.get("ZAPI_INSTANCE_TOKEN", "").strip()
        and os.environ.get("ZAPI_CLIENT_TOKEN", "").strip()
    )


def _whatsapp_chunk_text(text: str, max_len: int = _WHATSAPP_MSG_MAX) -> List[str]:
    t = text.strip()
    if not t:
        return []
    if len(t) <= max_len:
        return [t]
    chunks: List[str] = []
    start = 0
    while start < len(t):
        chunks.append(t[start : start + max_len])
        start += max_len
    return chunks


def _zapi_send_text(phone: str, text: str) -> None:
    if not requests or not _zapi_send_configured():
        logger.warning("Z-API: envio não configurado ou requests indisponível")
        return
    instance_id = os.environ["ZAPI_INSTANCE_ID"].strip()
    instance_token = os.environ["ZAPI_INSTANCE_TOKEN"].strip()
    client_token = os.environ["ZAPI_CLIENT_TOKEN"].strip()
    url = (
        f"https://api.z-api.io/instances/{instance_id}/token/{instance_token}/send-text"
    )
    for part in _whatsapp_chunk_text(text):
        try:
            r = requests.post(
                url,
                headers={
                    "Client-Token": client_token,
                    "Content-Type": "application/json",
                },
                json={"phone": phone, "message": part},
                timeout=90,
            )
            if r.status_code != 200:
                logger.warning("Z-API send-text HTTP %s: %s", r.status_code, r.text[:300])
        except Exception as ex:
            logger.warning("Z-API send-text falhou: %s", ex)


def _zapi_chat_key(payload: Dict[str, Any]) -> str:
    phone = str(payload.get("phone") or "").strip()
    if payload.get("isGroup") and payload.get("participantPhone"):
        return f"{phone}__{payload.get('participantPhone')}"
    return phone or "unknown"


def _zapi_process_webhook_payload(payload: Dict[str, Any]) -> None:
    """
    Processa webhook Z-API (texto): Ollama → resposta → send-text.
    Executar em BackgroundTasks (fora do request thread).
    """
    if not isinstance(payload, dict):
        return
    if payload.get("type") != "ReceivedCallback":
        return
    if payload.get("fromMe"):
        return
    text_obj = payload.get("text")
    if not isinstance(text_obj, dict):
        return
    user_msg = (text_obj.get("message") or "").strip()
    if not user_msg:
        return

    mid = payload.get("messageId")
    if mid is not None:
        mid_s = str(mid)
        if mid_s in _zapi_seen_message_ids:
            logger.debug("Z-API webhook duplicado ignorado: %s", mid_s)
            return
        _zapi_seen_message_ids.append(mid_s)

    phone = str(payload.get("phone") or "").strip()
    if not phone:
        logger.warning("Z-API: payload sem phone")
        return

    chat_key = _zapi_chat_key(payload)
    hist = _zapi_histories.setdefault(chat_key, [])
    hist.append({"role": "user", "content": user_msg})
    del hist[: max(0, len(hist) - 24)]

    if not requests:
        logger.error("Z-API: requests não instalado")
        return

    b = _get_brain()
    use_agent = os.environ.get("WHATSAPP_ZAPI_AGENT_MODE", "true").lower() not in (
        "0",
        "false",
        "no",
    )

    ollama_messages: List[Dict[str, str]] = []
    if use_agent:
        system = _load_evolving_agent_system_prompt()
        extra = os.environ.get("AGENT_SYSTEM_PROMPT_SUFFIX", "").strip()
        if extra:
            system = f"{system}\n\n{extra}"
        ollama_messages.append({"role": "system", "content": system})
    else:
        wa_sys = os.environ.get(
            "WHATSAPP_ZAPI_CHAT_SYSTEM",
            "És o assistente CHOKMAH. Responde em português de forma clara e breve, "
            "como numa conversa por WhatsApp.",
        )
        ollama_messages.append({"role": "system", "content": wa_sys})

    for turn in hist:
        ollama_messages.append(
            {"role": turn["role"], "content": turn["content"]}
        )

    try:
        data = _ollama_chat_request(
            b.ollama_base_url, b.ollama_model, ollama_messages, timeout=180
        )
    except HTTPException as he:
        _zapi_send_text(
            phone,
            "Desculpe, o serviço de IA não está disponível no momento. "
            f"({he.detail})",
        )
        return
    except Exception as ex:
        logger.exception("Z-API: Ollama falhou")
        _zapi_send_text(phone, _ollama_unreachable_message(ex, b.ollama_base_url))
        return

    try:
        raw_content = _extract_message_content(data)
    except HTTPException:
        _zapi_send_text(phone, "Resposta inválida do modelo local.")
        return

    reasoning = ""
    answer = raw_content
    if use_agent:
        reasoning, answer = _split_agent_output(raw_content)
        if not answer.strip():
            answer = raw_content

    hist.append({"role": "assistant", "content": answer.strip()})
    del hist[: max(0, len(hist) - 24)]

    if use_agent:
        try:
            ep_body = ChatRequestModel(
                message=user_msg[:2000],
                messages=[],
                mode="agent",
                session_id=f"zapi:{chat_key}",
                task_type="whatsapp_zapi",
                context={
                    "channel": "whatsapp_zapi",
                    "phone": phone[:32],
                    "is_group": bool(payload.get("isGroup")),
                },
            )
            _log_agent_episode(ep_body, answer.strip(), reasoning)
        except Exception as ex:
            logger.debug("Z-API episódio agente: %s", ex)

    _zapi_send_text(phone, answer.strip())


def _collect_host_metrics() -> Dict[str, Any]:
    """
    Métricas reais do hospedeiro onde corre a API (CPU/RAM/swap/discos), via psutil.
    Útil para HUD tipo «central de comando» no frontend; não substitui monitorização de produção.
    """
    try:
        import platform as plat

        import psutil
    except ImportError:
        return {"available": False, "reason": "psutil_unavailable"}

    try:
        boot = float(psutil.boot_time())
        now_ts = datetime.now(timezone.utc).timestamp()
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        cpu_logical = int(psutil.cpu_count(logical=True) or 1)
        cpu_physical = psutil.cpu_count(logical=False)
        # Amostra curta para percentagem útil num único pedido HTTP
        cpu_pct = float(psutil.cpu_percent(interval=0.08))
        try:
            per_core = [float(x) for x in psutil.cpu_percent(interval=0, percpu=True)]
        except Exception:
            per_core = None

        disks: List[Dict[str, Any]] = []
        try:
            for part in psutil.disk_partitions(all=False):
                if not part.fstype or part.fstype.lower() == "cdfs":
                    continue
                try:
                    u = psutil.disk_usage(part.mountpoint)
                    disks.append(
                        {
                            "mountpoint": part.mountpoint,
                            "device": part.device,
                            "fstype": part.fstype,
                            "total": int(u.total),
                            "used": int(u.used),
                            "free": int(u.free),
                            "percent": float(u.percent),
                        }
                    )
                except (PermissionError, OSError):
                    continue
        except Exception:
            disks = []

        disks.sort(key=lambda d: d.get("total", 0), reverse=True)

        load_avg: Optional[List[float]] = None
        if hasattr(os, "getloadavg"):
            try:
                load_avg = [float(x) for x in os.getloadavg()]
            except OSError:
                load_avg = None

        process_count: Optional[int] = None
        try:
            process_count = len(psutil.pids())
        except Exception:
            process_count = None

        net_io: Optional[Dict[str, int]] = None
        try:
            nio = psutil.net_io_counters()
            if nio:
                net_io = {
                    "bytes_sent": int(nio.bytes_sent),
                    "bytes_recv": int(nio.bytes_recv),
                    "packets_sent": int(getattr(nio, "packets_sent", 0)),
                    "packets_recv": int(getattr(nio, "packets_recv", 0)),
                    "errin": int(getattr(nio, "errin", 0)),
                    "errout": int(getattr(nio, "errout", 0)),
                    "dropin": int(getattr(nio, "dropin", 0)),
                    "dropout": int(getattr(nio, "dropout", 0)),
                }
        except Exception:
            net_io = None

        disk_io: Optional[Dict[str, int]] = None
        try:
            dio = psutil.disk_io_counters(perdisk=False)
            if dio:
                disk_io = {
                    "read_bytes": int(dio.read_bytes),
                    "write_bytes": int(dio.write_bytes),
                    "read_count": int(dio.read_count),
                    "write_count": int(dio.write_count),
                }
        except Exception:
            disk_io = None

        net_interfaces: List[Dict[str, Any]] = []
        try:
            stats_map = psutil.net_if_stats()
            pernic = psutil.net_io_counters(pernic=True)
            for name, io in list(pernic.items())[:12]:
                st = stats_map.get(name)
                net_interfaces.append(
                    {
                        "name": name[:32],
                        "bytes_sent": int(io.bytes_sent),
                        "bytes_recv": int(io.bytes_recv),
                        "packets_sent": int(io.packets_sent),
                        "packets_recv": int(io.packets_recv),
                        "is_up": bool(st.isup) if st is not None else None,
                        "speed_mbps": int(st.speed) if st is not None and st.speed > 0 else None,
                    }
                )
        except Exception:
            net_interfaces = []

        return {
            "available": True,
            "hostname": plat.node() or "",
            "platform": f"{plat.system()} {plat.release()}".strip(),
            "python_bits": 64 if sys.maxsize > 2**32 else 32,
            "boot_time_utc": datetime.fromtimestamp(boot, tz=timezone.utc).isoformat(),
            "uptime_sec": max(0.0, now_ts - boot),
            "cpu_percent": cpu_pct,
            "cpu_count_logical": cpu_logical,
            "cpu_count_physical": int(cpu_physical) if cpu_physical is not None else None,
            "cpu_per_core": per_core,
            "memory": {
                "total": int(mem.total),
                "available": int(mem.available),
                "used": int(mem.used),
                "percent": float(mem.percent),
            },
            "swap": {
                "total": int(swap.total),
                "used": int(swap.used),
                "free": int(swap.free),
                "percent": float(swap.percent),
            },
            "disks": disks[:8],
            "process_count": process_count,
            "load_average": load_avg,
            "net_io": net_io,
            "disk_io": disk_io,
            "net_interfaces": net_interfaces[:8],
        }
    except Exception as ex:
        logger.warning("system/host: falha ao recolher métricas: %s", ex)
        return {"available": False, "reason": "collection_error", "detail": str(ex)}


def create_app() -> FastAPI:
    app = FastAPI(title="IA Biomimética — Bio Console API", version=VERSION)

    _cors_override = os.environ.get("BIO_CONSOLE_CORS_REGEX")
    cors_regex = (
        _cors_override.strip()
        if _cors_override and _cors_override.strip()
        else _CORS_LAN_REGEX
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_allow_origins(),
        allow_origin_regex=cors_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get(f"{API_PREFIX}/health")
    def health() -> Dict[str, Any]:
        b = _get_brain()
        ollama_ok = _ollama_tags_reachable(b.ollama_base_url)
        vault = vault_root_from_env()
        return {
            "api": "ok",
            "ollama": {
                "available": ollama_ok,
                "base_url": b.ollama_base_url,
                "model": b.ollama_model,
                "last_check_utc": _utc_now(),
            },
            "obsidian": {
                "vault_configured": vault is not None,
                "vault_ready": bool(vault and vault.is_dir()),
                "chokmah_folder": chokmah_subdir(),
            },
            "version": VERSION,
        }

    @app.get(f"{API_PREFIX}/system/host")
    def system_host() -> Dict[str, Any]:
        """
        CPU/RAM/swap/discos do **servidor** onde corre esta API (psutil).
        O browser não tem acesso a estes valores; use quando a API aponta para a sua máquina ou LAN.
        """
        return _collect_host_metrics()

    @app.get(f"{API_PREFIX}/brain/status")
    def brain_status() -> Dict[str, Any]:
        b = _get_brain()
        ollama_ok = _ollama_tags_reachable(b.ollama_base_url)
        return {
            "available": ollama_ok,
            "base_url": b.ollama_base_url,
            "model": b.ollama_model,
            "last_check_utc": _utc_now(),
        }

    @app.post(f"{API_PREFIX}/orchestrate/recommend")
    def recommend(task: TaskRequestModel) -> Dict[str, Any]:
        engine = get_engine()
        task_dict = task.model_dump()
        try:
            raw = engine.recommend_provider(task_dict)
        except Exception as e:
            logger.exception("recommend_provider falhou")
            raise HTTPException(status_code=500, detail=str(e)) from e

        rec = _normalize_recommendation(raw, task)
        entry = {
            "id": str(uuid.uuid4()),
            "task": task_dict,
            "recommendation": rec,
            "created_at": _utc_now(),
        }
        hist: List[Dict[str, Any]] = _state["history"]
        hist.insert(0, entry)
        del hist[500:]

        return rec

    @app.get(f"{API_PREFIX}/history/recommendations")
    def history_recommendations(limit: int = 20, offset: int = 0) -> Dict[str, Any]:
        items = _state["history"][offset : offset + limit]
        return {"items": items, "total": len(_state["history"])}

    @app.post(f"{API_PREFIX}/settings/brain")
    def settings_brain(settings: BrainSettingsModel) -> BrainSettingsModel:
        _state["brain"] = settings.model_dump()
        reset_engine()
        return settings

    @app.get(f"{API_PREFIX}/agent/welcome")
    def agent_welcome() -> Dict[str, Any]:
        """
        Mensagem de apresentação para nova conversa (UI pode ler em voz com ElevenLabs).
        Personalizar: CHOKMAH_WELCOME_MESSAGE ou CHOKMAH_AGENT_NAME no .env.
        Regista abertura no Obsidian se cofre e OBSIDIAN_LOG_AGENT_EVENTS activos.
        """
        name = os.environ.get("CHOKMAH_AGENT_NAME", "CHOKMAH").strip() or "CHOKMAH"
        custom = os.environ.get("CHOKMAH_WELCOME_MESSAGE", "").strip()
        text = custom if custom else _default_chokmah_welcome(name)
        _maybe_obsidian_log_agent_event(
            kind="abertura_ui",
            detail="Pedido de boas-vindas / apresentação ao utilizador (nova conversa).",
            agent_name=name,
        )
        return {
            "message": text,
            "agent_name": name,
            "pillars": [
                "evolucao_biomimetica",
                "memoria_obsidian",
                "dialogo_voz",
            ],
        }

    @app.get(f"{API_PREFIX}/agent/episodes")
    def agent_episodes(limit: int = 30) -> Dict[str, Any]:
        """Últimos episódios do modo agente (memória operacional para evolução / auditoria)."""
        eps = _state.get("agent_episodes") or []
        limit = max(1, min(100, limit))
        return {"items": eps[:limit], "total": len(eps)}

    @app.get(f"{API_PREFIX}/evolution/status")
    def evolution_status() -> Dict[str, Any]:
        """Métricas recentes, ciclos biomiméticos e estatísticas do cérebro local (Ollama/mock)."""
        try:
            eng = get_engine()
            snap = eng.get_agent_evolution_snapshot()
        except Exception as e:
            logger.exception("evolution_status")
            raise HTTPException(status_code=500, detail=str(e)) from e
        return {
            **snap,
            "agent_episodes_logged": len(_state.get("agent_episodes") or []),
        }

    @app.get(f"{API_PREFIX}/whatsapp/zapi/status")
    def whatsapp_zapi_status() -> Dict[str, Any]:
        """Estado da integração Z-API (sem expor tokens)."""
        return {
            "api_version": VERSION,
            "webhook_post_url_relative": f"{API_PREFIX}/whatsapp/zapi/webhook",
            "zapi_send_configured": _zapi_send_configured(),
            "webhook_secret_enabled": bool(os.environ.get("ZAPI_WEBHOOK_SECRET", "").strip()),
            "whatsapp_agent_mode_env": os.environ.get("WHATSAPP_ZAPI_AGENT_MODE", "true"),
            "z_api_docs": "https://developer.z-api.io/",
        }

    @app.post(f"{API_PREFIX}/whatsapp/zapi/webhook")
    def whatsapp_zapi_webhook(
        background_tasks: BackgroundTasks,
        body: Dict[str, Any] = Body(...),
        secret: Optional[str] = Query(
            None,
            description="Obrigatório se ZAPI_WEBHOOK_SECRET estiver definido",
        ),
    ) -> Dict[str, Any]:
        """
        Webhook «Ao receber» da Z-API. Configure no painel Z-API (HTTPS).
        Ex.: `https://seu-dominio/api/v1/whatsapp/zapi/webhook?secret=...`
        """
        expected = os.environ.get("ZAPI_WEBHOOK_SECRET", "").strip()
        if expected and (secret or "").strip() != expected:
            raise HTTPException(status_code=401, detail="secret de webhook inválido")
        background_tasks.add_task(_zapi_process_webhook_payload, body)
        return {"received": True}

    @app.get(f"{API_PREFIX}/tts/elevenlabs/status")
    def tts_elevenlabs_status() -> Dict[str, Any]:
        """Indica se TTS ElevenLabs está configurável (sem expor segredos)."""
        refresh_bio_console_dotenv_from_files()
        key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        vid = os.environ.get("ELEVENLABS_VOICE_ID", "").strip()
        ssl_relaxed = os.environ.get("ELEVENLABS_SSL_VERIFY", "").strip().lower() in (
            "0",
            "false",
            "no",
            "off",
        )
        ca = os.environ.get("ELEVENLABS_CA_BUNDLE", "").strip()
        lang = bool(os.environ.get("ELEVENLABS_LANGUAGE_CODE", "").strip())
        model_id = os.environ.get("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2").strip()
        bio_override = (_REPO_ROOT / "bio_console.env").is_file()
        return {
            "available": bool(key and vid),
            "api_key_set": bool(key),
            "default_voice_set": bool(vid),
            "ssl_verify_relaxed": ssl_relaxed,
            "ca_bundle_configured": bool(ca) and Path(ca).expanduser().is_file(),
            "language_code_set": lang,
            "model_id": (model_id or "eleven_multilingual_v2")[:64],
            "voice_id_tail": _elevenlabs_voice_id_tail(vid),
            "bio_console_env_present": bio_override,
        }

    @app.get(f"{API_PREFIX}/obsidian/status")
    def obsidian_status() -> Dict[str, Any]:
        """Cofre Obsidian (ficheiros locais). Sem OBSIDIAN_VAULT_ROOT as gravações ficam desativadas."""
        root = vault_root_from_env()
        auto = os.environ.get("OBSIDIAN_AUTO_LOG_CHAT", "true").strip().lower()
        auto_on = auto not in ("0", "false", "no", "off")
        return {
            "vault_configured": root is not None,
            "vault_ready": bool(root and root.is_dir()),
            "chokmah_folder": chokmah_subdir(),
            "write_token_required": bool(os.environ.get("OBSIDIAN_WRITE_TOKEN", "").strip()),
            "auto_log_chat": bool(root and root.is_dir() and auto_on),
        }

    @app.post(f"{API_PREFIX}/obsidian/note")
    def obsidian_note(request: Request, note: ObsidianNoteWriteModel) -> Dict[str, Any]:
        expected = os.environ.get("OBSIDIAN_WRITE_TOKEN", "").strip()
        if expected:
            got = (request.headers.get("x-obsidian-write-token") or "").strip()
            if got != expected:
                raise HTTPException(status_code=401, detail="token de escrita Obsidian inválido")

        root = vault_root_from_env()
        if not root or not root.is_dir():
            raise HTTPException(
                status_code=503,
                detail="Defina OBSIDIAN_VAULT_ROOT com caminho absoluto da pasta do cofre Obsidian",
            )
        extra = note.frontmatter_extra or {}
        for _k, v in extra.items():
            if not isinstance(v, (str, int, float, bool)):
                raise HTTPException(
                    status_code=400,
                    detail="frontmatter_extra: use apenas string, número ou booleano",
                )
        try:
            result = obsidian_write_note(
                vault=root,
                relative_md=note.relative_path,
                title=note.title,
                body=note.body,
                tags=list(note.tags or []),
                append=bool(note.append),
                frontmatter_extra=extra or None,
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        except OSError as e:
            logger.warning("Obsidian write: %s", e)
            raise HTTPException(status_code=500, detail=f"erro ao gravar: {e}") from e

        return {"ok": True, **result}

    @app.post(f"{API_PREFIX}/tts/elevenlabs")
    def tts_elevenlabs(body: ElevenLabsTTSRequestModel) -> Response:
        """
        Proxy Text-to-Speech ElevenLabs (áudio MPEG). A API key fica apenas no servidor.
        """
        refresh_bio_console_dotenv_from_files()
        if not requests:
            raise HTTPException(status_code=503, detail="requests não instalado")
        api_key = os.environ.get("ELEVENLABS_API_KEY", "").strip()
        if not api_key:
            raise HTTPException(
                status_code=503,
                detail="Defina ELEVENLABS_API_KEY no ambiente do servidor",
            )
        voice = (body.voice_id or os.environ.get("ELEVENLABS_VOICE_ID", "")).strip()
        if not voice:
            raise HTTPException(
                status_code=503,
                detail="Defina ELEVENLABS_VOICE_ID ou envie voice_id no JSON",
            )
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
        payload = _elevenlabs_tts_json_body(body.text)
        q = _elevenlabs_tts_query_params()
        try:
            r = requests.post(
                url,
                params=q or None,
                headers={
                    "xi-api-key": api_key,
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120,
                verify=_elevenlabs_requests_verify(),
            )
        except Exception as e:
            logger.warning("ElevenLabs TTS falhou (rede): %s", e)
            hint = ""
            if "CERTIFICATE_VERIFY_FAILED" in str(e) or "SSL" in str(e):
                hint = (
                    " Se estiver atrás de proxy corporativo, defina ELEVENLABS_CA_BUNDLE=caminho\\ca.pem "
                    "ou temporariamente ELEVENLABS_SSL_VERIFY=false no .env da API."
                )
            raise HTTPException(status_code=502, detail=f"ElevenLabs: {e}{hint}") from e

        if r.status_code != 200:
            err = r.text[:500] if r.text else r.reason
            logger.warning("ElevenLabs HTTP %s: %s", r.status_code, err)
            raise HTTPException(
                status_code=502,
                detail=f"ElevenLabs HTTP {r.status_code}",
            )

        return Response(
            content=r.content,
            media_type="audio/mpeg",
            headers={"Cache-Control": "no-store"},
        )

    @app.post(f"{API_PREFIX}/chat")
    def chat(body: ChatRequestModel) -> Dict[str, Any]:
        b = _get_brain()
        if not requests:
            raise HTTPException(status_code=503, detail="requests não instalado no backend")

        messages: List[Dict[str, str]] = []
        for m in body.messages:
            if m.content.strip():
                messages.append({"role": m.role, "content": m.content})
        if body.message.strip():
            messages.append({"role": "user", "content": body.message.strip()})

        if not messages:
            raise HTTPException(status_code=400, detail="message ou messages obrigatório")

        try:
            max_hist = int(os.environ.get("CHAT_MAX_MESSAGES", "40"))
        except ValueError:
            max_hist = 40
        messages = _trim_chat_messages(messages, max_hist)

        mode = (body.mode or "chat").strip().lower()
        is_agent = mode == "agent"

        ollama_messages: List[Dict[str, str]]
        if is_agent:
            system = _load_evolving_agent_system_prompt()
            extra = os.environ.get("AGENT_SYSTEM_PROMPT_SUFFIX", "").strip()
            if extra:
                system = f"{system}\n\n{extra}"
            ollama_messages = [{"role": "system", "content": system}, *messages]
        else:
            chat_sys = _load_chat_conversation_system_prompt()
            extra_chat = os.environ.get("CHAT_SYSTEM_PROMPT_SUFFIX", "").strip()
            if extra_chat:
                chat_sys = f"{chat_sys}\n\n{extra_chat}"
            ollama_messages = [{"role": "system", "content": chat_sys}, *messages]

        try:
            data = _ollama_chat_request(
                b.ollama_base_url, b.ollama_model, ollama_messages, timeout=180
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.warning("Ollama chat falhou: %s", e)
            raise HTTPException(
                status_code=502,
                detail=_ollama_unreachable_message(e, b.ollama_base_url),
            ) from e

        raw_content = _extract_message_content(data)

        if is_agent:
            reasoning, answer = _split_agent_output(raw_content)
            if not answer:
                answer = raw_content
            biomimetic = _log_agent_episode(body, answer, reasoning)
            _maybe_obsidian_log_chat(body, answer, reasoning or None, "agent")
            return {
                "answer": answer,
                "provider": "local",
                "strategy": body.task_type or "agent",
                "metadata": {
                    "ollama_model": b.ollama_model,
                    "mode": "agent",
                    "reasoning_trace": reasoning or None,
                    "session_id": body.session_id,
                    "biomimetic": biomimetic,
                    "raw": data,
                },
            }

        _maybe_obsidian_log_chat(body, raw_content, None, "chat")
        return {
            "answer": raw_content,
            "provider": "local",
            "strategy": body.task_type or "chat",
            "metadata": {"ollama_model": b.ollama_model, "mode": "chat", "raw": data},
        }

    @app.get("/")
    def root() -> Dict[str, str]:
        return {
            "service": "bio-console-api",
            "docs": "/docs",
            "api": API_PREFIX,
        }

    return app


app = create_app()

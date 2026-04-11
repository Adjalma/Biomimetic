"""
Contrato da Bio Console API (evolução biomimética + chat agente).

Requer PyTorch (import do motor). Sem Ollama: usa monkeypatch em _ollama_chat_request.
"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

pytest.importorskip("torch")

import app.bio_console_api as bc  # noqa: E402


def _fake_evolution_snapshot() -> dict:
    return {
        "performance_history_recent": [0.55, 0.6],
        "agent_biomimetic_cycles_total": 2,
        "last_biomimetic_evolution_unix": 0.0,
        "local_brain_performance": None,
        "local_brain_learning_entries": 0,
        "evolve_every_n_agent_episodes": 48,
        "evolve_cooldown_sec": 900.0,
        "evolution_worker_running": False,
        "evolution_queued": False,
        "evolution_profile": "minimal",
        "evolution_async": True,
    }


@pytest.fixture
def engine_mock() -> MagicMock:
    eng = MagicMock()
    eng.get_agent_evolution_snapshot.return_value = _fake_evolution_snapshot()
    eng.ingest_agent_biomimetic_episode.return_value = {
        "quality_score": 0.72,
        "biomimetic_feedback_recorded": True,
        "evolution_cycle_ran": False,
        "evolution_cycle_scheduled": False,
    }
    return eng


@pytest.fixture
def client(monkeypatch, engine_mock: MagicMock) -> TestClient:
    monkeypatch.setattr(bc, "get_engine", lambda: engine_mock)
    return TestClient(bc.app)


def test_health_ok(client: TestClient):
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    body = r.json()
    assert body.get("api") == "ok"
    assert "ollama" in body


def test_evolution_status_merges_engine_and_episodes(client: TestClient, engine_mock: MagicMock):
    r = client.get("/api/v1/evolution/status")
    assert r.status_code == 200
    data = r.json()
    assert data.get("evolution_profile") == "minimal"
    assert "agent_episodes_logged" in data
    engine_mock.get_agent_evolution_snapshot.assert_called_once()


def test_agent_welcome_ok(client: TestClient):
    r = client.get("/api/v1/agent/welcome")
    assert r.status_code == 200
    data = r.json()
    assert "message" in data and len(data["message"]) > 20
    assert data.get("agent_name")
    assert isinstance(data.get("pillars"), list)


def test_agent_episodes_empty(client: TestClient):
    r = client.get("/api/v1/agent/episodes?limit=5")
    assert r.status_code == 200
    data = r.json()
    assert data.get("total") == 0
    assert data.get("items") == []


def test_chat_agent_splits_reasoning(monkeypatch, engine_mock: MagicMock):
    monkeypatch.setattr(bc, "get_engine", lambda: engine_mock)

    def fake_ollama(*_a, **_k):
        return {
            "message": {
                "content": "---RACIOCINIO---\nPasso a passo.\n---RESPOSTA---\nOlá."
            }
        }

    monkeypatch.setattr(bc, "_ollama_chat_request", fake_ollama)
    monkeypatch.setattr(bc, "_ollama_tags_reachable", lambda _url: True)

    c = TestClient(bc.app)
    r = c.post(
        "/api/v1/chat",
        json={
            "message": "oi",
            "messages": [],
            "mode": "agent",
            "session_id": "s1",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("answer") == "Olá."
    meta = body.get("metadata") or {}
    assert meta.get("mode") == "agent"
    assert "Passo a passo" in (meta.get("reasoning_trace") or "")
    bio = meta.get("biomimetic") or {}
    assert bio.get("quality_score") == 0.72
    engine_mock.ingest_agent_biomimetic_episode.assert_called_once()


def test_chat_requires_message(client: TestClient):
    r = client.post("/api/v1/chat", json={"message": "", "messages": []})
    assert r.status_code == 400


def test_chat_agent_appends_obsidian_dialog(tmp_path, monkeypatch, engine_mock: MagicMock):
    vault = tmp_path / "vault"
    vault.mkdir()
    monkeypatch.setenv("OBSIDIAN_VAULT_ROOT", str(vault))
    monkeypatch.setenv("OBSIDIAN_AUTO_LOG_CHAT", "true")
    monkeypatch.setenv("OBSIDIAN_CHOKMAH_RELATIVE", "CHOKMAH")
    monkeypatch.setattr(bc, "get_engine", lambda: engine_mock)

    def fake_ollama(*_a, **_k):
        return {"message": {"content": "---RACIOCINIO---\npassos\n---RESPOSTA---\nOi."}}

    monkeypatch.setattr(bc, "_ollama_chat_request", fake_ollama)
    monkeypatch.setattr(bc, "_ollama_tags_reachable", lambda _url: True)

    c = TestClient(bc.app)
    r = c.post(
        "/api/v1/chat",
        json={"message": "ola", "messages": [], "mode": "agent", "session_id": "s99"},
    )
    assert r.status_code == 200
    day = date.today().isoformat()
    p = vault / "CHOKMAH" / "dialogos" / f"{day}.md"
    assert p.is_file()
    text = p.read_text(encoding="utf-8")
    assert "ola" in text
    assert "Oi." in text
    assert "passos" in text


def test_tts_elevenlabs_status(client: TestClient):
    r = client.get("/api/v1/tts/elevenlabs/status")
    assert r.status_code == 200
    data = r.json()
    assert "available" in data
    assert "api_key_set" in data
    assert "default_voice_set" in data
    assert "ssl_verify_relaxed" in data
    assert "ca_bundle_configured" in data
    assert "language_code_set" in data
    assert "model_id" in data
    assert "voice_id_tail" in data
    assert data.get("voice_id_tail") is None or isinstance(data.get("voice_id_tail"), str)
    assert isinstance(data.get("bio_console_env_present"), bool)


def test_elevenlabs_voice_id_tail_unit():
    assert bc._elevenlabs_voice_id_tail("abcdefghijklmnop") == "klmnop"
    assert bc._elevenlabs_voice_id_tail("short") == "short"
    assert bc._elevenlabs_voice_id_tail("") is None
    assert bc._elevenlabs_voice_id_tail("   ") is None


def test_tts_elevenlabs_proxy_payload_and_query(monkeypatch, client: TestClient):
    monkeypatch.setattr(bc, "refresh_bio_console_dotenv_from_files", lambda: None)
    monkeypatch.setenv("ELEVENLABS_API_KEY", "test-key")
    monkeypatch.setenv("ELEVENLABS_VOICE_ID", "voice-id-1")
    monkeypatch.setenv("ELEVENLABS_SPEED", "0.88")
    monkeypatch.setenv("ELEVENLABS_LANGUAGE_CODE", "pt")
    monkeypatch.setenv("ELEVENLABS_OUTPUT_FORMAT", "mp3_44100_128")
    monkeypatch.setenv("ELEVENLABS_OPTIMIZE_STREAMING_LATENCY", "0")
    calls: list[dict] = []

    def fake_post(url, headers=None, json=None, params=None, timeout=None, verify=None):
        calls.append({"url": url, "json": json, "params": params or {}})
        class Resp:
            status_code = 200
            content = b"\xff\xf3"
            text = ""

        return Resp()

    monkeypatch.setattr(bc.requests, "post", fake_post)
    r = client.post("/api/v1/tts/elevenlabs", json={"text": "  Olá mundo  "})
    assert r.status_code == 200
    assert len(calls) == 1
    body = calls[0]["json"]
    assert body["text"] == "Olá mundo"
    assert body["language_code"] == "pt"
    assert body["voice_settings"]["speed"] == 0.88
    assert calls[0]["params"].get("output_format") == "mp3_44100_128"
    assert calls[0]["params"].get("optimize_streaming_latency") == 0
    assert "voice-id-1" in calls[0]["url"]


def test_elevenlabs_voice_settings_natural_defaults(monkeypatch):
    for k in (
        "ELEVENLABS_SPEED",
        "ELEVENLABS_STABILITY",
        "ELEVENLABS_SIMILARITY_BOOST",
        "ELEVENLABS_STYLE",
    ):
        monkeypatch.delenv(k, raising=False)
    s = bc._elevenlabs_voice_settings()
    assert s["speed"] == 0.97
    assert s["stability"] == 0.36
    assert s["similarity_boost"] == 0.78
    assert s["style"] == 0.32


def test_whatsapp_zapi_status(client: TestClient):
    r = client.get("/api/v1/whatsapp/zapi/status")
    assert r.status_code == 200
    data = r.json()
    assert data.get("zapi_send_configured") is False
    assert "webhook_post_url_relative" in data


def test_whatsapp_zapi_webhook_ack(client: TestClient):
    r = client.post(
        "/api/v1/whatsapp/zapi/webhook",
        json={"type": "ReceivedCallback", "fromMe": True, "phone": "5511999999999"},
    )
    assert r.status_code == 200
    assert r.json().get("received") is True


def test_obsidian_status(monkeypatch, client: TestClient):
    monkeypatch.delenv("OBSIDIAN_VAULT_ROOT", raising=False)
    r = client.get("/api/v1/obsidian/status")
    assert r.status_code == 200
    data = r.json()
    assert data.get("vault_configured") is False
    assert data.get("auto_log_chat") is False
    assert "chokmah_folder" in data


def test_health_includes_obsidian(monkeypatch, client: TestClient):
    monkeypatch.delenv("OBSIDIAN_VAULT_ROOT", raising=False)
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    obs = (r.json().get("obsidian") or {})
    assert "vault_configured" in obs
    assert "chokmah_folder" in obs


def test_obsidian_note_requires_vault(monkeypatch, engine_mock: MagicMock):
    monkeypatch.delenv("OBSIDIAN_VAULT_ROOT", raising=False)
    monkeypatch.setattr(bc, "get_engine", lambda: engine_mock)
    c = TestClient(bc.app)
    r = c.post(
        "/api/v1/obsidian/note",
        json={
            "relative_path": "x.md",
            "body": "conteúdo",
        },
    )
    assert r.status_code == 503


def test_obsidian_note_writes_file(tmp_path, monkeypatch, engine_mock: MagicMock):
    vault = tmp_path / "vault"
    vault.mkdir()
    monkeypatch.setenv("OBSIDIAN_VAULT_ROOT", str(vault))
    monkeypatch.setenv("OBSIDIAN_CHOKMAH_RELATIVE", "CHOKMAH")
    monkeypatch.delenv("OBSIDIAN_WRITE_TOKEN", raising=False)
    monkeypatch.setattr(bc, "get_engine", lambda: engine_mock)

    c = TestClient(bc.app)
    r = c.post(
        "/api/v1/obsidian/note",
        json={
            "relative_path": "notas/teste.md",
            "title": "Título",
            "body": "Corpo **markdown**.",
            "tags": ["chokmah"],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("ok") is True
    assert data.get("mode") == "create"
    out = vault / "CHOKMAH" / "notas" / "teste.md"
    assert out.is_file()
    text = out.read_text(encoding="utf-8")
    assert "Título" in text
    assert "Corpo **markdown**." in text
    assert "chokmah" in text


def test_obsidian_note_rejects_traversal(tmp_path, monkeypatch, engine_mock: MagicMock):
    vault = tmp_path / "vault"
    vault.mkdir()
    monkeypatch.setenv("OBSIDIAN_VAULT_ROOT", str(vault))
    monkeypatch.delenv("OBSIDIAN_WRITE_TOKEN", raising=False)
    monkeypatch.setattr(bc, "get_engine", lambda: engine_mock)
    c = TestClient(bc.app)
    r = c.post(
        "/api/v1/obsidian/note",
        json={"relative_path": "../escape.md", "body": "x"},
    )
    assert r.status_code == 400


def test_system_host_shape(client: TestClient):
    r = client.get("/api/v1/system/host")
    assert r.status_code == 200
    body = r.json()
    assert "available" in body
    if body.get("available") is True:
        assert "cpu_percent" in body
        assert "memory" in body and isinstance(body["memory"], dict)
        assert "percent" in body["memory"]

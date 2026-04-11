# Bio Console API — contrato resumido

Prefixo: **`/api/v1`** (exceto `GET /`).

## Autenticação

Não há autenticação nesta API de consola local. **Não expor em Internet pública** sem reverse proxy, TLS, rate limit e auth.

## Endpoints

| Método | Caminho | Descrição |
|--------|---------|-----------|
| GET | `/health` | Estado da API e reachability Ollama (tags). |
| GET | `/system/host` | CPU/RAM/swap/discos, **PIDs**, **loadavg** (Unix), **net_io** e **net_interfaces** (acumulado desde arranque), **disk_io** agregado — psutil no servidor. |
| GET | `/brain/status` | Modelo/URL Ollama configurados. |
| POST | `/orchestrate/recommend` | Corpo: `TaskRequestModel` → recomendação (`recommend_provider`). |
| GET | `/history/recommendations` | Histórico de recomendações (memória). |
| POST | `/settings/brain` | Atualiza cérebro; reinicializa motor. |
| POST | `/chat` | Chat Ollama; ver corpo abaixo. |
| GET | `/agent/episodes` | Últimos episódios modo agente (`limit` 1–100). |
| GET | `/evolution/status` | Snapshot autoevolução + fila em background + stats cérebro. |
| GET | `/tts/elevenlabs/status` | ElevenLabs: `available`, `model_id`, `language_code_set`, `voice_id_tail`, `bio_console_env_present`, SSL — sem expor chave. |
| POST | `/tts/elevenlabs` | Corpo JSON `{ "text": "...", "voice_id?": "..." }` → **audio/mpeg** (proxy; prosódia e `language_code` via env). |
| GET | `/whatsapp/zapi/status` | Integração Z-API (WhatsApp): envio configurado, path do webhook. |
| POST | `/whatsapp/zapi/webhook` | Webhook Z-API «Ao receber»; query opcional `secret` se `ZAPI_WEBHOOK_SECRET` definido. |

## `POST /chat`

Corpo JSON (Pydantic):

- `message` (string)
- `messages` (lista `{ role, content, created_at? }`)
- `task_type`, `context` opcionais
- `mode`: `"chat"` | `"agent"` (default `chat`)
- `session_id` opcional (continuidade)

**Modo `agent`:** mensagem `system` com prompt CHOKMAH; resposta com `---RACIOCINIO---` / `---RESPOSTA---`.  
`metadata` inclui `reasoning_trace`, `biomimetic` (`quality_score`, `evolution_cycle_scheduled`, …).

## Variáveis de ambiente (evolução gradual)

| Variável | Efeito |
|----------|--------|
| `AGENT_BIOMIMETIC_EVOLVE_EVERY` | Episódios entre ciclos (default `48`; `0` desliga). |
| `AGENT_BIOMIMETIC_EVOLVE_COOLDOWN_SEC` | Cooldown entre ciclos (default `900`). |
| `AGENT_EVOLUTION_ASYNC` | `true` (default): ciclo em thread daemon. |
| `AGENT_EVOLUTION_PROFILE` | `minimal` \| `balanced` \| `full`. |
| `AGENT_EVOLUTION_PHASE_SLEEP_SEC` | Pausa entre fases (CPU). |
| `AGENT_SYSTEM_PROMPT_SUFFIX` | Texto extra no system prompt do agente. |
| `BIO_CONSOLE_EXTRA_CORS_ORIGINS` | Origens CORS extra (vírgula). |
| `ELEVENLABS_API_KEY` | Chave API ElevenLabs (só servidor). |
| `ELEVENLABS_VOICE_ID` | ID da voz por omissão (trocar voz = maior impacto na “humanidade”). |
| `ELEVENLABS_MODEL_ID` | Opcional (default `eleven_multilingual_v2`). |
| `ELEVENLABS_STABILITY`, `ELEVENLABS_SIMILARITY_BOOST`, `ELEVENLABS_STYLE`, `ELEVENLABS_USE_SPEAKER_BOOST` | Prosódia (0–1); defaults na API favorecem menos monotonia. |
| `ELEVENLABS_SPEED` | Velocidade da fala (≈0,5–1,35); default interno ~0,97 se omitido. |
| `ELEVENLABS_LANGUAGE_CODE` | Ex.: `pt` — reforça pronúncia/normalização para o idioma. |
| `ELEVENLABS_OUTPUT_FORMAT` | Query opcional, ex. `mp3_44100_128`. |
| `ELEVENLABS_OPTIMIZE_STREAMING_LATENCY` | `0`–`4` na query (maior = mais otimização de latência, menos qualidade de som). |
| `ZAPI_INSTANCE_ID`, `ZAPI_INSTANCE_TOKEN`, `ZAPI_CLIENT_TOKEN` | Envio de respostas WhatsApp (Z-API). |
| `ZAPI_WEBHOOK_SECRET` | Segredo na query `?secret=` do webhook. |
| `WHATSAPP_ZAPI_AGENT_MODE` | `true` / `false` — modo agente no WhatsApp. |

Ver também [`teams-elevenlabs-demo.md`](teams-elevenlabs-demo.md), [`zapi-whatsapp-chokmah.md`](zapi-whatsapp-chokmah.md).

## OpenAPI

Com o servidor em execução: **`http://localhost:8000/docs`**.

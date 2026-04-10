# Bio Console API — contrato resumido

Prefixo: **`/api/v1`** (exceto `GET /`).

## Autenticação

Não há autenticação nesta API de consola local. **Não expor em Internet pública** sem reverse proxy, TLS, rate limit e auth.

## Endpoints

| Método | Caminho | Descrição |
|--------|---------|-----------|
| GET | `/health` | Estado da API e reachability Ollama (tags). |
| GET | `/brain/status` | Modelo/URL Ollama configurados. |
| POST | `/orchestrate/recommend` | Corpo: `TaskRequestModel` → recomendação (`recommend_provider`). |
| GET | `/history/recommendations` | Histórico de recomendações (memória). |
| POST | `/settings/brain` | Atualiza cérebro; reinicializa motor. |
| POST | `/chat` | Chat Ollama; ver corpo abaixo. |
| GET | `/agent/episodes` | Últimos episódios modo agente (`limit` 1–100). |
| GET | `/evolution/status` | Snapshot autoevolução + fila em background + stats cérebro. |
| GET | `/tts/elevenlabs/status` | Se ElevenLabs está configurado (`available`, sem expor chave). |
| POST | `/tts/elevenlabs` | Corpo JSON `{ "text": "..." }` → resposta **audio/mpeg** (proxy ElevenLabs). |
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
| `ELEVENLABS_VOICE_ID` | ID da voz por omissão. |
| `ELEVENLABS_MODEL_ID` | Opcional (default `eleven_multilingual_v2`). |
| `ZAPI_INSTANCE_ID`, `ZAPI_INSTANCE_TOKEN`, `ZAPI_CLIENT_TOKEN` | Envio de respostas WhatsApp (Z-API). |
| `ZAPI_WEBHOOK_SECRET` | Segredo na query `?secret=` do webhook. |
| `WHATSAPP_ZAPI_AGENT_MODE` | `true` / `false` — modo agente no WhatsApp. |

Ver também [`teams-elevenlabs-demo.md`](teams-elevenlabs-demo.md), [`zapi-whatsapp-chokmah.md`](zapi-whatsapp-chokmah.md).

## OpenAPI

Com o servidor em execução: **`http://localhost:8000/docs`**.

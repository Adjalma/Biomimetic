# WhatsApp via Z-API + CHOKMAH (Bio Console API)

Integração para a **IA responder automaticamente** quando alguém envia **texto** para o número ligado à tua instância Z-API.

## O que precisas (Z-API + servidor)

1. **Instância Z-API** ligada ao WhatsApp (QR no painel).
2. No painel Z-API, webhook **«Ao receber»** apontando para uma URL **HTTPS** (a Z-API não aceita HTTP).
3. Na mesma conta Z-API: **Instance ID**, **Instance token** e **Client-Token** (header de segurança — ver [introdução API](https://developer.z-api.io/api-reference/introduction)).

## Variáveis de ambiente (servidor da Bio Console)

| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `ZAPI_INSTANCE_ID` | Sim, para **enviar** respostas | ID da instância no painel |
| `ZAPI_INSTANCE_TOKEN` | Sim | Token da instância |
| `ZAPI_CLIENT_TOKEN` | Sim | Client-Token da conta |
| `ZAPI_WEBHOOK_SECRET` | Recomendado | Token secreto; o webhook deve incluir `?secret=VALOR` na URL |
| `WHATSAPP_ZAPI_AGENT_MODE` | Não | `true` (default): modo agente CHOKMAH no Ollama; `false`: respostas mais curtas (system prompt simples) |
| `WHATSAPP_ZAPI_CHAT_SYSTEM` | Não | Se `WHATSAPP_ZAPI_AGENT_MODE=false`, texto do system prompt |

O **email** da conta Z-API **não** entra no código — só os tokens acima.

## Endpoints deste projeto

- `GET /api/v1/whatsapp/zapi/status` — indica se o envio Z-API está configurado.
- `POST /api/v1/whatsapp/zapi/webhook` — corpo JSON igual ao webhook [«Ao receber»](https://developer.z-api.io/webhooks/on-message-received-examples) (ex.: mensagem de **texto** com `type: ReceivedCallback`).

Exemplo de URL no painel Z-API:

```text
https://SEU_DOMINIO/api/v1/whatsapp/zapi/webhook?secret=SEU_SEGREDO_LONGO
```

## Testar no teu PC (HTTPS)

O Z-API exige **HTTPS**. Opções comuns:

- **ngrok** / **Cloudflare Tunnel** / **localhost.run** — expõe `https://...` para `localhost:8000`.
- Servidor com domínio e TLS (nginx + Let’s Encrypt).

Fluxo: sobes a Bio Console API → túnel HTTPS → colas a URL completa (com `?secret=`) no webhook Z-API → envias mensagem de texto ao número → o servidor chama o **Ollama** e devolve texto com **send-text** da Z-API.

## Comportamento

- Ignora `fromMe: true` (evita loop com mensagens enviadas por ti).
- Ignora tipos que não sejam texto simples no objeto `text.message`.
- Mantém **histórico curto** por conversa (telefone ou grupo; em grupo usa `participantPhone` na chave quando existir).
- Mensagens longas são **partidas** (~3800 caracteres por bloco).
- Com `WHATSAPP_ZAPI_AGENT_MODE=true`, só a parte **---RESPOSTA---** vai para o WhatsApp; o raciocínio entra nos **episódios** do agente no backend (evolução), como no chat web.

## Limitações (v1)

- Áudio, imagem e documentos **não** são tratados (só texto).
- Grupos: testar com cuidado (muitas mensagens = mais carga no Ollama).

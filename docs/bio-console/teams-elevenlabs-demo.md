# ElevenLabs + demo em Microsoft Teams — expectativas realistas

## O que já tens no projeto

- **Voz (TTS):** `POST /api/v1/tts/elevenlabs` com texto → áudio MP3 (proxy no servidor; a chave **não** vai para o browser).
- **Chat:** `POST /api/v1/chat` (Ollama) como hoje.
- **UI:** botão **Ouvir** nas respostas da IA (quando o servidor reporta `GET /tts/elevenlabs/status` → `available: true`).

### Variáveis de ambiente (servidor da Bio Console API)

| Variável | Obrigatório | Descrição |
|----------|-------------|-----------|
| `ELEVENLABS_API_KEY` | Sim, para TTS | Chave na consola ElevenLabs (não uses email no código; só esta chave). |
| `ELEVENLABS_VOICE_ID` | Sim, por omissão | ID da voz (página da voz no ElevenLabs). |
| `ELEVENLABS_MODEL_ID` | Não | Default `eleven_multilingual_v2`. |

Reinicia a API após alterar envs.

**Segurança:** não commits, não partilhes a chave em reunião nem no chat. Em produção: API atrás de auth + HTTPS.

---

## “A IA entra sozinha no Teams e fala” — o que isso significa tecnicamente

A Microsoft **não** oferece um “link mágico” para um executável genérico entrar como participante com áudio bidireccional sem uma destas linhas:

1. **Integração oficial** — Azure / Microsoft Graph / Bot Framework / Teams apps (permissões, registo de aplicação, muitas vezes envolvimento de IT).
2. **Fornecedor de meeting bots** — serviços comerciais que já fazem join + áudio + conformidade contratual.
3. **Demo no teu PC (mais rápido para mostrar)** — **tu** entras no Teams; o áudio da IA vai para o microfone da reunião via **cabo de áudio virtual** (ex. VB-Audio Virtual Cable): o browser reproduz o MP3 da ElevenLabs nesse dispositivo e o Teams usa esse dispositivo como microfone. Os outros ouvem a “voz da IA” como se falasses tu — com consentimento explícito da sala.

**Ouvir a reunião** e responder sozinho exige ainda **captura do áudio da reunião** (loopback ou stream do bot) → **STT (Whisper / Azure)** → o teu `POST /chat` → TTS → microfone virtual. Isso é um **segundo projeto** (pipeline tempo real + latência + permissões).

---

## Autonomia e “evolução”

- **Entrar na reunião e falar** é **automação + integração**, não é o mesmo que o motor biomimético `auto_evolve` que já tens (que actua sobre o modelo interno / meta-learning).
- Para **demo ética** com todos cientes: combina **CHOKMAH no ecrã** + **voz ElevenLabs** +, se quiseres “voz na sala”, **microfone virtual** com aviso na reunião: *“Vou usar assistente de voz sintética para as próximas respostas.”*

---

## Próximo passo se quiseres bot “de verdade” no Teams

1. Alinhar com **IT / jurídico** (gravação, dados, política Microsoft).
2. Escolher caminho: **Azure Communication Services** + Graph, **Copilot extensibility**, ou **fornecedor de meeting bot**.
3. Orçar tempo (semanas a meses), não horas.

Para **mostrar já** aos colegas: usa o fluxo **ecrã partilhado + Ouvir** ou **microfone virtual** com aprovação da sala.

Conta **Google Meet** pessoal: mesmo tipo de limites — ver [`google-meet-chokmah-demo.md`](google-meet-chokmah-demo.md).

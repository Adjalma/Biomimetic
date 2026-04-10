# Google Meet (conta pessoal) + CHOKMAH — o que é realista

## Meet “não empresarial” é mais fácil para *bot oficial*?

**Não muito.** O Google Meet (Workspace ou conta Gmail) **não expõe** uma API pública do tipo “este URL de reunião aceita um robô com microfone e altifalante” como num jogo. O que muda em conta pessoal é sobretudo **menos camadas de IT** — não um canal técnico novo.

Isto aproxima-se do [guia Teams/ElevenLabs](teams-elevenlabs-demo.md): integração “de verdade” passa por produtos Google (Calendar/Workspace APIs, extensões, parceiros) ou automação frágil (não recomendada para produção).

---

## Demo boa para mostrar aos amigos (consumidor)

1. **Abre o Meet** no Chrome (reunião criada com a tua conta Gmail).
2. **Partilha o ecrã** com a janela do CHOKMAH (`your-app-creator`) — todos veem o chat e o raciocínio do agente.
3. **Voz:** com ElevenLabs configurada no servidor, usa **Ouvir** na resposta; se quiserem **ouvir a voz na sala**, usa um **microfone virtual** (ex. VB-Audio Cable no Windows): o áudio do browser sai nesse dispositivo e no Meet escolhes esse microfone. **Avisa a sala** que é voz sintética.
4. **Tu colas na CHOKMAH** o que foi dito na reunião (ou transcreves numa frase) — o modelo responde; podes usar **Ouvir** de novo.

Isto já é um fluxo **claro, consentido e controlado** por ti.

---

## Evolução (o que o código faz agora)

Em **Configurações**, activa **“Etiquetar sessão Google Meet (demo)”**.  
Cada mensagem em modo **agente** envia no `context` da API:

- `meet_channel`: `google_meet_consumer`
- `session_purpose`: `meet_demo`

No backend, os **episódios** guardam `meet_channel` e o `ingest_agent_biomimetic_episode` recebe esse contexto em `task_data.context.client`, o que **influencia a semente** das tarefas de meta-learning (episódios distintos de “chat normal”).

Assim podes, no futuro, filtrar ou pesar métricas por origem Meet vs desktop.

---

## Próximo passo técnico (se quiseres ir além)

- **STT em tempo real** (áudio do Meet → texto) — ex.: captura de áudio do sistema + Whisper local/API, depois o mesmo `POST /chat`.
- **Automatizar “colar pergunta”** — atalhos ou extensão (cuidado com políticas do Chrome e da Google).

Quando tiveres STT+chat+TTS num loop, aí sim aproximas de “assistente na reunião”, ainda **sob o teu controlo** e com **consentimento** explícito dos participantes.

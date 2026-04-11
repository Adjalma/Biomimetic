# Agente CHOKMAH — o que já tens e o que falta

## Já implementado (base do agente)

| Capacidade | Onde |
|------------|------|
| Raciocínio estruturado + episódios | `POST /api/v1/chat` modo `agent` → `ingest_agent_biomimetic_episode` |
| Autoevolução gradual (biomimética) | Motor `AutoEvolvingAISystem`, envs `AGENT_*`, `GET /evolution/status` |
| Diálogo voz + texto | Frontend: Falar, ElevenLabs, modo «Voz primeiro» |
| Memória em ficheiros | Obsidian: `dialogos/AAAA-MM-DD.md` (cada troca), `agent/eventos-*.md` (aberturas), `POST /obsidian/note` |
| Apresentação ao iniciar | `GET /api/v1/agent/welcome` + UI em conversa nova |

## Lacunas para «entrar e fazer sozinho» (autonomia forte)

1. **Objectivos e plano** — Hoje o agente só reage a mensagens. Falta: fila de tarefas, passos, «fazer X até concluir», confirmação humana para acções sensíveis.
2. **Ferramentas (tools)** — Chamar APIs, ler ficheiros (sandbox), executar scripts, com política explícita do que é permitido.
3. **Loop próprio** — Acordar em horários ou eventos sem mensagem do utilizador (scheduler + custos/limites).
4. **Aprender com erros de forma fechada** — Hoje: episódios genéricos. Falta: etiquetar falha (utilizador ou validador), reforço negativo explícito, métricas por tipo de erro.
5. **Obsidian «tudo»** — Já há diálogos + eventos. Falta opcional: exportar raciocínio completo sempre, snapshots de evolução, anexar erros de API, embeddings/RAG a partir do cofre.
6. **Criatividade com limites** — System prompt + temperatura Ollama; falta perfis (explorador vs conservador) e guardrails por domínio.

## Ordem sugerida de evolução

1. Tools seguras (lista fechada) + uma tarefa demo (ex.: «resumir nota Obsidian X»).
2. Feedback explícito no UI («resposta útil?») → episódio com `quality_hint`.
3. Job leve «recordar no Obsidian» pós-chat (já parcialmente coberto).
4. RAG: indexar `CHOKMAH/` e injectar contexto no `chat` (política de privacidade).

Personalização rápida: `.env` com `CHOKMAH_AGENT_NAME`, `CHOKMAH_WELCOME_MESSAGE`, e prompts em `AGENT_SYSTEM_PROMPT_SUFFIX`.

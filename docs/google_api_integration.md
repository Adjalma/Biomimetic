# Integração Google APIs - Fase 6: Percepção Multimodal

## Visão Geral
Esta integração conecta o sistema biomimético AI-Biomimetica com Google Calendar API, permitindo percepção do mundo real via calendários, eventos e agendamentos.

## Arquitetura

### Módulos
```
src/google/
├── __init__.py
└── google_calendar_client.py  # Cliente principal
```

### Dependências
Ver `requirements/requirements_google.txt`:
```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib google-auth
```

## Configuração

### 1. Credenciais Google Cloud
1. Acesse [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Projeto: `chokmah-493015` (ou crie novo)
3. Criar credenciais OAuth 2.0 → "Aplicativo da Web"
4. Configurar URLs de redirecionamento:
   - `http://localhost:8000/auth/callback`
   - `http://localhost:8000/oauth2callback`
5. Ativar APIs necessárias:
   - **Calendar API** (obrigatório)
   - Gmail API (opcional)
   - Drive API (opcional)
6. Baixar credenciais como `credentials.json`

### 2. Configuração Local
```bash
# Copiar exemplo de credenciais
cp credentials.example.json credentials.json

# Editar com suas credenciais (NUNCA commitar!)
nano credentials.json

# Instalar dependências
pip install -r requirements/requirements_google.txt
```

### 3. Segurança
- **NUNCA** commitar `credentials.json` ou `token.pickle`
- Ambos estão no `.gitignore`
- Regenerar chaves se expostas publicamente
- Usar variáveis de ambiente em produção

## Uso

### Exemplo Básico
```python
from src.google.google_calendar_client import GoogleCalendarClient

# Inicializar cliente
client = GoogleCalendarClient()

# Autenticar (abrirá browser na primeira vez)
service = client.authenticate()

# Buscar próximos eventos
events = client.get_upcoming_events(10)
for event in events:
    print(client.format_event_for_display(event))
```

### Métodos Principais

#### `get_upcoming_events(max_results=10)`
Retorna próximos eventos do calendário primário.

#### `create_event(event_data)`
Cria novo evento no calendário.

#### `get_today_events()`
Retorna eventos do dia atual.

#### `get_calendar_list()`
Lista todos calendários disponíveis.

## Integração com Sistema Biomimético

### Conexão com Obsidian
```python
from src.google.google_calendar_client import GoogleCalendarClient
from src.app.obsidian_vault import ObsidianVault

# Buscar eventos
client = GoogleCalendarClient()
events = client.get_upcoming_events(5)

# Salvar no Obsidian
obsidian = ObsidianVault()
obsidian.save_note({
    "title": "Próximos Eventos Google Calendar",
    "content": f"Eventos: {events}",
    "tags": ["google-calendar", "percepção-multimodal"]
})
```

### Meta-Learning
Eventos do calendário podem ser usados para:
- Treinamento de priorização contextual
- Otimização de horários biomiméticos
- Aprendizado de padrões de reunião

## Fluxo de Autenticação OAuth2
1. Primeira execução abre browser para login Google
2. Usuário autoriza aplicação
3. Token salvo em `storage/token.pickle`
4. Tokens são reutilizados até expirarem
5. Refresh automático quando expirado

## Troubleshooting

### Erro "invalid_client"
- Verificar `credentials.json` correto
- Confirmar URLs de redirecionamento no Console
- Verificar se APIs estão ativadas

### Erro "access_denied"
- Verificar escopos solicitados
- Usuário precisa autorizar aplicação

### Browser não abre
- Executar em ambiente com interface gráfica
- Usar `flow.run_console()` para modo texto

## Próximos Passos (Fases 6.x)

### Fase 6.1: Leitura de Calendário ✅
- [x] Autenticação OAuth2
- [x] Leitura eventos
- [x] Integração básica

### Fase 6.2: Escrita no Calendário
- [ ] Criação eventos
- [ ] Atualização eventos
- [ ] Exclusão eventos

### Fase 6.3: Gmail API
- [ ] Leitura emails
- [ ] Envio emails
- [ ] Classificação automática

### Fase 6.4: Drive API
- [ ] Leitura documentos
- [ ] Criação documentos
- [ ] Compartilhamento

## Contribuição
- Mantenha `credentials.example.json` atualizado
- Documente novas funcionalidades aqui
- Teste em ambiente isolado antes de produção

## Segurança
- Rotação periódica de chaves OAuth
- Logs de acesso a APIs
- Monitoramento de uso anômalo
- Backup seguro de tokens
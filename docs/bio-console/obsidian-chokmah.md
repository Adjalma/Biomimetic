# Obsidian + Bio Console (fase 1)

Integração por **ficheiros Markdown** no cofre local. O Obsidian lê automaticamente o que a API grava em `OBSIDIAN_CHOKMAH_RELATIVE` (por defeito `CHOKMAH/` dentro do cofre).

## Configuração

| Variável | Descrição |
|----------|-----------|
| `OBSIDIAN_VAULT_ROOT` | Caminho **absoluto** da pasta do cofre (a mesma que abres no Obsidian). |
| `OBSIDIAN_CHOKMAH_RELATIVE` | Subpasta dentro do cofre (default: `CHOKMAH`). |
| `OBSIDIAN_WRITE_TOKEN` | Opcional. Se definido, `POST /api/v1/obsidian/note` exige o cabeçalho `X-Obsidian-Write-Token` com o mesmo valor. |

### Se `obsidian/status` mostra `vault_configured: false`

No Windows, com `uvicorn --reload`, o **processo que responde aos pedidos** pode ser um subprocesso que **não herda** as variáveis que definiste com `$env:...` na mesma janela. Soluções:

1. **Recomendado:** ficheiro **`.env`** na pasta `AI-Biomimetica` com uma linha `OBSIDIAN_VAULT_ROOT=C:\...\Chokma` (copiar de `.env.example`). A API carrega `.env` ao arrancar com **`override=True`**, para valores do ficheiro prevalecerem sobre variáveis de ambiente vazias no Windows (útil também para `ELEVENLABS_*`).
2. Ou desativar reload: `$env:BIO_CONSOLE_RELOAD = "0"` antes de `python scripts/run_bio_console_api.py`.
3. Confirmar que o `Invoke-RestMethod` fala com **esta** instância (porta 8000, servidor ainda a correr).

## API

- `GET /api/v1/obsidian/status` — cofre configurado e pronto para escrita.
- `GET /api/v1/health` — inclui bloco `obsidian` resumido.
- `POST /api/v1/obsidian/note` — corpo JSON:

```json
{
  "relative_path": "episodios/2026-04-10-sessao.md",
  "title": "Sessão CHOKMAH",
  "body": "Resumo ou resposta a arquivar.\n\nPodes usar [[outra nota]] para wikilinks.",
  "tags": ["chokmah", "bio-console"],
  "append": false,
  "frontmatter_extra": { "session_id": "abc-123" }
}
```

- `append: true` — se o ficheiro já existir, acrescenta uma secção com data UTC (sem duplicar o frontmatter inicial).

Restrições: caminho relativo só com `.md`, sem `..`, caracteres seguros (letras, números, `_`, `-`, `.`, `/`).

## O teu cofre (estrutura real)

Se a pasta de projeto for `C:\Users\XBZF\Projetos Triarc\Chokmah`, o Obsidian costuma abrir **uma subpasta** onde está a pasta oculta `.obsidian`. Neste caso o **cofre** é:

`C:\Users\XBZF\Projetos Triarc\Chokmah\Chokma`

(É essa pasta que deves pôr em `OBSIDIAN_VAULT_ROOT`, não o pai `Chokmah`.)

As notas da API ficam por defeito em `...\Chokma\CHOKMAH\` (subpasta criada automaticamente).

## Exemplo rápido (PowerShell)

Na pasta `AI-Biomimetica` do repositório, com o venv ativo:

```powershell
$env:OBSIDIAN_VAULT_ROOT = "C:\Users\XBZF\Projetos Triarc\Chokmah\Chokma"
# opcional: outra subpasta em vez da default CHOKMAH
# $env:OBSIDIAN_CHOKMAH_RELATIVE = "CHOKMAH"

Set-Location "C:\Users\XBZF\Projetos Triarc\IA-autoevolutiva\AI-Biomimetica"
python scripts/run_bio_console_api.py
```

A API usa a porta **8000** por defeito (`BIO_CONSOLE_PORT` para mudar). Teste de gravação:

```powershell
Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:8000/api/v1/obsidian/note" `
  -ContentType "application/json" `
  -Body '{"relative_path":"notas/teste-api.md","body":"Hello CHOKMAH","tags":["teste"]}'
```

Ficheiro criado: `...\Chokma\CHOKMAH\notas\teste-api.md` (reabre o cofre no Obsidian ou espera o refresh).

## Próximos passos (fase 2)

- Botão no frontend “Guardar no Obsidian”.
- Leitura de excertos do cofre para contexto (RAG).
- Plugin [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) apenas se precisares de abrir notas a partir da API.

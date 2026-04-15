# Guia de Configuração - Sistema Biomimético

## ❗ PROBLEMA COMUM
Se você vê a mensagem **"A conexão com localhost foi recusada"** ou **"first. foi inesperado"**, siga ESTE guio.

## 🚀 SOLUÇÃO EM 3 PASSOS

### PASSO 1: INSTALAR DEPENDÊNCIAS ESSENCIAIS
```powershell
.\install_essential.bat
```
**OU** se esse arquivo não existir:
```powershell
# Criar ambiente virtual
python -m venv venv

# Ativar
venv\Scripts\activate.bat

# Instalar pacotes ESSENCIAIS
pip install fastapi uvicorn pydantic numpy requests
```

### PASSO 2: TESTAR INSTALAÇÃO
```powershell
.\test_backend.bat
```
Isso vai abrir uma janela mostrando se há erros. **Mantenha a janela aberta** e veja os erros.

### PASSO 3: INICIAR SISTEMA
```powershell
.\run.bat
```
**Escolha:** `4` (Start Both)

## 🔧 SOLUÇÕES PARA ERROS COMUNS

### Erro: "No module named 'fastapi'"
- Execute o **PASSO 1** acima
- Verifique se o ambiente virtual foi ativado (deve aparecer `(venv)` no prompt)

### Erro: "primeiro. foi inesperado" ou script fecha
- Use **PowerShell** em vez de Command Prompt
- Ou execute o script PowerShell:
  ```powershell
  .\start.ps1
  ```

### Erro: "A conexão com localhost foi recusada"
O backend inicia mas fecha imediatamente. Para ver o erro:

1. Abra uma nova janela **Command Prompt** (cmd.exe)
2. Navegue até a pasta do projeto
3. Execute:
   ```cmd
   venv\Scripts\activate.bat
   python src/core/evolution/evolution_api.py
   ```
4. **Mantenha essa janela aberta** e veja os erros que aparecem

### Erro: "ModuleNotFoundError" para torch, transformers, etc.
Esses são pacotes **opcionais**. Ignore os warnings. O sistema deve funcionar sem eles.

## 📁 ESTRUTURA DE ARQUIVOS

```
Biomimetic/
├── venv/                    # Ambiente virtual (criado automaticamente)
├── src/core/evolution/
│   ├── evolution_api.py     # API principal (BACKEND)
│   ├── genome_mutator.py    # Módulo de mutação
│   └── ... outros módulos
├── frontend/               # Dashboard (se existir)
├── *.bat                   # Scripts de inicialização
└── *.ps1                   # Scripts PowerShell
```

## 🌐 URLs QUANDO FUNCIONAR

- **API Backend:** http://localhost:8000
- **Documentação API:** http://localhost:8000/docs
- **Dashboard Frontend:** http://localhost:3000

## 🔍 VERIFICAÇÃO RÁPIDA

```powershell
# Teste se o backend está respondendo
curl http://localhost:8000/health

# Ou no PowerShell:
Invoke-WebRequest -Uri "http://localhost:8000/health"
```

## 💡 DICA IMPORTANTE

Se nada funcionar, inicie os componentes **manualmente em janelas separadas**:

**Janela 1 - Backend:**
```cmd
cd "C:\Users\XBZF\Projetos Triarc\Biomimetic\Biomimetic"
venv\Scripts\activate.bat
python src/core/evolution/evolution_api.py
```

**Janela 2 - Frontend (se necessário):**
```cmd
cd "C:\Users\XBZF\Projetos Triarc\Biomimetic\Biomimetic\frontend"
npm install
npm run dev
```

**Mantenha ambas as janelas abertas!**

---

## 📞 SUPORTE

Se ainda tiver problemas:
1. Execute `.\test_backend.bat` e envie a saída
2. Ou execute manualmente o backend e envie os erros

**O sistema foi testado e funciona. O problema geralmente é falta de dependências ou ambiente virtual.**
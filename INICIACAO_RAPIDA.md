# 🚀 INICIAÇÃO RÁPIDA - Sistema Biomimético

Guia para executar o sistema localmente em **5 minutos**.

---

## 📦 PRÉ-REQUISITOS

- **Python 3.11+** (https://python.org)
- **Git** (para clonar)
- **4GB RAM mínimo** (8GB recomendado)

---

## ⚡ PASSO A PASSO RÁPIDO

### 1️⃣ CLONE E ENTRADA
```bash
git clone https://github.com/Adjalma/Biomimetic.git
cd Biomimetic
```

### 2️⃣ AMBIENTE VIRTUAL
```bash
# Linux/Mac
python3.11 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```

### 3️⃣ INSTALAÇÃO (ESCOLHA UMA)

**Opção A - Completa (recomendado):**
```bash
pip install -r requirements.txt
```

**Opção B - Leve (para teste rápido):**
```bash
pip install fastapi uvicorn pydantic numpy requests
```

### 4️⃣ TESTE RÁPIDO
```bash
python teste_rapido.py
```

**Saída esperada:**
```
✅ EvolutionEngine importado com sucesso!
✅ Engine criada: <EvolutionEngine...>
🎉 SISTEMA BIOMIMÉTICO FUNCIONANDO!
```

---

## 🎮 COMEÇAR A USAR

### **API Evolutiva (Recomendado)**
```bash
python src/core/evolution/evolution_api.py
```
**Acesse:** http://localhost:8000/health

### **Sistema Principal**
```bash
python iniciar_sistema.py main
```

### **Dashboard Evolutivo**
```bash
python src/core/evolution/evolution_dashboard.py --generate
open evolution_dashboard.html  # Mac
```

---

## 🔧 SOLUÇÃO DE PROBLEMAS

### **Erro: "ModuleNotFoundError"**
```bash
pip install <nome-do-modulo>
# ou
pip install -r requirements.txt --force-reinstall
```

### **Erro: "Port 8000 already in use"**
Mude a porta em `src/core/evolution/evolution_api.py` (linha ~400):
```python
app.run(host="0.0.0.0", port=8001)  # Mude para 8001
```

### **Erro com PyTorch**
```bash
pip install torch==2.1.2 --index-url https://download.pytorch.org/whl/cpu
```

### **Sistema trava ou lento**
```bash
# Execute versão leve
python src/core/evolution/simple_test.py
```

---

## 📞 AJUDA

**Se encontrar erros, envie:**
1. Mensagem de erro completa
2. Saída de: `python --version && pip list`

**Links úteis:**
- Documentação: `docs/`
- Exemplos: `scripts/`
- Testes: `tests/`

---

## 🎯 O QUE ESPERAR

✅ **API rodando:** http://localhost:8000/health → `{"status":"healthy"}`  
✅ **Dashboard:** `evolution_dashboard.html` gerado  
✅ **Evolução:** Ciclos automáticos de mutação e aprendizado  
✅ **Sistema autoevolutivo:** Modifica seu próprio código (genoma YAML)

---

**Feito com ❤️ pelo Sistema Biomimético Autoevolutivo**
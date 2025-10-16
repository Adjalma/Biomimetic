# 🤝 Guia de Contribuição

Obrigado por considerar contribuir para o Sistema de IA Autoevolutiva Biomimética! Este documento fornece diretrizes e informações para contribuidores.

## 📋 Índice

- [Como Contribuir](#como-contribuir)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Padrões de Código](#padrões-de-código)
- [Processo de Pull Request](#processo-de-pull-request)
- [Reportar Bugs](#reportar-bugs)
- [Solicitar Features](#solicitar-features)

## 🚀 Como Contribuir

### 1. Fork e Clone

```bash
# Fork o repositório no GitHub
# Clone seu fork localmente
git clone https://github.com/SEU-USUARIO/AI-Biomimetica.git
cd AI-Biomimetica

# Adicione o repositório original como upstream
git remote add upstream https://github.com/Adjalma/AI-Biomimetica.git
```

### 2. Configuração do Ambiente

```bash
# Criar ambiente virtual
python -m venv venv_ai_py311

# Ativar ambiente virtual (Windows)
venv_ai_py311\Scripts\activate

# Ativar ambiente virtual (Linux/Mac)
source venv_ai_py311/bin/activate

# Instalar dependências
pip install -r requirements/requirements_final.txt

# Instalar dependências de desenvolvimento
pip install -r requirements/requirements_dev.txt
```

### 3. Criar Branch

```bash
# Atualizar main
git checkout main
git pull upstream main

# Criar nova branch para sua feature
git checkout -b feature/nome-da-feature
```

## 📝 Padrões de Código

### Python

- **PEP 8**: Seguir as convenções de estilo Python
- **Type Hints**: Obrigatórios em todas as funções públicas
- **Docstrings**: Documentação completa em português
- **Imports**: Organizados (stdlib, third-party, local)

```python
def exemplo_funcao(parametro: str) -> Dict[str, Any]:
    """
    Exemplo de função bem documentada.
    
    Args:
        parametro: Descrição do parâmetro
        
    Returns:
        Dicionário com os resultados
        
    Raises:
        ValueError: Quando o parâmetro é inválido
    """
    pass
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

def funcao_com_log():
    logger.info("Iniciando processamento")
    try:
        # código aqui
        logger.debug("Processamento concluído")
    except Exception as e:
        logger.error(f"Erro no processamento: {e}")
        raise
```

### Testes

- **Cobertura**: Mínimo 80% para novas funcionalidades
- **Nomenclatura**: `test_nome_da_funcao`
- **Estrutura**: Arrange, Act, Assert

```python
import pytest
from src.app.main import MainAI

def test_inicializacao_sistema():
    """Testa a inicialização do sistema principal."""
    # Arrange
    ai_system = MainAI()
    
    # Act
    result = ai_system.initialize_system()
    
    # Assert
    assert result is True
    assert ai_system.is_initialized is True
```

## 🔄 Processo de Pull Request

### 1. Desenvolvimento

```bash
# Fazer commits pequenos e descritivos
git add .
git commit -m "feat: adiciona nova funcionalidade X"

# Push para sua branch
git push origin feature/nome-da-feature
```

### 2. Mensagens de Commit

Use o padrão Conventional Commits:

- `feat:` Nova funcionalidade
- `fix:` Correção de bug
- `docs:` Documentação
- `style:` Formatação
- `refactor:` Refatoração
- `test:` Testes
- `chore:` Tarefas de manutenção

### 3. Pull Request

1. **Título**: Descritivo e claro
2. **Descrição**: 
   - O que foi implementado
   - Por que foi implementado
   - Como testar
   - Screenshots (se aplicável)
3. **Checklist**: Marcar todos os itens

```markdown
## 📝 Descrição

Implementa nova funcionalidade de análise de performance.

## 🎯 Motivação

Melhorar o monitoramento do sistema em tempo real.

## 🧪 Como Testar

1. Execute `python src/app/main.py`
2. Acesse o dashboard em `http://localhost:8000`
3. Verifique as métricas de performance

## ✅ Checklist

- [x] Código segue padrões PEP 8
- [x] Testes unitários adicionados
- [x] Documentação atualizada
- [x] Logs adicionados
- [x] Type hints implementados
```

## 🐛 Reportar Bugs

Use o template de issue para bugs:

```markdown
## 🐛 Descrição do Bug

Descrição clara e concisa do problema.

## 🔄 Passos para Reproduzir

1. Vá para '...'
2. Clique em '...'
3. Role até '...'
4. Veja o erro

## 🎯 Comportamento Esperado

Descrição do que deveria acontecer.

## 📸 Screenshots

Se aplicável, adicione screenshots.

## 💻 Ambiente

- OS: [ex: Windows 10]
- Python: [ex: 3.11.0]
- Versão: [ex: 2.0.0]

## 📋 Logs

```
Cole aqui os logs relevantes
```

## ✅ Checklist

- [ ] Verifiquei se o bug já foi reportado
- [ ] Incluí informações suficientes para reproduzir
- [ ] Adicionei logs relevantes
```

## 💡 Solicitar Features

Use o template de issue para features:

```markdown
## 💡 Feature Request

### 📝 Descrição

Descrição clara e concisa da feature solicitada.

### 🎯 Problema que Resolve

Que problema esta feature resolveria?

### 💭 Solução Proposta

Descrição da solução que você gostaria de ver.

### 🔄 Alternativas Consideradas

Outras soluções que você considerou.

### 📋 Contexto Adicional

Qualquer outro contexto sobre a feature.
```

## 🔍 Code Review

### Para Revisores

- **Seja construtivo**: Foque no código, não na pessoa
- **Explique o porquê**: Justifique suas sugestões
- **Seja específico**: Indique linhas e arquivos
- **Aprenda**: Code review é uma oportunidade de aprendizado

### Para Autores

- **Seja receptivo**: Feedback é para melhorar o código
- **Responda**: Discuta pontos levantados
- **Aprenda**: Use feedback para melhorar futuras contribuições

## 📚 Recursos Adicionais

- [PEP 8 - Style Guide](https://pep8.org/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Pytest Documentation](https://docs.pytest.org/)

## ❓ Dúvidas?

Se você tem dúvidas sobre como contribuir:

1. Verifique a documentação em `docs/`
2. Procure em issues existentes
3. Abra uma issue para discussão
4. Entre em contato com os mantenedores

---

**Obrigado por contribuir! 🎉**

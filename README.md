# 🧠 Sistema de IA Autoevolutiva Biomimética

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Desenvolvimento-yellow.svg)](https://github.com/Adjalma/AI-Biomimetica)

## 📋 Visão Geral

Este é um sistema avançado de Inteligência Artificial autoevolutiva inspirado em processos biomiméticos naturais. O sistema combina algoritmos genéticos, redes neurais evolutivas e sistemas V2 integrados para criar uma IA que evolui e se adapta continuamente.

### ✨ Características Principais

- **🤖 IA Autoevolutiva**: Sistema que evolui e se adapta automaticamente
- **🧬 Algoritmos Genéticos**: Implementação biomimética de evolução
- **🔍 Busca Vetorial FAISS**: Sistema de busca semântica avançada
- **📊 Dashboard GIC**: Interface para Geração Inteligente de Conteúdo
- **🛡️ Sistemas V2**: Arquitetura modular e escalável
- **📈 Monitoramento em Tempo Real**: Métricas e logs detalhados

## 🏗️ Arquitetura do Sistema

### Estrutura de Diretórios

```
Projeto_AI2/
├── src/                          # Código fonte principal
│   ├── app/                      # Aplicações principais
│   │   ├── main.py              # Sistema principal da IA
│   │   ├── main_optimized.py    # Versão otimizada do sistema
│   │   ├── app_gic.py           # Dashboard web GIC
│   │   ├── gic_ia_integrada.py  # Sistema GIC integrado
│   │   └── iniciar_gic_ia.py    # Script de inicialização
│   ├── core/                     # Núcleo da IA evolutiva
│   │   ├── ia_evolutiva_compativel.py
│   │   └── main_evolutivo_compativel.py
│   ├── agents/                   # Agentes especializados
│   │   └── sistema_principal/
│   ├── faiss_engine/             # Sistema FAISS para busca vetorial
│   │   ├── biblioteca_central_faiss.py
│   │   ├── sistema_agentes_faiss_integrado.py
│   │   └── sistema_faiss_enterprise.py
│   ├── knowledge_bus/            # Barramento de conhecimento
│   │   ├── barramento_conhecimento_unificado.py
│   │   └── guardiao_conhecimento.py
│   ├── pipelines/                # Pipelines de processamento
│   │   ├── ia_pipeline/         # Pipeline principal de IA
│   │   ├── gerador_procedimentos_academia.py
│   │   └── gic_justificativas.py
│   ├── systems/                  # Sistemas integrados
│   │   ├── sistemas/            # Sistemas V2
│   │   └── integrar_frameworks_ia.py
│   ├── utils/                    # Utilitários
│   ├── config/                   # Configurações
│   │   ├── config_optimized.py
│   │   ├── sistema_config.json
│   │   └── utilizacao.json
│   └── templates/                # Templates HTML
│       ├── dashboard.html
│       └── gic_dashboard.html
├── storage/                      # Dados persistentes
│   ├── databases/                # Bancos de dados
│   ├── logs/                     # Logs do sistema
│   ├── backups/                  # Backups
│   ├── indices/                  # Índices FAISS
│   ├── outputs/                  # Saídas e relatórios
│   └── models/                   # Modelos treinados
├── tests/                        # Testes automatizados
├── scripts/                      # Scripts de execução
├── docs/                         # Documentação
├── requirements/                 # Dependências
└── venv_ai_py311/               # Ambiente virtual principal
```

## 🚀 Início Rápido

### 📋 Pré-requisitos

- Python 3.11 ou superior
- Git
- 8GB RAM mínimo (recomendado 16GB)
- 10GB espaço em disco

### 1. Clonagem e Configuração

```bash
# Clonar o repositório
git clone https://github.com/Adjalma/AI-Biomimetica.git
cd AI-Biomimetica

# Criar ambiente virtual
python -m venv venv_ai_py311

# Ativar ambiente virtual (Windows)
venv_ai_py311\Scripts\activate

# Ativar ambiente virtual (Linux/Mac)
source venv_ai_py311/bin/activate

# Instalar dependências
pip install -r requirements/requirements_final.txt
```

### 2. Configuração Inicial

```bash
# Executar script de validação
python scripts/validar_sistema.py

# Inicializar sistema
python iniciar_sistema.py
```

### 3. Executar Sistema Principal

```bash
# Sistema principal da IA
python src/app/main.py

# Versão otimizada
python src/app/main_optimized.py

# Dashboard GIC
python src/app/app_gic.py
```

### 4. Inicializar GIC com IA

```bash
# Inicialização completa do GIC
python src/app/iniciar_gic_ia.py
```

## 🔧 Componentes Principais

### 1. Sistema Evolutivo Principal (`src/app/main.py`)

**Função**: Coordena todos os componentes do sistema de IA autoevolutiva.

**Funcionalidades**:
- Execução de ciclos evolutivos controlados
- Integração com sistemas V2
- Monitoramento de performance em tempo real
- Salvamento automático de estados

**Como usar**:
```python
from src.app.main import MainAI

# Criar instância do sistema
ai_system = MainAI()

# Inicializar sistema
ai_system.initialize_system()

# Executar evolução
ai_system.run_evolution(generations=10)
```

### 2. Sistema GIC Integrado (`src/app/gic_ia_integrada.py`)

**Função**: Sistema de Geração Inteligente de Conteúdo com IA integrada.

**Funcionalidades**:
- Geração de justificativas contratuais
- Análise de aderência legal
- Simulação de cenários contrafactuais
- Integração com barramento de conhecimento

**Como usar**:
```python
from src.app.gic_ia_integrada import GICIAIntegrada

# Criar instância do GIC
gic = GICIAIntegrada()

# Gerar justificativa
resultado = gic.gerar_justificativa_avancada(
    objeto_aditivo="Aquisição de equipamentos",
    valor=1000000,
    justificativa_base="Necessidade operacional"
)
```

### 3. Barramento de Conhecimento (`src/knowledge_bus/`)

**Função**: Gerencia e protege dados críticos do sistema.

**Funcionalidades**:
- Armazenamento seguro de conhecimento
- Versionamento de dados
- Auditoria de acesso
- Integração com FAISS

### 4. Sistema FAISS (`src/faiss_engine/`)

**Função**: Busca vetorial e indexação de conhecimento.

**Funcionalidades**:
- Indexação de documentos
- Busca semântica
- Clustering de dados
- Integração com sistemas V2

## 📊 Sistemas V2 Integrados

### 1. Guardião de Conhecimento
- **Função**: Protege e gerencia dados críticos
- **Localização**: `src/knowledge_bus/guardiao_conhecimento.py`

### 2. Simulador Contrafactual
- **Função**: Testa cenários alternativos
- **Localização**: `src/systems/simulador_contrafactual.py`

### 3. Academia de Agentes
- **Função**: Treina e especializa agentes IA
- **Localização**: `src/systems/sistemas/academia_agentes.py`

### 4. Minerador de Padrões
- **Função**: Descobre padrões em dados complexos
- **Localização**: `src/pipelines/gerador_procedimentos_academia.py`

### 5. Gerador de Procedimentos
- **Função**: Cria procedimentos automatizados
- **Localização**: `src/pipelines/gerador_procedimentos_academia.py`

## 🔍 Monitoramento e Logs

### Logs do Sistema
- **Localização**: `storage/logs/`
- **Arquivos principais**:
  - `main_system.log`: Logs do sistema principal
  - `gic_ia.log`: Logs do sistema GIC
  - `evolutionary_ai.log`: Logs da evolução

### Métricas de Performance
- Fitness médio por geração
- Tempo de execução
- Uso de recursos
- Status dos sistemas V2

## 🛠️ Configuração Avançada

### Arquivos de Configuração
- `src/config/config_optimized.py`: Configurações otimizadas
- `src/config/sistema_config.json`: Configurações do sistema
- `src/config/utilizacao.json`: Configurações de utilização

### Parâmetros Principais
```python
config = {
    'population_size': 50,        # Tamanho da população
    'mutation_rate': 0.1,         # Taxa de mutação
    'crossover_rate': 0.8,        # Taxa de crossover
    'max_generations': 100,       # Máximo de gerações
    'fitness_threshold': 0.95     # Limiar de fitness
}
```

## 🧪 Testes

### Executar Testes
```bash
# Executar todos os testes
python -m pytest tests/

# Teste específico
python tests/test_gic_functionality.py
```

### Testes Disponíveis
- `test_gic_functionality.py`: Testes do sistema GIC
- `testar_integracao_v2.py`: Testes de integração V2
- `testar_sistemas_v2.py`: Testes dos sistemas V2

## 📈 Performance e Otimização

### Otimizações Implementadas
- Paralelização de operações
- Cache inteligente
- Compressão de dados
- Indexação otimizada

### Monitoramento de Recursos
- Uso de CPU e memória
- Tempo de resposta
- Throughput de processamento
- Qualidade das soluções

## 🔒 Segurança

### Medidas de Segurança
- Criptografia de dados sensíveis
- Controle de acesso baseado em roles
- Auditoria de operações
- Backup automático

### Dados Protegidos
- Conhecimento crítico
- Configurações do sistema
- Logs de auditoria
- Modelos treinados

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, siga estas diretrizes:

### 📝 Como Contribuir

1. **Fork** o repositório
2. **Clone** seu fork localmente
3. **Crie** uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
4. **Commit** suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
5. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
6. **Abra** um Pull Request

### 📋 Padrões de Código

- **Documentação**: Completa em português
- **Type Hints**: Obrigatórios em todas as funções
- **Logging**: Estruturado com níveis apropriados
- **Testes**: Unitários obrigatórios para novas funcionalidades
- **Formatação**: Seguir PEP 8

### 🐛 Reportar Bugs

Use o sistema de [Issues](https://github.com/Adjalma/AI-Biomimetica/issues) para reportar bugs. Inclua:

- Descrição detalhada do problema
- Passos para reproduzir
- Ambiente (OS, Python version)
- Logs relevantes

## 📚 Documentação

### 📖 Documentação Adicional
- [`docs/`](docs/): Documentação técnica completa
- [`docs/README_SISTEMAS_V2.md`](docs/README_SISTEMAS_V2.md): Sistemas V2
- [`docs/README_INTEGRACAO_V2.md`](docs/README_INTEGRACAO_V2.md): Guia de integração
- [`docs/ANALISE_SISTEMA_IA_REAL.md`](docs/ANALISE_SISTEMA_IA_REAL.md): Análise do sistema

### 🔍 Debug e Troubleshooting

- **Logs**: Verificar em `storage/logs/`
- **Debug**: Usar nível DEBUG para diagnóstico
- **Métricas**: Monitorar performance em tempo real
- **Validação**: Executar `python scripts/validar_sistema.py`

## 📊 Roadmap

### 🎯 Versão 3.0 (Próxima)
- [ ] Interface web completa
- [ ] API REST para integração
- [ ] Sistema de plugins
- [ ] Machine Learning pipelines

### ✅ Versão 2.0 (Atual)
- [x] Reorganização da estrutura
- [x] Integração de sistemas V2
- [x] Otimizações de performance
- [x] Documentação completa

### 📜 Versão 1.0
- [x] Sistema base de IA evolutiva
- [x] Implementação inicial do GIC
- [x] Estrutura básica de componentes

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **Desenvolvedor Principal** - [Adjalma](https://github.com/Adjalma)

## 🙏 Agradecimentos

- Comunidade Python
- Bibliotecas de IA/ML open source
- Contribuidores do projeto

---

<div align="center">

**Desenvolvido com ❤️ para evolução contínua da Inteligência Artificial**

[![GitHub stars](https://img.shields.io/github/stars/Adjalma/AI-Biomimetica.svg?style=social&label=Star)](https://github.com/Adjalma/AI-Biomimetica)
[![GitHub forks](https://img.shields.io/github/forks/Adjalma/AI-Biomimetica.svg?style=social&label=Fork)](https://github.com/Adjalma/AI-Biomimetica)

</div>

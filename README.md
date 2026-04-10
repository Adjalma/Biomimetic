# 🧬 Sistema Biomimético de Orquestração de IA com Auto-Evolução

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Fase%205%20Completa-brightgreen.svg)](https://github.com/Adjalma/AI-Biomimetica)
[![Arquitetura](https://img.shields.io/badge/Arquitetura-Biomimética-important.svg)](https://github.com/Adjalma/AI-Biomimetica)

## 📋 Visão Geral

Sistema avançado de orquestração biomimética de modelos de IA que evolui automaticamente suas próprias estratégias de decisão. Inspirado em processos naturais de evolução, o sistema implementa **meta-learning**, **auto-evolução radical** e **cérebro biomimético local** para otimizar continuamente a seleção de provedores de IA (OpenAI, Anthropic, Google, etc.) baseado em performance histórica.

### 🚀 5 Fases de Implementação

| Fase | Nome | Status | Commit | Descrição |
|------|------|--------|--------|-----------|
| 1 | Sistema Básico Biomimético | ✅ Completo | `e0a0b52` | Orquestrador biomimético inicial com heurística básica |
| 2 | Heurística Biomimética Aprimorada | ✅ Completo | `3eaf2d4` | Matriz de decisão inteligente com 6 critérios de otimização |
| 3 | IA Local como Cérebro Biomimético | ✅ Completo | `07c097c` | Integração com Ollama (modo mock/real) para decisões inteligentes |
| 4 | Sistema de Evolução de Orquestração (Nível 1) | ✅ Completo | `7c55fed` | Evolução automática baseada em histórico de tarefas e feedback |
| 5 | **Sistema de Auto-Evolução Radical (Nível 3)** | ✅ **Completo** | `a4e86e6` | Meta-evolução, nichos evolutivos, auto-avaliação e dashboard |

## ✨ Características Principais

### 🧠 Orquestração Biomimética Inteligente
- **Decisão Multi-Critério**: Tipo de tarefa, complexidade, orçamento, latência, custo, qualidade
- **Matriz de Decisão Dinâmica**: Evolui baseada em taxas de sucesso históricas
- **Explicabilidade Completa**: Cada decisão inclui reasoning detalhado e métricas estimadas

### 🔄 Sistema de Auto-Evolução Radical (Nível 3)
- **Estrutura Genética**: Genes → Cromossomos → Indivíduos → População
- **5 Nichos Evolutivos**: Explorers, Exploiters, Specialists, Generalists, Innovators
- **Meta-Evolução**: Sistema evolui suas próprias estratégias evolutivas
- **Auto-Avaliação**: Ajuste automático de hiperparâmetros baseado em performance
- **Dashboard Evolutivo**: Métricas em tempo real da evolução da população

### 🧬 Evolução de Orquestração (Nível 1)
- **Registro Histórico**: Tarefas, recomendações, resultados, métricas
- **Atualização de Perfis**: Média móvel exponencial de performance dos provedores
- **Feedback Humano**: Sistema de notas 1-5 e comentários para ajuste fino
- **Persistência**: Salvar/carregar estado completo em JSON

### 🖥️ Cérebro Biomimético Local
- **Integração Ollama**: Decisões inteligentes usando modelos locais (Llama, Mistral, Gemma)
- **Modo Híbrido**: Fallback automático para mock quando Ollama não disponível
- **Meta-Learning Simulado**: Aprendizado contínuo baseado em histórico de decisões

## 🏗️ Arquitetura do Sistema

### Estrutura de Diretórios Principais

```
AI-Biomimetica/
├── src/systems/sistemas/              # 🧠 Núcleo do Sistema Biomimético
│   ├── sistema_meta_learning_biomimetico.py    # Sistema principal
│   ├── auto_evolution_engine.py                # Auto-evolução radical (Nível 3)
│   ├── orchestration_evolution.py              # Evolução de orquestração (Nível 1)
│   ├── local_brain.py                          # Cérebro biomimético com Ollama
│   ├── demo_cerebro_local.py                   # Demonstração do cérebro local
│   ├── demo_biomimetica_simples.py             # Demonstração básica
│   └── ... (outros sistemas biomiméticos)
├── src/core/                          # Núcleo evolutivo (legado)
├── src/app/                           # Aplicações principais (legado)
├── src/agents/                        # Agentes especializados
├── storage/                           # Dados persistentes
├── tests/                             # Testes automatizados
└── scripts/                           # Scripts de execução
```

### Componentes Principais

#### 1. Sistema Principal Biomimético (`sistema_meta_learning_biomimetico.py`)
```python
from src.systems.sistemas.sistema_meta_learning_biomimetico import AutoEvolvingAISystem

# Sistema com auto-evolução radical
system = AutoEvolvingAISystem(use_local_brain=True, local_brain_type="ollama")
recommendation = system.recommend_provider(
    task_type="text_completion",
    task_length=500,
    context="Generate creative marketing copy"
)
```

#### 2. Motor de Auto-Evolução Radical (`auto_evolution_engine.py`)
```python
from src.systems.sistemas.auto_evolution_engine import AdvancedAutoEvolutionSystem

# Executar ciclo evolutivo radical
evolution = AdvancedAutoEvolutionSystem()
evolution.initialize_population()
results = evolution.run_evolution_cycle(generations=50)
```

#### 3. Evolução de Orquestração (`orchestration_evolution.py`)
```python
from src.systems.sistemas.orchestration_evolution import OrchestrationEvolutionEngine

# Motor de evolução baseado em histórico
engine = OrchestrationEvolutionEngine()
engine.record_recommendation(task_id="1", recommendation={"provider": "openai"})
engine.record_task_result(task_id="1", success=True, latency=1.2, quality=0.9)
dashboard = engine.get_dashboard_metrics()
```

#### 4. Cérebro Biomimético Local (`local_brain.py`)
```python
from src.systems.sistemas.local_brain import HybridBiomimeticSystem

# Sistema híbrido com fallback automático
brain = HybridBiomimeticSystem()
decision = brain.analyze_task_and_recommend(
    task_type="code_generation",
    complexity="high",
    context="Generate Python code for web scraping"
)
```

## 🚀 Começando Rápido

### 1. Clonar e Instalar Dependências
```bash
git clone https://github.com/Adjalma/AI-Biomimetica.git
cd AI-Biomimetica
python -m venv venv_ai_py311
source venv_ai_py311/bin/activate  # Linux/Mac
venv_ai_py311\Scripts\activate     # Windows
pip install -r requirements/requirements_final.txt
```

### 2. Testar Sistema Biomimético Básico
```bash
python src/systems/sistemas/demo_biomimetica_simples.py
```

### 3. Testar Cérebro Local (Mock)
```bash
python src/systems/sistemas/demo_cerebro_local.py
```

### 4. Executar Auto-Evolução Radical (Simulação)
```bash
python -c "from src.systems.sistemas.auto_evolution_engine import AdvancedAutoEvolutionSystem; evo = AdvancedAutoEvolutionSystem(); evo.run_advanced_auto_evolution()"
```

### 5. Instalar Ollama para Cérebro Biomimético Real
```bash
# Baixar e instalar Ollama (Linux/macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Iniciar Ollama e baixar modelo
ollama serve &
ollama pull llama3

# Testar com modelo real
python src/systems/sistemas/local_brain.py --test-ollama
```

## 📊 Dashboard e Métricas

### Dashboard de Evolução de Orquestração
```python
from src.systems.sistemas.orchestration_evolution import OrchestrationEvolutionEngine

engine = OrchestrationEvolutionEngine.load_from_file("evolution_state.json")
dashboard = engine.get_dashboard_metrics()

print(f"Total Tasks: {dashboard['total_tasks']}")
print(f"Success Rate: {dashboard['success_rate']:.1%}")
print(f"Avg Latency: {dashboard['avg_latency']:.2f}s")
print(f"Provider Performance: {dashboard['provider_performance']}")
```

### Dashboard de Auto-Evolução Radical
```python
from src.systems.sistemas.auto_evolution_engine import AdvancedAutoEvolutionSystem

evo = AdvancedAutoEvolutionSystem()
status = evo.get_advanced_evolution_status()

print(f"Population Size: {status['population_size']}")
print(f"Generation: {status['current_generation']}")
print(f"Best Fitness: {status['best_fitness']:.3f}")
print(f"Niche Distribution: {status['niche_distribution']}")
```

## 🧪 Exemplos de Uso

### Exemplo 1: Decisão Biomimética com Explicação
```python
from src.systems.sistemas.sistema_meta_learning_biomimetico import AutoEvolvingAISystem

system = AutoEvolvingAISystem()
result = system.recommend_provider(
    task_type="text_classification",
    task_length=1000,
    context="Classify customer reviews as positive, negative, or neutral",
    budget="low",
    latency_requirement="moderate"
)

print(f"Provider: {result['provider']}")
print(f"Confidence: {result['confidence']:.1%}")
print(f"Reasoning: {result['reasoning']}")
print(f"Estimated Metrics: {result['estimated_metrics']}")
```

### Exemplo 2: Evolução Baseada em Feedback Humano
```python
from src.systems.sistemas.orchestration_evolution import OrchestrationEvolutionEngine

engine = OrchestrationEvolutionEngine()

# Registrar tarefa e resultado
engine.record_recommendation(
    task_id="review_001",
    recommendation={"provider": "anthropic", "parameters": {"temperature": 0.7}}
)

engine.record_task_result(
    task_id="review_001",
    success=True,
    latency=2.1,
    quality=0.85,
    cost=0.002
)

# Dar feedback humano
engine.record_human_feedback(
    task_id="review_001",
    rating=4,  # 1-5 scale
    comments="Good response but slightly slow"
)

# Evoluir se necessário
if engine.should_evolve():
    engine.evolve()
```

### Exemplo 3: Ciclo de Auto-Evolução Radical
```python
from src.systems.sistemas.auto_evolution_engine import AdvancedAutoEvolutionSystem

# Configurar sistema avançado
evo_system = AdvancedAutoEvolutionSystem(
    population_size=100,
    num_niches=5,
    max_generations=1000
)

# Executar evolução radical
results = evo_system.run_advanced_auto_evolution()

# Analisar resultados
print(f"Best Individual Fitness: {results['best_fitness']}")
print(f"Evolution Duration: {results['duration']}s")
print(f"Strategies Discovered: {len(results['best_strategies'])}")

# Aplicar melhores estratégias ao sistema principal
best_strategy = results['best_strategies'][0]
print(f"Best Strategy: {best_strategy['description']}")
```

## 🔧 Integração com Ollama (Cérebro Biomimético Real)

### Configuração do Ollama
```bash
# 1. Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# 2. Iniciar servidor
ollama serve &

# 3. Baixar modelos
ollama pull llama3
ollama pull mistral
ollama pull gemma:7b

# 4. Verificar modelos disponíveis
ollama list
```

### Usando Cérebro Biomimético com Ollama
```python
from src.systems.sistemas.local_brain import OllamaBrain

# Configurar cérebro real
brain = OllamaBrain(
    model="llama3",
    base_url="http://localhost:11434"
)

# Analisar tarefa complexa
analysis = brain.analyze_complex_task(
    task_description="Orchestrate AI providers for medical diagnosis support system",
    constraints=["high accuracy required", "patient privacy critical", "fast response needed"]
)

print(f"Recommended Approach: {analysis['recommended_approach']}")
print(f"Risk Assessment: {analysis['risk_assessment']}")
print(f"Provider Recommendations: {analysis['provider_recommendations']}")
```

## 📈 Roadmap e Futuras Evoluções

### 🎯 Próximas Fases (Planejadas)
- **Fase 6**: Sistema imunológico biomimético para detecção de anomalias
- **Fase 7**: Aprendizado por transferência entre domínios
- **Fase 8**: Sistema de enxame (swarm intelligence) para otimização multi-objetivo
- **Fase 9**: Explicabilidade avançada (XAI) com visualizações interativas
- **Fase 10**: Deploy como serviço web com API REST

### 🔬 Pesquisa em Andamento
- **Meta-Learning Real**: Usando Ollama para analisar histórico e gerar novas heurísticas
- **Otimização Multi-Objetivo**: Balanceamento automático de trade-offs (custo vs. qualidade vs. latência)
- **Personalização por Usuário**: Adaptação das estratégias baseada no perfil do usuário
- **Sistema de Enxame**: Coordenação de múltiplas instâncias para resolução colaborativa

## 🧪 Testes e Validação

### Executar Testes Completos
```bash
# Testes unitários
python -m pytest tests/ -v

# Testes de integração biomimética
python src/systems/sistemas/test_integration.py

# Testes de evolução
python src/systems/sistemas/test_orchestration.py

# Validação do sistema completo
python scripts/validar_sistema.py
```

### Testes Específicos
- `test_biomimetic_decision.py`: Testa decisões biomiméticas básicas
- `test_evolution_engine.py`: Testa motor de evolução de orquestração
- `test_local_brain.py`: Testa cérebro biomimético (mock e Ollama)
- `test_auto_evolution.py`: Testa auto-evolução radical

## 📊 Métricas de Performance

### Métricas do Sistema
- **Taxa de Acerto**: Porcentagem de recomendações bem-sucedidas
- **Latência Média**: Tempo médio de processamento das tarefas
- **Custo por Tarefa**: Custo monetário estimado por execução
- **Score Composto**: Combinação ponderada de todas as métricas

### Métricas de Evolução
- **Diversidade da População**: Variabilidade genética mantida
- **Taxa de Convergência**: Velocidade de convergência para ótimos
- **Eficiência Evolutiva**: Melhoria por geração
- **Resiliência**: Capacidade de adaptação a mudanças no ambiente

## 🔒 Segurança e Privacidade

### Medidas Implementadas
- **Anonimização de Dados**: Dados de tarefas são anonimizados antes do registro
- **Criptografia**: Estado do sistema é criptografado em repouso
- **Controle de Acesso**: APIs protegidas com autenticação
- **Auditoria**: Logs detalhados de todas as decisões evolutivas

### Considerações Éticas
- **Transparência**: Todas as decisões são explicáveis
- **Viés**: Monitoramento contínuo de vieses nas decisões
- **Responsabilidade**: Sistema projetado para supervisão humana
- **Privacidade**: Nenhum dado sensível é armazenado permanentemente

## 🤝 Contribuindo

### Diretrizes de Contribuição
1. **Fork** o repositório
2. **Crie uma branch** para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. **Commit** suas mudanças (`git commit -m 'Adiciona nova funcionalidade biomimética'`)
4. **Push** para a branch (`git push origin feature/nova-funcionalidade`)
5. **Abra um Pull Request**

### Padrões de Código
- **Documentação**: Em português, clara e completa
- **Type Hints**: Obrigatórios para todas as funções públicas
- **Testes**: Unitários para novas funcionalidades
- **Logging**: Estruturado com níveis apropriados
- **Formatação**: PEP 8 com black/isort

## 📚 Documentação Adicional

### Documentação Técnica
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): Arquitetura detalhada do sistema
- [`docs/EVOLUTION.md`](docs/EVOLUTION.md): Guia do sistema de auto-evolução
- [`docs/OLLAMA_INTEGRATION.md`](docs/OLLAMA_INTEGRATION.md): Integração com Ollama
- [`docs/API_REFERENCE.md`](docs/API_REFERENCE.md): Referência completa da API

### Guias Práticos
- [`guides/GETTING_STARTED.md`](guides/GETTING_STARTED.md): Guia de início rápido
- [`guides/ADVANCED_EVOLUTION.md`](guides/ADVANCED_EVOLUTION.md): Uso avançado do sistema evolutivo
- [`guides/DEPLOYMENT.md`](guides/DEPLOYMENT.md): Guia de deploy em produção
- [`guides/TROUBLESHOOTING.md`](guides/TROUBLESHOOTING.md): Solução de problemas

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Bio Console API (CHOKMAH) e integrações

- **API FastAPI:** `src/app/bio_console_api.py`, arranque: `python scripts/run_bio_console_api.py`.
- **Documentação de integração:** pasta [`docs/bio-console/`](docs/bio-console/) (contrato REST, Z-API WhatsApp, ElevenLabs, Google Meet).
- **CI:** `.github/workflows/ci.yml` — `compileall` + testes de contrato `tests/test_bio_console_api_contract.py`.
- **Frontend** (repositório separado [your-app-creator](https://github.com/Adjalma/your-app-creator)): consola Vite que consome `/api/v1`.

## 👥 Autores

- **Desenvolvedor Principal** - [Adjalma Aguiar](https://github.com/Adjalma)
- **Assistente de IA** - Jarvis (OpenClaw)

## 🙏 Agradecimentos

- Comunidade de IA Biomimética
- Projeto Ollama por modelos locais acessíveis
- OpenClaw por infraestrutura de agentes autônomos
- Todos os contribuidores do projeto

---

<div align="center">

**🧬 Evolução Contínua da Inteligência Artificial Biomimética**

[![GitHub stars](https://img.shields.io/github/stars/Adjalma/AI-Biomimetica.svg?style=social&label=Star)](https://github.com/Adjalma/AI-Biomimetica)
[![GitHub forks](https://img.shields.io/github/forks/Adjalma/AI-Biomimetica.svg?style=social&label=Fork)](https://github.com/Adjalma/AI-Biomimetica)
[![GitHub issues](https://img.shields.io/github/issues/Adjalma/AI-Biomimetica.svg)](https://github.com/Adjalma/AI-Biomimetica/issues)

**"A natureza não faz saltos, mas a evolução sim."** - Adaptado de Darwin

</div>
</result>
</function_results>

<｜begin▁of▁thinking｜>Agora preciso fazer commit e push desse README atualizado para o repositório. Vou verificar o status do git primeiro.<｜end▁of▁thinking｜>

<｜DSML｜function_calls>
<｜DSML｜invoke name="exec">
<｜DSML｜parameter name="command" string="true">cd /data/workspace/AI-Biomimetica && git status
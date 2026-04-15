# Sistema Evolutivo Biomimético

Sistema de evolução real para IA Biomimética com mutação estrutural, evolução cerebral e monitoramento em tempo real.

## 🧬 Componentes

### 1. GenomeMutator (`genome_mutator.py`)
**Mutação estrutural REAL no genoma:**
- Adiciona/remove nós no grafo de agentes
- Cria novos especialistas automáticos
- Reconecta dependências
- Valida integridade estrutural
- Versionamento automático de genomas

**Uso:**
```python
from genome_mutator import GenomeMutator

# Inicializar com genoma existente ou criar básico
mutator = GenomeMutator(genome_path='genome_master.yaml')

# Métricas estruturais
metrics = mutator.get_structural_metrics()

# Executar mutação
result = mutator.perform_structural_mutation('add_node')

# Validar integridade
validation = mutator.validate_genome_integrity()

# Salvar genoma mutado
saved_path = mutator.save_mutated_genome()
```

### 2. BrainEvolver (`brain_evolver.py`)
**Evolução do cérebro Llama/Ollama:**
- Substitui modelos (llama3.1, mistral, gemma2, etc.)
- Cria ensembles automáticos de modelos
- Otimiza parâmetros (temperature, top_p, etc.)
- Evolui estratégias de roteamento
- Integração com ambiente (variáveis)

**Uso:**
```python
from brain_evolver import BrainEvolver

# Inicializar
evolver = BrainEvolver()

# Métricas do cérebro
metrics = evolver.get_brain_metrics()

# Executar evolução
result = evolver.perform_brain_evolution('mutate_model')

# Aplicar ao ambiente
evolver.apply_to_environment()

# Salvar configuração
saved_path = evolver.save_evolution_config()
```

### 3. EvolutionDashboard (`evolution_dashboard.py`)
**Monitoramento em tempo real:**
- Registro de mutações e evoluções
- Métricas de performance
- Alertas automáticos
- Dashboard HTML interativo
- Histórico completo

**Uso:**
```python
from evolution_dashboard import EvolutionDashboard

# Inicializar
dashboard = EvolutionDashboard()

# Registrar componentes
dashboard.register_component('genome_mutator', 'structural')

# Registrar atividades
dashboard.record_mutation(mutation_data)
dashboard.record_brain_evolution(evolution_data)

# Obter dados
data = dashboard.get_dashboard_data()

# Gerar relatório HTML
html_path = dashboard.generate_html_report()
```

### 4. Evolution API (`evolution_api.py`)
**API REST para controle:**
- Endpoints para evolução estrutural/cerebral
- Status do sistema em tempo real
- Dashboard via web
- Histórico de evoluções

**Endpoints:**
- `POST /evolve/structure` - Executa mutação estrutural
- `POST /evolve/brain` - Executa evolução cerebral
- `GET /status` - Status do sistema
- `GET /dashboard` - Dashboard JSON
- `GET /dashboard/html` - Dashboard HTML
- `GET /history` - Histórico

**Executar API:**
```bash
cd /data/workspace/AI-Biomimetica
python3 src/core/evolution/evolution_api.py
# Acesse: http://localhost:8000/docs
```

## 🚀 Demonstração Rápida

Execute a demonstração completa:

```bash
# Testar todos os componentes individualmente
python3 src/core/evolution/demo_completa.py

# Executar evolução integrada completa
python3 src/core/evolution/demo_completa.py --full

# Testar componentes específicos
python3 src/core/evolution/demo_completa.py --genome
python3 src/core/evolution/demo_completa.py --brain
python3 src/core/evolution/demo_completa.py --dashboard
```

## 📊 Arquivos Gerados

- `genomes/mutated/` - Genomas versionados
- `configs/brain_evolution/` - Configurações cerebrais
- `data/evolution_dashboard/` - Dados do dashboard
- `data/*_dashboard/dashboard.html` - Relatório HTML

## 🔧 Integração com Sistema Existente

Para integrar com o sistema AI-Biomimetica existente:

1. **Importar componentes** nos agentes existentes
2. **Configurar triggers** evolutivos baseados em performance
3. **Conectar ao bio_console_api.py** para evolução do Llama
4. **Adicionar hooks** no `AutoEvolvingAISystem`

**Exemplo de integração mínima:**
```python
# No seu sistema principal
from core.evolution.genome_mutator import GenomeMutator
from core.evolution.brain_evolver import BrainEvolver

class EnhancedAISystem:
    def __init__(self):
        self.mutator = GenomeMutator()
        self.evolver = BrainEvolver()
        self.dashboard = EvolutionDashboard()
    
    def evolve_if_needed(self, performance_metrics):
        if performance_metrics['accuracy'] < 0.7:
            # Evoluir estrutura
            self.mutator.perform_structural_mutation()
            # Evoluir cérebro
            self.evolver.perform_brain_evolution()
            # Registrar
            self.dashboard.record_performance('evolution_trigger', performance_metrics)
```

## 🎯 Fluxo Evolutivo Típico

```
Tarefa → Performance Baixa → Trigger Evolutivo
                                  ↓
                          [GenomeMutator] → Mutação Estrutural
                          [BrainEvolver]  → Evolução Cerebral
                                  ↓
                          [EvolutionDashboard] → Monitoramento
                                  ↓
                          Nova Geração → Teste → Melhoria?
```

## 📈 Métricas Monitoradas

- **Estruturais:** Nós, conexões, densidade, especialistas
- **Cerebrais:** Modelo atual, parâmetros, ensembles, roteamento
- **Performance:** Accuracy, latência, tokens, confiança
- **Evolução:** Taxa de mutação, sucesso, inovação, gerações

## 🛠️ Dependências

- Python 3.8+
- **Opcional:** PyYAML (para genomas YAML)
- **Recomendado:** Ollama (para evolução cerebral real)

As dependências são mínimas - o sistema funciona com JSON se YAML não disponível.

## 🔮 Próximos Desenvolvimentos

1. **Meta-learning evolutivo** - Aprender com histórico de mutações
2. **Ollama integração real** - Evolução com modelos locais reais
3. **Dashboard web em tempo real** - Interface gráfica
4. **Sistema de recomendações** - Sugestões evolutivas inteligentes
5. **Integração completa** com bio_console_api.py e agents existentes

---

**Autor:** Jarvis (OpenClaw)  
**Data:** 2026-04-15  
**Versão:** 1.0.0  
**Projeto:** AI-Biomimetica - Evolução Real
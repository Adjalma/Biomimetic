#!/usr/bin/env python3
"""
SISTEMA META-LEARNING BIOMIMÉTICO AUTOEVOLUTIVO
Versão 4.0 - Meta-learning + Evolução Biomimética + Auto-evolução
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import json
import logging
import random
import time
from typing import Dict, Any, List, Tuple, Optional, Callable
from datetime import datetime
import os
import asyncio
import copy
from collections import deque
import pickle
import threading

# Orchestration evolution imports
try:
    from .orchestration_evolution import OrchestrationEvolutionEngine
    ORCHESTRATION_EVOLUTION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ OrchestrationEvolutionEngine não disponível: {e}")
    ORCHESTRATION_EVOLUTION_AVAILABLE = False

# learn2learn: opcional (extensão C no Windows / PyPI só sdist). Este ficheiro NÃO usa APIs
# l2l — o adaptador meta é BiomimeticMetaLearner (PyTorch). Flags definidos após logger.

# Neuroevolution imports
NEUROEVOLUTION_AVAILABLE = False
try:
    import neat
    from neat import nn as neat_nn
    NEUROEVOLUTION_AVAILABLE = True
except ImportError:
    print("⚠️ Neuroevolution frameworks não disponíveis")

# XAI imports — Captum é o necessário para ExplanationEngine (IntegratedGradients).
# shap/lime são opcionais (lime costuma falhar por timeout/mirror no Nexus corporativo).
XAI_AVAILABLE = False
IntegratedGradients = None  # type: ignore[misc, assignment]
try:
    from captum.attr import IntegratedGradients
    XAI_AVAILABLE = True
except ImportError:
    print("⚠️ XAI (captum) não disponível — instale: pip install captum")
try:
    import shap  # noqa: F401 — opcional para extensões futuras
except ImportError:
    pass
try:
    import lime  # noqa: F401 — opcional; muitas vezes problemático em Windows/Nexus
except ImportError:
    pass

# IA Local como Cérebro Biomimético
try:
    from .local_brain import HybridBiomimeticSystem
    LOCAL_BRAIN_AVAILABLE = True
except ImportError:
    print("⚠️ Módulo local_brain não disponível")
    LOCAL_BRAIN_AVAILABLE = False

# Sistema de Auto-Evolução Avançado (Nível 3)
try:
    from .auto_evolution_engine import AdvancedAutoEvolutionSystem
    AUTO_EVOLUTION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Módulo auto_evolution_engine não disponível: {e}")
    AUTO_EVOLUTION_AVAILABLE = False

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

LEARN2LEARN_AVAILABLE = False
try:
    import learn2learn as l2l  # noqa: F401 — opcional; utilitários/datasets não usados aqui
    LEARN2LEARN_AVAILABLE = True
except ImportError:
    logger.info(
        "learn2learn não instalado (opcional). "
        "Meta-learning via BiomimeticMetaLearner (PyTorch) segue ativo; "
        "para o pacote: MSVC Build Tools + pip install learn2learn — ver requirements_learn2learn_notes.txt"
    )

# Caminho _meta_learning_adaptation usa só PyTorch (inner/outer loop); não exige learn2learn.
META_LEARNING_AVAILABLE = True

HIGHER_AVAILABLE = False
try:
    import higher  # noqa: F401 — FOMAML (gradientes através do inner loop)
    HIGHER_AVAILABLE = True
except ImportError:
    logger.info(
        "Pacote 'higher' não instalado — meta-learning usa Reptile (outer loop explícito). "
        "Para FOMAML: pip install higher (ver requirements_meta_learning.txt)."
    )


class BiomimeticMetaLearner:
    """
    Meta-learner biomimético (aprender a aprender).

    - Com `higher`: **FOMAML** (first-order MAML) — gradiente do erro na *query* passa aos
      pesos meta iniciais (inner loop diferenciável).
    - Sem `higher`: **Reptile** — após adaptação por SGD num clone, θ ← θ + ε(θ_adapt − θ).

    Tarefas: tuplas (support_x, support_y, query_x, query_y) ou legado (x, y) repartido ao meio.
    """

    def __init__(
        self,
        model: nn.Module,
        meta_lr: float = 0.01,
        adaptation_steps: int = 5,
        inner_lr: float = 0.05,
        num_classes: int = 128,
    ):
        self.model = model
        self.meta_lr = meta_lr
        self.inner_lr = inner_lr
        self.adaptation_steps = adaptation_steps
        self.num_classes = num_classes
        self.meta_optimizer = torch.optim.Adam(self.model.parameters(), lr=meta_lr)

        self.meta_history = []
        self.task_performance = {}
        self.knowledge_base = {}

        self.plasticity_rate = 0.1
        self.consolidation_strength = 0.8
        self.forgetting_rate = 0.05

    def _normalize_task(
        self, task: Tuple[torch.Tensor, ...]
    ) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        if len(task) == 4:
            sx, sy, qx, qy = task
            return sx, sy, qx, qy
        x, y = task[0], task[1]
        half = max(1, x.size(0) // 2)
        return x[:half], y[:half], x[half:], y[half:]

    def _fomaml_step(
        self, tasks: List[Tuple[torch.Tensor, ...]]
    ) -> float:
        import higher as higher_pkg

        self.model.train()
        self.meta_optimizer.zero_grad()
        total_q = None
        n = 0
        for raw in tasks:
            sx, sy, qx, qy = self._normalize_task(raw)
            inner_opt = torch.optim.SGD(self.model.parameters(), lr=self.inner_lr)
            with higher_pkg.innerloop_ctx(self.model, inner_opt) as (fmodel, diffopt):
                for _ in range(self.adaptation_steps):
                    loss_s = F.cross_entropy(fmodel(sx), sy)
                    diffopt.step(loss_s)
                loss_q = F.cross_entropy(fmodel(qx), qy)
            n += 1
            total_q = loss_q if total_q is None else total_q + loss_q
        assert total_q is not None
        total_q = total_q / n
        total_q.backward()
        self.meta_optimizer.step()
        loss_val = float(total_q.detach().item())
        self.meta_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "meta_loss": loss_val,
                "tasks_processed": len(tasks),
                "algorithm": "fomaml",
            }
        )
        return loss_val

    def _reptile_meta_step(
        self, tasks: List[Tuple[torch.Tensor, ...]]
    ) -> float:
        """Reptile: actualização explícita dos pesos meta (sem confundir com Adam no clone)."""
        self.model.train()
        scale = self.meta_lr / max(1, len(tasks))
        last_inner = 0.0
        for raw in tasks:
            sx, sy, _, _ = self._normalize_task(raw)
            adapted = copy.deepcopy(self.model)
            opt = torch.optim.SGD(adapted.parameters(), lr=self.inner_lr)
            for _ in range(self.adaptation_steps):
                opt.zero_grad()
                loss = F.cross_entropy(adapted(sx), sy)
                loss.backward()
                opt.step()
                last_inner = float(loss.detach().item())
            with torch.no_grad():
                for p_meta, p_adapt in zip(self.model.parameters(), adapted.parameters()):
                    p_meta.data.add_(scale * (p_adapt.data - p_meta.data))
        self.meta_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "meta_loss": last_inner,
                "tasks_processed": len(tasks),
                "algorithm": "reptile",
            }
        )
        return last_inner

    def meta_train_step(self, tasks: List[Tuple[torch.Tensor, ...]]) -> float:
        """
        Um passo de meta-treino: FOMAML (higher) ou Reptile.
        """
        if not tasks:
            return 0.0
        if HIGHER_AVAILABLE:
            try:
                return self._fomaml_step(tasks)
            except Exception as e:
                logger.warning("FOMAML falhou (%s); fallback Reptile.", e)
        return self._reptile_meta_step(tasks)

    def reptile_step(self, tasks: List[Tuple[torch.Tensor, ...]]) -> float:
        """
        Só Reptile (útil para comparar ou pipelines externos). Não combinar no mesmo batch
        que meta_train_step com FOMAML.
        """
        if not tasks:
            return 0.0
        return self._reptile_meta_step(tasks)
    
    def few_shot_adaptation(self, support_data: torch.Tensor, support_labels: torch.Tensor,
                           query_data: torch.Tensor, query_labels: torch.Tensor) -> float:
        """
        Few-shot learning adaptation
        """
        adapted_model = copy.deepcopy(self.model)
        optimizer = torch.optim.SGD(adapted_model.parameters(), lr=0.01)
        
        # Adapt on support set
        for _ in range(self.adaptation_steps):
            support_output = adapted_model(support_data)
            support_loss = F.cross_entropy(support_output, support_labels)
            optimizer.zero_grad()
            support_loss.backward()
            optimizer.step()
        
        # Evaluate on query set
        with torch.no_grad():
            query_output = adapted_model(query_data)
            query_loss = F.cross_entropy(query_output, query_labels)
            accuracy = (query_output.argmax(dim=1) == query_labels).float().mean()
        
        return query_loss.item(), accuracy.item()
    
    def elastic_weight_consolidation(self, important_weights: Dict[str, torch.Tensor], 
                                   fisher_info: Dict[str, torch.Tensor]) -> float:
        """
        Elastic Weight Consolidation to prevent catastrophic forgetting
        """
        ewc_loss = 0.0
        
        for name, param in self.model.named_parameters():
            if name in important_weights and name in fisher_info:
                ewc_loss += torch.sum(fisher_info[name] * (param - important_weights[name]) ** 2)
        
        return ewc_loss
    
    def update_knowledge_base(self, task_id: str, performance: float, 
                            task_characteristics: Dict[str, Any]):
        """
        Update knowledge base with task performance
        """
        self.knowledge_base[task_id] = {
            'performance': performance,
            'characteristics': task_characteristics,
            'timestamp': datetime.now().isoformat(),
            'adaptation_steps': self.adaptation_steps,
            'meta_lr': self.meta_lr
        }
    
    def get_meta_learning_stats(self) -> Dict[str, Any]:
        """
        Get meta-learning statistics
        """
        if not self.meta_history:
            return {
                "higher_available": HIGHER_AVAILABLE,
                "preferred_algorithm": "fomaml" if HIGHER_AVAILABLE else "reptile",
            }

        recent_losses = [h["meta_loss"] for h in self.meta_history[-10:]]
        recent_algos = [h.get("algorithm", "?") for h in self.meta_history[-5:]]

        return {
            "avg_meta_loss": float(np.mean(recent_losses)),
            "meta_loss_trend": float(np.mean(recent_losses[-5:]) - np.mean(recent_losses[:5]))
            if len(recent_losses) >= 5
            else 0.0,
            "total_tasks_processed": int(
                sum(h["tasks_processed"] for h in self.meta_history)
            ),
            "knowledge_base_size": len(self.knowledge_base),
            "adaptation_steps": self.adaptation_steps,
            "inner_lr": self.inner_lr,
            "meta_lr": self.meta_lr,
            "higher_available": HIGHER_AVAILABLE,
            "preferred_algorithm": "fomaml" if HIGHER_AVAILABLE else "reptile",
            "recent_algorithms": recent_algos,
        }

class BiomimeticEvolutionaryEngine:
    """
    Motor evolutivo biomimético com neuroevolução
    """
    
    def __init__(self, input_size: int = 512, output_size: int = 128):
        self.input_size = input_size
        self.output_size = output_size
        self.population = []
        self.generation = 0
        self.best_fitness = 0.0
        self.evolution_history = []
        
        # Biomimetic parameters
        self.mutation_rate = 0.15
        self.crossover_rate = 0.7
        self.selection_pressure = 0.8
        self.speciation_threshold = 0.3
        
        # NEAT configuration - comentado temporariamente
        # self.neat_config = self._create_neat_config()
        
        # Species management
        self.species = []
        self.species_fitness = {}
        
    def _create_neat_config(self):
        """
        Create NEAT configuration for biomimetic evolution
        COMENTADO TEMPORARIAMENTE - NEAT não disponível
        """
        if NEUROEVOLUTION_AVAILABLE:
            try:
                config_path = "config/neat_config.txt"
                
                # Create config directory if it doesn't exist
                os.makedirs(os.path.dirname(config_path), exist_ok=True)
                
                config_content = f"""
[NEAT]
fitness_criterion     = max
fitness_threshold     = 100
pop_size              = 50
reset_on_extinction   = False

[DefaultGenome]
# node activation options
activation_default      = tanh
activation_mutate_rate = 0.0
activation_options     = tanh

# node add/remove rates
node_add_prob           = 0.2
node_delete_prob        = 0.2

# node connection options
connection_add_prob    = 0.5
connection_delete_prob = 0.5

# network parameters
num_hidden              = 0
num_inputs              = {self.input_size}
num_outputs             = {self.output_size}

# node bias options
bias_init_mean          = 0.0
bias_init_stdev         = 1.0
bias_max_value          = 30.0
bias_min_value          = -30.0
bias_mutate_power       = 0.5
bias_mutate_rate        = 0.7
bias_replace_rate       = 0.1

# node response options
response_init_mean      = 1.0
response_init_stdev     = 0.0
response_max_value      = 30.0
response_min_value      = -30.0
response_mutate_power   = 0.0
response_mutate_rate    = 0.0
response_replace_rate   = 0.0

# connection weight options
weight_init_mean        = 0.0
weight_init_stdev       = 1.0
weight_max_value        = 30
weight_min_value        = -30
weight_mutate_power     = 0.5
weight_mutate_rate      = 0.8
weight_replace_rate     = 0.1

# connection enable options
enabled_default         = True
enabled_mutate_rate     = 0.01

feed_forward            = True
initial_connection      = full

# node add/remove rates
node_add_prob           = 0.2
node_delete_prob        = 0.2

# connection add/remove rates
connection_add_prob    = 0.5
connection_delete_prob = 0.5

# network parameters
num_hidden              = 0
num_inputs              = {self.input_size}
num_outputs             = {self.output_size}

[DefaultSpeciesSet]
compatibility_threshold = 3.0

[DefaultStagnation]
species_fitness_func = max
max_stagnation        = 20
species_elitism       = 2

[DefaultReproduction]
elitism            = 2
survival_threshold = 0.2
"""
                
                with open(config_path, 'w') as f:
                    f.write(config_content)
                
                return neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                  neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
            except Exception as e:
                print(f"⚠️ Erro ao criar configuração NEAT: {e}")
                return None
        else:
            print("⚠️ NEAT não disponível - configuração não criada")
            return None
    
    def initialize_neat_population(self):
        """
        Initialize NEAT population
        """
        if not NEUROEVOLUTION_AVAILABLE:
            logger.warning("NEAT não disponível, usando população padrão")
            return
        
        try:
            self.neat_population = neat.Population(self.neat_config)
            logger.info(f"População NEAT inicializada com {len(self.neat_population)} indivíduos")
        except Exception as e:
            logger.error(f"Erro na inicialização NEAT: {e}")
    
    def evolve_neat_generation(self, fitness_function: Callable) -> Dict[str, Any]:
        """
        Evolve one generation using NEAT
        """
        if not NEUROEVOLUTION_AVAILABLE:
            return self._evolve_standard_generation(fitness_function)
        
        try:
            # Evaluate fitness for all genomes
            for genome_id, genome in self.neat_population.population.items():
                fitness = fitness_function(genome)
                genome.fitness = fitness
            
            # Run one generation
            self.neat_population.run(fitness_function, 1)
            
            # Get best genome
            best_genome = max(self.neat_population.population.values(), key=lambda x: x.fitness)
            
            # Record evolution
            evolution_data = {
                'generation': self.generation,
                'best_fitness': best_genome.fitness,
                'population_size': len(self.neat_population.population),
                'species_count': len(self.neat_population.species.species),
                'timestamp': datetime.now().isoformat()
            }
            
            self.evolution_history.append(evolution_data)
            self.generation += 1
            
            return evolution_data
            
        except Exception as e:
            logger.error(f"Erro na evolução NEAT: {e}")
            return self._evolve_standard_generation(fitness_function)
    
    def _evolve_standard_generation(self, fitness_function: Callable) -> Dict[str, Any]:
        """
        Standard evolutionary algorithm as fallback
        """
        # Evaluate population
        for individual in self.population:
            individual['fitness'] = fitness_function(individual['model'])
        
        # Selection
        sorted_population = sorted(self.population, key=lambda x: x['fitness'], reverse=True)
        elite = sorted_population[:int(len(self.population) * 0.2)]
        
        # Crossover and mutation
        new_population = []
        for _ in range(len(self.population)):
            parent1 = random.choice(elite)
            parent2 = random.choice(elite)
            
            child = self._crossover(parent1, parent2)
            if random.random() < self.mutation_rate:
                child = self._mutate(child)
            
            new_population.append(child)
        
        self.population = new_population
        self.generation += 1
        
        best_fitness = max(individual['fitness'] for individual in self.population)
        
        return {
            'generation': self.generation,
            'best_fitness': best_fitness,
            'population_size': len(self.population),
            'timestamp': datetime.now().isoformat()
        }
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """
        Crossover between two individuals
        """
        # Simple parameter crossover
        child_model = copy.deepcopy(parent1['model'])
        
        for param1, param2 in zip(parent1['model'].parameters(), parent2['model'].parameters()):
            if random.random() < 0.5:
                param1.data = param2.data.clone()
        
        return {
            'id': f"child_{datetime.now().strftime('%H%M%S')}_{random.randint(1000, 9999)}",
            'model': child_model,
            'fitness': 0.0,
            'generation': self.generation + 1
        }
    
    def _mutate(self, individual: Dict) -> Dict:
        """
        Mutate individual
        """
        model = individual['model']
        
        for param in model.parameters():
            if random.random() < 0.1:
                mutation = torch.randn_like(param.data) * 0.1
                param.data += mutation
        
        return individual

class AutoEvolvingAISystem:
    """
    Sistema de IA Autoevolutiva com Meta-Learning Biomimético
    """
    
    def __init__(self, use_local_brain: bool = False, local_brain_type: str = "mock"):
        self.meta_learner = None
        self.evolutionary_engine = None
        self.current_model = None
        self.auto_evolution_active = False
        
        # Auto-evolution parameters
        self.evolution_trigger_threshold = 0.1
        self.performance_history = deque(maxlen=100)
        self.architecture_history = []
        # Episódios do modo agente → cérebro biomimético + ciclos de evolução
        self._agent_biomimetic_cycle_count = 0
        self._last_biomimetic_evolution_ts = 0.0
        # Evolução em segundo plano (não bloquear chat / UI)
        self._evolution_thread_lock = threading.Lock()
        self._evolution_worker_running = False
        self._evolution_queued_task: Optional[Dict[str, Any]] = None

        # XAI components
        self.explanation_engine = None
        self.confidence_estimator = None
        
        # IA Local como Cérebro Biomimético
        self.use_local_brain = use_local_brain and LOCAL_BRAIN_AVAILABLE
        self.local_brain = None
        self.local_brain_type = local_brain_type
        
        # Orchestration evolution
        self.orchestration_evolution = None
        
        # Sistema de Auto-Evolução Avançado (Nível 3)
        self.advanced_auto_evolution = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """
        Initialize all system components
        """
        # Create base model
        self.current_model = self._create_biomimetic_model()
        
        # Initialize meta-learner
        self.meta_learner = BiomimeticMetaLearner(self.current_model)
        
        # Initialize evolutionary engine
        self.evolutionary_engine = BiomimeticEvolutionaryEngine()
        self.evolutionary_engine.initialize_neat_population()
        
        # Initialize orchestration evolution engine
        if ORCHESTRATION_EVOLUTION_AVAILABLE:
            self.orchestration_evolution = OrchestrationEvolutionEngine()
            logger.info("✅ OrchestrationEvolutionEngine inicializado")
        else:
            logger.warning("⚠️ OrchestrationEvolutionEngine não disponível")
        
        # Initialize advanced auto-evolution system (Level 3)
        if AUTO_EVOLUTION_AVAILABLE:
            try:
                self.advanced_auto_evolution = AdvancedAutoEvolutionSystem(
                    use_local_brain=False,  # Sem Ollama por enquanto - você conectará depois
                    enable_meta_evolution=True
                )
                logger.info("🚀 Sistema de Auto-Evolução Avançado (Nível 3) inicializado")
            except Exception as e:
                logger.error(f"Erro ao inicializar sistema de auto-evolução avançado: {e}")
                self.advanced_auto_evolution = None
        else:
            logger.warning("⚠️ Sistema de Auto-Evolução Avançado não disponível")
        
        # Initialize XAI components
        if XAI_AVAILABLE:
            self.explanation_engine = ExplanationEngine(self.current_model)
            self.confidence_estimator = ConfidenceEstimator(self.current_model)
        
        # Initialize local brain if enabled
        if self.use_local_brain:
            try:
                lb_kwargs: Dict[str, Any] = {}
                if self.local_brain_type == "ollama":
                    lb_kwargs["model"] = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
                    lb_kwargs["base_url"] = os.environ.get(
                        "OLLAMA_BASE_URL", "http://localhost:11434"
                    )
                self.local_brain = HybridBiomimeticSystem(
                    brain_type=self.local_brain_type, **lb_kwargs
                )
                logger.info(f"🧠 Cérebro local inicializado (tipo: {self.local_brain_type})")
            except Exception as e:
                logger.error(f"Erro ao inicializar cérebro local: {e}")
                self.use_local_brain = False
        
        logger.info("✅ Sistema autoevolutivo inicializado")
    
    def _create_biomimetic_model(self) -> nn.Module:
        """
        Create biomimetic neural network model
        """
        class BiomimeticNN(nn.Module):
            def __init__(self, input_size=512, hidden_size=256, output_size=128):
                super().__init__()
                
                # Biomimetic architecture with skip connections
                self.input_layer = nn.Linear(input_size, hidden_size)
                self.hidden1 = nn.Linear(hidden_size, hidden_size)
                self.hidden2 = nn.Linear(hidden_size, hidden_size)
                self.output_layer = nn.Linear(hidden_size, output_size)
                
                # Attention mechanism
                self.attention = nn.MultiheadAttention(hidden_size, num_heads=8)
                
                # Dropout for regularization
                self.dropout = nn.Dropout(0.1)
                
                # Layer normalization
                self.layer_norm1 = nn.LayerNorm(hidden_size)
                self.layer_norm2 = nn.LayerNorm(hidden_size)
                
            def forward(self, x):
                # Input processing
                x = self.input_layer(x)
                x = F.relu(x)
                x = self.dropout(x)
                x = self.layer_norm1(x)
                
                # Hidden layers with skip connections
                residual = x
                x = self.hidden1(x)
                x = F.relu(x)
                x = self.dropout(x)
                x = x + residual  # Skip connection
                x = self.layer_norm2(x)
                
                # Attention mechanism
                x = x.unsqueeze(0)  # Add sequence dimension
                attn_output, _ = self.attention(x, x, x)
                x = attn_output.squeeze(0)
                
                # Final processing
                x = self.hidden2(x)
                x = F.relu(x)
                x = self.dropout(x)
                
                # Output
                output = self.output_layer(x)
                
                return output
        
        return BiomimeticNN()
    
    def recommend_provider(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recomenda provedor e parâmetros baseado em aprendizado biomimético.
        
        Heurística aprimorada com múltiplos fatores:
        - Tipo de tarefa
        - Comprimento do texto
        - Complexidade estimada
        - Custo simulado
        - Latência esperada
        - Qualidade histórica
        
        Args:
            task_data: Dados da tarefa incluindo tipo, comprimento, parâmetros
            
        Returns:
            Dicionário com recomendação:
            {
                "provider": "openai",  # ou "anthropic", "google", etc.
                "parameters": {"temperature": 0.7, "max_tokens": 100},
                "strategy": "default",
                "confidence": 0.8,
                "reasoning": "explicação da decisão"
            }
        """
        if self.use_local_brain and self.local_brain is not None:
            try:
                decision = asyncio.run(self.local_brain.recommend_provider(task_data))
                if self.orchestration_evolution is not None:
                    rec = {
                        k: v
                        for k, v in decision.items()
                        if k not in ("hybrid_metadata", "brain_type", "model_used")
                    }
                    self.orchestration_evolution.record_recommendation(task_data, rec)
                logger.info("Recomendação obtida via cérebro local (Ollama ou mock).")
                return decision
            except Exception as e:
                logger.warning(
                    "Cérebro local falhou (%s); continuando com heurística interna.", e
                )

        task_type = task_data.get("task_type", "text_completion")
        text_length = task_data.get("text_length", 0)
        context = task_data.get("context", {})
        
        # Fatores de decisão
        complexity = self._estimate_complexity(task_data)
        budget = context.get("budget", "balanced")  # low, balanced, high
        latency_requirement = context.get("latency", "standard")  # realtime, standard, batch
        
        # Perfis de provedores (simulados - evoluirão com aprendizado)
        provider_profiles = {
            "openai": {
                "strengths": ["text_completion", "code_generation", "creativity"],
                "cost_per_token": 0.00002,  # USD por token
                "avg_latency_ms": 300,
                "quality_scores": {
                    "text_completion": 0.85,
                    "text_classification": 0.78,
                    "code_generation": 0.88
                }
            },
            "anthropic": {
                "strengths": ["reasoning", "long_context", "safety"],
                "cost_per_token": 0.000025,
                "avg_latency_ms": 450,
                "quality_scores": {
                    "text_completion": 0.82,
                    "text_classification": 0.85,
                    "reasoning": 0.90
                }
            },
            "google": {
                "strengths": ["translation", "summarization", "search"],
                "cost_per_token": 0.000015,
                "avg_latency_ms": 200,
                "quality_scores": {
                    "text_completion": 0.80,
                    "translation": 0.92,
                    "summarization": 0.87
                }
            },
            "huggingface": {
                "strengths": ["classification", "ner", "custom_models"],
                "cost_per_token": 0.000005,  # Mais barato
                "avg_latency_ms": 150,
                "quality_scores": {
                    "text_classification": 0.83,
                    "ner": 0.89,
                    "sentiment_analysis": 0.86
                }
            },
            "local": {
                "strengths": ["privacy", "zero_cost", "customization"],
                "cost_per_token": 0.0,
                "avg_latency_ms": 1000,  # Mais lento
                "quality_scores": {
                    "text_completion": 0.65,
                    "text_classification": 0.70
                }
            }
        }
        
        # Matriz de decisão baseada em tipo de tarefa
        task_to_provider_map = {
            "text_completion": {
                "high_quality": "openai",
                "low_cost": "huggingface",
                "fast": "google",
                "reasoning": "anthropic"
            },
            "text_classification": {
                "high_quality": "anthropic",
                "low_cost": "huggingface",
                "fast": "google",
                "balanced": "openai"
            },
            "code_generation": {
                "high_quality": "openai",
                "low_cost": "local",
                "balanced": "openai"
            },
            "translation": {
                "high_quality": "google",
                "balanced": "openai"
            },
            "summarization": {
                "high_quality": "google",
                "balanced": "openai"
            },
            "ner": {
                "high_quality": "huggingface",
                "balanced": "anthropic"
            },
            "sentiment_analysis": {
                "high_quality": "huggingface",
                "balanced": "openai"
            }
        }
        
        # Determinar critério baseado em contexto
        if budget == "low":
            primary_criterion = "low_cost"
        elif latency_requirement == "realtime":
            primary_criterion = "fast"
        elif complexity > 0.7:
            primary_criterion = "high_quality"
        else:
            primary_criterion = "balanced"
        
        # Selecionar provedor
        provider_map = task_to_provider_map.get(task_type, task_to_provider_map["text_completion"])
        provider = provider_map.get(primary_criterion, "openai")
        
        # Ajustar parâmetros baseado na tarefa
        parameters = self._get_optimal_parameters(task_type, text_length, complexity)
        
        # Calcular confiança baseada em correspondência com perfil
        profile = provider_profiles[provider]
        base_confidence = profile["quality_scores"].get(task_type, 0.7)
        
        # Ajustar confiança baseado em fatores contextuais
        confidence_adjustments = {
            "text_length": min(1.0, text_length / 1000),  # Textos mais longos têm confiança reduzida
            "complexity": 1.0 - (complexity * 0.2),  # Alta complexidade reduz confiança
            "budget_match": 1.0 if (budget == "low" and provider == "huggingface") or 
                                 (budget != "low") else 0.8
        }
        
        confidence = base_confidence * 0.7 + np.mean(list(confidence_adjustments.values())) * 0.3
        confidence = max(0.3, min(0.95, confidence))
        
        # Determinar estratégia
        strategy = self._determine_strategy(task_type, complexity, text_length)
        
        # Explicação da decisão (para logging e transparência)
        reasoning = (
            f"Tarefa: {task_type}. "
            f"Critério: {primary_criterion} (budget={budget}, latency={latency_requirement}, complexity={complexity:.2f}). "
            f"Provedor selecionado: {provider} (confidence={confidence:.2f}). "
            f"Estratégia: {strategy}."
        )
        
        # Registrar recomendação para evolução de orquestração
        if self.orchestration_evolution is not None:
            recommendation = {
                "provider": provider,
                "parameters": parameters,
                "strategy": strategy,
                "confidence": float(confidence),
                "reasoning": reasoning,
                "metadata": {
                    "primary_criterion": primary_criterion,
                    "complexity_score": complexity,
                    "estimated_cost": self._estimate_cost(provider, text_length, profile),
                    "estimated_latency_ms": profile["avg_latency_ms"]
                }
            }
            self.orchestration_evolution.record_recommendation(task_data, recommendation)
            logger.debug(f"Recomendação registrada para evolução de orquestração")
        
        logger.info(f"Recomendação biomimética: {reasoning}")
        
        return {
            "provider": provider,
            "parameters": parameters,
            "strategy": strategy,
            "confidence": float(confidence),
            "reasoning": reasoning,
            "metadata": {
                "primary_criterion": primary_criterion,
                "complexity_score": complexity,
                "estimated_cost": self._estimate_cost(provider, text_length, profile),
                "estimated_latency_ms": profile["avg_latency_ms"]
            }
        }
    
    def _estimate_complexity(self, task_data: Dict[str, Any]) -> float:
        """
        Estima complexidade da tarefa (0.0 a 1.0)
        Baseado em múltiplos fatores: comprimento, tipo de tarefa, conteúdo
        """
        task_type = task_data.get("task_type", "text_completion")
        text_length = task_data.get("text_length", 0)
        
        # Fatores de complexidade
        length_factor = min(1.0, text_length / 5000)  # Textos muito longos são mais complexos
        
        # Complexidade por tipo de tarefa
        task_complexity = {
            "text_completion": 0.3,
            "text_classification": 0.4,
            "sentiment_analysis": 0.5,
            "summarization": 0.6,
            "translation": 0.7,
            "code_generation": 0.8,
            "ner": 0.7,
            "reasoning": 0.9
        }.get(task_type, 0.5)
        
        # Combinar fatores (ponderado)
        complexity = (length_factor * 0.3) + (task_complexity * 0.7)
        return max(0.1, min(1.0, complexity))
    
    def _get_optimal_parameters(self, task_type: str, text_length: int, complexity: float) -> Dict[str, Any]:
        """
        Retorna parâmetros otimizados baseado no tipo de tarefa e complexidade
        """
        base_params = {}
        
        # Parâmetros base por tipo de tarefa
        if task_type == "text_completion":
            base_params = {
                "temperature": max(0.3, min(0.9, 0.7 - (complexity * 0.2))),  # Mais determinístico para tarefas complexas
                "max_tokens": min(500, max(50, int(text_length * 0.5))),
                "top_p": 0.95,
                "frequency_penalty": 0.1 if complexity > 0.6 else 0.0
            }
        elif task_type == "text_classification":
            base_params = {
                "temperature": 0.3,  # Baixa temperatura para classificação determinística
                "max_tokens": 10,
                "logprobs": 3,
                "echo": False
            }
        elif task_type == "code_generation":
            base_params = {
                "temperature": 0.5,
                "max_tokens": min(1000, text_length * 2),
                "stop": ["\n\n", "def ", "class "]
            }
        elif task_type in ["translation", "summarization"]:
            base_params = {
                "temperature": 0.4,
                "max_tokens": min(300, int(text_length * 0.7)),
                "top_p": 0.9
            }
        else:
            base_params = {
                "temperature": 0.7,
                "max_tokens": 200,
                "top_p": 0.95
            }
        
        # Ajustar baseado na complexidade
        if complexity > 0.7:
            base_params["temperature"] = max(0.2, base_params.get("temperature", 0.7) * 0.8)
            if "max_tokens" in base_params:
                base_params["max_tokens"] = int(base_params["max_tokens"] * 1.2)
        
        return base_params
    
    def _determine_strategy(self, task_type: str, complexity: float, text_length: int) -> str:
        """
        Determina estratégia de execução baseado nas características da tarefa
        """
        strategies = []
        
        # Estratégias baseadas no tipo de tarefa
        if task_type == "text_completion":
            strategies.append("default")
            if complexity > 0.6:
                strategies.append("chain_of_thought")
            if text_length > 1000:
                strategies.append("chunked_processing")
                
        elif task_type == "text_classification":
            if complexity > 0.5:
                strategies.append("few_shot")
            else:
                strategies.append("zero_shot")
            strategies.append("confidence_threshold")
            
        elif task_type == "code_generation":
            strategies.append("syntax_aware")
            strategies.append("test_driven")
            
        elif task_type in ["translation", "summarization"]:
            strategies.append("preserve_context")
            if text_length > 500:
                strategies.append("hierarchical")
                
        else:
            strategies.append("default")
        
        # Adicionar estratégias baseadas em complexidade
        if complexity > 0.8:
            strategies.append("verification_step")
        if text_length > 2000:
            strategies.append("streaming_output")
        
        # Retornar estratégia primária + secundárias
        primary = strategies[0] if strategies else "default"
        secondary = strategies[1:] if len(strategies) > 1 else []
        
        if secondary:
            return f"{primary}+{'+'.join(secondary[:2])}"
        return primary
    
    def _estimate_cost(self, provider: str, text_length: int, profile: Dict[str, Any]) -> float:
        """
        Estima custo da execução em USD (simulado)
        """
        tokens_estimated = text_length * 1.3  # Fator de conversão texto→token
        cost_per_token = profile.get("cost_per_token", 0.00002)
        
        # Custo base
        base_cost = tokens_estimated * cost_per_token
        
        # Adicionar custo fixo por requisição (simulado)
        fixed_cost = 0.0001 if provider != "local" else 0.0
        
        return round(base_cost + fixed_cost, 6)
    
    def record_task_result(self, task_data: Dict[str, Any], result: Dict[str, Any]):
        """
        Registra resultado de uma tarefa para aprendizado do sistema biomimético.
        
        Args:
            task_data: Dados da tarefa original (mesmos passados para recommend_provider)
            result: Resultado da execução incluindo métricas
                - provider: provedor utilizado
                - quality_score: qualidade da execução (0-1)
                - latency_ms: latência em milissegundos
                - success: bool indicando sucesso
        """
        # Por enquanto, apenas armazenar para análise futura
        # Futuramente, usar para meta-learning e evolução
        
        if not hasattr(self, 'task_history'):
            self.task_history = []
        
        self.task_history.append({
            "timestamp": datetime.now().isoformat(),
            "task_data": task_data,
            "result": result
        })
        
        # Limitar histórico para evitar crescimento infinito
        if len(self.task_history) > 1000:
            self.task_history = self.task_history[-500:]
        
        # Registrar resultado para evolução de orquestração
        if self.orchestration_evolution is not None:
            self.orchestration_evolution.record_result(task_data, result)
            logger.debug(f"Resultado registrado para evolução de orquestração")
        
        logger.info(f"Resultado de tarefa registrado. Histórico: {len(self.task_history)} entradas")
    
    def get_orchestration_dashboard(self) -> Dict[str, Any]:
        """
        Obter dados do dashboard de evolução de orquestração.
        
        Returns:
            Dicionário com métricas, histórico e sugestões de melhoria
        """
        if self.orchestration_evolution is not None:
            return self.orchestration_evolution.get_dashboard_data()
        else:
            return {"error": "OrchestrationEvolutionEngine não disponível"}
    
    def run_advanced_auto_evolution(self, task_pool: List[Dict[str, Any]], 
                                  evaluation_fn: Callable) -> Dict[str, Any]:
        """
        Executar ciclo de auto-evolução avançada (Nível 3)
        
        Args:
            task_pool: Lista de tarefas para avaliação
            evaluation_fn: Função para avaliar indivíduos (recebe phenotype e task_data, retorna fitness)
        
        Returns:
            Resultados do ciclo de evolução
        """
        if self.advanced_auto_evolution is None:
            logger.error("Sistema de auto-evolução avançado não disponível")
            return {"error": "AdvancedAutoEvolutionSystem não inicializado"}
        
        try:
            logger.info("🚀 Iniciando ciclo de auto-evolução avançada (Nível 3)")
            results = self.advanced_auto_evolution.run_evolution_cycle(task_pool, evaluation_fn)
            
            # Registrar no orchestration evolution se disponível
            if self.orchestration_evolution is not None:
                task_data = {
                    'task_type': 'advanced_evolution_cycle',
                    'evolution_cycle': results.get('evolution_cycle', 0),
                    'performance': results.get('evolution_results', {})
                }
                
                recommendation = {
                    'provider': 'advanced_auto_evolution',
                    'parameters': results.get('evolution_results', {}).get('evolution_strategies', {}),
                    'confidence': results.get('evolution_results', {}).get('best_fitness', 0.0),
                    'reasoning': f"Ciclo avançado {results.get('evolution_cycle', 0)}"
                }
                
                result = {
                    'success': results.get('evolution_results', {}).get('best_fitness', 0.0) > 0.5,
                    'performance_score': results.get('evolution_results', {}).get('best_fitness', 0.0),
                    'quality_score': results.get('evolution_results', {}).get('diversity', 0.0)
                }
                
                self.orchestration_evolution.record_recommendation(task_data, recommendation)
                self.orchestration_evolution.record_result(task_data, result)
            
            return results
            
        except Exception as e:
            logger.error(f"Erro ao executar auto-evolução avançada: {e}")
            return {"error": str(e)}
    
    def get_advanced_evolution_status(self) -> Dict[str, Any]:
        """
        Obter status do sistema de auto-evolução avançada
        
        Returns:
            Status do sistema avançado
        """
        if self.advanced_auto_evolution is None:
            return {"error": "AdvancedAutoEvolutionSystem não disponível"}
        
        return self.advanced_auto_evolution.get_system_status()
    
    def auto_evolve(self, performance_metric: float, task_data: Dict[str, Any]):
        """
        Trigger auto-evolution based on performance
        """
        self.performance_history.append(performance_metric)
        
        # Check if evolution is needed
        if len(self.performance_history) >= 10:
            recent_avg = np.mean(list(self.performance_history)[-5:])
            previous_avg = np.mean(list(self.performance_history)[-10:-5])
            
            performance_degradation = previous_avg - recent_avg
            
            if performance_degradation > self.evolution_trigger_threshold:
                logger.info(f"🔄 Auto-evolução ativada! Degradação: {performance_degradation:.4f}")
                self._schedule_gradual_auto_evolution(task_data)

    def ingest_agent_biomimetic_episode(
        self,
        task_data: Dict[str, Any],
        reasoning: str,
        answer: str,
    ) -> Dict[str, Any]:
        """
        Regista um turno do modo agente no cérebro híbrido e alimenta métricas autoevolutivas.

        O histórico de ``auto_evolve`` com valores estáveis raramente induz ``performance_degradation``;
        por isso existe também um ciclo periódico agendado com
        ``_schedule_gradual_auto_evolution`` (intervalo, cooldown, perfil e thread em background).
        """
        reasoning = reasoning or ""
        answer = answer or ""
        has_reasoning = len(reasoning.strip()) > 0
        quality = float(
            min(
                1.0,
                0.28
                + (0.32 if has_reasoning else 0.0)
                + min(0.38, len(reasoning) / 1400.0)
                + min(0.22, len(answer) / 2800.0),
            )
        )
        success = len(answer.strip()) >= 8
        result_payload: Dict[str, Any] = {
            "success": success,
            "quality_score": quality,
            "provider": "local",
        }
        if self.use_local_brain and self.local_brain is not None:
            try:
                self.local_brain.record_task_result(task_data, result_payload)
            except Exception as e:
                logger.warning("record_task_result (episódio agente): %s", e)

        self.auto_evolve(quality, task_data)

        out: Dict[str, Any] = {
            "quality_score": quality,
            "biomimetic_feedback_recorded": bool(
                self.use_local_brain and self.local_brain is not None
            ),
            "evolution_cycle_ran": False,
            "evolution_cycle_scheduled": False,
        }

        every = int(os.environ.get("AGENT_BIOMIMETIC_EVOLVE_EVERY", "48"))
        cooldown = float(os.environ.get("AGENT_BIOMIMETIC_EVOLVE_COOLDOWN_SEC", "900"))
        self._agent_biomimetic_cycle_count += 1

        if every > 0 and self._agent_biomimetic_cycle_count % every == 0:
            now = time.time()
            if now - self._last_biomimetic_evolution_ts >= cooldown:
                self._last_biomimetic_evolution_ts = now
                try:
                    self._schedule_gradual_auto_evolution(task_data)
                    async_on = os.environ.get("AGENT_EVOLUTION_ASYNC", "true").lower() not in (
                        "0",
                        "false",
                        "no",
                    )
                    if async_on:
                        out["evolution_cycle_scheduled"] = True
                    else:
                        out["evolution_cycle_ran"] = True
                except Exception as e:
                    logger.warning("Ciclo auto-evolução (agente biomimético): %s", e)

        return out

    def get_agent_evolution_snapshot(self) -> Dict[str, Any]:
        """Estado resumido para observabilidade (API / painel)."""
        lb_stats = None
        learn_sz = 0
        if self.use_local_brain and self.local_brain is not None:
            lb_stats = self.local_brain.get_performance_stats()
            learn_sz = self.local_brain.get_learning_history_size()
        with self._evolution_thread_lock:
            worker_running = self._evolution_worker_running
            queued = self._evolution_queued_task is not None
        profile = os.environ.get("AGENT_EVOLUTION_PROFILE", "minimal").strip().lower()
        if profile not in ("minimal", "balanced", "full"):
            profile = "minimal"
        return {
            "performance_history_recent": list(self.performance_history)[-25:],
            "agent_biomimetic_cycles_total": self._agent_biomimetic_cycle_count,
            "last_biomimetic_evolution_unix": self._last_biomimetic_evolution_ts,
            "local_brain_performance": lb_stats,
            "local_brain_learning_entries": learn_sz,
            "evolve_every_n_agent_episodes": int(
                os.environ.get("AGENT_BIOMIMETIC_EVOLVE_EVERY", "48")
            ),
            "evolve_cooldown_sec": float(
                os.environ.get("AGENT_BIOMIMETIC_EVOLVE_COOLDOWN_SEC", "900")
            ),
            "evolution_worker_running": worker_running,
            "evolution_queued": queued,
            "evolution_profile": profile,
            "evolution_async": os.environ.get("AGENT_EVOLUTION_ASYNC", "true").lower()
            not in ("0", "false", "no"),
        }

    def _sleep_evolution_phase(self) -> None:
        """Pequena pausa entre fases para não monopolizar CPU (uso gradual)."""
        try:
            sec = float(os.environ.get("AGENT_EVOLUTION_PHASE_SLEEP_SEC", "0.03"))
        except ValueError:
            sec = 0.03
        if sec > 0:
            time.sleep(sec)

    def _perform_auto_evolution_profiled(self, task_data: Dict[str, Any]) -> None:
        """
        Ciclo autoevolutivo com perfil configurável.

        - **minimal** (default): só meta-learning (MAML/Reptile) — alinhado a “otimização
          baseada em gradientes” na taxonomia meta-learning / guia biomimético.
        - **balanced**: + consolidação + “arquitetura” leve, sem geração NEAT pesada.
        - **full**: meta + neuroevolução + resto (mais custoso; pode picar CPU).
        """
        profile = os.environ.get("AGENT_EVOLUTION_PROFILE", "minimal").strip().lower()
        if profile not in ("minimal", "balanced", "full"):
            profile = "minimal"

        self._meta_learning_adaptation(
            task_data, propagate_perf_to_auto_evolve=False
        )
        self._sleep_evolution_phase()

        if profile in ("balanced", "full"):
            self._architecture_evolution()
            self._sleep_evolution_phase()
            self._knowledge_consolidation()
            self._sleep_evolution_phase()

        if profile == "full":
            self._evolutionary_optimization(task_data)

        logger.info("✅ Auto-evolução concluída (perfil=%s)", profile)

    def _schedule_gradual_auto_evolution(self, task_data: Dict[str, Any]) -> None:
        """
        Agenda evolução sem bloquear o pedido HTTP: thread em daemon + fila de 1 slot
        (coalesce pedidos simultâneos).
        """
        sync = os.environ.get("AGENT_EVOLUTION_ASYNC", "true").lower() in (
            "0",
            "false",
            "no",
        )
        if sync:
            try:
                self._perform_auto_evolution_profiled(dict(task_data))
            except Exception as e:
                logger.warning("Auto-evolução síncrona: %s", e)
            return

        with self._evolution_thread_lock:
            if self._evolution_worker_running:
                self._evolution_queued_task = dict(task_data)
                logger.debug("Evolução em curso; ciclo extra coalescido na fila.")
                return
            self._evolution_worker_running = True

        td = dict(task_data)

        def worker() -> None:
            current: Optional[Dict[str, Any]] = td
            try:
                while current is not None:
                    try:
                        self._perform_auto_evolution_profiled(current)
                    except Exception as e:
                        logger.warning("Ciclo auto-evolução em background: %s", e)
                    with self._evolution_thread_lock:
                        nxt = self._evolution_queued_task
                        self._evolution_queued_task = None
                        if nxt is None:
                            self._evolution_worker_running = False
                            current = None
                        else:
                            current = nxt
            except Exception:
                with self._evolution_thread_lock:
                    self._evolution_worker_running = False
                    self._evolution_queued_task = None

        threading.Thread(
            target=worker, daemon=True, name="biomimetic-evolution"
        ).start()

    def _perform_auto_evolution(self, task_data: Dict[str, Any]):
        """Compatível com chamadas internas antigas: usa perfil + mesma pipeline."""
        self._perform_auto_evolution_profiled(task_data)

    def _meta_learning_adaptation(
        self,
        task_data: Dict[str, Any],
        *,
        propagate_perf_to_auto_evolve: bool = True,
    ):
        """
        Adapt using meta-learning
        """
        if not META_LEARNING_AVAILABLE:
            return

        try:
            tasks = self._create_few_shot_tasks(task_data)
            meta_loss = self.meta_learner.meta_train_step(tasks)
            algo = (
                self.meta_learner.meta_history[-1].get("algorithm", "?")
                if self.meta_learner.meta_history
                else "?"
            )
            # Liga ao ciclo auto-evolutivo: melhor meta-loss => métrica mais alta
            perf = 1.0 / (1.0 + float(meta_loss))
            if propagate_perf_to_auto_evolve:
                self.auto_evolve(perf, task_data)
            logger.info(
                "Meta-learning (%s): loss=%.4f, perf_metric=%.4f",
                algo,
                meta_loss,
                perf,
            )

        except Exception as e:
            logger.error(f"Erro no meta-learning: {e}")
    
    def _evolutionary_optimization(self, task_data: Dict[str, Any]):
        """
        Optimize using evolutionary algorithms
        """
        def fitness_function(individual):
            if hasattr(individual, 'fitness'):
                # NEAT genome
                return self._evaluate_neat_genome(individual, task_data)
            else:
                # Standard model
                return self._evaluate_model(individual['model'], task_data)
        
        # Run evolutionary optimization
        evolution_result = self.evolutionary_engine.evolve_neat_generation(fitness_function)
        
        logger.info(f"Evolução: fitness={evolution_result['best_fitness']:.4f}")
    
    def _architecture_evolution(self):
        """
        Evolve neural architecture
        """
        # Add new layers if beneficial
        if random.random() < 0.1:
            self._add_layer()
        
        # Remove layers if beneficial
        if random.random() < 0.05:
            self._remove_layer()
        
        # Modify connections
        if random.random() < 0.2:
            self._modify_connections()
    
    def _add_layer(self):
        """
        Add new layer to model
        """
        # Implementation for adding layers
        pass
    
    def _remove_layer(self):
        """
        Remove layer from model
        """
        # Implementation for removing layers
        pass
    
    def _modify_connections(self):
        """
        Modify neural connections
        """
        # Implementation for modifying connections
        pass
    
    def _knowledge_consolidation(self):
        """
        Consolidate learned knowledge
        """
        # Elastic Weight Consolidation
        if hasattr(self.meta_learner, 'important_weights'):
            ewc_loss = self.meta_learner.elastic_weight_consolidation(
                self.meta_learner.important_weights,
                self.meta_learner.fisher_info
            )
            logger.info(f"EWC Loss: {ewc_loss:.4f}")
    
    def _create_few_shot_tasks(
        self, task_data: Dict[str, Any]
    ) -> List[Tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]]:
        """
        Gera tarefas N-way episódicas (support / query) para meta-treino.
        Usa seed derivada do contexto para tarefas menos triviais que ruído i.i.d. puro.
        """
        n_tasks = int(os.environ.get("META_NUM_TASKS", "5"))
        n_support = int(os.environ.get("META_N_SUPPORT", "8"))
        n_query = int(os.environ.get("META_N_QUERY", "8"))
        seed_base = abs(
            hash(
                (
                    task_data.get("task_type", ""),
                    task_data.get("text_length", 0),
                    str(task_data.get("context", {})),
                )
            )
        ) % (2**31)
        tasks = []
        n_cls = 128
        for t in range(n_tasks):
            g = torch.Generator(device="cpu")
            g.manual_seed(seed_base + t * 9973)
            # Protótipo por tarefa + ruído (cada episódio com tendência de classe)
            proto = torch.randn(512, generator=g)
            sx = torch.randn(n_support, 512, generator=g) * 0.15 + proto
            qx = torch.randn(n_query, 512, generator=g) * 0.2 + proto
            center = int(torch.randint(0, n_cls, (1,), generator=g).item())
            spread = 3
            sy = torch.clamp(
                center + torch.randint(-spread, spread + 1, (n_support,), generator=g),
                0,
                n_cls - 1,
            )
            qy = torch.clamp(
                center + torch.randint(-spread, spread + 1, (n_query,), generator=g),
                0,
                n_cls - 1,
            )
            tasks.append((sx, sy, qx, qy))
        return tasks
    
    def _evaluate_neat_genome(self, genome, task_data: Dict[str, Any]) -> float:
        """
        Evaluate NEAT genome
        """
        try:
            # Create neural network from genome
            net = neat_nn.FeedForwardNetwork.create(genome, self.evolutionary_engine.neat_config)
            
            # Evaluate on task
            inputs = torch.randn(32, self.evolutionary_engine.input_size)
            outputs = []
            
            for input_data in inputs:
                output = net.activate(input_data.numpy())
                outputs.append(output)
            
            # Calculate fitness
            outputs = torch.tensor(outputs)
            fitness = 1.0 / (1.0 + torch.std(outputs).item())
            
            return fitness
            
        except Exception as e:
            logger.error(f"Erro na avaliação NEAT: {e}")
            return 0.0
    
    def _evaluate_model(self, model: nn.Module, task_data: Dict[str, Any]) -> float:
        """
        Evaluate standard model
        """
        try:
            with torch.no_grad():
                inputs = torch.randn(32, 512)
                outputs = model(inputs)
                fitness = 1.0 / (1.0 + torch.std(outputs).item())
                return fitness
        except Exception as e:
            logger.error(f"Erro na avaliação do modelo: {e}")
            return 0.0
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get complete system status
        """
        status = {
            'auto_evolution_active': self.auto_evolution_active,
            'current_generation': self.evolutionary_engine.generation,
            'best_fitness': self.evolutionary_engine.best_fitness,
            'meta_learning_stats': self.meta_learner.get_meta_learning_stats(),
            'performance_history': list(self.performance_history),
            'architecture_history': len(self.architecture_history),
            'frameworks_available': {
                'meta_learning': META_LEARNING_AVAILABLE,
                'higher_fomaml': HIGHER_AVAILABLE,
                'learn2learn': LEARN2LEARN_AVAILABLE,
                'neuroevolution': NEUROEVOLUTION_AVAILABLE,
                'xai': XAI_AVAILABLE,
            }
        }
        
        return status
    
    def save_system_state(self, filename: str = None):
        """
        Save complete system state
        """
        if filename is None:
            filename = f"auto_evolving_ai_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pkl"
        
        state = {
            'system_info': {
                'name': 'AutoEvolvingAISystem',
                'version': '4.0.0',
                'timestamp': datetime.now().isoformat()
            },
            'current_model_state': self.current_model.state_dict(),
            'meta_learner_history': self.meta_learner.meta_history,
            'evolution_history': self.evolutionary_engine.evolution_history,
            'performance_history': list(self.performance_history),
            'architecture_history': self.architecture_history,
            'system_status': self.get_system_status()
        }
        
        with open(filename, 'wb') as f:
            pickle.dump(state, f)
        
        logger.info(f"Estado do sistema salvo em: {filename}")
        return filename

class ExplanationEngine:
    """
    Engine for explainable AI (XAI)
    """
    
    def __init__(self, model: nn.Module):
        self.model = model
        if IntegratedGradients is None:
            raise RuntimeError("Captum (IntegratedGradients) não está disponível")
        self.integrated_gradients = IntegratedGradients(model)
    
    def explain_prediction(self, input_data: torch.Tensor, target_class: int = None) -> Dict[str, Any]:
        """
        Explain model prediction
        """
        if not XAI_AVAILABLE:
            return {"explanation": "XAI não disponível"}
        
        try:
            # Get model prediction
            with torch.no_grad():
                output = self.model(input_data)
                prediction = output.argmax(dim=1).item()
                confidence = F.softmax(output, dim=1).max().item()
            
            # Generate explanations
            attributions = self.integrated_gradients.attribute(input_data, target=target_class or prediction)
            
            explanation = {
                'prediction': prediction,
                'confidence': confidence,
                'attributions': attributions.tolist(),
                'feature_importance': torch.abs(attributions).mean(dim=0).tolist()
            }
            
            return explanation
            
        except Exception as e:
            logger.error(f"Erro na explicação: {e}")
            return {"error": str(e)}

class ConfidenceEstimator:
    """
    Estimate model confidence and uncertainty
    """
    
    def __init__(self, model: nn.Module):
        self.model = model
    
    def estimate_confidence(self, input_data: torch.Tensor) -> Dict[str, float]:
        """
        Estimate model confidence
        """
        try:
            with torch.no_grad():
                output = self.model(input_data)
                probabilities = F.softmax(output, dim=1)
                
                # Maximum probability as confidence
                confidence = probabilities.max().item()
                
                # Entropy as uncertainty measure
                entropy = -torch.sum(probabilities * torch.log(probabilities + 1e-8)).item()
                
                # Variance as uncertainty measure
                variance = torch.var(probabilities).item()
            
            return {
                'confidence': confidence,
                'entropy': entropy,
                'variance': variance,
                'uncertainty': 1.0 - confidence
            }
            
        except Exception as e:
            logger.error(f"Erro na estimativa de confiança: {e}")
            return {'confidence': 0.0, 'error': str(e)}

def main():
    """
    Teste do sistema autoevolutivo com meta-learning biomimético
    """
    print("🧬 SISTEMA AUTOEVOLUTIVO COM META-LEARNING BIOMIMÉTICO")
    print("=" * 70)
    print("🎯 Características:")
    print("   • Meta-learning (MAML, Reptile)")
    print("   • Evolução biomimética (NEAT)")
    print("   • Auto-evolução baseada em performance")
    print("   • XAI (Explainable AI)")
    print("   • Elastic Weight Consolidation")
    print("   • Few-shot learning")
    print("=" * 70)
    
    # Criar sistema autoevolutivo
    ai_system = AutoEvolvingAISystem()
    
    # Simular treinamento e auto-evolução
    print("\n🚀 Simulando treinamento e auto-evolução...")
    
    for epoch in range(10):
        # Simular performance
        performance = 0.5 + 0.1 * epoch + random.uniform(-0.05, 0.05)
        
        # Task data
        task_data = {
            'task_type': 'contract_analysis',
            'difficulty': random.uniform(0.1, 0.9),
            'data_size': random.randint(100, 1000)
        }
        
        # Trigger auto-evolution
        ai_system.auto_evolve(performance, task_data)
        
        print(f"Época {epoch + 1}: Performance = {performance:.4f}")
    
    # Status final
    status = ai_system.get_system_status()
    
    print("\n📊 STATUS FINAL:")
    print(f"   • Geração: {status['current_generation']}")
    print(f"   • Melhor Fitness: {status['best_fitness']:.4f}")
    print(f"   • Meta-learning: {status['meta_learning_stats']}")
    print(f"   • Frameworks: {status['frameworks_available']}")
    
    # Salvar estado
    state_file = ai_system.save_system_state()
    print(f"💾 Estado salvo: {state_file}")
    
    print("\n🎉 Sistema autoevolutivo com meta-learning biomimético executado!")
    print("✅ Pronto para análise de contratos e justificativas!")

if __name__ == "__main__":
    main() 
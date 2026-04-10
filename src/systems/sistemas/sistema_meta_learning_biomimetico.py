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
import copy
from collections import deque
import pickle

# Orchestration evolution imports
try:
    from .orchestration_evolution import OrchestrationEvolutionEngine
    ORCHESTRATION_EVOLUTION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ OrchestrationEvolutionEngine não disponível: {e}")
    ORCHESTRATION_EVOLUTION_AVAILABLE = False

# Meta-learning imports
META_LEARNING_AVAILABLE = False
try:
    # learn2learn tem incompatibilidade - comentando temporariamente
    # import learn2learn as l2l
    # from higher import innerloop_ctx
    META_LEARNING_AVAILABLE = False
    print("⚠️ learn2learn não disponível por incompatibilidade")
except ImportError:
    print("⚠️ Meta-learning frameworks não disponíveis")

# Neuroevolution imports
NEUROEVOLUTION_AVAILABLE = False
try:
    import neat
    from neat import nn as neat_nn
    NEUROEVOLUTION_AVAILABLE = True
except ImportError:
    print("⚠️ Neuroevolution frameworks não disponíveis")

# XAI imports
XAI_AVAILABLE = False
try:
    import shap
    import lime
    from captum.attr import IntegratedGradients
    XAI_AVAILABLE = True
except ImportError:
    print("⚠️ XAI frameworks não disponíveis")

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

class BiomimeticMetaLearner:
    """
    Meta-learner biomimético que aprende a aprender
    Implementa MAML, Reptile e outros algoritmos meta-learning
    """
    
    def __init__(self, model: nn.Module, meta_lr: float = 0.01, adaptation_steps: int = 5):
        self.model = model
        self.meta_lr = meta_lr
        self.adaptation_steps = adaptation_steps
        self.meta_optimizer = torch.optim.Adam(self.model.parameters(), lr=meta_lr)
        
        # Histórico de meta-learning
        self.meta_history = []
        self.task_performance = {}
        self.knowledge_base = {}
        
        # Biomimetic parameters
        self.plasticity_rate = 0.1
        self.consolidation_strength = 0.8
        self.forgetting_rate = 0.05
        
    def meta_train_step(self, tasks: List[Tuple[torch.Tensor, torch.Tensor]]) -> float:
        """
        Meta-training step usando MAML (Model-Agnostic Meta-Learning)
        """
        meta_loss = 0.0
        
        for task_data, task_labels in tasks:
            # Clone model for task-specific adaptation
            adapted_model = copy.deepcopy(self.model)
            task_optimizer = torch.optim.SGD(adapted_model.parameters(), lr=0.01)
            
            # Inner loop - adapt to specific task
            for _ in range(self.adaptation_steps):
                task_output = adapted_model(task_data)
                task_loss = F.cross_entropy(task_output, task_labels)
                task_optimizer.zero_grad()
                task_loss.backward()
                task_optimizer.step()
            
            # Outer loop - meta-update
            meta_output = adapted_model(task_data)
            meta_task_loss = F.cross_entropy(meta_output, task_labels)
            meta_loss += meta_task_loss
        
        # Meta-optimization
        self.meta_optimizer.zero_grad()
        meta_loss.backward()
        self.meta_optimizer.step()
        
        # Record meta-learning progress
        self.meta_history.append({
            'timestamp': datetime.now().isoformat(),
            'meta_loss': meta_loss.item(),
            'tasks_processed': len(tasks)
        })
        
        return meta_loss.item()
    
    def reptile_step(self, tasks: List[Tuple[torch.Tensor, torch.Tensor]]) -> float:
        """
        Reptile meta-learning algorithm
        """
        reptile_loss = 0.0
        
        for task_data, task_labels in tasks:
            # Task-specific adaptation
            adapted_model = copy.deepcopy(self.model)
            task_optimizer = torch.optim.SGD(adapted_model.parameters(), lr=0.01)
            
            for _ in range(self.adaptation_steps):
                task_output = adapted_model(task_data)
                task_loss = F.cross_entropy(task_output, task_labels)
                task_optimizer.zero_grad()
                task_loss.backward()
                task_optimizer.step()
            
            # Reptile update: move towards adapted parameters
            for param, adapted_param in zip(self.model.parameters(), adapted_model.parameters()):
                param.data += self.meta_lr * (adapted_param.data - param.data)
            
            reptile_loss += task_loss.item()
        
        return reptile_loss
    
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
            return {}
        
        recent_losses = [h['meta_loss'] for h in self.meta_history[-10:]]
        
        return {
            'avg_meta_loss': np.mean(recent_losses),
            'meta_loss_trend': np.mean(recent_losses[-5:]) - np.mean(recent_losses[:5]),
            'total_tasks_processed': sum(h['tasks_processed'] for h in self.meta_history),
            'knowledge_base_size': len(self.knowledge_base),
            'adaptation_steps': self.adaptation_steps,
            'meta_lr': self.meta_lr
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
                self.local_brain = HybridBiomimeticSystem(brain_type=self.local_brain_type)
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
                self._perform_auto_evolution(task_data)
    
    def _perform_auto_evolution(self, task_data: Dict[str, Any]):
        """
        Perform auto-evolution process
        """
        # 1. Meta-learning adaptation
        self._meta_learning_adaptation(task_data)
        
        # 2. Evolutionary optimization
        self._evolutionary_optimization(task_data)
        
        # 3. Architecture evolution
        self._architecture_evolution()
        
        # 4. Knowledge consolidation
        self._knowledge_consolidation()
        
        logger.info("✅ Auto-evolução concluída")
    
    def _meta_learning_adaptation(self, task_data: Dict[str, Any]):
        """
        Adapt using meta-learning
        """
        if not META_LEARNING_AVAILABLE:
            return
        
        try:
            # Create few-shot tasks
            tasks = self._create_few_shot_tasks(task_data)
            
            # Meta-training
            meta_loss = self.meta_learner.meta_train_step(tasks)
            
            # Reptile step
            reptile_loss = self.meta_learner.reptile_step(tasks)
            
            logger.info(f"Meta-learning: loss={meta_loss:.4f}, reptile={reptile_loss:.4f}")
            
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
    
    def _create_few_shot_tasks(self, task_data: Dict[str, Any]) -> List[Tuple[torch.Tensor, torch.Tensor]]:
        """
        Create few-shot learning tasks
        """
        # Simulate few-shot tasks
        tasks = []
        for _ in range(5):
            # Create synthetic task data
            task_inputs = torch.randn(10, 512)
            task_labels = torch.randint(0, 128, (10,))
            tasks.append((task_inputs, task_labels))
        
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
                'neuroevolution': NEUROEVOLUTION_AVAILABLE,
                'xai': XAI_AVAILABLE
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
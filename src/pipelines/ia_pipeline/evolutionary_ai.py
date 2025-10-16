"""
IA Autoevolutiva Biomimética com Meta-Learning
==============================================

Sistema de IA que evolui sua própria arquitetura usando princípios biomiméticos
e meta-learning para otimização contínua e adaptação a novos cenários.

Características:
- Meta-learning (aprender a aprender)
- Evolução biomimética (algoritmos genéticos)
- Auto-evolução de arquitetura neural
- Sistema de segurança e guardrails
- Otimização para hardware disponível
- Aprendizado contínuo e adaptativo
"""

import os
import json
import logging
import time
import random
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Union, Callable
from dataclasses import dataclass, field
from datetime import datetime
import pickle
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Função para serializar datetime
def serialize_datetime(obj):
    """Serializa objetos datetime para JSON"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Aplicar em todas as funções de salvamento
def save_evolution_state(self, filename: str = None) -> str:
    """Salva estado da evolução com correção de datetime"""
    if filename is None:
        filename = f"evolution_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    state = {
        'generation': self.generation,
        'best_fitness': self.best_individual.fitness_score if self.best_individual else 0.0,
        'population_size': len(self.population),
        'evolution_history': [
            {
                'generation': hist.generation,
                'best_fitness': hist.best_fitness,
                'timestamp': hist.timestamp.isoformat() if hasattr(hist, 'timestamp') else datetime.now().isoformat()
            }
            for hist in self.evolution_history
        ],
        'timestamp': datetime.now().isoformat()
    }
    
    with open(filename, 'w') as f:
        json.dump(state, f, indent=2, default=serialize_datetime)
    
    return filename


# Machine Learning e Deep Learning
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
from torch.optim import Adam, SGD
from torch.optim.lr_scheduler import ReduceLROnPlateau

# Transformers e modelos avançados
from transformers import (
    AutoTokenizer, AutoModel, AutoModelForSequenceClassification,
    pipeline, TextGenerationPipeline, Trainer, TrainingArguments
)

# Meta-learning
# import learn2learn  # Removido por compatibilidade as l2l
# from learn2learn  # Removido por compatibilidade.algorithms import MAML, Reptile
# from learn2learn  # Removido por compatibilidade.optim import MetaSGD

# Algoritmos genéticos e evolução
from deap import base, creator, tools, algorithms
import networkx as nx

# NLP e processamento
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
try:
    from framework_integration import framework_manager
except ImportError:
    # Fallback se não conseguir importar
    framework_manager = None

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evolutionary_ai.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configurações globais
EVOLUTION_CONFIG = {
    'population_size': 50,
    'generations': 100,
    'mutation_rate': 0.1,
    'crossover_rate': 0.7,
    'elite_size': 5,
    'meta_learning_steps': 5,
    'fitness_threshold': 0.85,
    'max_architecture_complexity': 1000000,  # Parâmetros máximos
    'safety_threshold': 0.95,
    'evolution_rate_limit': 0.1,  # Máximo de mudança por geração
}

# Estruturas de dados
@dataclass
class NeuralArchitecture:
    """Arquitetura neural evolutiva"""
    layers: List[Dict[str, Any]]
    connections: List[Tuple[int, int]]
    hyperparameters: Dict[str, Any]
    fitness_score: float = 0.0
    generation: int = 0
    parent_id: Optional[str] = None
    mutation_history: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    safety_score: float = 1.0
    complexity_score: float = 0.0
    
    def __post_init__(self):
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Gera ID único para a arquitetura"""
        arch_str = json.dumps(self.layers, sort_keys=True) + str(self.connections)
        return hashlib.md5(arch_str.encode()).hexdigest()[:16]

@dataclass
class MetaLearningTask:
    """Tarefa de meta-learning"""
    task_id: str
    task_type: str
    input_data: Any
    target_data: Any
    task_metadata: Dict[str, Any]
    difficulty: float = 1.0
    adaptation_steps: int = 5

@dataclass
class EvolutionState:
    """Estado da evolução"""
    generation: int
    best_fitness: float
    population: List[NeuralArchitecture]
    task_history: List[MetaLearningTask]
    evolution_stats: Dict[str, Any]
    safety_violations: int = 0
    last_improvement: int = 0

class BiomimeticEvolution:
    """Evolução biomimética inspirada na natureza"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or EVOLUTION_CONFIG
        self.population = []
        self.generation = 0
        self.best_individual = None
        self.evolution_history = []
        self.safety_monitor = SafetyMonitor()
        self.meta_learner = MetaLearner()
        
        # Adicionar atributo evolution_engine para compatibilidade
        self.evolution_engine = self
        
        # Configurar algoritmo genético
        self._setup_genetic_algorithm()
        
        logger.info("Sistema de evolução biomimética inicializado")
    
    def _setup_genetic_algorithm(self):
        """Configura o algoritmo genético usando DEAP"""
        # Criar tipos para o algoritmo genético
        if not hasattr(creator, "FitnessMax"):
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMax)
        
        self.toolbox = base.Toolbox()
        
        # Operadores genéticos
        self.toolbox.register("evaluate", self._evaluate_fitness)
        self.toolbox.register("mate", self._crossover)
        self.toolbox.register("mutate", self._mutate)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
    
    def _evaluate_fitness(self, individual):
        """Método de avaliação de fitness para DEAP"""
        try:
            # Converter indivíduo DEAP para NeuralArchitecture
            if isinstance(individual, list):
                # Criar arquitetura a partir da lista
                arch = NeuralArchitecture(
                    layers=individual[:len(individual)//2] if len(individual) > 1 else [],
                    connections=individual[len(individual)//2:] if len(individual) > 1 else [],
                    hyperparameters={'learning_rate': 0.001, 'dropout': 0.2}
                )
            else:
                arch = individual
            
            # Avaliar usando o método existente
            tasks = self._generate_default_tasks()
            fitness = self._evaluate_individual(arch, tasks)
            
            return (fitness,)
        except Exception as e:
            logger.error(f"Erro no _evaluate_fitness: {e}")
            return (0.0,)
    
    def _mutate(self, individual):
        """Método de mutação para DEAP"""
        try:
            # Mutação simples para indivíduos DEAP
            if random.random() < 0.1:  # 10% chance de mutação
                if len(individual) > 0:
                    idx = random.randint(0, len(individual) - 1)
                    individual[idx] = random.uniform(0, 1)
            return (individual,)
        except Exception as e:
            logger.error(f"Erro no _mutate: {e}")
            return (individual,)
    
    def _generate_default_tasks(self) -> List[MetaLearningTask]:
        """Gera tarefas padrão para evolução"""
        tasks = []
        
        # Tarefa de classificação
        classification_task = MetaLearningTask(
            task_id="classification_001",
            task_type="classification",
            input_data=np.random.randn(100, 512),
            target_data=np.random.randint(0, 2, (100, 1)),
            task_metadata={"num_classes": 2},
            difficulty=0.5
        )
        tasks.append(classification_task)
        
        # Tarefa de regressão
        regression_task = MetaLearningTask(
            task_id="regression_001",
            task_type="regression",
            input_data=np.random.randn(100, 512),
            target_data=np.random.randn(100, 1),
            task_metadata={"output_dim": 1},
            difficulty=0.6
        )
        tasks.append(regression_task)
        
        return tasks
    
    def evolve_population(self, tasks: List[MetaLearningTask]) -> EvolutionState:
        """Evolui a população usando princípios biomiméticos"""
        logger.info(f"Iniciando evolução da geração {self.generation}")
        
        # Avaliar população atual
        fitness_scores = []
        for individual in self.population:
            fitness = self._evaluate_individual(individual, tasks)
            individual.fitness_score = fitness
            fitness_scores.append(fitness)
        
        # Verificar segurança
        safety_violations = self.safety_monitor.check_population(self.population)
        
        # Seleção natural (elitismo + torneio)
        elite = self._select_elite()
        offspring = self._generate_offspring()
        
        # Mutação biomimética
        mutated_offspring = self._biomimetic_mutation(offspring)
        
        # Meta-learning para adaptação rápida
        adapted_offspring = self._meta_learning_adaptation(mutated_offspring, tasks)
        
        # Nova população
        self.population = elite + adapted_offspring
        self.generation += 1
        
        # Atualizar estatísticas
        best_fitness = max(fitness_scores)
        self.best_individual = self.population[np.argmax(fitness_scores)]
        
        evolution_state = EvolutionState(
            generation=self.generation,
            best_fitness=best_fitness,
            population=self.population.copy(),
            task_history=tasks,
            evolution_stats=self._calculate_evolution_stats(),
            safety_violations=safety_violations
        )
        
        self.evolution_history.append(evolution_state)
        logger.info(f"Evolução da geração {self.generation} concluída. Melhor fitness: {best_fitness:.4f}")
        
        return evolution_state
    
    def _evaluate_individual(self, individual: NeuralArchitecture, tasks: List[MetaLearningTask]) -> float:
        """Avalia um indivíduo usando múltiplas métricas com validação de segurança"""
        try:
            # Validação de segurança prévia
            if not self._validate_architecture_safety(individual):
                logger.warning(f"Arquitetura {individual.id} falhou na validação de segurança")
                return 0.1
            
            # Performance em tarefas de meta-learning
            meta_performance = self.meta_learner.evaluate_architecture(individual, tasks)
            
            # Complexidade da arquitetura
            complexity_penalty = self._calculate_complexity_penalty(individual)
            
            # Segurança
            safety_score = self.safety_monitor.evaluate_individual(individual)
            
            # Fitness final (média ponderada)
            fitness = (
                0.6 * meta_performance +
                0.2 * (1.0 - complexity_penalty) +
                0.2 * safety_score
            )
            
            # Penalizar se segurança muito baixa
            if safety_score < 0.3:
                fitness *= 0.5
                logger.warning(f"Arquitetura {individual.id} penalizada por baixa segurança: {safety_score}")
            
            individual.performance_metrics = {
                'meta_performance': meta_performance,
                'complexity_penalty': complexity_penalty,
                'safety_score': safety_score,
                'fitness': fitness
            }
            
            return max(0.0, min(1.0, fitness))
            
        except Exception as e:
            logger.error(f"Erro na avaliação do indivíduo: {e}")
            return 0.1  # Fitness mínimo em caso de erro
    
    def _validate_architecture_safety(self, individual: NeuralArchitecture) -> bool:
        """Valida se a arquitetura é segura antes da avaliação"""
        try:
            # Verificar número de camadas
            if len(individual.layers) > 15:
                logger.warning(f"Arquitetura com muitas camadas: {len(individual.layers)}")
                return False
            
            # Verificar tamanho das camadas
            for i, layer in enumerate(individual.layers):
                units = layer.get('units', 64)
                if units < 8 or units > 1024:
                    logger.warning(f"Camada {i} com unidades inválidas: {units}")
                    return False
                
                # Verificar se é attention e se units é divisível por 8
                if layer.get('type') == 'attention':
                    if units % 8 != 0:
                        logger.warning(f"Camada attention {i} com units não divisível por 8: {units}")
                        return False
            
            # Verificar hiperparâmetros
            if 'learning_rate' in individual.hyperparameters:
                lr = individual.hyperparameters['learning_rate']
                if lr <= 0 or lr > 1.0:
                    logger.warning(f"Learning rate inválido: {lr}")
                    return False
            
            if 'dropout' in individual.hyperparameters:
                dropout = individual.hyperparameters['dropout']
                if dropout < 0 or dropout > 0.8:
                    logger.warning(f"Dropout inválido: {dropout}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação de segurança: {e}")
            return False
    
    def _biomimetic_mutation(self, offspring: List[NeuralArchitecture]) -> List[NeuralArchitecture]:
        """Mutação inspirada em processos biológicos"""
        mutated = []
        
        for individual in offspring:
            if random.random() < self.config['mutation_rate']:
                # Tipos de mutação biomimética
                mutation_type = random.choice([
                    'point_mutation',      # Mutação pontual
                    'structural_mutation', # Mutação estrutural
                    'regulatory_mutation', # Mutação regulatória
                    'epigenetic_mutation'  # Mutação epigenética
                ])
                
                mutated_individual = self._apply_biomimetic_mutation(individual, mutation_type)
                mutated.append(mutated_individual)
            else:
                mutated.append(individual)
        
        return mutated
    
    def _apply_biomimetic_mutation(self, individual: NeuralArchitecture, mutation_type: str) -> NeuralArchitecture:
        """Aplica mutação biomimética específica"""
        new_individual = NeuralArchitecture(
            layers=individual.layers.copy(),
            connections=individual.connections.copy(),
            hyperparameters=individual.hyperparameters.copy(),
            parent_id=individual.id,
            generation=individual.generation + 1
        )
        
        if mutation_type == 'point_mutation':
            # Mutação pontual: altera parâmetros específicos
            if new_individual.layers:
                layer_idx = random.randint(0, len(new_individual.layers) - 1)
                layer = new_individual.layers[layer_idx]
                if 'units' in layer:
                    layer['units'] = max(1, layer['units'] + random.randint(-10, 10))
        
        elif mutation_type == 'structural_mutation':
            # Mutação estrutural: adiciona/remove camadas
            if random.random() < 0.5 and len(new_individual.layers) < 10:
                # Adicionar camada
                new_layer = {
                    'type': random.choice(['dense', 'conv', 'lstm', 'attention']),
                    'units': random.randint(32, 512),
                    'activation': random.choice(['relu', 'tanh', 'sigmoid', 'leaky_relu'])
                }
                new_individual.layers.append(new_layer)
            elif len(new_individual.layers) > 1:
                # Remover camada
                remove_idx = random.randint(0, len(new_individual.layers) - 1)
                new_individual.layers.pop(remove_idx)
        
        elif mutation_type == 'regulatory_mutation':
            # Mutação regulatória: altera hiperparâmetros
            if 'learning_rate' in new_individual.hyperparameters:
                new_individual.hyperparameters['learning_rate'] *= random.uniform(0.5, 2.0)
            if 'dropout' in new_individual.hyperparameters:
                new_individual.hyperparameters['dropout'] = random.uniform(0.1, 0.5)
        
        elif mutation_type == 'epigenetic_mutation':
            # Mutação epigenética: altera conexões
            if len(new_individual.connections) > 0:
                # Adicionar conexão skip
                max_layer = len(new_individual.layers) - 1
                if max_layer > 0:
                    from_layer = random.randint(0, max_layer - 1)
                    to_layer = random.randint(from_layer + 1, max_layer)
                    new_connection = (from_layer, to_layer)
                    if new_connection not in new_individual.connections:
                        new_individual.connections.append(new_connection)
        
        new_individual.mutation_history.append(f"{mutation_type}_{time.time()}")
        return new_individual
    
    def _meta_learning_adaptation(self, offspring: List[NeuralArchitecture], tasks: List[MetaLearningTask]) -> List[NeuralArchitecture]:
        """Adapta indivíduos usando meta-learning"""
        adapted = []
        
        for individual in offspring:
            # Aplicar meta-learning para adaptação rápida
            adapted_individual = self.meta_learner.adapt_architecture(individual, tasks)
            adapted.append(adapted_individual)
        
        return adapted
    
    def _calculate_complexity_penalty(self, individual: NeuralArchitecture) -> float:
        """Calcula penalidade por complexidade excessiva"""
        total_params = sum(layer.get('units', 0) for layer in individual.layers)
        complexity_ratio = total_params / self.config['max_architecture_complexity']
        return min(1.0, complexity_ratio)
    
    def _select_elite(self) -> List[NeuralArchitecture]:
        """Seleciona os melhores indivíduos (elitismo)"""
        sorted_population = sorted(self.population, key=lambda x: x.fitness_score, reverse=True)
        return sorted_population[:self.config['elite_size']]
    
    def _generate_offspring(self) -> List[NeuralArchitecture]:
        """Gera descendentes através de crossover"""
        offspring = []
        population_size = len(self.population)
        
        while len(offspring) < population_size - self.config['elite_size']:
            # Seleção de pais
            parent1 = random.choice(self.population)
            parent2 = random.choice(self.population)
            
            if random.random() < self.config['crossover_rate']:
                # Crossover
                child = self._crossover(parent1, parent2)
            else:
                # Clonagem
                child = NeuralArchitecture(
                    layers=parent1.layers.copy(),
                    connections=parent1.connections.copy(),
                    hyperparameters=parent1.hyperparameters.copy(),
                    parent_id=parent1.id,
                    generation=parent1.generation + 1
                )
            
            offspring.append(child)
        
        return offspring
    
    def _crossover(self, parent1: NeuralArchitecture, parent2: NeuralArchitecture) -> NeuralArchitecture:
        """Realiza crossover entre dois pais"""
        # Crossover de camadas
        crossover_point = random.randint(0, min(len(parent1.layers), len(parent2.layers)))
        child_layers = parent1.layers[:crossover_point] + parent2.layers[crossover_point:]
        
        # Crossover de conexões
        child_connections = parent1.connections + parent2.connections
        child_connections = list(set(child_connections))  # Remove duplicatas
        
        # Crossover de hiperparâmetros
        child_hyperparams = {}
        for key in set(parent1.hyperparameters.keys()) | set(parent2.hyperparameters.keys()):
            if random.random() < 0.5:
                child_hyperparams[key] = parent1.hyperparameters.get(key, 0)
            else:
                child_hyperparams[key] = parent2.hyperparameters.get(key, 0)
        
        return NeuralArchitecture(
            layers=child_layers,
            connections=child_connections,
            hyperparameters=child_hyperparams,
            parent_id=f"{parent1.id}_{parent2.id}",
            generation=max(parent1.generation, parent2.generation) + 1
        )
    
    def _calculate_evolution_stats(self) -> Dict[str, Any]:
        """Calcula estatísticas da evolução"""
        if not self.population:
            return {}
        
        fitness_scores = [ind.fitness_score for ind in self.population]
        
        return {
            'mean_fitness': np.mean(fitness_scores),
            'std_fitness': np.std(fitness_scores),
            'max_fitness': np.max(fitness_scores),
            'min_fitness': np.min(fitness_scores),
            'diversity': self._calculate_diversity(),
            'convergence_rate': self._calculate_convergence_rate()
        }
    
    def _calculate_diversity(self) -> float:
        """Calcula diversidade da população"""
        if len(self.population) < 2:
            return 0.0
        
        # Diversidade baseada em diferenças de arquitetura
        diversity_scores = []
        for i in range(len(self.population)):
            for j in range(i + 1, len(self.population)):
                diff = self._architecture_difference(self.population[i], self.population[j])
                diversity_scores.append(diff)
        
        return np.mean(diversity_scores) if diversity_scores else 0.0
    
    def _architecture_difference(self, arch1: NeuralArchitecture, arch2: NeuralArchitecture) -> float:
        """Calcula diferença entre duas arquiteturas"""
        # Diferença no número de camadas
        layer_diff = abs(len(arch1.layers) - len(arch2.layers)) / max(len(arch1.layers), len(arch2.layers), 1)
        
        # Diferença nas conexões
        conn_diff = len(set(arch1.connections) ^ set(arch2.connections)) / max(len(arch1.connections), len(arch2.connections), 1)
        
        # Diferença nos hiperparâmetros
        param_diff = 0
        all_params = set(arch1.hyperparameters.keys()) | set(arch2.hyperparameters.keys())
        for param in all_params:
            val1 = arch1.hyperparameters.get(param, 0)
            val2 = arch2.hyperparameters.get(param, 0)
            param_diff += abs(val1 - val2) / max(abs(val1), abs(val2), 1)
        
        param_diff /= max(len(all_params), 1)
        
        return (layer_diff + conn_diff + param_diff) / 3
    
    def _calculate_convergence_rate(self) -> float:
        """Calcula taxa de convergência"""
        if len(self.evolution_history) < 2:
            return 0.0
        
        recent_fitness = [state.best_fitness for state in self.evolution_history[-5:]]
        if len(recent_fitness) < 2:
            return 0.0
        
        # Taxa de melhoria
        improvements = 0
        for i in range(1, len(recent_fitness)):
            if recent_fitness[i] > recent_fitness[i-1]:
                improvements += 1
        
        return improvements / (len(recent_fitness) - 1)
    
    def _create_random_architecture(self) -> NeuralArchitecture:
        """Cria arquitetura neural aleatória com validação de segurança"""
        num_layers = random.randint(2, 6)  # Máximo de 6 camadas para segurança
        layers = []
        
        for i in range(num_layers):
            layer_type = random.choice(['dense', 'lstm', 'attention'])
            
            # Definir unidades baseado no tipo de camada
            if layer_type == 'attention':
                # Para attention, garantir que seja divisível por 8
                units = random.choice([64, 128, 256])  # Valores seguros
            else:
                units = random.randint(32, 256)
            
            layer = {
                'type': layer_type,
                'units': units,
                'activation': random.choice(['relu', 'tanh', 'sigmoid', 'leaky_relu'])
            }
            layers.append(layer)
        
        # Conexões aleatórias (limitadas para segurança)
        connections = []
        max_connections = min(num_layers - 1, 2)  # Máximo de 2 conexões skip
        for i in range(num_layers - 1):
            if random.random() < 0.15 and len(connections) < max_connections:  # 15% chance
                to_layer = random.randint(i + 1, num_layers - 1)
                connections.append((i, to_layer))
        
        # Hiperparâmetros aleatórios com validação
        hyperparameters = {
            'learning_rate': random.uniform(0.001, 0.01),  # Range conservador
            'dropout': random.uniform(0.1, 0.3),  # Range seguro
            'batch_size': random.choice([16, 32, 64])  # Valores seguros
        }
        
        return NeuralArchitecture(
            layers=layers,
            connections=connections,
            hyperparameters=hyperparameters,
            generation=0
        )

class MetaLearner:
    """Sistema de Meta-Learning para adaptação rápida"""
    
    def __init__(self):
        self.adaptation_history = []
        self.knowledge_base = {}
        self.adaptation_strategies = {}
        logger.info("Sistema de meta-learning inicializado")
    
    def quick_adaptation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Adaptação rápida a uma nova tarefa"""
        task_type = task.get('type', 'unknown')
        task_data = task.get('data', [])
        task_target = task.get('target', [])
        
        # Simular adaptação rápida
        adaptation_steps = 5
        learning_progress = []
        
        for step in range(adaptation_steps):
            # Simular aprendizado incremental
            progress = (step + 1) / adaptation_steps
            accuracy = 0.3 + (progress * 0.6)  # Melhoria gradual
            
            learning_progress.append({
                'step': step + 1,
                'accuracy': accuracy,
                'progress': progress
            })
        
        # Calcular performance final
        final_accuracy = learning_progress[-1]['accuracy']
        
        result = {
            'success': final_accuracy > 0.5,
            'performance': final_accuracy,
            'adaptation_steps': adaptation_steps,
            'learning_progress': learning_progress,
            'task_type': task_type
        }
        
        # Registrar na história
        self.adaptation_history.append({
            'timestamp': datetime.now().isoformat(),
            'task': task_type,
            'result': result
        })
        
        return result
    
    def knowledge_transfer(self, source_task: Dict[str, Any], target_task: Dict[str, Any]) -> Dict[str, Any]:
        """Transferência de conhecimento entre tarefas"""
        source_type = source_task.get('type', 'unknown')
        target_type = target_task.get('type', 'unknown')
        
        # Simular transferência de conhecimento
        transfer_efficiency = 0.7 if source_type == target_type else 0.3
        knowledge_gained = transfer_efficiency * 0.5
        
        return {
            'transfer_success': transfer_efficiency > 0.2,
            'transfer_efficiency': transfer_efficiency,
            'knowledge_gained': knowledge_gained,
            'source_task': source_type,
            'target_task': target_type
        }
    
    # Adicionar métodos faltantes ao MetaLearner
    def evaluate_architecture(self, individual, tasks):
        """Avalia arquitetura usando meta-learning"""
        try:
            # Simular avaliação de arquitetura
            base_score = 0.5
            
            # Avaliar em múltiplas tarefas
            task_scores = []
            for task in tasks:
                # Simular performance na tarefa
                task_performance = 0.3 + (hash(str(individual.id)) % 100) / 100.0
                task_scores.append(task_performance)
            
            # Score final é a média das tarefas
            final_score = sum(task_scores) / len(task_scores) if task_scores else base_score
            return max(0.0, min(1.0, final_score))
            
        except Exception as e:
            logger.warning(f"Erro na avaliação de arquitetura: {e}")
            return 0.5
    
    def adapt_architecture(self, individual, tasks):
        """Adapta arquitetura usando meta-learning"""
        try:
            # Criar cópia do indivíduo
            adapted = type(individual)(
                layers=individual.layers.copy(),
                connections=individual.connections.copy(),
                hyperparameters=individual.hyperparameters.copy(),
                parent_id=individual.id,
                generation=individual.generation + 1
            )
            
            # Aplicar adaptações baseadas nas tarefas
            for task in tasks:
                if task.task_type == "classification":
                    # Adaptar para classificação
                    if adapted.hyperparameters.get('learning_rate', 0.001) > 0.01:
                        adapted.hyperparameters['learning_rate'] *= 0.9
                elif task.task_type == "regression":
                    # Adaptar para regressão
                    if len(adapted.layers) < 5:
                        adapted.layers.append({
                            'type': 'dense',
                            'units': 64,
                            'activation': 'relu'
                        })
            
            return adapted
            
        except Exception as e:
            logger.warning(f"Erro na adaptação de arquitetura: {e}")
            return individual
    

class AttentionWrapper(nn.Module):
    """Wrapper para camadas de atenção com validação de segurança"""
    
    def __init__(self, attention_layer: nn.MultiheadAttention, embed_dim: int):
        super().__init__()
        self.attention_layer = attention_layer
        self.embed_dim = embed_dim
        self.projection = nn.Linear(embed_dim, embed_dim)
    
    def forward(self, x):
        try:
            # Garantir que x tenha as dimensões corretas
            if x.dim() == 2:
                x = x.unsqueeze(0)  # Adicionar dimensão de batch se necessário
            
            # Para MultiheadAttention, precisamos de query, key, value
            # Usar x como query, key e value
            attn_output, _ = self.attention_layer(x, x, x)
            
            # Projeção adicional para estabilidade
            output = self.projection(attn_output)
            
            return output
            
        except Exception as e:
            logger.warning(f"Erro na camada de atenção: {e}")
            # Fallback: retornar entrada sem modificação
            return x

class SafetyMonitor:
    """Monitor de segurança para evolução controlada"""
    
    def __init__(self):
        self.safety_rules = self._initialize_safety_rules()
        self.violation_history = []
        self.safety_threshold = 0.95
        
        logger.info("Sistema de monitoramento de segurança inicializado")
    
    def _initialize_safety_rules(self) -> Dict[str, Callable]:
        """Inicializa regras de segurança"""
        return {
            'complexity_limit': self._check_complexity_limit,
            'performance_degradation': self._check_performance_degradation,
            'stability_check': self._check_stability,
            'resource_usage': self._check_resource_usage,
            'behavior_consistency': self._check_behavior_consistency
        }
    
    def check_population(self, population: List[NeuralArchitecture]) -> int:
        """Verifica segurança de toda a população"""
        violations = 0
        
        for individual in population:
            if not self.evaluate_individual(individual):
                violations += 1
        
        return violations
    
    def evaluate_individual(self, individual: NeuralArchitecture) -> float:
        """Avalia segurança de um indivíduo"""
        safety_scores = []
        
        for rule_name, rule_func in self.safety_rules.items():
            try:
                score = rule_func(individual)
                safety_scores.append(score)
            except Exception as e:
                logger.warning(f"Erro na regra de segurança {rule_name}: {e}")
                safety_scores.append(0.0)
        
        # Score de segurança é a média das regras
        safety_score = np.mean(safety_scores) if safety_scores else 0.0
        individual.safety_score = safety_score
        
        return safety_score
    
    def _check_complexity_limit(self, individual: NeuralArchitecture) -> float:
        """Verifica se a complexidade está dentro dos limites"""
        total_params = sum(layer.get('units', 0) for layer in individual.layers)
        max_params = 1000000  # 1M parâmetros
        
        if total_params > max_params:
            return 0.0
        
        # Score baseado na eficiência (menos parâmetros = melhor)
        efficiency = 1.0 - (total_params / max_params)
        return max(0.0, efficiency)
    
    def _check_performance_degradation(self, individual: NeuralArchitecture) -> float:
        """Verifica se não há degradação significativa de performance"""
        if not hasattr(individual, 'performance_metrics'):
            return 1.0
        
        metrics = individual.performance_metrics
        if 'meta_performance' not in metrics:
            return 1.0
        
        # Penalizar se performance for muito baixa
        performance = metrics['meta_performance']
        if performance < 0.3:
            return 0.0
        
        return performance
    
    def _check_stability(self, individual: NeuralArchitecture) -> float:
        """Verifica estabilidade da arquitetura"""
        # Verificar se não há camadas com 0 unidades
        for layer in individual.layers:
            if layer.get('units', 0) <= 0:
                return 0.0
        
        # Verificar se conexões são válidas
        max_layer_idx = len(individual.layers) - 1
        for from_layer, to_layer in individual.connections:
            if from_layer < 0 or to_layer < 0 or from_layer > max_layer_idx or to_layer > max_layer_idx:
                return 0.0
            if from_layer >= to_layer:  # Conexões devem ser direcionadas
                return 0.0
        
        return 1.0
    
    def _check_resource_usage(self, individual: NeuralArchitecture) -> float:
        """Verifica uso de recursos"""
        # Estimativa de memória baseada na arquitetura
        estimated_memory = sum(layer.get('units', 0) for layer in individual.layers) * 4  # bytes
        max_memory = 4 * 1024 * 1024 * 1024  # 4GB
        
        if estimated_memory > max_memory:
            return 0.0
        
        memory_efficiency = 1.0 - (estimated_memory / max_memory)
        return max(0.0, memory_efficiency)
    
    def _check_behavior_consistency(self, individual: NeuralArchitecture) -> float:
        """Verifica consistência de comportamento"""
        # Verificar se hiperparâmetros estão em ranges razoáveis
        hyperparams = individual.hyperparameters
        
        if 'learning_rate' in hyperparams:
            lr = hyperparams['learning_rate']
            if lr <= 0 or lr > 1.0:
                return 0.0
        
        if 'dropout' in hyperparams:
            dropout = hyperparams['dropout']
            if dropout < 0 or dropout > 0.9:
                return 0.0
        
        return 1.0

class EvolutionaryAI:
    """IA Autoevolutiva Biomimética Principal"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or EVOLUTION_CONFIG
        self.population = []
        self.generation = 0
        self.best_individual = None
        self.evolution_history = []
        self.safety_monitor = SafetyMonitor()
        self.meta_learner = MetaLearner()
        
        # Adicionar atributo evolution_engine para compatibilidade
        self.evolution_engine = self
        
        # Configurar algoritmo genético
        self._setup_genetic_algorithm()
        
        logger.info("Sistema de evolução biomimética inicializado")
    
    def _setup_genetic_algorithm(self):
        """Configura o algoritmo genético usando DEAP"""
        # Criar tipos para o algoritmo genético
        if not hasattr(creator, "FitnessMax"):
            creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        if not hasattr(creator, "Individual"):
            creator.create("Individual", list, fitness=creator.FitnessMax)
        
        self.toolbox = base.Toolbox()
        
        # Operadores genéticos
        self.toolbox.register("evaluate", self._evaluate_fitness)
        self.toolbox.register("mate", self._crossover)
        self.toolbox.register("mutate", self._mutate)
        self.toolbox.register("select", tools.selTournament, tournsize=3)
    
    def _evaluate_fitness(self, individual):
        """Método de avaliação de fitness para DEAP"""
        try:
            # Converter indivíduo DEAP para NeuralArchitecture
            if isinstance(individual, list):
                # Criar arquitetura a partir da lista
                arch = NeuralArchitecture(
                    layers=individual[:len(individual)//2] if len(individual) > 1 else [],
                    connections=individual[len(individual)//2:] if len(individual) > 1 else [],
                    hyperparameters={'learning_rate': 0.001, 'dropout': 0.2}
                )
            else:
                arch = individual
            
            # Avaliar usando o método existente
            tasks = self._generate_default_tasks()
            fitness = self._evaluate_individual(arch, tasks)
            
            return (fitness,)
        except Exception as e:
            logger.error(f"Erro no _evaluate_fitness: {e}")
            return (0.0,)
    
    def _mutate(self, individual):
        """Método de mutação para DEAP"""
        try:
            # Mutação simples para indivíduos DEAP
            if random.random() < 0.1:  # 10% chance de mutação
                if len(individual) > 0:
                    idx = random.randint(0, len(individual) - 1)
                    individual[idx] = random.uniform(0, 1)
            return (individual,)
        except Exception as e:
            logger.error(f"Erro no _mutate: {e}")
            return (individual,)
    
    def _generate_default_tasks(self) -> List[MetaLearningTask]:
        """Gera tarefas padrão para evolução"""
        tasks = []
        
        # Tarefa de classificação
        classification_task = MetaLearningTask(
            task_id="classification_001",
            task_type="classification",
            input_data=np.random.randn(100, 512),
            target_data=np.random.randint(0, 2, (100, 1)),
            task_metadata={"num_classes": 2},
            difficulty=0.5
        )
        tasks.append(classification_task)
        
        # Tarefa de regressão
        regression_task = MetaLearningTask(
            task_id="regression_001",
            task_type="regression",
            input_data=np.random.randn(100, 512),
            target_data=np.random.randn(100, 1),
            task_metadata={"output_dim": 1},
            difficulty=0.6
        )
        tasks.append(regression_task)
        
        return tasks
    
    def evolve_population(self, tasks: List[MetaLearningTask]) -> EvolutionState:
        """Evolui a população usando princípios biomiméticos"""
        logger.info(f"Iniciando evolução da geração {self.generation}")
        
        # Avaliar população atual
        fitness_scores = []
        for individual in self.population:
            fitness = self._evaluate_individual(individual, tasks)
            individual.fitness_score = fitness
            fitness_scores.append(fitness)
        
        # Verificar segurança
        safety_violations = self.safety_monitor.check_population(self.population)
        
        # Seleção natural (elitismo + torneio)
        elite = self._select_elite()
        offspring = self._generate_offspring()
        
        # Mutação biomimética
        mutated_offspring = self._biomimetic_mutation(offspring)
        
        # Meta-learning para adaptação rápida
        adapted_offspring = self._meta_learning_adaptation(mutated_offspring, tasks)
        
        # Nova população
        self.population = elite + adapted_offspring
        self.generation += 1
        
        # Atualizar estatísticas
        best_fitness = max(fitness_scores)
        self.best_individual = self.population[np.argmax(fitness_scores)]
        
        evolution_state = EvolutionState(
            generation=self.generation,
            best_fitness=best_fitness,
            population=self.population.copy(),
            task_history=tasks,
            evolution_stats=self._calculate_evolution_stats(),
            safety_violations=safety_violations
        )
        
        self.evolution_history.append(evolution_state)
        logger.info(f"Evolução da geração {self.generation} concluída. Melhor fitness: {best_fitness:.4f}")
        
        return evolution_state
    
    def _evaluate_individual(self, individual: NeuralArchitecture, tasks: List[MetaLearningTask]) -> float:
        """Avalia um indivíduo usando múltiplas métricas com validação de segurança"""
        try:
            # Validação de segurança prévia
            if not self._validate_architecture_safety(individual):
                logger.warning(f"Arquitetura {individual.id} falhou na validação de segurança")
                return 0.1
            
            # Performance em tarefas de meta-learning
            meta_performance = self.meta_learner.evaluate_architecture(individual, tasks)
            
            # Complexidade da arquitetura
            complexity_penalty = self._calculate_complexity_penalty(individual)
            
            # Segurança
            safety_score = self.safety_monitor.evaluate_individual(individual)
            
            # Fitness final (média ponderada)
            fitness = (
                0.6 * meta_performance +
                0.2 * (1.0 - complexity_penalty) +
                0.2 * safety_score
            )
            
            # Penalizar se segurança muito baixa
            if safety_score < 0.3:
                fitness *= 0.5
                logger.warning(f"Arquitetura {individual.id} penalizada por baixa segurança: {safety_score}")
            
            individual.performance_metrics = {
                'meta_performance': meta_performance,
                'complexity_penalty': complexity_penalty,
                'safety_score': safety_score,
                'fitness': fitness
            }
            
            return max(0.0, min(1.0, fitness))
            
        except Exception as e:
            logger.error(f"Erro na avaliação do indivíduo: {e}")
            return 0.1  # Fitness mínimo em caso de erro
    
    def _validate_architecture_safety(self, individual: NeuralArchitecture) -> bool:
        """Valida se a arquitetura é segura antes da avaliação"""
        try:
            # Verificar número de camadas
            if len(individual.layers) > 15:
                logger.warning(f"Arquitetura com muitas camadas: {len(individual.layers)}")
                return False
            
            # Verificar tamanho das camadas
            for i, layer in enumerate(individual.layers):
                units = layer.get('units', 64)
                if units < 8 or units > 1024:
                    logger.warning(f"Camada {i} com unidades inválidas: {units}")
                    return False
                
                # Verificar se é attention e se units é divisível por 8
                if layer.get('type') == 'attention':
                    if units % 8 != 0:
                        logger.warning(f"Camada attention {i} com units não divisível por 8: {units}")
                        return False
            
            # Verificar hiperparâmetros
            if 'learning_rate' in individual.hyperparameters:
                lr = individual.hyperparameters['learning_rate']
                if lr <= 0 or lr > 1.0:
                    logger.warning(f"Learning rate inválido: {lr}")
                    return False
            
            if 'dropout' in individual.hyperparameters:
                dropout = individual.hyperparameters['dropout']
                if dropout < 0 or dropout > 0.8:
                    logger.warning(f"Dropout inválido: {dropout}")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Erro na validação de segurança: {e}")
            return False
    
    def _biomimetic_mutation(self, offspring: List[NeuralArchitecture]) -> List[NeuralArchitecture]:
        """Mutação inspirada em processos biológicos"""
        mutated = []
        
        for individual in offspring:
            if random.random() < self.config['mutation_rate']:
                # Tipos de mutação biomimética
                mutation_type = random.choice([
                    'point_mutation',      # Mutação pontual
                    'structural_mutation', # Mutação estrutural
                    'regulatory_mutation', # Mutação regulatória
                    'epigenetic_mutation'  # Mutação epigenética
                ])
                
                mutated_individual = self._apply_biomimetic_mutation(individual, mutation_type)
                mutated.append(mutated_individual)
            else:
                mutated.append(individual)
        
        return mutated
    
    def _apply_biomimetic_mutation(self, individual: NeuralArchitecture, mutation_type: str) -> NeuralArchitecture:
        """Aplica mutação biomimética específica"""
        new_individual = NeuralArchitecture(
            layers=individual.layers.copy(),
            connections=individual.connections.copy(),
            hyperparameters=individual.hyperparameters.copy(),
            parent_id=individual.id,
            generation=individual.generation + 1
        )
        
        if mutation_type == 'point_mutation':
            # Mutação pontual: altera parâmetros específicos
            if new_individual.layers:
                layer_idx = random.randint(0, len(new_individual.layers) - 1)
                layer = new_individual.layers[layer_idx]
                if 'units' in layer:
                    layer['units'] = max(1, layer['units'] + random.randint(-10, 10))
        
        elif mutation_type == 'structural_mutation':
            # Mutação estrutural: adiciona/remove camadas
            if random.random() < 0.5 and len(new_individual.layers) < 10:
                # Adicionar camada
                new_layer = {
                    'type': random.choice(['dense', 'conv', 'lstm', 'attention']),
                    'units': random.randint(32, 512),
                    'activation': random.choice(['relu', 'tanh', 'sigmoid', 'leaky_relu'])
                }
                new_individual.layers.append(new_layer)
            elif len(new_individual.layers) > 1:
                # Remover camada
                remove_idx = random.randint(0, len(new_individual.layers) - 1)
                new_individual.layers.pop(remove_idx)
        
        elif mutation_type == 'regulatory_mutation':
            # Mutação regulatória: altera hiperparâmetros
            if 'learning_rate' in new_individual.hyperparameters:
                new_individual.hyperparameters['learning_rate'] *= random.uniform(0.5, 2.0)
            if 'dropout' in new_individual.hyperparameters:
                new_individual.hyperparameters['dropout'] = random.uniform(0.1, 0.5)
        
        elif mutation_type == 'epigenetic_mutation':
            # Mutação epigenética: altera conexões
            if len(new_individual.connections) > 0:
                # Adicionar conexão skip
                max_layer = len(new_individual.layers) - 1
                if max_layer > 0:
                    from_layer = random.randint(0, max_layer - 1)
                    to_layer = random.randint(from_layer + 1, max_layer)
                    new_connection = (from_layer, to_layer)
                    if new_connection not in new_individual.connections:
                        new_individual.connections.append(new_connection)
        
        new_individual.mutation_history.append(f"{mutation_type}_{time.time()}")
        return new_individual
    
    def _meta_learning_adaptation(self, offspring: List[NeuralArchitecture], tasks: List[MetaLearningTask]) -> List[NeuralArchitecture]:
        """Adapta indivíduos usando meta-learning"""
        adapted = []
        
        for individual in offspring:
            # Aplicar meta-learning para adaptação rápida
            adapted_individual = self.meta_learner.adapt_architecture(individual, tasks)
            adapted.append(adapted_individual)
        
        return adapted
    
    def _calculate_complexity_penalty(self, individual: NeuralArchitecture) -> float:
        """Calcula penalidade por complexidade excessiva"""
        total_params = sum(layer.get('units', 0) for layer in individual.layers)
        complexity_ratio = total_params / self.config['max_architecture_complexity']
        return min(1.0, complexity_ratio)
    
    def _select_elite(self) -> List[NeuralArchitecture]:
        """Seleciona os melhores indivíduos (elitismo)"""
        sorted_population = sorted(self.population, key=lambda x: x.fitness_score, reverse=True)
        return sorted_population[:self.config['elite_size']]
    
    def _generate_offspring(self) -> List[NeuralArchitecture]:
        """Gera descendentes através de crossover"""
        offspring = []
        population_size = len(self.population)
        
        while len(offspring) < population_size - self.config['elite_size']:
            # Seleção de pais
            parent1 = random.choice(self.population)
            parent2 = random.choice(self.population)
            
            if random.random() < self.config['crossover_rate']:
                # Crossover
                child = self._crossover(parent1, parent2)
            else:
                # Clonagem
                child = NeuralArchitecture(
                    layers=parent1.layers.copy(),
                    connections=parent1.connections.copy(),
                    hyperparameters=parent1.hyperparameters.copy(),
                    parent_id=parent1.id,
                    generation=parent1.generation + 1
                )
            
            offspring.append(child)
        
        return offspring
    
    def _crossover(self, parent1: NeuralArchitecture, parent2: NeuralArchitecture) -> NeuralArchitecture:
        """Realiza crossover entre dois pais"""
        # Crossover de camadas
        crossover_point = random.randint(0, min(len(parent1.layers), len(parent2.layers)))
        child_layers = parent1.layers[:crossover_point] + parent2.layers[crossover_point:]
        
        # Crossover de conexões
        child_connections = parent1.connections + parent2.connections
        child_connections = list(set(child_connections))  # Remove duplicatas
        
        # Crossover de hiperparâmetros
        child_hyperparams = {}
        for key in set(parent1.hyperparameters.keys()) | set(parent2.hyperparameters.keys()):
            if random.random() < 0.5:
                child_hyperparams[key] = parent1.hyperparameters.get(key, 0)
            else:
                child_hyperparams[key] = parent2.hyperparameters.get(key, 0)
        
        return NeuralArchitecture(
            layers=child_layers,
            connections=child_connections,
            hyperparameters=child_hyperparams,
            parent_id=f"{parent1.id}_{parent2.id}",
            generation=max(parent1.generation, parent2.generation) + 1
        )
    
    def _calculate_evolution_stats(self) -> Dict[str, Any]:
        """Calcula estatísticas da evolução"""
        if not self.population:
            return {}
        
        fitness_scores = [ind.fitness_score for ind in self.population]
        
        return {
            'mean_fitness': np.mean(fitness_scores),
            'std_fitness': np.std(fitness_scores),
            'max_fitness': np.max(fitness_scores),
            'min_fitness': np.min(fitness_scores),
            'diversity': self._calculate_diversity(),
            'convergence_rate': self._calculate_convergence_rate()
        }
    
    def _calculate_diversity(self) -> float:
        """Calcula diversidade da população"""
        if len(self.population) < 2:
            return 0.0
        
        # Diversidade baseada em diferenças de arquitetura
        diversity_scores = []
        for i in range(len(self.population)):
            for j in range(i + 1, len(self.population)):
                diff = self._architecture_difference(self.population[i], self.population[j])
                diversity_scores.append(diff)
        
        return np.mean(diversity_scores) if diversity_scores else 0.0
    
    def _architecture_difference(self, arch1: NeuralArchitecture, arch2: NeuralArchitecture) -> float:
        """Calcula diferença entre duas arquiteturas"""
        # Diferença no número de camadas
        layer_diff = abs(len(arch1.layers) - len(arch2.layers)) / max(len(arch1.layers), len(arch2.layers), 1)
        
        # Diferença nas conexões
        conn_diff = len(set(arch1.connections) ^ set(arch2.connections)) / max(len(arch1.connections), len(arch2.connections), 1)
        
        # Diferença nos hiperparâmetros
        param_diff = 0
        all_params = set(arch1.hyperparameters.keys()) | set(arch2.hyperparameters.keys())
        for param in all_params:
            val1 = arch1.hyperparameters.get(param, 0)
            val2 = arch2.hyperparameters.get(param, 0)
            param_diff += abs(val1 - val2) / max(abs(val1), abs(val2), 1)
        
        param_diff /= max(len(all_params), 1)
        
        return (layer_diff + conn_diff + param_diff) / 3
    
    def _calculate_convergence_rate(self) -> float:
        """Calcula taxa de convergência"""
        if len(self.evolution_history) < 2:
            return 0.0
        
        recent_fitness = [state.best_fitness for state in self.evolution_history[-5:]]
        if len(recent_fitness) < 2:
            return 0.0
        
        # Taxa de melhoria
        improvements = 0
        for i in range(1, len(recent_fitness)):
            if recent_fitness[i] > recent_fitness[i-1]:
                improvements += 1
        
        return improvements / (len(recent_fitness) - 1)
    
    def _create_random_architecture(self) -> NeuralArchitecture:
        """Cria arquitetura neural aleatória com validação de segurança"""
        num_layers = random.randint(2, 6)  # Máximo de 6 camadas para segurança
        layers = []
        
        for i in range(num_layers):
            layer_type = random.choice(['dense', 'lstm', 'attention'])
            
            # Definir unidades baseado no tipo de camada
            if layer_type == 'attention':
                # Para attention, garantir que seja divisível por 8
                units = random.choice([64, 128, 256])  # Valores seguros
            else:
                units = random.randint(32, 256)
            
            layer = {
                'type': layer_type,
                'units': units,
                'activation': random.choice(['relu', 'tanh', 'sigmoid', 'leaky_relu'])
            }
            layers.append(layer)
        
        # Conexões aleatórias (limitadas para segurança)
        connections = []
        max_connections = min(num_layers - 1, 2)  # Máximo de 2 conexões skip
        for i in range(num_layers - 1):
            if random.random() < 0.15 and len(connections) < max_connections:  # 15% chance
                to_layer = random.randint(i + 1, num_layers - 1)
                connections.append((i, to_layer))
        
        # Hiperparâmetros aleatórios com validação
        hyperparameters = {
            'learning_rate': random.uniform(0.001, 0.01),  # Range conservador
            'dropout': random.uniform(0.1, 0.3),  # Range seguro
            'batch_size': random.choice([16, 32, 64])  # Valores seguros
        }
        
        return NeuralArchitecture(
            layers=layers,
            connections=connections,
            hyperparameters=hyperparameters,
            generation=0
        )
    
    def evolve(self, tasks: List[MetaLearningTask] = None) -> EvolutionState:
        """Executa uma geração de evolução"""
        if tasks is None:
            tasks = self._generate_default_tasks()
        
        # Executar evolução
        evolution_state = self.evolution_engine.evolve_population(tasks)
        self.current_state = evolution_state
        
        # Verificar convergência
        if self._check_convergence(evolution_state):
            logger.info("Evolução convergiu!")
        
        return evolution_state
    
    def _generate_default_tasks(self) -> List[MetaLearningTask]:
        """Gera tarefas padrão para evolução"""
        tasks = []
        
        # Tarefa de classificação
        classification_task = MetaLearningTask(
            task_id="classification_001",
            task_type="classification",
            input_data=np.random.randn(100, 512),
            target_data=np.random.randint(0, 2, (100, 1)),
            task_metadata={"num_classes": 2},
            difficulty=0.5
        )
        tasks.append(classification_task)
        
        # Tarefa de regressão
        regression_task = MetaLearningTask(
            task_id="regression_001",
            task_type="regression",
            input_data=np.random.randn(100, 512),
            target_data=np.random.randn(100, 1),
            task_metadata={"output_dim": 1},
            difficulty=0.6
        )
        tasks.append(regression_task)
        
        return tasks
    
    def _check_convergence(self, state: EvolutionState) -> bool:
        """Verifica se a evolução convergiu"""
        if len(self.evolution_engine.evolution_history) < 10:
            return False
        
        # Verificar se fitness não melhorou nas últimas 10 gerações
        recent_fitness = [s.best_fitness for s in self.evolution_engine.evolution_history[-10:]]
        if len(recent_fitness) < 10:
            return False
        
        # Calcular melhoria média
        improvements = []
        for i in range(1, len(recent_fitness)):
            improvement = recent_fitness[i] - recent_fitness[i-1]
            improvements.append(improvement)
        
        avg_improvement = np.mean(improvements)
        
        # Convergência se melhoria média < threshold
        return avg_improvement < 0.001
    
    def get_best_architecture(self) -> Optional[NeuralArchitecture]:
        """Retorna a melhor arquitetura encontrada"""
        if self.evolution_engine.best_individual:
            return self.evolution_engine.best_individual
        
        if self.evolution_engine.population:
            return max(self.evolution_engine.population, key=lambda x: x.fitness_score)
        
        return None
    
    def add_task(self, task: MetaLearningTask):
        """Adiciona nova tarefa ao registro"""
        self.task_registry.append(task)
        logger.info(f"Nova tarefa adicionada: {task.task_id}")
    
    def add_custom_task(self, task_data: Dict[str, Any]):
        """Adiciona tarefa customizada a partir de dicionário"""
        task_id = task_data.get('task_id', f"task_{len(self.task_registry)}")
        task_type = task_data.get('type', 'classification')
        input_data = task_data.get('input_data')
        target_data = task_data.get('target_data')
        metadata = task_data.get('metadata', {})
        difficulty = task_data.get('difficulty', 1.0)
        adaptation_steps = task_data.get('adaptation_steps', 5)
        
        task = MetaLearningTask(
            task_id=task_id,
            task_type=task_type,
            input_data=input_data,
            target_data=target_data,
            task_metadata=metadata,
            difficulty=difficulty,
            adaptation_steps=adaptation_steps
        )
        self.add_task(task)
        return task_id
    
    def start_evolution(self, generations: int = 10) -> Dict[str, Any]:
        """Inicia processo de evolução e retorna resultados"""
        logger.info(f"Iniciando evolução por {generations} gerações")
        
        start_time = time.time()
        evolution_history = []
        generations_completed = 0
        initial_fitness = 0.0
        
        for gen in range(generations):
            logger.info(f"Geração {gen + 1}/{generations}")
            
            # Executar evolução
            state = self.evolve()
            evolution_history.append(state)
            generations_completed += 1
            
            # Guardar fitness inicial
            if gen == 0:
                initial_fitness = state.best_fitness if state else 0.0
            
            # Verificar convergência
            if self._check_convergence(state):
                logger.info(f"Evolução convergiu na geração {gen + 1}")
                break
        
        evolution_time = time.time() - start_time
        best_fitness = state.best_fitness if state else 0.0
        
        # Calcular taxa de melhoria
        improvement_rate = 0.0
        if initial_fitness > 0:
            improvement_rate = (best_fitness - initial_fitness) / initial_fitness
        
        # Calcular violações de segurança
        safety_violations = sum(state.safety_violations for state in evolution_history) if evolution_history else 0
        
        return {
            'generations_completed': generations_completed,
            'evolution_time': evolution_time,
            'best_fitness': best_fitness,
            'improvement_rate': improvement_rate,
            'safety_violations': safety_violations,
            'evolution_history': evolution_history
        }
    
    @property
    def ai(self):
        """Propriedade para compatibilidade com testes"""
        return self.evolution_engine
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Retorna métricas de performance atuais"""
        if not self.current_state:
            return {"status": "Não evoluiu ainda"}
        
        return {
            "generation": self.current_state.generation,
            "best_fitness": self.current_state.best_fitness,
            "population_size": len(self.current_state.population),
            "safety_violations": self.current_state.safety_violations,
            "evolution_stats": self.current_state.evolution_stats
        }
    
    def save_state(self, filepath: str) -> bool:
        """Salva estado atual da IA"""
        try:
            state_data = {
                "current_state": self.current_state,
                "task_registry": self.task_registry,
                "config": self.config
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(state_data, f)
            
            logger.info(f"Estado salvo em: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """Carrega estado salvo da IA"""
        try:
            with open(filepath, 'rb') as f:
                state_data = pickle.load(f)
            
            self.current_state = state_data.get("current_state")
            self.task_registry = state_data.get("task_registry", [])
            self.config.update(state_data.get("config", {}))
            
            logger.info(f"Estado carregado de: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")
            return False
        self.task_registry.append(task)
        logger.info(f"Nova tarefa adicionada: {task.task_id}")
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da evolução"""
        if not self.evolution_engine.evolution_history:
            return {}
        
        latest_state = self.evolution_engine.evolution_history[-1]
        
        return {
            'current_generation': latest_state.generation,
            'best_fitness': latest_state.best_fitness,
            'population_size': len(latest_state.population),
            'safety_violations': latest_state.safety_violations,
            'evolution_stats': latest_state.evolution_stats,
            'total_generations': len(self.evolution_engine.evolution_history)
        }
    
    def save_system_state(self) -> str:
        """Salva estado do sistema e retorna caminho do arquivo"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_state_{timestamp}.pkl"
            filepath = os.path.join(os.getcwd(), filename)
            
            success = self.save_state(filepath)
            if success:
                return filepath
            else:
                return ""
        except Exception as e:
            logger.error(f"Erro ao salvar estado do sistema: {e}")
            return ""
    
    def load_system_state(self, filepath: str) -> bool:
        """Carrega estado do sistema"""
        try:
            return self.load_state(filepath)
        except Exception as e:
            logger.error(f"Erro ao carregar estado do sistema: {e}")
            return False
    
    def initialize_population(self, population_size: int = 50):
        """Inicializa a população com indivíduos aleatórios"""
        logger.info(f"Inicializando população com {population_size} indivíduos")
        
        self.population = []
        for i in range(population_size):
            # Criar arquitetura neural aleatória
            layers = []
            num_layers = random.randint(2, 6)
            
            for layer_idx in range(num_layers):
                layer_type = random.choice(['dense', 'attention', 'conv'])
                units = random.choice([32, 64, 128, 256, 512])
                
                layer = {
                    'type': layer_type,
                    'units': units,
                    'activation': random.choice(['relu', 'tanh', 'sigmoid'])
                }
                layers.append(layer)
            
            # Hiperparâmetros
            hyperparameters = {
                'learning_rate': random.uniform(0.0001, 0.01),
                'dropout': random.uniform(0.1, 0.5),
                'batch_size': random.choice([16, 32, 64, 128])
            }
            
            # Criar indivíduo
            individual = NeuralArchitecture(
                layers=layers,
                connections=[(i, i+1) for i in range(len(layers)-1)],
                hyperparameters=hyperparameters,
                generation=0
            )
            
            self.population.append(individual)
        
        logger.info(f"✅ População inicializada com {len(self.population)} indivíduos")
    
    def get_best_architecture(self) -> Optional[NeuralArchitecture]:
        """Retorna a melhor arquitetura encontrada"""
        if self.evolution_engine.best_individual:
            return self.evolution_engine.best_individual
        
        if self.evolution_engine.population:
            return max(self.evolution_engine.population, key=lambda x: x.fitness_score)
        
        return None

# Funções de interface
def create_evolutionary_ai(config: Dict[str, Any] = None) -> EvolutionaryAI:
    """Cria instância da IA autoevolutiva"""
    return EvolutionaryAI(config)

def evolve_ai(ai: EvolutionaryAI, generations: int = 10, tasks: List[MetaLearningTask] = None) -> List[EvolutionState]:
    """Executa múltiplas gerações de evolução"""
    states = []
    
    for generation in range(generations):
        logger.info(f"Executando geração {generation + 1}/{generations}")
        state = ai.evolve(tasks)
        states.append(state)
        
        # Verificar se convergiu
        if ai._check_convergence(state):
            logger.info(f"Evolução convergiu na geração {generation + 1}")
            break
    
    return states

def get_ai_performance(ai: EvolutionaryAI) -> Dict[str, Any]:
    """Retorna performance atual da IA"""
    return ai.get_evolution_stats() 
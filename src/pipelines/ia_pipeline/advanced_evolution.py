"""
Evolução Avançada para IA Autoevolutiva
=======================================

Upgrade dos Mecanismos de Evolução:
1. Função de Aptidão Multi-objetivo
2. Novos Operadores Genéticos
3. Meta-Learning Avançado
4. Sistema de Validação Robusto
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

# Algoritmos genéticos e evolução
from deap import base, creator, tools, algorithms
import networkx as nx

# NLP e processamento
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('advanced_evolution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class MultiObjectiveFitness:
    """Função de aptidão multi-objetivo"""
    accuracy: float = 0.0
    efficiency: float = 0.0
    interpretability: float = 0.0
    robustness: float = 0.0
    overall_score: float = 0.0
    
    def calculate_overall(self, weights: Dict[str, float]) -> float:
        """Calcula score geral baseado nos pesos"""
        self.overall_score = (
            weights.get('accuracy', 0.4) * self.accuracy +
            weights.get('efficiency', 0.2) * self.efficiency +
            weights.get('interpretability', 0.2) * self.interpretability +
            weights.get('robustness', 0.2) * self.robustness
        )
        return self.overall_score

@dataclass
class AdvancedNeuralArchitecture:
    """Arquitetura neural avançada com capacidades evolutivas"""
    layers: List[Dict[str, Any]]
    connections: List[Tuple[int, int]]
    hyperparameters: Dict[str, Any]
    modules: List[Dict[str, Any]] = field(default_factory=list)  # Módulos reutilizáveis
    fitness: MultiObjectiveFitness = field(default_factory=MultiObjectiveFitness)
    generation: int = 0
    parent_id: Optional[str] = None
    mutation_history: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    safety_score: float = 1.0
    complexity_score: float = 0.0
    interpretability_score: float = 0.0
    robustness_score: float = 0.0
    
    def __post_init__(self):
        self.id = self._generate_id()
        self._calculate_complexity()
    
    def _generate_id(self) -> str:
        """Gera ID único para a arquitetura"""
        arch_str = json.dumps(self.layers, sort_keys=True) + str(self.connections)
        return hashlib.md5(arch_str.encode()).hexdigest()[:16]
    
    def _calculate_complexity(self):
        """Calcula score de complexidade"""
        total_params = sum(layer.get('parameters', 0) for layer in self.layers)
        total_connections = len(self.connections)
        self.complexity_score = (total_params + total_connections) / 1000000  # Normalizado

class AdvancedGeneticOperators:
    """Operadores genéticos avançados"""
    
    @staticmethod
    def modularization_mutation(individual: AdvancedNeuralArchitecture) -> AdvancedNeuralArchitecture:
        """Mutação de modularização - encapsula sub-redes em módulos reutilizáveis"""
        try:
            # Identificar padrões de conexão que podem formar módulos
            if len(individual.layers) < 3:
                return individual
            
            # Encontrar grupos de camadas conectadas
            graph = nx.Graph()
            for i, layer in enumerate(individual.layers):
                graph.add_node(i)
            
            for conn in individual.connections:
                graph.add_edge(conn[0], conn[1])
            
            # Encontrar comunidades usando algoritmo de detecção de comunidades
            communities = list(nx.community.greedy_modularity_communities(graph))
            
            if len(communities) > 1:
                # Criar módulo a partir da maior comunidade
                largest_community = max(communities, key=len)
                if len(largest_community) >= 2:
                    module = {
                        'type': 'functional_module',
                        'layers': list(largest_community),
                        'input_layer': min(largest_community),
                        'output_layer': max(largest_community),
                        'connections': [conn for conn in individual.connections 
                                      if conn[0] in largest_community and conn[1] in largest_community]
                    }
                    
                    individual.modules.append(module)
                    individual.mutation_history.append(f"modularization_{len(individual.modules)}")
            
            return individual
        except Exception as e:
            logger.error(f"Erro na mutação de modularização: {e}")
            return individual
    
    @staticmethod
    def fusion_mutation(individual: AdvancedNeuralArchitecture) -> AdvancedNeuralArchitecture:
        """Mutação de fusão - combina neurônios com funções similares"""
        try:
            if len(individual.layers) < 2:
                return individual
            
            # Identificar camadas com funções similares (mesmo tipo e tamanho similar)
            similar_layers = []
            for i, layer1 in enumerate(individual.layers):
                for j, layer2 in enumerate(individual.layers[i+1:], i+1):
                    if (layer1.get('type') == layer2.get('type') and
                        abs(layer1.get('size', 0) - layer2.get('size', 0)) < 10):
                        similar_layers.append((i, j))
            
            if similar_layers:
                # Escolher um par aleatório para fusão
                i, j = random.choice(similar_layers)
                
                # Criar camada fusionada
                fused_layer = {
                    'type': individual.layers[i]['type'],
                    'size': max(individual.layers[i].get('size', 0), 
                              individual.layers[j].get('size', 0)),
                    'parameters': individual.layers[i].get('parameters', 0) + 
                                individual.layers[j].get('parameters', 0),
                    'fusion_source': [i, j]
                }
                
                # Substituir camadas originais pela fusionada
                individual.layers[i] = fused_layer
                individual.layers.pop(j)
                
                # Atualizar conexões
                new_connections = []
                for conn in individual.connections:
                    if conn[0] == j:
                        new_connections.append((i, conn[1]))
                    elif conn[1] == j:
                        new_connections.append((conn[0], i))
                    elif conn[0] != j and conn[1] != j:
                        new_connections.append(conn)
                
                individual.connections = new_connections
                individual.mutation_history.append(f"fusion_{i}_{j}")
            
            return individual
        except Exception as e:
            logger.error(f"Erro na mutação de fusão: {e}")
            return individual
    
    @staticmethod
    def adaptive_mutation(individual: AdvancedNeuralArchitecture, 
                         performance_history: List[float]) -> AdvancedNeuralArchitecture:
        """Mutação adaptativa baseada no histórico de performance"""
        try:
            if len(performance_history) < 3:
                return individual
            
            # Calcular tendência de performance
            recent_performance = performance_history[-3:]
            trend = (recent_performance[-1] - recent_performance[0]) / len(recent_performance)
            
            if trend < 0:  # Performance decaindo
                # Mutação mais agressiva
                mutation_strength = 0.3
            elif trend > 0.1:  # Performance melhorando
                # Mutação conservadora
                mutation_strength = 0.05
            else:
                # Mutação moderada
                mutation_strength = 0.1
            
            # Aplicar mutação baseada na força calculada
            if random.random() < mutation_strength:
                if random.random() < 0.5:
                    individual = AdvancedGeneticOperators.modularization_mutation(individual)
                else:
                    individual = AdvancedGeneticOperators.fusion_mutation(individual)
                
                individual.mutation_history.append(f"adaptive_{mutation_strength:.2f}")
            
            return individual
        except Exception as e:
            logger.error(f"Erro na mutação adaptativa: {e}")
            return individual

class AdvancedFitnessEvaluator:
    """Avaliador de aptidão multi-objetivo"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.weights = config.get('fitness_weights', {
            'accuracy': 0.4,
            'efficiency': 0.2,
            'interpretability': 0.2,
            'robustness': 0.2
        })
    
    def evaluate_accuracy(self, individual: AdvancedNeuralArchitecture, 
                         test_data: Any) -> float:
        """Avalia precisão do modelo"""
        try:
            # Implementação simplificada - em produção seria mais robusta
            model = self._create_model_from_architecture(individual)
            if model is None:
                return 0.0
            
            # Simular avaliação de precisão
            accuracy = random.uniform(0.6, 0.95)  # Placeholder
            return accuracy
        except Exception as e:
            logger.error(f"Erro na avaliação de precisão: {e}")
            return 0.0
    
    def evaluate_efficiency(self, individual: AdvancedNeuralArchitecture) -> float:
        """Avalia eficiência computacional"""
        try:
            # Calcular parâmetros totais
            total_params = sum(layer.get('parameters', 0) for layer in individual.layers)
            
            # Calcular complexidade de conexões
            connection_complexity = len(individual.connections)
            
            # Score de eficiência (menor é melhor)
            efficiency_score = 1.0 / (1.0 + total_params / 1000000 + connection_complexity / 1000)
            
            return efficiency_score
        except Exception as e:
            logger.error(f"Erro na avaliação de eficiência: {e}")
            return 0.0
    
    def evaluate_interpretability(self, individual: AdvancedNeuralArchitecture) -> float:
        """Avalia interpretabilidade do modelo"""
        try:
            interpretability_score = 0.0
            
            # Pontuar por modularização
            if individual.modules:
                interpretability_score += 0.3
            
            # Pontuar por arquitetura simples
            if len(individual.layers) <= 10:
                interpretability_score += 0.2
            
            # Pontuar por conexões diretas
            direct_connections = sum(1 for conn in individual.connections 
                                   if abs(conn[0] - conn[1]) == 1)
            if direct_connections / max(len(individual.connections), 1) > 0.7:
                interpretability_score += 0.2
            
            # Pontuar por camadas com nomes descritivos
            descriptive_layers = sum(1 for layer in individual.layers 
                                   if layer.get('name', '').startswith(('input', 'output', 'hidden')))
            if descriptive_layers > 0:
                interpretability_score += 0.3
            
            return min(interpretability_score, 1.0)
        except Exception as e:
            logger.error(f"Erro na avaliação de interpretabilidade: {e}")
            return 0.0
    
    def evaluate_robustness(self, individual: AdvancedNeuralArchitecture, 
                          noisy_data: Any) -> float:
        """Avalia robustez do modelo"""
        try:
            # Simular teste com dados ruidosos
            base_accuracy = random.uniform(0.7, 0.9)
            noisy_accuracy = base_accuracy * random.uniform(0.8, 1.0)
            
            # Score de robustez baseado na degradação
            robustness_score = noisy_accuracy / base_accuracy
            
            return robustness_score
        except Exception as e:
            logger.error(f"Erro na avaliação de robustez: {e}")
            return 0.0
    
    def evaluate_individual(self, individual: AdvancedNeuralArchitecture, 
                          test_data: Any, noisy_data: Any = None) -> MultiObjectiveFitness:
        """Avalia indivíduo completo"""
        try:
            fitness = MultiObjectiveFitness()
            
            # Avaliar cada objetivo
            fitness.accuracy = self.evaluate_accuracy(individual, test_data)
            fitness.efficiency = self.evaluate_efficiency(individual)
            fitness.interpretability = self.evaluate_interpretability(individual)
            fitness.robustness = self.evaluate_robustness(individual, noisy_data or test_data)
            
            # Calcular score geral
            fitness.calculate_overall(self.weights)
            
            # Atualizar indivíduo
            individual.fitness = fitness
            
            return fitness
        except Exception as e:
            logger.error(f"Erro na avaliação completa: {e}")
            return MultiObjectiveFitness()
    
    def _create_model_from_architecture(self, individual: AdvancedNeuralArchitecture) -> Optional[nn.Module]:
        """Cria modelo PyTorch a partir da arquitetura"""
        try:
            # Implementação simplificada
            layers = []
            input_size = 768  # Tamanho padrão para transformers
            
            for layer in individual.layers:
                layer_type = layer.get('type', 'linear')
                layer_size = layer.get('size', 512)
                
                if layer_type == 'linear':
                    layers.append(nn.Linear(input_size, layer_size))
                    layers.append(nn.ReLU())
                    input_size = layer_size
                elif layer_type == 'dropout':
                    layers.append(nn.Dropout(layer.get('dropout_rate', 0.1)))
                elif layer_type == 'attention':
                    layers.append(nn.MultiheadAttention(layer_size, num_heads=8))
            
            if layers:
                model = nn.Sequential(*layers)
                return model
            
            return None
        except Exception as e:
            logger.error(f"Erro ao criar modelo: {e}")
            return None

class AdvancedEvolutionEngine:
    """Motor de evolução avançado"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.fitness_evaluator = AdvancedFitnessEvaluator(config)
        self.genetic_operators = AdvancedGeneticOperators()
        self.population = []
        self.generation = 0
        self.best_individual = None
        self.performance_history = []
        
        # Configurar algoritmo genético
        self._setup_genetic_algorithm()
        
        logger.info("Motor de evolução avançado inicializado")
    
    def _setup_genetic_algorithm(self):
        """Configura o algoritmo genético usando DEAP"""
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
            # Converter indivíduo DEAP para AdvancedNeuralArchitecture
            if isinstance(individual, list):
                arch = AdvancedNeuralArchitecture(
                    layers=individual[:len(individual)//2] if len(individual) > 1 else [],
                    connections=individual[len(individual)//2:] if len(individual) > 1 else [],
                    hyperparameters={'learning_rate': 0.001, 'dropout': 0.2}
                )
            else:
                arch = individual
            
            # Avaliar usando o avaliador avançado
            test_data = self._generate_test_data()
            fitness = self.fitness_evaluator.evaluate_individual(arch, test_data)
            
            return (fitness.overall_score,)
        except Exception as e:
            logger.error(f"Erro no _evaluate_fitness: {e}")
            return (0.0,)
    
    def _mutate(self, individual):
        """Método de mutação avançada para DEAP"""
        try:
            # Aplicar mutações avançadas
            if random.random() < 0.1:  # 10% chance de mutação
                if len(individual) > 0:
                    # Mutação modularização
                    if random.random() < 0.3:
                        individual = self.genetic_operators.modularization_mutation(individual)
                    
                    # Mutação fusão
                    elif random.random() < 0.3:
                        individual = self.genetic_operators.fusion_mutation(individual)
                    
                    # Mutação adaptativa
                    else:
                        individual = self.genetic_operators.adaptive_mutation(
                            individual, self.performance_history
                        )
            
            return (individual,)
        except Exception as e:
            logger.error(f"Erro no _mutate: {e}")
            return (individual,)
    
    def _crossover(self, parent1, parent2):
        """Crossover avançado"""
        try:
            # Implementação de crossover
            if len(parent1) > 1 and len(parent2) > 1:
                crossover_point = random.randint(1, min(len(parent1), len(parent2)) - 1)
                child = parent1[:crossover_point] + parent2[crossover_point:]
                return child
            return parent1
        except Exception as e:
            logger.error(f"Erro no crossover: {e}")
            return parent1
    
    def _generate_test_data(self):
        """Gera dados de teste"""
        # Implementação simplificada
        return np.random.randn(100, 768)
    
    def evolve_population(self, generations: int = 10) -> List[Dict[str, Any]]:
        """Evolui a população por N gerações"""
        results = []
        
        for gen in range(generations):
            logger.info(f"Iniciando geração {gen + 1}/{generations}")
            
            # Avaliar população atual
            fitnesses = []
            for individual in self.population:
                test_data = self._generate_test_data()
                fitness = self.fitness_evaluator.evaluate_individual(individual, test_data)
                fitnesses.append(fitness.overall_score)
            
            # Atualizar histórico de performance
            if fitnesses:
                avg_fitness = np.mean(fitnesses)
                self.performance_history.append(avg_fitness)
                
                # Encontrar melhor indivíduo
                best_idx = np.argmax(fitnesses)
                self.best_individual = self.population[best_idx]
            
            # Aplicar operadores genéticos
            new_population = []
            
            # Elitismo
            elite_size = self.config.get('elite_size', 5)
            elite = sorted(self.population, key=lambda x: x.fitness.overall_score, reverse=True)[:elite_size]
            new_population.extend(elite)
            
            # Gerar descendentes
            while len(new_population) < len(self.population):
                # Seleção
                parent1, parent2 = random.sample(self.population, 2)
                
                # Crossover
                if random.random() < self.config.get('crossover_rate', 0.7):
                    child = self._crossover(parent1, parent2)
                else:
                    child = parent1
                
                # Mutação
                if random.random() < self.config.get('mutation_rate', 0.1):
                    child = self._mutate(child)
                
                new_population.append(child)
            
            self.population = new_population
            self.generation += 1
            
            # Registrar resultados
            result = {
                'generation': self.generation,
                'avg_fitness': avg_fitness if fitnesses else 0.0,
                'best_fitness': max(fitnesses) if fitnesses else 0.0,
                'population_size': len(self.population),
                'best_individual_id': self.best_individual.id if self.best_individual else None
            }
            results.append(result)
            
            logger.info(f"Geração {gen + 1} concluída - Fitness médio: {avg_fitness:.4f}")
        
        return results
    
    def initialize_population(self, size: int = 50):
        """Inicializa população com arquiteturas aleatórias"""
        self.population = []
        
        for _ in range(size):
            individual = self._create_random_architecture()
            self.population.append(individual)
        
        logger.info(f"População inicializada com {size} indivíduos")
    
    def _create_random_architecture(self) -> AdvancedNeuralArchitecture:
        """Cria arquitetura neural aleatória"""
        layers = []
        connections = []
        
        # Criar camadas aleatórias
        num_layers = random.randint(3, 10)
        layer_sizes = [768] + [random.randint(256, 1024) for _ in range(num_layers - 2)] + [512]
        
        for i, size in enumerate(layer_sizes):
            layer = {
                'type': random.choice(['linear', 'dropout', 'attention']),
                'size': size,
                'parameters': size * (layer_sizes[i-1] if i > 0 else 768),
                'name': f'layer_{i}'
            }
            layers.append(layer)
        
        # Criar conexões
        for i in range(len(layers) - 1):
            connections.append((i, i + 1))
        
        # Adicionar algumas conexões skip
        for _ in range(random.randint(0, 3)):
            if len(layers) > 2:
                start = random.randint(0, len(layers) - 3)
                end = random.randint(start + 2, len(layers) - 1)
                connections.append((start, end))
        
        return AdvancedNeuralArchitecture(
            layers=layers,
            connections=connections,
            hyperparameters={
                'learning_rate': random.uniform(0.0001, 0.01),
                'dropout': random.uniform(0.1, 0.5)
            }
        )
    
    def get_best_architecture(self) -> Optional[AdvancedNeuralArchitecture]:
        """Retorna a melhor arquitetura encontrada"""
        return self.best_individual
    
    def save_state(self, filepath: str) -> bool:
        """Salva estado da evolução"""
        try:
            state = {
                'generation': self.generation,
                'population': [ind.__dict__ for ind in self.population],
                'best_individual': self.best_individual.__dict__ if self.best_individual else None,
                'performance_history': self.performance_history,
                'config': self.config
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(state, f)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
            return False
    
    def load_state(self, filepath: str) -> bool:
        """Carrega estado da evolução"""
        try:
            with open(filepath, 'rb') as f:
                state = pickle.load(f)
            
            self.generation = state['generation']
            self.performance_history = state['performance_history']
            self.config = state['config']
            
            # Reconstruir população
            self.population = []
            for ind_dict in state['population']:
                individual = AdvancedNeuralArchitecture(**ind_dict)
                self.population.append(individual)
            
            # Reconstruir melhor indivíduo
            if state['best_individual']:
                self.best_individual = AdvancedNeuralArchitecture(**state['best_individual'])
            
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")
            return False 
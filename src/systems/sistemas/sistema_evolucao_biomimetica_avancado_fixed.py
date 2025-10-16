#!/usr/bin/env python3
"""
SISTEMA DE EVOLUÇÃO BIOMIMÉTICA AVANÇADO - VERSÃO CORRIGIDA
Versão 3.1 - Corrigido imports e compatibilidade de dimensões
"""

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
import math

# Verificar se PyTorch está disponível
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch não disponível - usando numpy como fallback")

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BiomimeticNeuralNetwork:
    """
    Rede Neural Biomimética com fallback para numpy
    """
    
    def __init__(self, input_size: int = 512, hidden_size: int = 256, output_size: int = 128):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Parâmetros biomiméticos
        self.plasticity_rate = 0.1
        self.homeostasis_threshold = 0.5
        self.adaptation_rate = 0.05
        self.memory_decay = 0.95
        
        if TORCH_AVAILABLE:
            self._init_torch_model()
        else:
            self._init_numpy_model()
        
        # Sistema de memória biomimético
        self.memory_bank = deque(maxlen=1000)
        self.activity_history = deque(maxlen=100)
        
    def _init_torch_model(self):
        """Inicializa modelo PyTorch"""
        self.model = nn.Sequential(
            nn.Linear(self.input_size, self.hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(self.hidden_size, self.hidden_size // 2),
            nn.ReLU(),
            nn.Linear(self.hidden_size // 2, self.hidden_size // 4),
            nn.ReLU(),
            nn.Linear(self.hidden_size // 4, self.output_size)
        )
        
        self.synaptic_strength = torch.ones(self.hidden_size) * 0.5
        self.attention_weights = torch.ones(self.hidden_size) / self.hidden_size
        
    def _init_numpy_model(self):
        """Inicializa modelo numpy"""
        # Pesos das camadas
        self.weights = []
        self.biases = []
        
        layer_sizes = [self.input_size, self.hidden_size, self.hidden_size // 2, 
                      self.hidden_size // 4, self.output_size]
        
        for i in range(len(layer_sizes) - 1):
            # Inicialização Xavier
            scale = np.sqrt(2.0 / (layer_sizes[i] + layer_sizes[i + 1]))
            self.weights.append(np.random.randn(layer_sizes[i], layer_sizes[i + 1]) * scale)
            self.biases.append(np.random.randn(layer_sizes[i + 1]) * 0.1)
        
        self.synaptic_strength = np.ones(self.hidden_size) * 0.5
        self.attention_weights = np.ones(self.hidden_size) / self.hidden_size
        
    def forward(self, x):
        """Forward pass compatível"""
        if TORCH_AVAILABLE:
            return self._forward_torch(x)
        else:
            return self._forward_numpy(x)
    
    def _forward_torch(self, x):
        """Forward pass PyTorch"""
        # Processamento biomimético
        x = self._biomimetic_processing_torch(x)
        
        # Forward pass
        output = self.model(x)
        
        # Atualizar memória e atividade
        self._update_memory_torch(x)
        self._update_activity_torch(output)
        
        return output
    
    def _forward_numpy(self, x):
        """Forward pass numpy"""
        # Processamento biomimético
        x = self._biomimetic_processing_numpy(x)
        
        # Forward pass
        for i, (weight, bias) in enumerate(zip(self.weights, self.biases)):
            x = np.dot(x, weight) + bias
            if i < len(self.weights) - 1:  # Não aplicar ReLU na última camada
                x = np.maximum(0, x)  # ReLU
        
        # Atualizar memória e atividade
        self._update_memory_numpy(x)
        self._update_activity_numpy(x)
        
        return x
    
    def _biomimetic_processing_torch(self, x):
        """Processamento biomimético PyTorch"""
        if hasattr(self.model, 'training') and self.model.training:
            mean = x.mean(dim=0, keepdim=True)
            std = x.std(dim=0, keepdim=True) + 1e-8
            x = (x - mean) / std
        
        attention = torch.sigmoid(self.attention_weights[:x.size(-1)])
        x = x * attention.unsqueeze(0)
        
        return x
    
    def _biomimetic_processing_numpy(self, x):
        """Processamento biomimético numpy"""
        # Normalização
        mean = np.mean(x, axis=0, keepdims=True)
        std = np.std(x, axis=0, keepdims=True) + 1e-8
        x = (x - mean) / std
        
        # Atenção
        attention = 1.0 / (1.0 + np.exp(-self.attention_weights[:x.shape[-1]]))
        x = x * attention
        
        return x
    
    def _update_memory_torch(self, x):
        """Atualiza memória PyTorch"""
        if len(self.memory_bank) < self.memory_bank.maxlen:
            pattern = x.detach().mean(dim=0)
            self.memory_bank.append(pattern)
    
    def _update_memory_numpy(self, x):
        """Atualiza memória numpy"""
        if len(self.memory_bank) < self.memory_bank.maxlen:
            pattern = np.mean(x, axis=0)
            self.memory_bank.append(pattern)
    
    def _update_activity_torch(self, output):
        """Atualiza atividade PyTorch"""
        activity_level = torch.abs(output).mean().item()
        self.activity_history.append(activity_level)
    
    def _update_activity_numpy(self, output):
        """Atualiza atividade numpy"""
        activity_level = np.mean(np.abs(output))
        self.activity_history.append(activity_level)
    
    def get_biomimetic_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas biomiméticas"""
        if TORCH_AVAILABLE:
            return {
                'synaptic_strength_mean': self.synaptic_strength.mean().item(),
                'synaptic_strength_std': self.synaptic_strength.std().item(),
                'activity_history_mean': np.mean(list(self.activity_history)) if self.activity_history else 0.0,
                'memory_utilization': len(self.memory_bank) / self.memory_bank.maxlen,
                'attention_weights_mean': self.attention_weights.mean().item()
            }
        else:
            return {
                'synaptic_strength_mean': np.mean(self.synaptic_strength),
                'synaptic_strength_std': np.std(self.synaptic_strength),
                'activity_history_mean': np.mean(list(self.activity_history)) if self.activity_history else 0.0,
                'memory_utilization': len(self.memory_bank) / self.memory_bank.maxlen,
                'attention_weights_mean': np.mean(self.attention_weights)
            }

class MetaLearningBiomimeticEngine:
    """
    Motor de Meta-Learning Biomimético
    """
    
    def __init__(self, model: BiomimeticNeuralNetwork):
        self.model = model
        if TORCH_AVAILABLE:
            self.meta_optimizer = torch.optim.Adam(self.model.model.parameters(), lr=0.001)
        
        # Parâmetros de meta-learning
        self.meta_lr = 0.01
        self.adaptation_steps = 5
        self.task_memory = {}
        self.knowledge_base = {}
        
    def meta_train_step(self, tasks: List[Tuple]) -> float:
        """Meta-training step biomimético"""
        if not TORCH_AVAILABLE:
            return self._meta_train_numpy(tasks)
        
        meta_loss = 0.0
        
        for task_data, task_labels in tasks:
            # Adaptação rápida
            adapted_model = self._quick_adaptation_torch(task_data, task_labels)
            
            # Meta-update
            meta_output = adapted_model(task_data)
            task_loss = F.cross_entropy(meta_output, task_labels)
            meta_loss += task_loss
        
        # Otimização meta
        self.meta_optimizer.zero_grad()
        meta_loss.backward()
        self.meta_optimizer.step()
        
        return meta_loss.item()
    
    def _meta_train_numpy(self, tasks: List[Tuple]) -> float:
        """Meta-training numpy"""
        total_loss = 0.0
        
        for task_data, task_labels in tasks:
            # Simulação simples de meta-learning
            adapted_model = copy.deepcopy(self.model)
            
            # Forward pass
            output = adapted_model.forward(task_data)
            
            # Calcular perda simples
            if len(output.shape) > 1:
                predictions = np.argmax(output, axis=1)
                accuracy = np.mean(predictions == task_labels)
                loss = 1.0 - accuracy
            else:
                loss = np.mean((output - task_labels) ** 2)
            
            total_loss += loss
        
        return total_loss / len(tasks)
    
    def _quick_adaptation_torch(self, task_data, task_labels):
        """Adaptação rápida PyTorch"""
        adapted_model = copy.deepcopy(self.model)
        task_optimizer = torch.optim.SGD(adapted_model.model.parameters(), lr=self.meta_lr)
        
        for _ in range(self.adaptation_steps):
            task_output = adapted_model.forward(task_data)
            task_loss = F.cross_entropy(task_output, task_labels)
            
            task_optimizer.zero_grad()
            task_loss.backward()
            task_optimizer.step()
        
        return adapted_model
    
    def few_shot_learning(self, support_data, support_labels, query_data, query_labels):
        """Few-shot learning biomimético"""
        if TORCH_AVAILABLE:
            return self._few_shot_torch(support_data, support_labels, query_data, query_labels)
        else:
            return self._few_shot_numpy(support_data, support_labels, query_data, query_labels)
    
    def _few_shot_torch(self, support_data, support_labels, query_data, query_labels):
        """Few-shot PyTorch"""
        adapted_model = self._quick_adaptation_torch(support_data, support_labels)
        
        with torch.no_grad():
            query_output = adapted_model.forward(query_data)
            query_loss = F.cross_entropy(query_output, query_labels)
            accuracy = (query_output.argmax(dim=1) == query_labels).float().mean()
        
        return query_loss.item(), accuracy.item()
    
    def _few_shot_numpy(self, support_data, support_labels, query_data, query_labels):
        """Few-shot numpy"""
        # Simulação simples
        adapted_model = copy.deepcopy(self.model)
        
        # Forward pass
        query_output = adapted_model.forward(query_data)
        
        # Calcular métricas
        if len(query_output.shape) > 1:
            predictions = np.argmax(query_output, axis=1)
            accuracy = np.mean(predictions == query_labels)
        else:
            accuracy = 1.0 - np.mean((query_output - query_labels) ** 2)
        
        loss = 1.0 - accuracy
        
        return loss, accuracy

class BiomimeticEvolutionaryEngine:
    """
    Motor Evolutivo Biomimético
    """
    
    def __init__(self, population_size: int = 50):
        self.population_size = population_size
        self.population = []
        self.generation = 0
        self.evolution_history = []
        
        # Parâmetros evolutivos
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.selection_pressure = 0.8
        
    def initialize_population(self, input_size: int = 512, output_size: int = 128):
        """Inicializa população biomimética"""
        logger.info(f"🧬 Inicializando população de {self.population_size} indivíduos")
        
        for i in range(self.population_size):
            individual = {
                'id': f"ind_{i}_{self.generation}",
                'model': BiomimeticNeuralNetwork(input_size, 256, output_size),
                'fitness': 0.0,
                'age': 0,
                'adaptability': random.uniform(0.5, 1.0),
                'complexity': random.uniform(0.3, 0.8)
            }
            self.population.append(individual)
        
        logger.info(f"✅ População inicializada com {len(self.population)} indivíduos")
    
    def evaluate_fitness(self, individual: Dict, task_data: Dict[str, Any]) -> float:
        """Avalia fitness biomimético"""
        model = individual['model']
        
        try:
            # Dados de entrada compatíveis
            input_size = model.input_size
            input_data = np.random.randn(10, input_size)
            
            # Forward pass
            output = model.forward(input_data)
            
            # Métricas de fitness
            performance_score = self._calculate_performance_score(output)
            adaptability_score = individual['adaptability']
            complexity_score = individual['complexity']
            biomimetic_score = self._calculate_biomimetic_score(model)
            
            # Fitness combinado
            fitness = (
                performance_score * 0.4 +
                adaptability_score * 0.2 +
                complexity_score * 0.2 +
                biomimetic_score * 0.2
            )
            
            return fitness
            
        except Exception as e:
            logger.error(f"❌ Erro na avaliação de fitness: {e}")
            return 0.0
    
    def _calculate_performance_score(self, output) -> float:
        """Calcula score de performance"""
        if TORCH_AVAILABLE:
            output_variance = output.var().item()
            output_stability = 1.0 / (1.0 + output.std().item())
        else:
            output_variance = np.var(output)
            output_stability = 1.0 / (1.0 + np.std(output))
        
        return (output_variance * 0.6 + output_stability * 0.4)
    
    def _calculate_biomimetic_score(self, model: BiomimeticNeuralNetwork) -> float:
        """Calcula score biomimético"""
        stats = model.get_biomimetic_stats()
        
        synaptic_health = 1.0 - abs(stats['synaptic_strength_mean'] - 0.5)
        activity_balance = 1.0 - abs(stats['activity_history_mean'] - 0.5)
        memory_efficiency = stats['memory_utilization']
        attention_balance = 1.0 - abs(stats['attention_weights_mean'] - 0.5)
        
        biomimetic_score = (
            synaptic_health * 0.3 +
            activity_balance * 0.3 +
            memory_efficiency * 0.2 +
            attention_balance * 0.2
        )
        
        return biomimetic_score
    
    def evolve_generation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evolui uma geração biomimética"""
        logger.info(f"🔄 Evoluindo geração {self.generation + 1}")
        
        # Avaliar fitness
        for individual in self.population:
            individual['fitness'] = self.evaluate_fitness(individual, task_data)
            individual['age'] += 1
        
        # Estatísticas da geração
        fitnesses = [ind['fitness'] for ind in self.population]
        best_fitness = max(fitnesses)
        avg_fitness = np.mean(fitnesses)
        
        # Seleção simples
        sorted_population = sorted(self.population, key=lambda x: x['fitness'], reverse=True)
        
        # Elitismo
        elite_size = max(1, int(self.population_size * 0.1))
        new_population = sorted_population[:elite_size]
        
        # Reprodução
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(sorted_population[:len(sorted_population)//2], 2)
            child = self._crossover(parent1, parent2)
            child = self._mutate(child)
            new_population.append(child)
        
        # Atualizar população
        self.population = new_population[:self.population_size]
        self.generation += 1
        
        # Registrar histórico
        generation_stats = {
            'generation': self.generation,
            'best_fitness': best_fitness,
            'avg_fitness': avg_fitness,
            'population_size': len(self.population),
            'timestamp': datetime.now().isoformat()
        }
        self.evolution_history.append(generation_stats)
        
        logger.info(f"✅ Geração {self.generation} concluída. Melhor fitness: {best_fitness:.4f}")
        
        return generation_stats
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        """Crossover biomimético"""
        child = copy.deepcopy(parent1)
        child['id'] = f"child_{len(self.population)}_{self.generation}"
        child['age'] = 0
        
        # Crossover de características
        child['adaptability'] = (parent1['adaptability'] + parent2['adaptability']) / 2
        child['complexity'] = (parent1['complexity'] + parent2['complexity']) / 2
        
        return child
    
    def _mutate(self, individual: Dict) -> Dict:
        """Mutação biomimética"""
        mutated = copy.deepcopy(individual)
        
        # Mutação de características
        if random.random() < self.mutation_rate:
            mutated['adaptability'] += random.uniform(-0.1, 0.1)
            mutated['adaptability'] = np.clip(mutated['adaptability'], 0.1, 1.0)
        
        if random.random() < self.mutation_rate:
            mutated['complexity'] += random.uniform(-0.1, 0.1)
            mutated['complexity'] = np.clip(mutated['complexity'], 0.1, 1.0)
        
        return mutated
    
    def get_best_individual(self) -> Optional[Dict]:
        """Retorna o melhor indivíduo"""
        if not self.population:
            return None
        
        return max(self.population, key=lambda x: x['fitness'])
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas da evolução"""
        if not self.evolution_history:
            return {}
        
        recent_generations = self.evolution_history[-10:]
        
        return {
            'total_generations': self.generation,
            'current_population_size': len(self.population),
            'best_fitness_history': [gen['best_fitness'] for gen in recent_generations],
            'avg_fitness_history': [gen['avg_fitness'] for gen in recent_generations]
        }

class AdvancedBiomimeticAI:
    """
    IA Biomimética Avançada
    """
    
    def __init__(self):
        self.model = BiomimeticNeuralNetwork()
        self.meta_engine = MetaLearningBiomimeticEngine(self.model)
        self.evolution_engine = BiomimeticEvolutionaryEngine()
        
        # Estado do sistema
        self.generation = 0
        self.meta_learning_cycles = 0
        self.best_performance = 0.0
        
    def initialize_system(self):
        """Inicializa o sistema completo"""
        logger.info("🧠 Inicializando IA Biomimética Avançada")
        
        # Inicializar população evolutiva
        self.evolution_engine.initialize_population()
        
        logger.info("✅ Sistema inicializado com sucesso")
    
    def train_on_task(self, task_data: np.ndarray, task_labels: np.ndarray) -> Dict[str, Any]:
        """Treina o sistema em uma tarefa específica"""
        logger.info("🎯 Treinando em tarefa específica")
        
        # Meta-learning
        meta_loss = self.meta_engine.meta_train_step([(task_data, task_labels)])
        
        # Avaliar performance
        output = self.model.forward(task_data)
        performance = self._evaluate_performance(output, task_labels)
        
        # Atualizar estatísticas
        self.meta_learning_cycles += 1
        self.best_performance = max(self.best_performance, performance)
        
        # Verificar se deve evoluir
        if self.meta_learning_cycles % 5 == 0:
            self._trigger_evolution({'input_size': task_data.shape[1]})
        
        return {
            'meta_loss': meta_loss,
            'performance': performance,
            'best_performance': self.best_performance,
            'meta_learning_cycles': self.meta_learning_cycles,
            'generation': self.generation
        }
    
    def _evaluate_performance(self, output: np.ndarray, labels: np.ndarray) -> float:
        """Avalia performance do modelo"""
        try:
            if len(output.shape) > 1:
                predictions = np.argmax(output, axis=1)
                accuracy = np.mean(predictions == labels)
            else:
                accuracy = 1.0 - np.mean((output - labels) ** 2)
            
            return accuracy
        except:
            return 0.0
    
    def _trigger_evolution(self, task_data: Dict[str, Any]):
        """Dispara processo evolutivo"""
        logger.info("🧬 Disparando evolução biomimética")
        
        # Evoluir população
        evolution_stats = self.evolution_engine.evolve_generation(task_data)
        
        # Obter melhor indivíduo
        best_individual = self.evolution_engine.get_best_individual()
        
        if best_individual and best_individual['fitness'] > self.best_performance:
            # Substituir modelo atual pelo melhor evolutivo
            self.model = copy.deepcopy(best_individual['model'])
            self.meta_engine.model = self.model
            self.best_performance = best_individual['fitness']
            
            logger.info(f"🔄 Modelo atualizado com indivíduo evolutivo. Fitness: {best_individual['fitness']:.4f}")
        
        self.generation += 1
    
    def few_shot_adaptation(self, support_data: np.ndarray, support_labels: np.ndarray,
                           query_data: np.ndarray, query_labels: np.ndarray) -> Dict[str, float]:
        """Adaptação few-shot biomimética"""
        logger.info("🎯 Adaptação few-shot biomimética")
        
        loss, accuracy = self.meta_engine.few_shot_learning(
            support_data, support_labels, query_data, query_labels
        )
        
        return {
            'loss': loss,
            'accuracy': accuracy,
            'adaptation_success': accuracy > 0.7
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema"""
        evolution_stats = self.evolution_engine.get_evolution_stats()
        biomimetic_stats = self.model.get_biomimetic_stats()
        
        return {
            'generation': self.generation,
            'meta_learning_cycles': self.meta_learning_cycles,
            'best_performance': self.best_performance,
            'evolution_stats': evolution_stats,
            'biomimetic_stats': biomimetic_stats,
            'population_size': len(self.evolution_engine.population),
            'torch_available': TORCH_AVAILABLE
        }

def main():
    """Função principal"""
    print("🧠 SISTEMA DE EVOLUÇÃO BIOMIMÉTICA AVANÇADO - VERSÃO CORRIGIDA")
    print("=" * 70)
    
    # Criar sistema
    ai_system = AdvancedBiomimeticAI()
    ai_system.initialize_system()
    
    # Simular treinamento
    print("🚀 Iniciando treinamento biomimético...")
    
    for cycle in range(10):
        # Dados de treinamento simulados
        task_data = np.random.randn(32, 512)
        task_labels = np.random.randint(0, 10, (32,))
        
        # Treinar
        results = ai_system.train_on_task(task_data, task_labels)
        
        print(f"Ciclo {cycle + 1}: Performance = {results['performance']:.4f}, Meta-loss = {results['meta_loss']:.4f}")
        
        # Few-shot adaptation
        if cycle % 3 == 0:
            support_data = np.random.randn(5, 512)
            support_labels = np.random.randint(0, 5, (5,))
            query_data = np.random.randn(10, 512)
            query_labels = np.random.randint(0, 5, (10,))
            
            adaptation_results = ai_system.few_shot_adaptation(
                support_data, support_labels, query_data, query_labels
            )
            
            print(f"  Few-shot: Accuracy = {adaptation_results['accuracy']:.4f}")
    
    # Status final
    status = ai_system.get_system_status()
    
    print(f"\n📊 RESULTADOS FINAIS:")
    print(f"Geração: {status['generation']}")
    print(f"Melhor performance: {status['best_performance']:.4f}")
    print(f"População: {status['population_size']}")
    print(f"PyTorch disponível: {status['torch_available']}")
    
    print("\n🎉 SISTEMA BIOMIMÉTICO EXECUTADO COM SUCESSO!")

if __name__ == "__main__":
    main() 
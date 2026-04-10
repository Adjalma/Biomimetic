"""
AI Engine - Sistema Biomimético Evolucionário com Meta-Learning
Versão corrigida e otimizada
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import copy
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime
import json
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NeuralNetwork(nn.Module):
    """Rede neural biomimética com arquitetura evolucionária simplificada"""
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int, 
                 complexity: float = 1.0, plasticity: float = 0.5):
        super(NeuralNetwork, self).__init__()
        
        self.input_size = input_size
        self.output_size = output_size
        self.complexity = complexity
        self.plasticity = plasticity
        
        # Calcular tamanhos das camadas baseado na complexidade
        base_hidden = max(4, int(hidden_size * complexity))
        # Garantir que seja divisível por 4 para atenção
        if base_hidden % 4 != 0:
            base_hidden = ((base_hidden // 4) + 1) * 4
        
        self.hidden_size = base_hidden
        
        # Arquitetura simplificada e robusta
        self.layers = nn.ModuleList()
        
        # Camada de entrada
        self.layers.append(nn.Linear(input_size, self.hidden_size))
        self.layers.append(nn.ReLU())
        self.layers.append(nn.Dropout(0.1))
        
        # Camada oculta adicional se complexidade > 1.2
        if complexity > 1.2:
            mid_size = max(4, self.hidden_size // 2)
            if mid_size % 4 != 0:
                mid_size = ((mid_size // 4) + 1) * 4
            self.layers.append(nn.Linear(self.hidden_size, mid_size))
            self.layers.append(nn.ReLU())
            self.layers.append(nn.Dropout(0.1))
            self.hidden_size = mid_size
        
        # Camada de saída
        self.layers.append(nn.Linear(self.hidden_size, output_size))
        
        # Mecanismo de atenção simplificado (apenas se hidden_size >= 4)
        if self.hidden_size >= 4:
            num_heads = min(2, self.hidden_size // 4)  # Máximo 2 heads para estabilidade
            self.attention = nn.MultiheadAttention(self.hidden_size, num_heads=num_heads, batch_first=True)
            self.use_attention = True
        else:
            self.use_attention = False
        
        # Memória de longo prazo (apenas se hidden_size >= 8)
        if self.hidden_size >= 8:
            self.memory = nn.LSTM(self.hidden_size, self.hidden_size, batch_first=True)
            self.use_memory = True
        else:
            self.use_memory = False
        
    def forward(self, x):
        # Processamento através das camadas
        for i, layer in enumerate(self.layers):
            if isinstance(layer, nn.Linear):
                x = layer(x)
            elif isinstance(layer, nn.ReLU):
                x = layer(x)
            elif isinstance(layer, nn.Dropout):
                x = layer(x)
        
        # Mecanismo de atenção (se disponível)
        if self.use_attention and x.dim() == 2:
            x = x.unsqueeze(1)  # Adicionar dimensão de sequência
            attn_output, _ = self.attention(x, x, x)
            x = attn_output.squeeze(1) if attn_output.size(1) == 1 else attn_output
        
        # Memória de longo prazo (se disponível)
        if self.use_memory and x.dim() == 2:
            x = x.unsqueeze(1)
            lstm_out, _ = self.memory(x)
            x = lstm_out.squeeze(1) if lstm_out.size(1) == 1 else lstm_out
        
        return x

class BiomimeticEvolutionaryAI:
    """Sistema de IA Biomimético Evolucionário com Meta-Learning"""
    
    def __init__(self, population_size: int = 50, input_size: int = 10, 
                 hidden_size: int = 64, output_size: int = 1, 
                 enable_meta_learning: bool = True, 
                 evolution_rate: float = 0.1,
                 mutation_rate: float = 0.05,
                 crossover_rate: float = 0.7):
        
        self.population_size = population_size
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.enable_meta_learning = enable_meta_learning
        self.evolution_rate = evolution_rate
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        
        # Dispositivo
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Usando dispositivo: {self.device}")
        
        # População inicial
        self.population = []
        self.fitness_scores = []
        self.generation = 0
        self.best_individual = None
        self.best_fitness = -float('inf')
        
        # Meta-learning
        self.meta_learner = None
        if enable_meta_learning:
            self.meta_learner = self._create_meta_learner()
        
        # Histórico de evolução
        self.evolution_history = []
        self.performance_metrics = {
            'fitness_history': [],
            'diversity_history': [],
            'complexity_history': [],
            'adaptation_history': []
        }
        
        # Inicializar população
        self._initialize_population()
        
        logger.info(f"Sistema Biomimético Evolucionário inicializado com {population_size} indivíduos")
    
    def _create_meta_learner(self):
        """Cria o meta-learner para few-shot learning"""
        try:
            import higher
            meta_model = NeuralNetwork(
                input_size=self.input_size,
                hidden_size=self.hidden_size,
                output_size=self.output_size,
                complexity=1.0,  # Complexidade fixa para meta-learner
                plasticity=0.8
            ).to(self.device)
            
            meta_optimizer = optim.Adam(meta_model.parameters(), lr=0.001)
            return {'model': meta_model, 'optimizer': meta_optimizer}
        except Exception as e:
            logger.warning(f"Meta-learner não pôde ser criado: {e}")
            return None
    
    def _initialize_population(self):
        """Inicializa a população com indivíduos diversos"""
        logger.info("Inicializando população...")
        
        for i in range(self.population_size):
            # Variação de complexidade (mais conservadora)
            complexity = 0.8 + random.random() * 0.8  # Entre 0.8 e 1.6
            plasticity = 0.1 + random.random() * 0.9
            
            individual = {
                'id': i,
                'model': NeuralNetwork(
                    input_size=self.input_size,
                    hidden_size=self.hidden_size,
                    output_size=self.output_size,
                    complexity=complexity,
                    plasticity=plasticity
                ).to(self.device),
                'complexity': complexity,
                'plasticity': plasticity,
                'age': 0,
                'fitness': 0.0,
                'adaptation_score': 0.0,
                'diversity_score': 0.0
            }
            
            self.population.append(individual)
            self.fitness_scores.append(0.0)
        
        logger.info(f"População inicializada com {len(self.population)} indivíduos")
    
    def _evaluate_fitness(self, individual: Dict) -> float:
        """Avalia o fitness de um indivíduo usando múltiplos critérios"""
        try:
            model = individual['model']
            model.eval()
            
            # Dados de teste sintéticos
            X = torch.randn(100, self.input_size).to(self.device)
            y = torch.randn(100, self.output_size).to(self.device)
            
            # Predição
            with torch.no_grad():
                predictions = model(X)
                mse_loss = nn.MSELoss()(predictions, y)
                
                # Critérios múltiplos
                accuracy = 1.0 / (1.0 + mse_loss.item())
                complexity_bonus = individual['complexity'] * 0.05  # Reduzido
                plasticity_bonus = individual['plasticity'] * 0.05  # Reduzido
                adaptation_bonus = individual['adaptation_score'] * 0.1  # Reduzido
                diversity_bonus = individual['diversity_score'] * 0.05  # Reduzido
                
                # Fitness total
                fitness = accuracy + complexity_bonus + plasticity_bonus + adaptation_bonus + diversity_bonus
                
                return max(0.0, float(fitness))
            
        except Exception as e:
            logger.error(f"Erro na avaliação de fitness: {e}")
            return 0.0
    
    def _calculate_diversity(self) -> float:
        """Calcula a diversidade da população"""
        if len(self.population) < 2:
            return 0.0
        
        complexities = [ind['complexity'] for ind in self.population]
        plasticities = [ind['plasticity'] for ind in self.population]
        
        complexity_std = np.std(complexities)
        plasticity_std = np.std(plasticities)
        
        return (complexity_std + plasticity_std) / 2.0
    
    def _selection(self) -> List[Dict]:
        """Seleção por torneio com pressão seletiva adaptativa"""
        tournament_size = max(3, self.population_size // 10)
        selected = []
        
        for _ in range(self.population_size):
            # Torneio
            tournament = random.sample(self.population, tournament_size)
            winner = max(tournament, key=lambda x: x['fitness'])
            selected.append(copy.deepcopy(winner))
        
        return selected
    
    def _crossover(self, parent1: Dict, parent2: Dict) -> Tuple[Dict, Dict]:
        """Crossover biomimético com herança de características"""
        child1 = copy.deepcopy(parent1)
        child2 = copy.deepcopy(parent2)
        
        # Crossover de parâmetros
        if random.random() < self.crossover_rate:
            # Troca de complexidade
            child1['complexity'] = (parent1['complexity'] + parent2['complexity']) / 2
            child2['complexity'] = (parent1['complexity'] + parent2['complexity']) / 2
            
            # Troca de plasticidade
            child1['plasticity'] = (parent1['plasticity'] + parent2['plasticity']) / 2
            child2['plasticity'] = (parent1['plasticity'] + parent2['plasticity']) / 2
        
        # Crossover de pesos da rede neural (apenas se as arquiteturas forem compatíveis)
        if random.random() < self.crossover_rate:
            try:
                # Verificar se as arquiteturas são compatíveis
                if (child1['model'].hidden_size == child2['model'].hidden_size and
                    child1['model'].input_size == child2['model'].input_size and
                    child1['model'].output_size == child2['model'].output_size):

                    for param1, param2 in zip(child1['model'].parameters(), child2['model'].parameters()):
                        if random.random() < 0.5:
                            param1.data, param2.data = param2.data.clone(), param1.data.clone()
            except Exception as e:
                logger.warning(f"Erro no crossover de pesos: {e}")
        
        return child1, child2
    
    def _mutation(self, individual: Dict):
        """Mutação biomimética com diferentes tipos"""
        # Mutação de complexidade
        if random.random() < self.mutation_rate:
            individual['complexity'] += random.gauss(0, 0.05)  # Reduzido
            individual['complexity'] = max(0.5, min(2.0, individual['complexity']))  # Limites mais conservadores
        
        # Mutação de plasticidade
        if random.random() < self.mutation_rate:
            individual['plasticity'] += random.gauss(0, 0.05)  # Reduzido
            individual['plasticity'] = max(0.0, min(1.0, individual['plasticity']))
        
        # Mutação de pesos
        if random.random() < self.mutation_rate:
            for param in individual['model'].parameters():
                if random.random() < 0.05:  # Reduzido para 5% dos pesos
                    noise = torch.randn_like(param) * 0.005  # Reduzido
                    param.data += noise
        
        # Mutação estrutural (muito rara)
        if random.random() < self.mutation_rate * 0.01:  # Muito raro
            try:
                individual['model'] = NeuralNetwork(
                    input_size=self.input_size,
                    hidden_size=self.hidden_size,
                    output_size=self.output_size,
                    complexity=individual['complexity'],
                    plasticity=individual['plasticity']
                ).to(self.device)
            except Exception as e:
                logger.warning(f"Erro na mutação estrutural: {e}")
    
    def _adaptation_learning(self, individual: Dict):
        """Aprendizado adaptativo biomimético"""
        try:
            model = individual['model']
            model.train()
            
            # Dados de adaptação
            X = torch.randn(50, self.input_size).to(self.device)
            y = torch.randn(50, self.output_size).to(self.device)
            
            optimizer = optim.Adam(model.parameters(), lr=0.001 * individual['plasticity'])
            
            # Treinamento rápido
            for _ in range(3):  # Reduzido
                optimizer.zero_grad()
                predictions = model(X)
                loss = nn.MSELoss()(predictions, y)
                loss.backward()
                optimizer.step()
            
            # Atualizar score de adaptação
            individual['adaptation_score'] = 1.0 / (1.0 + loss.item())
            
        except Exception as e:
            logger.error(f"Erro no aprendizado adaptativo: {e}")
    
    def evolve_generation(self) -> List[float]:
        """Evolui uma geração completa"""
        logger.info(f"Evoluindo geração {self.generation + 1}...")
        
        # Avaliar fitness atual
        for i, individual in enumerate(self.population):
            individual['fitness'] = self._evaluate_fitness(individual)
            self.fitness_scores[i] = individual['fitness']
            
            # Aprendizado adaptativo (apenas para indivíduos com plasticidade alta)
            if individual['plasticity'] > 0.5:
                self._adaptation_learning(individual)
        
        # Atualizar melhor indivíduo
        best_idx = np.argmax(self.fitness_scores)
        if self.fitness_scores[best_idx] > self.best_fitness:
            self.best_fitness = self.fitness_scores[best_idx]
            self.best_individual = copy.deepcopy(self.population[best_idx])
        
        # Calcular métricas
        diversity = self._calculate_diversity()
        avg_complexity = np.mean([ind['complexity'] for ind in self.population])
        avg_adaptation = np.mean([ind['adaptation_score'] for ind in self.population])
        
        # Registrar histórico
        self.evolution_history.append({
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'avg_fitness': np.mean(self.fitness_scores),
            'diversity': diversity,
            'avg_complexity': avg_complexity,
            'avg_adaptation': avg_adaptation
        })
        
        # Seleção
        selected = self._selection()
        
        # Nova população
        new_population = []
        
        # Elitismo (manter os melhores)
        elite_size = max(1, self.population_size // 10)
        elite = sorted(self.population, key=lambda x: x['fitness'], reverse=True)[:elite_size]
        new_population.extend(elite)
        
        # Crossover e mutação
        while len(new_population) < self.population_size:
            parent1, parent2 = random.sample(selected, 2)
            child1, child2 = self._crossover(parent1, parent2)
            
            self._mutation(child1)
            self._mutation(child2)
            
            # Atualizar IDs e idade
            child1['id'] = len(new_population)
            child2['id'] = len(new_population) + 1
            child1['age'] = max(parent1['age'], parent2['age']) + 1
            child2['age'] = max(parent1['age'], parent2['age']) + 1
            
            new_population.append(child1)
            if len(new_population) < self.population_size:
                new_population.append(child2)
        
        # Atualizar população
        self.population = new_population[:self.population_size]
        self.generation += 1
        
        # Atualizar scores de diversidade
        for individual in self.population:
            individual['diversity_score'] = diversity
        
        logger.info(f"Geração {self.generation} completada. Melhor fitness: {self.best_fitness:.4f}")
        
        return self.fitness_scores.copy()
    
    def few_shot_learning(self, support_data: List[Tuple], query_data: List[Tuple]) -> float:
        """Few-shot learning usando meta-learning"""
        if not self.meta_learner or not self.enable_meta_learning:
            return 0.5  # Valor padrão
        
        try:
            import higher
            
            model = self.meta_learner['model']
            optimizer = self.meta_learner['optimizer']
            
            # Converter dados para tensores com dimensões corretas
            support_X = torch.tensor([list(x) for x in support_data], dtype=torch.float32).to(self.device)
            support_y = torch.tensor([list(x) for x in support_data], dtype=torch.float32).to(self.device)
            query_X = torch.tensor([list(x) for x in query_data], dtype=torch.float32).to(self.device)
            query_y = torch.tensor([list(x) for x in query_data], dtype=torch.float32).to(self.device)
            
            # Garantir dimensões corretas
            if support_X.size(1) != self.input_size:
                # Padding ou truncamento
                if support_X.size(1) < self.input_size:
                    padding = torch.zeros(support_X.size(0), self.input_size - support_X.size(1)).to(self.device)
                    support_X = torch.cat([support_X, padding], dim=1)
                else:
                    support_X = support_X[:, :self.input_size]
            
            if query_X.size(1) != self.input_size:
                if query_X.size(1) < self.input_size:
                    padding = torch.zeros(query_X.size(0), self.input_size - query_X.size(1)).to(self.device)
                    query_X = torch.cat([query_X, padding], dim=1)
                else:
                    query_X = query_X[:, :self.input_size]
            
            # Meta-learning com higher
            with higher.innerloop_ctx(model, optimizer) as (fmodel, diffopt):
                # Adaptação rápida
                for _ in range(3):
                    pred = fmodel(support_X)
                    loss = nn.MSELoss()(pred, support_y)
                    diffopt.step(loss)
                
                # Avaliação
                with torch.no_grad():
                    query_pred = fmodel(query_X)
                    accuracy = 1.0 / (1.0 + nn.MSELoss()(query_pred, query_y).item())
            
            return accuracy
            
        except Exception as e:
            logger.error(f"Erro no few-shot learning: {e}")
            return 0.5
    
    def get_evolution_stats(self) -> Dict:
        """Retorna estatísticas da evolução"""
        return {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'avg_fitness': np.mean(self.fitness_scores),
            'diversity': self._calculate_diversity(),
            'population_size': len(self.population),
            'best_complexity': self.best_individual['complexity'] if self.best_individual else 0,
            'best_plasticity': self.best_individual['plasticity'] if self.best_individual else 0
        }
    
    def save_evolution_state(self, path: str):
        """Salva o estado da evolução"""
        state = {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'evolution_history': self.evolution_history,
            'performance_metrics': self.performance_metrics,
            'best_individual': {
                'complexity': self.best_individual['complexity'],
                'plasticity': self.best_individual['plasticity'],
                'fitness': self.best_individual['fitness']
            } if self.best_individual else None
        }
        
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Estado da evolução salvo em: {path}")
    
    def load_evolution_state(self, path: str):
        """Carrega o estado da evolução"""
        if os.path.exists(path):
            with open(path, 'r') as f:
                state = json.load(f)
            
            self.generation = state.get('generation', 0)
            self.best_fitness = state.get('best_fitness', -float('inf'))
            self.evolution_history = state.get('evolution_history', [])
            self.performance_metrics = state.get('performance_metrics', {})
            
            logger.info(f"Estado da evolução carregado de: {path}")
        else:
            logger.warning(f"Arquivo de estado não encontrado: {path}")

# Função de conveniência para criar o sistema
def create_biomimetic_ai(population_size: int = 50, **kwargs) -> BiomimeticEvolutionaryAI:
    """Cria uma instância do sistema biomimético evolucionário"""
    return BiomimeticEvolutionaryAI(population_size=population_size, **kwargs) 
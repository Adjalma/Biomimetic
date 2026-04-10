"""
SISTEMA DE AUTO-EVOLUÇÃO RADICAL (NÍVEL 3)
===========================================

Sistema avançado de auto-evolução biomimética que implementa:
1. Auto-otimização de arquiteturas neurais
2. Meta-learning contínuo com aprendizado por transferência
3. Sistema de "mutações" genéticas controladas
4. Evolução baseada em swarms/enxames
5. Auto-avaliação e auto-correção
6. Transferência de conhecimento entre gerações

Arquitetura inspirada em:
- Algoritmos Genéticos Avançados
- Swarm Intelligence
- Meta-Learning (MAML, Reptile)
- Neuroevolution (NEAT, HyperNEAT)
- AutoML (Auto-Keras, Auto-PyTorch)
"""

import json
import random
import time
import math
import statistics
import hashlib
import copy
import itertools
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from collections import defaultdict, deque
from datetime import datetime
import logging
from dataclasses import dataclass, field

# Substituir numpy por implementações nativas
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    # Implementações alternativas
    class SimpleNP:
        @staticmethod
        def std(values):
            if len(values) < 2:
                return 0.0
            mean_val = statistics.mean(values)
            variance = sum((x - mean_val) ** 2 for x in values) / (len(values) - 1)
            return math.sqrt(variance)
        
        @staticmethod
        def mean(values):
            if not values:
                return 0.0
            return sum(values) / len(values)
        
        @staticmethod
        def random_randn(*args):
            # Gerar números aleatórios com distribuição normal aproximada
            if len(args) == 1:
                n = args[0]
                return [random.gauss(0, 1) for _ in range(n)]
            elif len(args) == 2:
                rows, cols = args
                return [[random.gauss(0, 1) for _ in range(cols)] for _ in range(rows)]
            return random.gauss(0, 1)
    
    np = SimpleNP()

# Fallbacks para dependências
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("⚠️ PyTorch não disponível - usando implementações simplificadas")

try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

logger = logging.getLogger(__name__)

# ============================================================================
# ESTRUTURAS DE DADOS PARA AUTO-EVOLUÇÃO
# ============================================================================

@dataclass
class Gene:
    """Gene representando uma característica evolutiva"""
    gene_type: str  # 'architecture', 'parameter', 'strategy', 'heuristic'
    value: Any
    mutation_rate: float = 0.1
    min_value: Optional[Any] = None
    max_value: Optional[Any] = None
    description: str = ""
    
    def mutate(self, generation: int):
        """Aplica mutação ao gene"""
        if random.random() < self.mutation_rate:
            if self.gene_type == 'architecture':
                # Mutação de arquitetura
                if isinstance(self.value, list):
                    # Adicionar/remover camadas
                    if random.random() < 0.3 and len(self.value) > 1:
                        if random.random() < 0.5:
                            self.value.pop(random.randint(0, len(self.value)-1))
                        else:
                            self.value.insert(random.randint(0, len(self.value)), 
                                           random.randint(64, 1024))
                    # Alterar tamanho de camada
                    idx = random.randint(0, len(self.value)-1)
                    self.value[idx] = max(32, min(2048, self.value[idx] + random.randint(-128, 128)))
            
            elif self.gene_type == 'parameter':
                # Mutação de parâmetro numérico
                if isinstance(self.value, (int, float)):
                    delta = random.uniform(-0.2, 0.2) * self.value
                    if self.min_value is not None:
                        delta = max(self.min_value - self.value, delta)
                    if self.max_value is not None:
                        delta = min(self.max_value - self.value, delta)
                    self.value += delta
            
            elif self.gene_type == 'strategy':
                # Mutação de estratégia categórica
                strategies = ['exploration', 'exploitation', 'balanced', 'adaptive', 'safe', 'radical']
                if self.value in strategies:
                    self.value = random.choice([s for s in strategies if s != self.value])
        
        return self

@dataclass
class Chromosome:
    """Cromossomo contendo genes para um indivíduo"""
    genes: Dict[str, Gene]
    fitness: float = 0.0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    mutations: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    age: int = 0  # Quantas gerações sobreviveu
    
    def __post_init__(self):
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """Gerar ID único baseado em genes"""
        gene_str = str(sorted(self.genes.items()))
        return hashlib.md5(gene_str.encode()).hexdigest()[:12]
    
    def mutate(self, generation: int) -> 'Chromosome':
        """Aplica mutação ao cromossomo"""
        mutated = copy.deepcopy(self)
        mutated.generation = generation
        mutated.age += 1
        
        # Aplicar mutação a cada gene
        for gene_name, gene in mutated.genes.items():
            mutated.genes[gene_name] = gene.mutate(generation)
            if gene.value != self.genes[gene_name].value:
                mutated.mutations.append(f"{gene_name}:{gene.value}")
        
        # Resetar fitness após mutação
        mutated.fitness = 0.0
        
        return mutated
    
    def crossover(self, other: 'Chromosome', generation: int) -> 'Chromosome':
        """Crossover entre dois cromossomos"""
        child_genes = {}
        
        for gene_name in self.genes:
            if gene_name in other.genes:
                # Crossover de ponto único ou uniforme
                if random.random() < 0.5:
                    child_genes[gene_name] = copy.deepcopy(self.genes[gene_name])
                else:
                    child_genes[gene_name] = copy.deepcopy(other.genes[gene_name])
            else:
                child_genes[gene_name] = copy.deepcopy(self.genes[gene_name])
        
        child = Chromosome(
            genes=child_genes,
            generation=generation,
            parent_ids=[self.id, other.id],
            age=0
        )
        
        return child
    
    def to_dict(self) -> Dict[str, Any]:
        """Converter cromossomo para dicionário"""
        return {
            'id': self.id,
            'genes': {k: {'type': v.gene_type, 'value': v.value, 'mutation_rate': v.mutation_rate} 
                     for k, v in self.genes.items()},
            'fitness': self.fitness,
            'generation': self.generation,
            'age': self.age,
            'performance_metrics': self.performance_metrics
        }

@dataclass
class Individual:
    """Indivíduo completo no sistema evolutivo"""
    chromosome: Chromosome
    phenotype: Optional[Any] = None  # Implementação concreta (model, estratégia, etc.)
    birth_time: float = field(default_factory=time.time)
    evaluation_count: int = 0
    evaluation_history: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        self.id = self.chromosome.id
    
    def evaluate(self, task_data: Dict[str, Any], evaluation_fn: Callable) -> float:
        """Avaliar indivíduo em uma tarefa"""
        self.evaluation_count += 1
        
        try:
            if self.phenotype is None:
                # Se não tem fenótipo, criar baseado nos genes
                self.phenotype = self._create_phenotype()
            
            fitness = evaluation_fn(self.phenotype, task_data)
            self.evaluation_history.append(fitness)
            self.chromosome.fitness = statistics.mean(self.evaluation_history[-10:]) if self.evaluation_history else 0.0
            
            # Atualizar métricas de performance
            self.chromosome.performance_metrics = {
                'avg_fitness': self.chromosome.fitness,
                'evaluations': self.evaluation_count,
                'stability': statistics.stdev(self.evaluation_history[-5:]) if len(self.evaluation_history) >= 5 else 0.0,
                'last_evaluation': time.time()
            }
            
            return fitness
        except Exception as e:
            logger.error(f"Erro ao avaliar indivíduo {self.id}: {e}")
            return 0.0
    
    def _create_phenotype(self):
        """Criar fenótipo (implementação concreta) baseado nos genes"""
        # Esta é uma implementação genérica - subclasses podem sobrescrever
        return {
            'architecture': self.chromosome.genes.get('architecture', Gene('architecture', [256, 128, 64])).value,
            'strategy': self.chromosome.genes.get('strategy', Gene('strategy', 'balanced')).value,
            'learning_rate': self.chromosome.genes.get('learning_rate', Gene('parameter', 0.001, 0.05)).value,
            'exploration_rate': self.chromosome.genes.get('exploration_rate', Gene('parameter', 0.1, 0.1)).value
        }

# ============================================================================
# MOTOR DE AUTO-EVOLUÇÃO AVANÇADO
# ============================================================================

class AutoEvolutionEngine:
    """
    Motor de auto-evolução radical (Nível 3)
    
    Características principais:
    1. Evolução contínua baseada em múltiplas métricas
    2. Sistema de nichos para diversidade
    3. Meta-learning das estratégias evolutivas
    4. Auto-avaliação e auto-correção
    5. Transferência de conhecimento entre gerações
    """
    
    def __init__(self, 
                 population_size: int = 100,
                 elite_size: int = 10,
                 mutation_rate: float = 0.3,
                 crossover_rate: float = 0.7,
                 max_generations: int = 1000,
                 diversity_threshold: float = 0.2):
        
        self.population_size = population_size
        self.elite_size = elite_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.max_generations = max_generations
        self.diversity_threshold = diversity_threshold
        
        # Populações
        self.population: List[Individual] = []
        self.elite: List[Individual] = []
        self.archive: List[Individual] = []  # Arquivo de indivíduos históricos
        self.extinct: List[Individual] = []  # Indivíduos extintos (para análise)
        
        # Estado evolutivo
        self.generation = 0
        self.best_fitness_history = []
        self.avg_fitness_history = []
        self.diversity_history = []
        self.innovation_history = []
        
        # Nichos evolutivos
        self.niches: Dict[str, List[Individual]] = defaultdict(list)
        self.niche_strategies = ['exploration', 'exploitation', 'generalist', 'specialist', 'innovator']
        
        # Meta-learning do motor
        self.evolution_strategies = {
            'mutation_strategy': 'adaptive',
            'selection_pressure': 0.5,
            'diversity_maintenance': 'niching',
            'innovation_rate': 0.1
        }
        
        # Inicializar população
        self._initialize_population()
        
        logger.info(f"✅ AutoEvolutionEngine inicializado (população: {population_size})")
    
    def _initialize_population(self):
        """Inicializar população com diversidade"""
        self.population = []
        
        for i in range(self.population_size):
            # Criar genes base
            genes = {
                'architecture': Gene('architecture', [random.choice([64, 128, 256, 512]) 
                                                    for _ in range(random.randint(2, 6))]),
                'learning_rate': Gene('parameter', random.uniform(0.0001, 0.01), 0.05),
                'dropout_rate': Gene('parameter', random.uniform(0.0, 0.5), 0.1),
                'optimizer': Gene('strategy', random.choice(['adam', 'sgd', 'rmsprop']), 0.2),
                'exploration_rate': Gene('parameter', random.uniform(0.05, 0.3), 0.1),
                'task_specialization': Gene('parameter', random.uniform(0.0, 1.0), 0.15),
            }
            
            chromosome = Chromosome(genes=genes, generation=0)
            individual = Individual(chromosome=chromosome)
            
            # Atribuir a um nicho
            niche = random.choice(self.niche_strategies)
            self.niches[niche].append(individual)
            
            self.population.append(individual)
    
    def evolve_generation(self, task_pool: List[Dict[str, Any]], evaluation_fn: Callable) -> Dict[str, Any]:
        """
        Executar uma geração completa de evolução
        
        Args:
            task_pool: Lista de tarefas para avaliação
            evaluation_fn: Função para avaliar indivíduos
        
        Returns:
            Estatísticas da geração
        """
        self.generation += 1
        logger.info(f"🧬 Geração {self.generation} iniciada")
        
        # 1. AVALIAR POPULAÇÃO
        fitness_scores = []
        for individual in self.population:
            # Selecionar tarefa apropriada para o indivíduo
            task = self._select_task_for_individual(individual, task_pool)
            fitness = individual.evaluate(task, evaluation_fn)
            fitness_scores.append(fitness)
        
        # 2. ATUALIZAR ESTATÍSTICAS
        if fitness_scores:
            best_fitness = max(fitness_scores)
            avg_fitness = statistics.mean(fitness_scores)
            self.best_fitness_history.append(best_fitness)
            self.avg_fitness_history.append(avg_fitness)
            
            # Calcular diversidade
            diversity = self._calculate_population_diversity()
            self.diversity_history.append(diversity)
        
        # 3. SELEÇÃO DE ELITE
        self._update_elite()
        
        # 4. ATUALIZAR NICHOS
        self._update_niches()
        
        # 5. GERAR NOVA POPULAÇÃO
        new_population = self._generate_new_population()
        
        # 6. ARMAZENAR HISTÓRICO
        self._archive_generation()
        
        # 7. AUTO-AVALIAR E AJUSTAR ESTRATÉGIA
        self._self_assess_and_adjust()
        
        # 8. SUBSTITUIR POPULAÇÃO
        self.population = new_population
        
        # Estatísticas da geração
        stats = {
            'generation': self.generation,
            'population_size': len(self.population),
            'best_fitness': best_fitness if fitness_scores else 0.0,
            'avg_fitness': avg_fitness if fitness_scores else 0.0,
            'diversity': diversity,
            'elite_size': len(self.elite),
            'niche_counts': {k: len(v) for k, v in self.niches.items()},
            'innovations': len(self.innovation_history) if hasattr(self, 'innovation_history') else 0
        }
        
        logger.info(f"🧬 Geração {self.generation} concluída - Fitness: {best_fitness:.4f} (avg: {avg_fitness:.4f})")
        return stats
    
    def _select_task_for_individual(self, individual: Individual, task_pool: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Selecionar tarefa apropriada para um indivíduo baseado em especialização"""
        if not task_pool:
            return {'task_type': 'general', 'complexity': 'medium'}
        
        # Se o indivíduo tem especialização, selecionar tarefa correspondente
        specialization = individual.chromosome.genes.get('task_specialization', Gene('parameter', 0.5)).value
        
        if specialization > 0.7 and len(task_pool) > 1:
            # Especialista - pegar tarefa mais desafiante
            return max(task_pool, key=lambda t: t.get('complexity', 0))
        elif specialization < 0.3:
            # Generalista - pegar tarefa média
            return task_pool[len(task_pool) // 2]
        else:
            # Aleatório
            return random.choice(task_pool)
    
    def _calculate_population_diversity(self) -> float:
        """Calcular diversidade genética da população"""
        if len(self.population) < 2:
            return 0.0
        
        gene_diversity = []
        for i in range(min(10, len(self.population))):
            for j in range(i+1, min(10, len(self.population))):
                ind1 = self.population[i]
                ind2 = self.population[j]
                
                # Comparar genes
                diff_count = 0
                total_genes = 0
                
                for gene_name in ind1.chromosome.genes:
                    if gene_name in ind2.chromosome.genes:
                        total_genes += 1
                        if ind1.chromosome.genes[gene_name].value != ind2.chromosome.genes[gene_name].value:
                            diff_count += 1
                
                if total_genes > 0:
                    gene_diversity.append(diff_count / total_genes)
        
        return statistics.mean(gene_diversity) if gene_diversity else 0.0
    
    def _update_elite(self):
        """Atualizar elite da população"""
        # Ordenar por fitness
        sorted_pop = sorted(self.population, key=lambda x: x.chromosome.fitness, reverse=True)
        self.elite = sorted_pop[:self.elite_size]
        
        # Manter elite no arquivo histórico
        for elite_ind in self.elite:
            if elite_ind not in self.archive:
                self.archive.append(copy.deepcopy(elite_ind))
    
    def _update_niches(self):
        """Atualizar distribuição por nichos"""
        # Limpar nichos
        self.niches = defaultdict(list)
        
        # Reclassificar população
        for individual in self.population:
            niche = self._classify_individual_to_niche(individual)
            self.niches[niche].append(individual)
    
    def _classify_individual_to_niche(self, individual: Individual) -> str:
        """Classificar indivíduo em um nicho"""
        # Baseado nos genes e performance
        exploration = individual.chromosome.genes.get('exploration_rate', Gene('parameter', 0.1)).value
        specialization = individual.chromosome.genes.get('task_specialization', Gene('parameter', 0.5)).value
        age = individual.chromosome.age
        
        if exploration > 0.25:
            return 'exploration'
        elif specialization > 0.7:
            return 'specialist'
        elif age > 10:  # Indivíduos velhos tendem a ser exploradores
            return 'exploitation'
        elif len(individual.evaluation_history) > 5 and statistics.stdev(individual.evaluation_history[-5:]) < 0.1:
            return 'generalist'
        else:
            return 'innovator'
    
    def _generate_new_population(self) -> List[Individual]:
        """Gerar nova população através de seleção, crossover e mutação"""
        new_population = []
        
        # 1. ELITISMO - manter elite
        for elite_ind in self.elite:
            new_population.append(copy.deepcopy(elite_ind))
        
        # 2. PRESERVAR DIVERSIDADE - manter indivíduos de nichos sub-representados
        niche_target = self.population_size // len(self.niche_strategies)
        for niche, individuals in self.niches.items():
            if len(individuals) < niche_target and individuals:
                # Adicionar representantes do nicho
                representative = random.choice(individuals)
                new_population.append(copy.deepcopy(representative))
        
        # 3. GERAR DESCENDENTES
        while len(new_population) < self.population_size:
            # Selecionar pais
            parent1 = self._select_parent()
            parent2 = self._select_parent()
            
            # Crossover
            if random.random() < self.crossover_rate and parent1.id != parent2.id:
                child_chromosome = parent1.chromosome.crossover(parent2.chromosome, self.generation)
            else:
                child_chromosome = copy.deepcopy(parent1.chromosome)
                child_chromosome.generation = self.generation
            
            # Mutação
            if random.random() < self.mutation_rate:
                child_chromosome = child_chromosome.mutate(self.generation)
                
                # Registrar inovação se for significativa
                if child_chromosome.mutations:
                    self.innovation_history.append({
                        'generation': self.generation,
                        'mutations': child_chromosome.mutations,
                        'parent_ids': child_chromosome.parent_ids
                    })
            
            # Criar novo indivíduo
            child = Individual(chromosome=child_chromosome)
            new_population.append(child)
        
        return new_population[:self.population_size]  # Garantir tamanho correto
    
    def _select_parent(self) -> Individual:
        """Selecionar pai usando seleção por torneio"""
        tournament_size = 3
        tournament = random.sample(self.population, min(tournament_size, len(self.population)))
        return max(tournament, key=lambda x: x.chromosome.fitness)
    
    def _archive_generation(self):
        """Arquivar informações da geração atual"""
        # Já estamos arquivando elite no método _update_elite
        # Aqui podemos adicionar métricas adicionais
        pass
    
    def _self_assess_and_adjust(self):
        """Auto-avaliar o motor evolutivo e ajustar parâmetros"""
        if len(self.best_fitness_history) < 5:
            return
        
        # Analisar tendências
        recent_best = self.best_fitness_history[-5:]
        recent_avg = self.avg_fitness_history[-5:]
        recent_div = self.diversity_history[-5:] if self.diversity_history else [0.5]
        
        best_stagnant = max(recent_best) - min(recent_best) < 0.01
        diversity_low = statistics.mean(recent_div) < self.diversity_threshold
        
        # Ajustar estratégias baseado em performance
        if best_stagnant:
            # Estagnação - aumentar exploração
            self.evolution_strategies['innovation_rate'] = min(0.3, self.evolution_strategies['innovation_rate'] + 0.05)
            self.mutation_rate = min(0.5, self.mutation_rate + 0.05)
            logger.info(f"🔄 Ajuste: Estagnação detectada - aumentando inovação para {self.evolution_strategies['innovation_rate']:.2f}")
        
        if diversity_low:
            # Diversidade baixa - preservar mais nichos
            self.evolution_strategies['diversity_maintenance'] = 'aggressive_niching'
            logger.info("🔄 Ajuste: Diversidade baixa - ativando preservação agressiva de nichos")
        
        # Ajustar tamanho de elite baseado em progresso
        progress = self.best_fitness_history[-1] - self.best_fitness_history[-5] if len(self.best_fitness_history) >= 5 else 0
        if progress < 0.01:
            # Progresso lento - reduzir elite para mais pressão seletiva
            self.elite_size = max(5, self.elite_size - 1)
        elif progress > 0.05:
            # Bom progresso - aumentar elite para preservar boas soluções
            self.elite_size = min(20, self.elite_size + 1)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Obter dados para dashboard de monitoramento"""
        return {
            'evolution_status': {
                'generation': self.generation,
                'population_size': len(self.population),
                'elite_size': len(self.elite),
                'archive_size': len(self.archive),
                'extinct_count': len(self.extinct)
            },
            'performance_metrics': {
                'best_fitness': self.best_fitness_history[-1] if self.best_fitness_history else 0.0,
                'avg_fitness': self.avg_fitness_history[-1] if self.avg_fitness_history else 0.0,
                'diversity': self.diversity_history[-1] if self.diversity_history else 0.0,
                'innovation_rate': self.evolution_strategies['innovation_rate']
            },
            'niche_distribution': {
                niche: len(individuals) 
                for niche, individuals in self.niches.items()
            },
            'evolution_strategies': self.evolution_strategies,
            'recent_innovations': self.innovation_history[-5:] if self.innovation_history else []
        }
    
    def get_best_individual(self) -> Optional[Individual]:
        """Obter melhor indivíduo atual"""
        if not self.population:
            return None
        return max(self.population, key=lambda x: x.chromosome.fitness)
    
    def save_state(self, filepath: str):
        """Salvar estado do motor evolutivo"""
        state = {
            'generation': self.generation,
            'population': [ind.chromosome.to_dict() for ind in self.population],
            'elite': [ind.chromosome.to_dict() for ind in self.elite],
            'archive': [ind.chromosome.to_dict() for ind in self.archive],
            'best_fitness_history': self.best_fitness_history,
            'avg_fitness_history': self.avg_fitness_history,
            'diversity_history': self.diversity_history,
            'innovation_history': self.innovation_history,
            'evolution_strategies': self.evolution_strategies,
            'config': {
                'population_size': self.population_size,
                'elite_size': self.elite_size,
                'mutation_rate': self.mutation_rate,
                'crossover_rate': self.crossover_rate
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"💾 Estado salvo em {filepath}")
    
    def load_state(self, filepath: str) -> bool:
        """Carregar estado do motor evolutivo"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Carregar configuração
            config = state.get('config', {})
            self.population_size = config.get('population_size', self.population_size)
            self.elite_size = config.get('elite_size', self.elite_size)
            self.mutation_rate = config.get('mutation_rate', self.mutation_rate)
            self.crossover_rate = config.get('crossover_rate', self.crossover_rate)
            
            # Carregar histórico
            self.generation = state.get('generation', 0)
            self.best_fitness_history = state.get('best_fitness_history', [])
            self.avg_fitness_history = state.get('avg_fitness_history', [])
            self.diversity_history = state.get('diversity_history', [])
            self.innovation_history = state.get('innovation_history', [])
            self.evolution_strategies = state.get('evolution_strategies', self.evolution_strategies)
            
            # Reconstruir população (simplificado - em produção precisaria reconstruir objetos completos)
            self.population = []
            for chrom_data in state.get('population', []):
                # Converter de volta para Chromosome e Individual
                genes = {}
                for gene_name, gene_data in chrom_data.get('genes', {}).items():
                    genes[gene_name] = Gene(
                        gene_type=gene_data.get('type', 'parameter'),
                        value=gene_data.get('value'),
                        mutation_rate=gene_data.get('mutation_rate', 0.1)
                    )
                
                chromosome = Chromosome(
                    genes=genes,
                    fitness=chrom_data.get('fitness', 0.0),
                    generation=chrom_data.get('generation', 0),
                    age=chrom_data.get('age', 0)
                )
                chromosome.id = chrom_data.get('id', chromosome.id)
                
                individual = Individual(chromosome=chromosome)
                self.population.append(individual)
            
            # Reconstruir elite (simplificado)
            self.elite = self.population[:self.elite_size] if self.population else []
            
            logger.info(f"📂 Estado carregado de {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")
            return False

# ============================================================================
# SISTEMA DE META-LEARNING EVOLUTIVO
# ============================================================================

class MetaEvolutionSystem:
    """
    Sistema de meta-learning que evolui as próprias estratégias evolutivas
    
    Implementa:
    1. Evolução de hiperparâmetros evolutivos
    2. Aprendizado por transferência entre domínios
    3. Auto-otimização do processo evolutivo
    4. Memória de longo prazo de estratégias bem-sucedidas
    """
    
    def __init__(self, base_engine: AutoEvolutionEngine):
        self.base_engine = base_engine
        self.strategy_memory = deque(maxlen=100)  # Memória de estratégias
        self.domain_knowledge = {}  # Conhecimento por domínio
        self.transfer_learning_buffer = []
        
        logger.info("✅ MetaEvolutionSystem inicializado")
    
    def evolve_strategies(self, performance_data: Dict[str, Any]):
        """
        Evoluir estratégias evolutivas baseado em performance
        
        Args:
            performance_data: Dados de performance do motor base
        """
        # Analisar performance atual
        analysis = self._analyze_performance(performance_data)
        
        # Gerar novas estratégias
        new_strategies = self._generate_strategy_variations(analysis)
        
        # Avaliar e selecionar melhores estratégias
        best_strategy = self._evaluate_strategies(new_strategies, performance_data)
        
        # Aplicar melhor estratégia ao motor base
        if best_strategy:
            self._apply_strategy_to_engine(best_strategy)
            
            # Armazenar na memória
            self.strategy_memory.append({
                'generation': self.base_engine.generation,
                'strategy': best_strategy,
                'performance_impact': analysis.get('improvement_potential', 0.0)
            })
    
    def _analyze_performance(self, performance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analisar performance do motor evolutivo"""
        analysis = {
            'convergence_rate': 0.0,
            'diversity_trend': 'stable',
            'innovation_efficiency': 0.0,
            'improvement_potential': 0.0
        }
        
        # Analisar histórico de fitness
        if len(self.base_engine.best_fitness_history) >= 10:
            recent = self.base_engine.best_fitness_history[-10:]
            early = self.base_engine.best_fitness_history[-20:-10] if len(self.base_engine.best_fitness_history) >= 20 else recent
            
            # Taxa de convergência
            analysis['convergence_rate'] = (max(recent) - min(recent)) / (max(early) - min(early)) if (max(early) - min(early)) > 0 else 1.0
            
            # Potencial de melhoria
            analysis['improvement_potential'] = 1.0 - (max(recent) / 1.0)  # Assumindo fitness máximo 1.0
        
        # Analisar diversidade
        if len(self.base_engine.diversity_history) >= 5:
            recent_div = self.base_engine.diversity_history[-5:]
            avg_div = statistics.mean(recent_div)
            
            if avg_div < self.base_engine.diversity_threshold * 0.8:
                analysis['diversity_trend'] = 'low'
            elif avg_div > self.base_engine.diversity_threshold * 1.2:
                analysis['diversity_trend'] = 'high'
            else:
                analysis['diversity_trend'] = 'optimal'
        
        # Eficiência de inovação
        if self.base_engine.innovation_history:
            recent_innovations = [i for i in self.base_engine.innovation_history 
                                 if i.get('generation', 0) >= self.base_engine.generation - 10]
            analysis['innovation_efficiency'] = len(recent_innovations) / 10.0  # Inovações por geração
        
        return analysis
    
    def _generate_strategy_variations(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Gerar variações de estratégias baseado na análise"""
        strategies = []
        
        base_strategy = self.base_engine.evolution_strategies.copy()
        
        # Gerar variações baseadas nos problemas identificados
        if analysis['diversity_trend'] == 'low':
            # Baixa diversidade - estratégias para aumentar diversidade
            strategies.append({
                **base_strategy,
                'diversity_maintenance': 'aggressive_niching',
                'mutation_strategy': 'explorative',
                'innovation_rate': min(0.3, base_strategy.get('innovation_rate', 0.1) + 0.1)
            })
            
            strategies.append({
                **base_strategy,
                'diversity_maintenance': 'island_model',
                'selection_pressure': max(0.3, base_strategy.get('selection_pressure', 0.5) - 0.2)
            })
        
        if analysis['convergence_rate'] < 0.5:
            # Convergência rápida - pode estar convergindo para ótimo local
            strategies.append({
                **base_strategy,
                'mutation_strategy': 'radical',
                'innovation_rate': min(0.4, base_strategy.get('innovation_rate', 0.1) + 0.2),
                'selection_pressure': max(0.3, base_strategy.get('selection_pressure', 0.5) - 0.1)
            })
        
        if analysis['improvement_potential'] > 0.3:
            # Alto potencial de melhoria - estratégias exploratórias
            strategies.append({
                **base_strategy,
                'mutation_strategy': 'adaptive_exploration',
                'exploration_ratio': 0.7,
                'exploitation_ratio': 0.3
            })
        
        # Estratégia conservadora (baseline)
        strategies.append(base_strategy)
        
        # Estratégia aleatória para exploração
        random_strategy = base_strategy.copy()
        random_strategy['mutation_strategy'] = random.choice(['adaptive', 'explorative', 'conservative', 'radical'])
        random_strategy['innovation_rate'] = random.uniform(0.05, 0.3)
        strategies.append(random_strategy)
        
        return strategies
    
    def _evaluate_strategies(self, strategies: List[Dict[str, Any]], 
                            performance_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Avaliar estratégias e selecionar a melhor"""
        if not strategies:
            return None
        
        # Avaliação simplificada - em implementação real seria mais complexa
        # Baseada na análise de problemas e histórico
        
        best_strategy = None
        best_score = -float('inf')
        
        for strategy in strategies:
            score = self._score_strategy(strategy, performance_data)
            if score > best_score:
                best_score = score
                best_strategy = strategy
        
        return best_strategy
    
    def _score_strategy(self, strategy: Dict[str, Any], performance_data: Dict[str, Any]) -> float:
        """Pontuar uma estratégia evolutiva"""
        score = 0.0
        
        # Pontuar baseado nos problemas identificados
        if performance_data.get('diversity', 0.0) < 0.2 and strategy.get('diversity_maintenance') in ['aggressive_niching', 'island_model']:
            score += 2.0
        
        if performance_data.get('best_fitness', 0.0) < 0.5 and strategy.get('mutation_strategy') == 'radical':
            score += 1.5
        
        if strategy.get('innovation_rate', 0.1) > 0.2:
            # Inovação alta - bom para estagnação, ruim se já tem boa performance
            if performance_data.get('best_fitness', 0.0) > 0.8:
                score -= 1.0  # Muita inovação pode atrapalhar
            else:
                score += 1.0
        
        # Preferir estratégias balanceadas
        if strategy.get('selection_pressure', 0.5) >= 0.4 and strategy.get('selection_pressure', 0.5) <= 0.6:
            score += 0.5
        
        return score
    
    def _apply_strategy_to_engine(self, strategy: Dict[str, Any]):
        """Aplicar estratégia ao motor evolutivo base"""
        # Atualizar estratégias do motor
        self.base_engine.evolution_strategies.update(strategy)
        
        # Ajustar parâmetros relacionados
        if 'innovation_rate' in strategy:
            self.base_engine.mutation_rate = strategy['innovation_rate'] * 0.5  # Relação aproximada
        
        if 'selection_pressure' in strategy:
            # Ajustar tamanho de elite baseado na pressão seletiva
            target_pressure = strategy['selection_pressure']
            current_elite_ratio = self.base_engine.elite_size / self.base_engine.population_size
            
            # Pressão alta = elite menor, pressão baixa = elite maior
            target_elite_ratio = 0.5 - (target_pressure - 0.5) * 0.3
            self.base_engine.elite_size = int(self.base_engine.population_size * target_elite_ratio)
            self.base_engine.elite_size = max(5, min(30, self.base_engine.elite_size))
        
        logger.info(f"🔄 Estratégia aplicada: {strategy.get('mutation_strategy', 'unknown')} "
                   f"(inovação: {strategy.get('innovation_rate', 0.1):.2f})")

# ============================================================================
# INTEGRAÇÃO COM SISTEMA PRINCIPAL
# ============================================================================

class AdvancedAutoEvolutionSystem:
    """
    Sistema completo de auto-evolução (Nível 3)
    
    Integra:
    1. AutoEvolutionEngine - evolução base
    2. MetaEvolutionSystem - meta-learning das estratégias
    3. OrchestrationEvolutionEngine - evolução de orquestração (Nível 1)
    4. LocalBrain - IA local como cérebro biomimético
    """
    
    def __init__(self, 
                 use_local_brain: bool = False,
                 local_brain_type: str = "mock",
                 enable_meta_evolution: bool = True):
        
        # Componentes principais
        self.auto_evolution_engine = AutoEvolutionEngine()
        self.meta_evolution_system = None
        self.orchestration_evolution = None
        self.local_brain = None
        
        # Configurações
        self.use_local_brain = use_local_brain
        self.local_brain_type = local_brain_type
        self.enable_meta_evolution = enable_meta_evolution
        
        # Estado do sistema
        self.evolution_cycles = 0
        self.total_evaluations = 0
        self.performance_trend = []
        self.adaptation_history = []
        
        # Inicializar componentes
        self._initialize_components()
        
        logger.info("🚀 AdvancedAutoEvolutionSystem inicializado (Nível 3)")
    
    def _initialize_components(self):
        """Inicializar todos os componentes"""
        # Inicializar meta-evolution se habilitado
        if self.enable_meta_evolution:
            self.meta_evolution_system = MetaEvolutionSystem(self.auto_evolution_engine)
            logger.info("✅ MetaEvolutionSystem inicializado")
        
        # Tentar inicializar orchestration evolution (Nível 1)
        try:
            from .orchestration_evolution import OrchestrationEvolutionEngine
            self.orchestration_evolution = OrchestrationEvolutionEngine()
            logger.info("✅ OrchestrationEvolutionEngine (Nível 1) integrado")
        except ImportError:
            logger.warning("⚠️ OrchestrationEvolutionEngine não disponível")
        
        # Inicializar local brain se habilitado
        if self.use_local_brain:
            try:
                from .local_brain import HybridBiomimeticSystem
                self.local_brain = HybridBiomimeticSystem(brain_type=self.local_brain_type)
                logger.info(f"🧠 Cérebro local inicializado (tipo: {self.local_brain_type})")
            except ImportError:
                logger.warning("⚠️ Módulo local_brain não disponível")
                self.use_local_brain = False
    
    def run_evolution_cycle(self, task_pool: List[Dict[str, Any]], evaluation_fn: Callable) -> Dict[str, Any]:
        """
        Executar um ciclo completo de evolução
        
        Args:
            task_pool: Tarefas para avaliação
            evaluation_fn: Função de avaliação
        
        Returns:
            Resultados do ciclo
        """
        self.evolution_cycles += 1
        logger.info(f"🔄 Ciclo de evolução {self.evolution_cycles} iniciado")
        
        # 1. EXECUTAR EVOLUÇÃO BASE
        evolution_results = self.auto_evolution_engine.evolve_generation(task_pool, evaluation_fn)
        self.total_evaluations += evolution_results.get('population_size', 0)
        
        # 2. APLICAR META-EVOLUÇÃO (se habilitado)
        if self.meta_evolution_system:
            self.meta_evolution_system.evolve_strategies(evolution_results)
        
        # 3. USAR CÉREBRO LOCAL PARA ANÁLISE (se disponível)
        if self.local_brain:
            self._consult_local_brain(evolution_results)
        
        # 4. REGISTRAR NO ORCHESTRATION EVOLUTION (se disponível)
        if self.orchestration_evolution:
            self._record_to_orchestration_evolution(evolution_results)
        
        # 5. ATUALIZAR HISTÓRICO E ANÁLISE
        self.performance_trend.append(evolution_results.get('best_fitness', 0.0))
        self.adaptation_history.append({
            'cycle': self.evolution_cycles,
            'strategies': self.auto_evolution_engine.evolution_strategies.copy(),
            'performance': evolution_results
        })
        
        # 6. AUTO-AVALIAR E AJUSTAR
        self._self_assess_and_adapt()
        
        results = {
            'evolution_cycle': self.evolution_cycles,
            'evolution_results': evolution_results,
            'system_state': self.get_system_status(),
            'best_individual': self.auto_evolution_engine.get_best_individual().chromosome.to_dict() 
                              if self.auto_evolution_engine.get_best_individual() else None
        }
        
        logger.info(f"🔄 Ciclo {self.evolution_cycles} concluído - "
                   f"Fitness: {evolution_results.get('best_fitness', 0.0):.4f}")
        
        return results
    
    def _consult_local_brain(self, evolution_results: Dict[str, Any]):
        """Consultar cérebro local para insights evolutivos"""
        try:
            # Preparar contexto para o cérebro local
            context = {
                'evolution_results': evolution_results,
                'system_state': self.get_system_status(),
                'generation': self.auto_evolution_engine.generation
            }
            
            # Consultar o cérebro para insights
            insight_task = {
                'task_type': 'evolution_insight',
                'context': json.dumps(context),
                'query': 'Analyze evolution performance and suggest improvements'
            }
            
            # Em implementação real, chamaria o cérebro local
            # insight = self.local_brain.analyze_evolution(insight_task)
            # Por enquanto é placeholder
            logger.debug("🧠 Consulta ao cérebro local (placeholder)")
            
        except Exception as e:
            logger.error(f"Erro ao consultar cérebro local: {e}")
    
    def _record_to_orchestration_evolution(self, evolution_results: Dict[str, Any]):
        """Registrar resultados no orchestration evolution (Nível 1)"""
        try:
            # Criar registro de tarefa para orchestration evolution
            task_data = {
                'task_type': 'evolution_cycle',
                'evolution_cycle': self.evolution_cycles,
                'performance': evolution_results
            }
            
            recommendation = {
                'provider': 'auto_evolution_engine',
                'parameters': self.auto_evolution_engine.evolution_strategies,
                'confidence': evolution_results.get('best_fitness', 0.0),
                'reasoning': f"Evolução ciclo {self.evolution_cycles}"
            }
            
            result = {
                'success': evolution_results.get('best_fitness', 0.0) > 0.5,
                'performance_score': evolution_results.get('best_fitness', 0.0),
                'efficiency': evolution_results.get('avg_fitness', 0.0) / max(0.001, evolution_results.get('best_fitness', 0.001)),
                'quality_score': evolution_results.get('diversity', 0.0)
            }
            
            # Registrar no orchestration evolution
            self.orchestration_evolution.record_recommendation(task_data, recommendation)
            self.orchestration_evolution.record_result(task_data, result)
            
        except Exception as e:
            logger.error(f"Erro ao registrar no orchestration evolution: {e}")
    
    def _self_assess_and_adapt(self):
        """Auto-avaliar sistema e adaptar configurações"""
        if len(self.performance_trend) < 5:
            return
        
        # Analisar tendência de performance
        recent_perf = self.performance_trend[-5:]
        perf_trend = self._calculate_trend(recent_perf)
        
        # Se performance estagnando ou decaindo, ajustar
        if perf_trend < 0.01:  # Estagnação
            logger.info("📉 Estagnação detectada - considerando ajustes no sistema")
            
            # Se temos meta-evolution, ele já deve ajustar
            # Aqui podemos ajustar configurações gerais
            if self.enable_meta_evolution and self.meta_evolution_system:
                # Forçar reavaliação de estratégias
                current_perf = {
                    'best_fitness': recent_perf[-1],
                    'avg_fitness': self.auto_evolution_engine.avg_fitness_history[-1] if self.auto_evolution_engine.avg_fitness_history else 0.0,
                    'diversity': self.auto_evolution_engine.diversity_history[-1] if self.auto_evolution_engine.diversity_history else 0.0
                }
                self.meta_evolution_system.evolve_strategies(current_perf)
    
    def _calculate_trend(self, values: List[float]) -> float:
        """Calcular tendência de uma série de valores"""
        if len(values) < 2:
            return 0.0
        
        # Regressão linear simples
        x = list(range(len(values)))
        y = values
        
        n = len(x)
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(x[i] * y[i] for i in range(n))
        sum_x2 = sum(x_i * x_i for x_i in x)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def get_system_status(self) -> Dict[str, Any]:
        """Obter status completo do sistema"""
        status = {
            'system_info': {
                'name': 'AdvancedAutoEvolutionSystem',
                'level': 3,
                'evolution_cycles': self.evolution_cycles,
                'total_evaluations': self.total_evaluations,
                'components_active': {
                    'auto_evolution_engine': True,
                    'meta_evolution_system': self.meta_evolution_system is not None,
                    'orchestration_evolution': self.orchestration_evolution is not None,
                    'local_brain': self.local_brain is not None
                }
            },
            'performance': {
                'current_fitness': self.performance_trend[-1] if self.performance_trend else 0.0,
                'performance_trend': self._calculate_trend(self.performance_trend[-10:]) if len(self.performance_trend) >= 10 else 0.0,
                'adaptation_count': len(self.adaptation_history)
            }
        }
        
        # Adicionar dados do motor evolutivo se disponível
        if self.auto_evolution_engine:
            status['evolution_engine'] = self.auto_evolution_engine.get_dashboard_data()
        
        return status
    
    def save_state(self, filepath: str):
        """Salvar estado completo do sistema"""
        state = {
            'evolution_cycles': self.evolution_cycles,
            'total_evaluations': self.total_evaluations,
            'performance_trend': self.performance_trend,
            'adaptation_history': self.adaptation_history,
            'system_config': {
                'use_local_brain': self.use_local_brain,
                'local_brain_type': self.local_brain_type,
                'enable_meta_evolution': self.enable_meta_evolution
            }
        }
        
        # Salvar estado do motor evolutivo
        if self.auto_evolution_engine:
            engine_state_path = filepath.replace('.json', '_engine.json')
            self.auto_evolution_engine.save_state(engine_state_path)
            state['engine_state_file'] = engine_state_path
        
        with open(filepath, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"💾 Estado do sistema salvo em {filepath}")
    
    def load_state(self, filepath: str) -> bool:
        """Carregar estado completo do sistema"""
        try:
            with open(filepath, 'r') as f:
                state = json.load(f)
            
            # Carregar estado básico
            self.evolution_cycles = state.get('evolution_cycles', 0)
            self.total_evaluations = state.get('total_evaluations', 0)
            self.performance_trend = state.get('performance_trend', [])
            self.adaptation_history = state.get('adaptation_history', [])
            
            # Carregar configurações
            config = state.get('system_config', {})
            self.use_local_brain = config.get('use_local_brain', self.use_local_brain)
            self.local_brain_type = config.get('local_brain_type', self.local_brain_type)
            self.enable_meta_evolution = config.get('enable_meta_evolution', self.enable_meta_evolution)
            
            # Carregar estado do motor evolutivo
            engine_state_file = state.get('engine_state_file')
            if engine_state_file and self.auto_evolution_engine:
                self.auto_evolution_engine.load_state(engine_state_file)
            
            logger.info(f"📂 Estado do sistema carregado de {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar estado do sistema: {e}")
            return False


# ============================================================================
# DEMONSTRAÇÃO E TESTES
# ============================================================================

def demo_auto_evolution():
    """Demonstração do sistema de auto-evolução"""
    print("🚀 DEMONSTRAÇÃO DO SISTEMA DE AUTO-EVOLUÇÃO (NÍVEL 3)")
    print("=" * 60)
    
    # Criar sistema
    system = AdvancedAutoEvolutionSystem(
        use_local_brain=False,  # Sem Ollama por enquanto
        enable_meta_evolution=True
    )
    
    # Função de avaliação simulada
    def simulated_evaluation(phenotype, task_data):
        """Função de avaliação simulada"""
        # Em sistema real, seria uma avaliação real do modelo
        complexity = task_data.get('complexity', 1.0)
        
        # Fitness baseado na arquitetura do fenótipo
        if isinstance(phenotype, dict):
            arch = phenotype.get('architecture', [])
            lr = phenotype.get('learning_rate', 0.001)
            
            # Fitness simulada: arquiteturas maiores e taxas de aprendizado moderadas performam melhor
            size_score = sum(arch) / (len(arch) * 512) if arch else 0.5
            lr_score = 1.0 - abs(lr - 0.005) / 0.005  # Ótimo em 0.005
            
            fitness = 0.7 * size_score + 0.3 * lr_score
            fitness *= complexity  # Tarefas mais complexas são mais difíceis
            
            # Adicionar algum ruído
            fitness += random.uniform(-0.1, 0.1)
            
            return max(0.0, min(1.0, fitness))
        
        return random.uniform(0.0, 1.0)
    
    # Pool de tarefas
    task_pool = [
        {'task_type': 'classification', 'complexity': 0.7},
        {'task_type': 'regression', 'complexity': 0.9},
        {'task_type': 'generation', 'complexity': 1.0},
        {'task_type': 'translation', 'complexity': 0.8},
        {'task_type': 'summarization', 'complexity': 0.6}
    ]
    
    # Executar alguns ciclos de evolução
    print("\n🧬 Executando ciclos de evolução...")
    for cycle in range(5):
        results = system.run_evolution_cycle(task_pool, simulated_evaluation)
        
        print(f"\nCiclo {cycle + 1}:")
        print(f"  Fitness: {results['evolution_results'].get('best_fitness', 0.0):.4f}")
        print(f"  Diversidade: {results['evolution_results'].get('diversity', 0.0):.3f}")
        print(f"  Nichos: {results['evolution_results'].get('niche_counts', {})}")
    
    # Mostrar status final
    print("\n📊 STATUS FINAL DO SISTEMA:")
    status = system.get_system_status()
    print(f"  Ciclos completados: {status['system_info']['evolution_cycles']}")
    print(f"  Total avaliações: {status['system_info']['total_evaluations']}")
    print(f"  Componentes ativos: {status['system_info']['components_active']}")
    
    # Mostrar melhor indivíduo
    best_ind = system.auto_evolution_engine.get_best_individual()
    if best_ind:
        print(f"\n🏆 MELHOR INDIVÍDUO (Fitness: {best_ind.chromosome.fitness:.4f}):")
        for gene_name, gene in best_ind.chromosome.genes.items():
            print(f"  {gene_name}: {gene.value} (mutação: {gene.mutation_rate:.3f})")
    
    print("\n🎯 Demonstração concluída!")
    return system


if __name__ == "__main__":
    # Executar demonstração
    demo_system = demo_auto_evolution()
    
    # Salvar estado
    demo_system.save_state("/tmp/auto_evolution_demo_state.json")
    print("💾 Estado salvo em /tmp/auto_evolution_demo_state.json")
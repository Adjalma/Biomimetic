#!/usr/bin/env python3
"""
Sistema de Evolucao Robusto com Metalearning e Biomimetica
Versao 2.0 - Melhorado com compatibilidade dimensional
"""

import torch
import torch.nn as nn
import numpy as np
import json
import logging
import random
import time
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetaLearningEngine:
    """Motor de metalearning para evolução biomimética"""
    
    def __init__(self):
        self.learning_history = []
        self.meta_parameters = {
            'learning_rate': 0.001,
            'adaptation_speed': 0.1,
            'knowledge_retention': 0.8,
            'exploration_rate': 0.2
        }
        self.knowledge_base = {}
    
    def learn_from_evolution(self, evolution_data: Dict[str, Any]):
        """Aprende com dados de evolução"""
        try:
            # Extrair padrões de sucesso
            success_patterns = self._extract_success_patterns(evolution_data)
            
            # Atualizar base de conhecimento
            self._update_knowledge_base(success_patterns)
            
            # Adaptar parâmetros meta
            self._adapt_meta_parameters(evolution_data)
            
            # Registrar aprendizado
            self.learning_history.append({
                'timestamp': datetime.now().isoformat(),
                'patterns_learned': len(success_patterns),
                'knowledge_size': len(self.knowledge_base),
                'meta_parameters': self.meta_parameters.copy()
            })
            
            logger.info(f"Metalearning: {len(success_patterns)} padrões aprendidos")
            
        except Exception as e:
            logger.error(f"Erro no metalearning: {e}")
    
    def _extract_success_patterns(self, evolution_data: Dict[str, Any]) -> List[Dict]:
        """Extrai padrões de sucesso da evolução"""
        patterns = []
        
        try:
            # Analisar fitness patterns
            if 'fitness_history' in evolution_data:
                fitness_data = evolution_data['fitness_history']
                
                # Padrão 1: Melhoria rápida
                if len(fitness_data) >= 3:
                    recent_improvement = fitness_data[-1] - fitness_data[-3]
                    if recent_improvement > 0.1:
                        patterns.append({
                            'type': 'rapid_improvement',
                            'value': recent_improvement,
                            'strategy': 'maintain_current_approach'
                        })
                
                # Padrão 2: Estagnação
                if len(fitness_data) >= 5:
                    recent_avg = np.mean(fitness_data[-3:])
                    previous_avg = np.mean(fitness_data[-6:-3])
                    if abs(recent_avg - previous_avg) < 0.01:
                        patterns.append({
                            'type': 'stagnation',
                            'value': recent_avg,
                            'strategy': 'increase_exploration'
                        })
            
            # Analisar arquitetura patterns
            if 'architecture_history' in evolution_data:
                arch_data = evolution_data['architecture_history']
                
                # Padrão 3: Arquiteturas bem-sucedidas
                successful_archs = [arch for arch in arch_data if arch.get('fitness', 0) > 0.8]
                if successful_archs:
                    patterns.append({
                        'type': 'successful_architecture',
                        'count': len(successful_archs),
                        'strategy': 'replicate_successful_patterns'
                    })
            
        except Exception as e:
            logger.error(f"Erro na extração de padrões: {e}")
        
        return patterns
    
    def _update_knowledge_base(self, patterns: List[Dict]):
        """Atualiza base de conhecimento"""
        for pattern in patterns:
            pattern_type = pattern['type']
            
            if pattern_type not in self.knowledge_base:
                self.knowledge_base[pattern_type] = []
            
            self.knowledge_base[pattern_type].append({
                'data': pattern,
                'timestamp': datetime.now().isoformat(),
                'usage_count': 0
            })
    
    def _adapt_meta_parameters(self, evolution_data: Dict[str, Any]):
        """Adapta parâmetros meta baseado na evolução"""
        try:
            # Adaptar taxa de exploração
            if 'stagnation' in [p['type'] for p in self._extract_success_patterns(evolution_data)]:
                self.meta_parameters['exploration_rate'] = min(0.5, self.meta_parameters['exploration_rate'] * 1.2)
            else:
                self.meta_parameters['exploration_rate'] = max(0.1, self.meta_parameters['exploration_rate'] * 0.9)
            
            # Adaptar velocidade de adaptação
            if 'rapid_improvement' in [p['type'] for p in self._extract_success_patterns(evolution_data)]:
                self.meta_parameters['adaptation_speed'] = min(0.3, self.meta_parameters['adaptation_speed'] * 1.1)
            
        except Exception as e:
            logger.error(f"Erro na adaptação de parâmetros: {e}")
    
    def get_evolution_strategy(self) -> Dict[str, Any]:
        """Retorna estratégia de evolução baseada no metalearning"""
        strategy = {
            'mutation_rate': 0.1,
            'crossover_rate': 0.7,
            'selection_pressure': 0.5,
            'exploration_focus': False
        }
        
        try:
            # Aplicar conhecimento aprendido
            if 'stagnation' in self.knowledge_base:
                strategy['mutation_rate'] = min(0.3, strategy['mutation_rate'] * 1.5)
                strategy['exploration_focus'] = True
            
            if 'rapid_improvement' in self.knowledge_base:
                strategy['selection_pressure'] = min(0.8, strategy['selection_pressure'] * 1.2)
            
            # Aplicar parâmetros meta
            strategy['mutation_rate'] *= (1 + self.meta_parameters['exploration_rate'])
            strategy['crossover_rate'] *= (1 - self.meta_parameters['exploration_rate'] * 0.5)
            
        except Exception as e:
            logger.error(f"Erro na geração de estratégia: {e}")
        
        return strategy

class BiomimeticEvolutionaryAI:
    """IA Autoevolutiva Biomimética com Metalearning"""
    
    def __init__(self):
        self.generation = 0
        self.population = []
        self.best_fitness = 0.0
        self.evolution_history = []
        self.meta_learning = MetaLearningEngine()
        self.compatibility_enabled = True
        
        # Configurações biomiméticas
        self.input_size = 512
        self.output_size = 128
        self.population_size = 12
        
    def initialize_population(self):
        """Inicializa população com arquiteturas biomiméticas"""
        logger.info(f"Inicializando população biomimética de {self.population_size} indivíduos")
        
        for i in range(self.population_size):
            individual = self._create_biomimetic_individual()
            self.population.append({
                'id': f"bio_{i}_{datetime.now().strftime('%H%M%S')}",
                'model': individual,
                'fitness': 0.0,
                'generation': 0,
                'biomimetic_score': 1.0,
                'meta_learning_score': 0.0
            })
        
        logger.info(f"População biomimética inicializada com {len(self.population)} indivíduos")
    
    def _create_biomimetic_individual(self) -> nn.Module:
        """Cria indivíduo com arquitetura biomimética"""
        # Arquitetura inspirada em redes neurais biológicas
        layers = []
        
        # Camada de entrada (receptores sensoriais)
        layers.append(nn.Linear(self.input_size, 256))
        layers.append(nn.ReLU())
        layers.append(nn.Dropout(0.2))
        
        # Camadas ocultas (neurônios intermediários)
        hidden_sizes = [256, 128, 64]
        for i in range(len(hidden_sizes) - 1):
            layers.append(nn.Linear(hidden_sizes[i], hidden_sizes[i + 1]))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
        
        # Camada de saída (neurônios motores)
        layers.append(nn.Linear(hidden_sizes[-1], self.output_size))
        
        return nn.Sequential(*layers)
    
    def evolve_with_metalearning(self, generations: int = 5):
        """Evolui população com metalearning biomimético"""
        logger.info(f"Iniciando evolução biomimética por {generations} gerações")
        
        for gen in range(generations):
            logger.info(f"Executando geração biomimética {gen + 1}/{generations}")
            
            # 1. Avaliar população atual
            self._evaluate_population_biomimetic()
            
            # 2. Aplicar metalearning
            evolution_data = self._prepare_evolution_data()
            self.meta_learning.learn_from_evolution(evolution_data)
            
            # 3. Obter estratégia de evolução
            strategy = self.meta_learning.get_evolution_strategy()
            
            # 4. Evoluir com estratégia adaptativa
            self._evolve_with_strategy(strategy)
            
            # 5. Registrar evolução
            self._record_biomimetic_evolution(gen + 1, strategy)
            
            logger.info(f"Geração {gen + 1} concluída. Fitness: {self.best_fitness:.4f}")
    
    def _evaluate_population_biomimetic(self):
        """Avalia população com critérios biomiméticos"""
        for individual in self.population:
            try:
                # Avaliação de performance
                test_input = torch.randn(100, self.input_size)
                model = individual['model']
                
                with torch.no_grad():
                    output = model(test_input)
                
                # Fitness biomimético
                fitness = self._calculate_biomimetic_fitness(output)
                individual['fitness'] = fitness
                
                # Score de metalearning
                meta_score = self._calculate_meta_learning_score(individual)
                individual['meta_learning_score'] = meta_score
                
                # Atualizar melhor fitness
                if fitness > self.best_fitness:
                    self.best_fitness = fitness
                    
            except Exception as e:
                logger.warning(f"Erro na avaliação biomimética: {e}")
                individual['fitness'] = 0.0
    
    def _calculate_biomimetic_fitness(self, output: torch.Tensor) -> float:
        """Calcula fitness baseado em critérios biomiméticos"""
        try:
            # Estabilidade (homeostase)
            stability = 1.0 / (1.0 + torch.std(output).item())
            
            # Diversidade (plasticidade sináptica)
            diversity = torch.var(output).item()
            
            # Eficiência energética (otimização)
            efficiency = 1.0 / (1.0 + torch.mean(torch.abs(output)).item())
            
            # Robustez (resiliência)
            robustness = 1.0 / (1.0 + torch.max(torch.abs(output)).item())
            
            # Fitness biomimético combinado
            fitness = (stability + diversity + efficiency + robustness) / 4.0
            return max(0.0, min(1.0, fitness))
            
        except Exception as e:
            logger.error(f"Erro no cálculo de fitness biomimético: {e}")
            return 0.0
    
    def _calculate_meta_learning_score(self, individual: Dict) -> float:
        """Calcula score de metalearning do indivíduo"""
        try:
            # Baseado na história de evolução
            if individual['generation'] > 0:
                return min(1.0, individual['generation'] * 0.1)
            return 0.0
        except Exception as e:
            logger.error(f"Erro no cálculo de score de metalearning: {e}")
            return 0.0
    
    def _prepare_evolution_data(self) -> Dict[str, Any]:
        """Prepara dados para metalearning"""
        return {
            'fitness_history': [ind['fitness'] for ind in self.population],
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'population_size': len(self.population),
            'meta_learning_history': self.meta_learning.learning_history
        }
    
    def _evolve_with_strategy(self, strategy: Dict[str, Any]):
        """Evolui população com estratégia adaptativa"""
        try:
            # Selecionar melhores com pressão adaptativa
            selection_pressure = strategy['selection_pressure']
            sorted_population = sorted(self.population, key=lambda x: x['fitness'], reverse=True)
            
            selection_size = max(2, int(len(sorted_population) * selection_pressure))
            best_individuals = sorted_population[:selection_size]
            
            # Criar nova população
            new_population = []
            
            # Elitismo - manter melhores
            for individual in best_individuals:
                new_population.append(individual.copy())
            
            # Crossover e mutação com taxas adaptativas
            while len(new_population) < len(self.population):
                parent1 = random.choice(best_individuals)
                parent2 = random.choice(best_individuals)
                
                child = self._create_adaptive_child(parent1, parent2, strategy)
                new_population.append(child)
            
            self.population = new_population
            self.generation += 1
            
        except Exception as e:
            logger.error(f"Erro na evolução com estratégia: {e}")
    
    def _create_adaptive_child(self, parent1: Dict, parent2: Dict, strategy: Dict) -> Dict:
        """Cria filho com adaptação baseada em estratégia"""
        try:
            # Crossover adaptativo
            if random.random() < strategy['crossover_rate']:
                child_model = self._adaptive_crossover(parent1['model'], parent2['model'])
            else:
                child_model = parent1['model']
            
            # Mutação adaptativa
            if random.random() < strategy['mutation_rate']:
                child_model = self._adaptive_mutation(child_model, strategy)
            
            # Criar indivíduo filho
            child = {
                'id': f"child_{datetime.now().strftime('%H%M%S')}_{random.randint(1000, 9999)}",
                'model': child_model,
                'fitness': 0.0,
                'generation': self.generation + 1,
                'biomimetic_score': 1.0,
                'meta_learning_score': 0.0
            }
            
            return child
            
        except Exception as e:
            logger.error(f"Erro na criação de filho adaptativo: {e}")
            return parent1.copy()
    
    def _adaptive_crossover(self, model1: nn.Module, model2: nn.Module) -> nn.Module:
        """Crossover adaptativo entre modelos"""
        try:
            state1 = model1.state_dict()
            state2 = model2.state_dict()
            
            new_model = type(model1)()
            
            for name, param in new_model.named_parameters():
                if name in state1 and name in state2:
                    # Crossover baseado em fitness
                    if random.random() < 0.6:  # Preferir melhor modelo
                        new_model._parameters[name] = nn.Parameter(state1[name].clone())
                    else:
                        new_model._parameters[name] = nn.Parameter(state2[name].clone())
                elif name in state1:
                    new_model._parameters[name] = nn.Parameter(state1[name].clone())
                elif name in state2:
                    new_model._parameters[name] = nn.Parameter(state2[name].clone())
            
            return new_model
            
        except Exception as e:
            logger.error(f"Erro no crossover adaptativo: {e}")
            return model1
    
    def _adaptive_mutation(self, model: nn.Module, strategy: Dict) -> nn.Module:
        """Mutação adaptativa baseada em estratégia"""
        try:
            mutated_model = type(model)()
            
            for name, param in model.named_parameters():
                if random.random() < strategy['mutation_rate']:
                    # Mutação adaptativa
                    mutation_strength = 0.01 * (1 + strategy['exploration_focus'])
                    noise = torch.randn_like(param) * mutation_strength
                    mutated_model._parameters[name] = nn.Parameter(param + noise)
                else:
                    mutated_model._parameters[name] = nn.Parameter(param.clone())
            
            return mutated_model
            
        except Exception as e:
            logger.error(f"Erro na mutação adaptativa: {e}")
            return model
    
    def _record_biomimetic_evolution(self, generation: int, strategy: Dict):
        """Registra evolução biomimética"""
        evolution_data = {
            'generation': generation,
            'best_fitness': self.best_fitness,
            'population_size': len(self.population),
            'timestamp': datetime.now().isoformat(),
            'strategy_used': strategy,
            'meta_learning_score': np.mean([ind['meta_learning_score'] for ind in self.population])
        }
        
        self.evolution_history.append(evolution_data)
    
    def get_best_individual(self) -> Optional[Dict]:
        """Retorna melhor indivíduo"""
        if not self.population:
            return None
        
        return max(self.population, key=lambda x: x['fitness'])
    
    def save_biomimetic_state(self, filename: str = None):
        """Salva estado biomimético"""
        if filename is None:
            filename = f"biomimetic_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        state = {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'evolution_history': self.evolution_history,
            'population_size': len(self.population),
            'meta_learning_history': self.meta_learning.learning_history,
            'knowledge_base_size': len(self.meta_learning.knowledge_base),
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Estado biomimético salvo em: {filename}")
        return filename

def main():
    """Teste do sistema biomimético com metalearning"""
    print("🧬 SISTEMA DE EVOLUÇÃO ROBUSTO COM METALEARNING")
    print("=" * 60)
    
    # Criar IA biomimética
    ai = BiomimeticEvolutionaryAI()
    
    # Inicializar população
    print("🔄 Inicializando população biomimética...")
    ai.initialize_population()
    
    # Executar evolução com metalearning
    print("🚀 Executando evolução biomimética...")
    start_time = time.time()
    
    ai.evolve_with_metalearning(generations=3)
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Resultados
    print("\n📊 RESULTADOS BIOMIMÉTICOS:")
    print("=" * 40)
    
    best_individual = ai.get_best_individual()
    if best_individual:
        print(f"🏆 Melhor indivíduo: {best_individual['id']}")
        print(f"🎯 Fitness: {best_individual['fitness']:.4f}")
        print(f"🧠 Meta-learning score: {best_individual['meta_learning_score']:.4f}")
    
    print(f"📊 Melhor fitness global: {ai.best_fitness:.4f}")
    print(f"🔄 Gerações completadas: {ai.generation}")
    print(f"👥 Tamanho da população: {len(ai.population)}")
    print(f"⏱️  Tempo de execução: {execution_time:.2f}s")
    
    # Metalearning stats
    print(f"\n🧠 METALEARNING:")
    print(f"   • Padrões aprendidos: {len(ai.meta_learning.knowledge_base)}")
    print(f"   • Histórico de aprendizado: {len(ai.meta_learning.learning_history)}")
    
    # Salvar estado
    state_file = ai.save_biomimetic_state()
    print(f"💾 Estado salvo em: {state_file}")
    
    print("\n🎉 Sistema biomimético com metalearning executado com sucesso!")
    print("✅ Evolução robusta e adaptativa implementada!")

if __name__ == "__main__":
    main() 
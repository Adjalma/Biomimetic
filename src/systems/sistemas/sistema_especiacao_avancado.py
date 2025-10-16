#!/usr/bin/env python3
"""
SISTEMA DE ESPECIAÇÃO AVANÇADO
==============================
Implementa a técnica de especiação do NEAT para simular populações maiores
com recursos limitados, melhorando a diversidade genética e evitando
convergência prematura.
"""

import os
import sys
import json
import time
import logging
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SpeciationSystem:
    """Sistema de especiação para melhorar diversidade genética"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'compatibility_threshold': 3.0,  # Distância para considerar compatível
            'species_target': 5,  # Número ideal de espécies
            'elite_size': 2,  # Indivíduos elite por espécie
            'stagnation_limit': 15,  # Gerações sem melhoria
            'crossover_rate': 0.75,
            'mutation_rate': 0.1,
            'population_size': 25
        }
        
        self.species = {}  # {species_id: [individuals]}
        self.species_history = []
        self.generation = 0
        self.stagnation_counter = {}
        
        logger.info("✅ Sistema de especiação inicializado")
    
    def calculate_genetic_distance(self, individual1: Dict, individual2: Dict) -> float:
        """Calcula distância genética entre dois indivíduos"""
        try:
            distance = 0.0
            
            # Distância estrutural (camadas)
            layers1 = individual1.get('layers', [])
            layers2 = individual2.get('layers', [])
            
            # Comparar número de camadas
            layer_diff = abs(len(layers1) - len(layers2))
            distance += layer_diff * 2.0
            
            # Comparar camadas comuns
            min_layers = min(len(layers1), len(layers2))
            for i in range(min_layers):
                layer1 = layers1[i]
                layer2 = layers2[i]
                
                # Comparar unidades
                units1 = layer1.get('units', 0)
                units2 = layer2.get('units', 0)
                distance += abs(units1 - units2) / 100.0
                
                # Comparar tipo de ativação
                if layer1.get('activation') != layer2.get('activation'):
                    distance += 1.0
            
            # Distância de conexões
            connections1 = individual1.get('connections', [])
            connections2 = individual2.get('connections', [])
            
            # Comparar número de conexões
            conn_diff = abs(len(connections1) - len(connections2))
            distance += conn_diff * 0.5
            
            # Comparar conexões comuns
            common_connections = set(connections1) & set(connections2)
            total_connections = set(connections1) | set(connections2)
            if total_connections:
                connection_similarity = len(common_connections) / len(total_connections)
                distance += (1.0 - connection_similarity) * 2.0
            
            # Distância de hiperparâmetros
            hyper1 = individual1.get('hyperparameters', {})
            hyper2 = individual2.get('hyperparameters', {})
            
            for key in set(hyper1.keys()) | set(hyper2.keys()):
                val1 = hyper1.get(key, 0)
                val2 = hyper2.get(key, 0)
                if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
                    distance += abs(val1 - val2) * 0.1
            
            return distance
            
        except Exception as e:
            logger.warning(f"Erro ao calcular distância genética: {e}")
            return 10.0  # Distância alta em caso de erro
    
    def assign_to_species(self, individuals: List[Dict]) -> Dict[str, List[Dict]]:
        """Atribui indivíduos a espécies baseado na distância genética"""
        species = {}
        species_representatives = []
        
        for individual in individuals:
            assigned = False
            
            # Tentar atribuir a uma espécie existente
            for species_id, representative in species_representatives:
                distance = self.calculate_genetic_distance(individual, representative)
                
                if distance <= self.config['compatibility_threshold']:
                    if species_id not in species:
                        species[species_id] = []
                    species[species_id].append(individual)
                    assigned = True
                    break
            
            # Criar nova espécie se não foi atribuído
            if not assigned:
                species_id = f"species_{len(species_representatives)}"
                species[species_id] = [individual]
                species_representatives.append((species_id, individual))
        
        return species
    
    def adjust_compatibility_threshold(self):
        """Ajusta threshold de compatibilidade para manter número ideal de espécies"""
        current_species = len(self.species)
        target_species = self.config['species_target']
        
        if current_species < target_species:
            # Muitas espécies, aumentar threshold
            self.config['compatibility_threshold'] *= 1.1
            logger.info(f"🔧 Aumentando threshold para {self.config['compatibility_threshold']:.2f}")
        elif current_species > target_species * 1.5:
            # Poucas espécies, diminuir threshold
            self.config['compatibility_threshold'] *= 0.9
            logger.info(f"🔧 Diminuindo threshold para {self.config['compatibility_threshold']:.2f}")
    
    def select_parents(self, species_id: str, individuals: List[Dict]) -> Tuple[Dict, Dict]:
        """Seleciona pais dentro de uma espécie usando torneio"""
        if len(individuals) < 2:
            # Se só há um indivíduo, clonar
            return individuals[0], individuals[0]
        
        # Torneio para seleção
        tournament_size = min(3, len(individuals))
        
        # Selecionar primeiro pai
        tournament1 = np.random.choice(individuals, tournament_size, replace=False)
        parent1 = max(tournament1, key=lambda x: x.get('fitness_score', 0))
        
        # Selecionar segundo pai
        tournament2 = np.random.choice(individuals, tournament_size, replace=False)
        parent2 = max(tournament2, key=lambda x: x.get('fitness_score', 0))
        
        return parent1, parent2
    
    def crossover(self, parent1: Dict, parent2: Dict) -> Dict:
        
        """Realiza crossover entre dois pais"""
        child = {
            'layers': [],
            'connections': [],
            'hyperparameters': {},
            'parent_id': f"{parent1.get('id', 'p1')}_{parent2.get('id', 'p2')}",
            'generation': self.generation + 1
        }
        
        # Crossover de camadas
        layers1 = parent1.get('layers', [])
        layers2 = parent2.get('layers', [])
        
        max_layers = max(len(layers1), len(layers2))
        for i in range(max_layers):
            if i < len(layers1) and i < len(layers2):
                # Crossover uniforme
                if np.random.random() < 0.5:
                    child['layers'].append(layers1[i].copy())
                else:
                    child['layers'].append(layers2[i].copy())
            elif i < len(layers1):
                child['layers'].append(layers1[i].copy())
            else:
                child['layers'].append(layers2[i].copy())
        
        # Crossover de conexões
        connections1 = parent1.get('connections', [])
        connections2 = parent2.get('connections', [])
        
        # Unir conexões únicas
        all_connections = list(set(connections1 + connections2))
        if all_connections:
            num_connections = min(len(all_connections), max(len(connections1), len(connections2)))
            child['connections'] = np.random.choice(all_connections, num_connections, replace=False).tolist()
        
        # Crossover de hiperparâmetros
        hyper1 = parent1.get('hyperparameters', {})
        hyper2 = parent2.get('hyperparameters', {})
        
        for key in set(hyper1.keys()) | set(hyper2.keys()):
            if key in hyper1 and key in hyper2:
                # Média ponderada
                child['hyperparameters'][key] = (hyper1[key] + hyper2[key]) / 2
            elif key in hyper1:
                child['hyperparameters'][key] = hyper1[key]
            else:
                child['hyperparameters'][key] = hyper2[key]
        
        return child
    
    def mutate(self, individual: Dict) -> Dict:
        """Aplica mutação em um indivíduo"""
        mutated = individual.copy()
        
        # Mutação estrutural
        if np.random.random() < self.config['mutation_rate']:
            layers = mutated.get('layers', [])
            if layers:
                # Mutar camada aleatória
                layer_idx = np.random.randint(0, len(layers))
                layer = layers[layer_idx]
                
                if 'units' in layer:
                    # Mutar número de unidades
                    layer['units'] = max(1, layer['units'] + np.random.randint(-10, 11))
                
                if 'activation' in layer:
                    # Mutar função de ativação
                    activations = ['relu', 'tanh', 'sigmoid', 'leaky_relu']
                    layer['activation'] = np.random.choice(activations)
        
        # Mutação de conexões
        if np.random.random() < self.config['mutation_rate']:
            connections = mutated.get('connections', [])
            if connections:
                # Adicionar ou remover conexão
                if np.random.random() < 0.5 and len(connections) > 0:
                    # Remover conexão
                    connections.pop(np.random.randint(0, len(connections)))
                else:
                    # Adicionar conexão
                    max_layer = len(mutated.get('layers', [])) - 1
                    if max_layer > 0:
                        from_layer = np.random.randint(0, max_layer)
                        to_layer = np.random.randint(from_layer + 1, max_layer + 1)
                        new_connection = (from_layer, to_layer)
                        if new_connection not in connections:
                            connections.append(new_connection)
        
        # Mutação de hiperparâmetros
        if np.random.random() < self.config['mutation_rate']:
            hyperparams = mutated.get('hyperparameters', {})
            if 'learning_rate' in hyperparams:
                hyperparams['learning_rate'] *= np.random.uniform(0.5, 2.0)
            if 'dropout' in hyperparams:
                hyperparams['dropout'] = np.random.uniform(0.1, 0.5)
        
        return mutated
    
    def evolve_species(self, individuals: List[Dict]) -> List[Dict]:
        """Evolui população usando especiação"""
        logger.info(f"🔄 Evoluindo população com especiação (geração {self.generation})")
        
        # Atribuir indivíduos a espécies
        self.species = self.assign_to_species(individuals)
        logger.info(f"📊 {len(self.species)} espécies identificadas")
        
        # Mostrar distribuição das espécies
        for species_id, species_individuals in self.species.items():
            best_fitness = max(ind.get('fitness_score', 0) for ind in species_individuals)
            logger.info(f"   🧬 {species_id}: {len(species_individuals)} indivíduos, melhor fitness: {best_fitness:.4f}")
        
        # Ajustar threshold de compatibilidade
        self.adjust_compatibility_threshold()
        
        # Evoluir cada espécie
        new_population = []
        
        for species_id, species_individuals in self.species.items():
            if len(species_individuals) < 2:
                # Espécie muito pequena, manter indivíduos
                new_population.extend(species_individuals)
                continue
            
            # Ordenar por fitness
            species_individuals.sort(key=lambda x: x.get('fitness_score', 0), reverse=True)
            
            # Manter elite
            elite_size = min(self.config['elite_size'], len(species_individuals))
            new_population.extend(species_individuals[:elite_size])
            
            # Gerar descendentes
            offspring_needed = len(species_individuals) - elite_size
            
            for _ in range(offspring_needed):
                # Selecionar pais
                parent1, parent2 = self.select_parents(species_id, species_individuals)
                
                # Crossover
                if np.random.random() < self.config['crossover_rate']:
                    child = self.crossover(parent1, parent2)
                else:
                    child = parent1.copy()
                
                # Mutação
                child = self.mutate(child)
                
                # Adicionar à nova população
                new_population.append(child)
        
        # Garantir tamanho da população
        while len(new_population) < self.config['population_size']:
            # Clonar melhor indivíduo
            best_individual = max(new_population, key=lambda x: x.get('fitness_score', 0))
            new_population.append(best_individual.copy())
        
        # Limitar tamanho da população
        if len(new_population) > self.config['population_size']:
            new_population = new_population[:self.config['population_size']]
        
        self.generation += 1
        
        # Registrar estatísticas
        self.species_history.append({
            'generation': self.generation,
            'num_species': len(self.species),
            'species_sizes': {k: len(v) for k, v in self.species.items()},
            'compatibility_threshold': self.config['compatibility_threshold']
        })
        
        logger.info(f"✅ Evolução concluída: {len(new_population)} indivíduos em {len(self.species)} espécies")
        
        return new_population
    
    def get_species_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas das espécies"""
        stats = {
            'generation': self.generation,
            'num_species': len(self.species),
            'total_individuals': sum(len(indivs) for indivs in self.species.values()),
            'species_distribution': {},
            'compatibility_threshold': self.config['compatibility_threshold']
        }
        
        for species_id, individuals in self.species.items():
            if individuals:
                best_fitness = max(ind.get('fitness_score', 0) for ind in individuals)
                avg_fitness = np.mean([ind.get('fitness_score', 0) for ind in individuals])
                
                stats['species_distribution'][species_id] = {
                    'size': len(individuals),
                    'best_fitness': best_fitness,
                    'avg_fitness': avg_fitness
                }
        
        return stats

class AdvancedEvolutionarySystem:
    """Sistema evolutivo avançado com especiação"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {
            'population_size': 25,
            'generations': 100,
            'knowledge_integration': True,
            'real_time_monitoring': True
        }
        
        self.speciation_system = SpeciationSystem()
        self.population = []
        self.knowledge_base = []
        self.evolution_history = []
        self.generation = 0
        
        logger.info("✅ Sistema evolutivo avançado inicializado")
    
    def load_knowledge(self):
        """Carrega conhecimento existente"""
        logger.info("📚 Carregando conhecimento existente...")
        
        knowledge_files = []
        for file in os.listdir('.'):
            if file.startswith('emergency_knowledge_') and file.endswith('.json'):
                knowledge_files.append(file)
        
        total_knowledge = 0
        for file in knowledge_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        self.knowledge_base.extend(data)
                        total_knowledge += len(data)
                    elif isinstance(data, dict):
                        if 'knowledge' in data:
                            self.knowledge_base.extend(data['knowledge'])
                            total_knowledge += len(data['knowledge'])
            except Exception as e:
                logger.warning(f"Erro ao carregar {file}: {e}")
        
        logger.info(f"✅ {total_knowledge:,} itens de conhecimento carregados")
        return total_knowledge
    
    def initialize_population(self):
        """Inicializa população com indivíduos diversos"""
        logger.info(f"🧬 Inicializando população com {self.config['population_size']} indivíduos...")
        
        self.population = []
        
        for i in range(self.config['population_size']):
            # Criar indivíduo diverso
            individual = self._create_diverse_individual(i)
            self.population.append(individual)
        
        logger.info("✅ População inicializada")
    
    def _create_diverse_individual(self, index: int) -> Dict:
        """Cria indivíduo com arquitetura diversa"""
        # Variação baseada no índice para garantir diversidade
        num_layers = 2 + (index % 4)  # 2-5 camadas
        
        layers = []
        for layer_idx in range(num_layers):
            layer = {
                'type': ['dense', 'conv', 'lstm', 'attention'][layer_idx % 4],
                'units': 32 + (layer_idx * 64) + (index * 16),
                'activation': ['relu', 'tanh', 'sigmoid', 'leaky_relu'][layer_idx % 4]
            }
            layers.append(layer)
        
        # Conexões variadas
        connections = []
        for i in range(num_layers - 1):
            if index % 2 == 0:  # Alguns indivíduos têm conexões skip
                connections.append((i, i + 1))
                if i > 0 and index % 3 == 0:
                    connections.append((i - 1, i + 1))
        
        # Hiperparâmetros variados
        hyperparameters = {
            'learning_rate': 0.001 * (1 + index * 0.1),
            'dropout': 0.1 + (index * 0.05) % 0.4
        }
        
        individual = {
            'id': f"ind_{index}_{int(time.time())}",
            'layers': layers,
            'connections': connections,
            'hyperparameters': hyperparameters,
            'fitness_score': 0.0,
            'generation': 0,
            'species_id': None
        }
        
        return individual
    
    def evaluate_fitness(self, individual: Dict) -> float:
        """Avalia fitness de um indivíduo"""
        try:
            # Simular avaliação baseada na arquitetura
            base_score = 0.3
            
            # Score baseado no número de camadas (não muito simples, não muito complexo)
            num_layers = len(individual.get('layers', []))
            if 2 <= num_layers <= 6:
                base_score += 0.2
            elif num_layers > 6:
                base_score -= 0.1
            
            # Score baseado na diversidade de tipos de camadas
            layer_types = [layer.get('type', '') for layer in individual.get('layers', [])]
            unique_types = len(set(layer_types))
            base_score += unique_types * 0.05
            
            # Score baseado nos hiperparâmetros
            hyperparams = individual.get('hyperparameters', {})
            if 'learning_rate' in hyperparams:
                lr = hyperparams['learning_rate']
                if 0.0001 <= lr <= 0.01:
                    base_score += 0.1
            
            # Score baseado no conhecimento (se disponível)
            if self.knowledge_base and len(self.knowledge_base) > 0:
                # Simular que indivíduos mais complexos podem processar mais conhecimento
                knowledge_bonus = min(0.2, len(self.knowledge_base) / 100000)
                base_score += knowledge_bonus
            
            # Adicionar variação aleatória para simular diferentes performances
            random_factor = np.random.normal(0, 0.05)
            final_score = max(0.0, min(1.0, base_score + random_factor))
            
            individual['fitness_score'] = final_score
            return final_score
            
        except Exception as e:
            logger.warning(f"Erro na avaliação de fitness: {e}")
            return 0.1
    
    def evolve_generation(self):
        """Evolui uma geração completa"""
        logger.info(f"🔄 Evoluindo geração {self.generation}")
        
        # Avaliar população atual
        for individual in self.population:
            self.evaluate_fitness(individual)
        
        # Estatísticas da geração atual
        fitness_scores = [ind.get('fitness_score', 0) for ind in self.population]
        best_fitness = max(fitness_scores)
        avg_fitness = np.mean(fitness_scores)
        
        logger.info(f"📊 Geração {self.generation}: Melhor={best_fitness:.4f}, Média={avg_fitness:.4f}")
        
        # Evoluir usando especiação
        self.population = self.speciation_system.evolve_species(self.population)
        
        # Registrar história
        evolution_data = {
            'generation': self.generation,
            'best_fitness': best_fitness,
            'avg_fitness': avg_fitness,
            'population_size': len(self.population),
            'species_stats': self.speciation_system.get_species_stats(),
            'timestamp': datetime.now().isoformat()
        }
        
        self.evolution_history.append(evolution_data)
        
        self.generation += 1
    
    def save_state(self):
        """Salva estado do sistema"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        state = {
            'system_info': {
                'name': 'Advanced Evolutionary System with Speciation',
                'version': '2.0.0',
                'timestamp': datetime.now().isoformat()
            },
            'config': self.config,
            'generation': self.generation,
            'population': self.population,
            'evolution_history': self.evolution_history,
            'species_stats': self.speciation_system.get_species_stats(),
            'knowledge_count': len(self.knowledge_base)
        }
        
        filename = f"advanced_evolution_state_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
            logger.info(f"💾 Estado salvo em: {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Erro ao salvar estado: {e}")
            return None
    
    def run_evolution(self, generations: int = 10):
        """Executa evolução por várias gerações"""
        logger.info(f"🚀 Iniciando evolução por {generations} gerações")
        
        # Carregar conhecimento
        self.load_knowledge()
        
        # Inicializar população
        self.initialize_population()
        
        # Executar evolução
        for gen in range(generations):
            try:
                self.evolve_generation()
                
                # Salvar estado periodicamente
                if gen % 5 == 0:
                    self.save_state()
                
                # Pausa entre gerações
                time.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Evolução interrompida pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro na geração {gen}: {e}")
                continue
        
        # Salvar estado final
        self.save_state()
        
        logger.info("✅ Evolução concluída!")

def main():
    """Função principal"""
    print("🧬 SISTEMA DE ESPECIAÇÃO AVANÇADO")
    print("=" * 50)
    
    # Configuração
    config = {
        'population_size': 25,
        'generations': 20,
        'knowledge_integration': True,
        'real_time_monitoring': True
    }
    
    # Criar sistema
    system = AdvancedEvolutionarySystem(config)
    
    # Executar evolução
    system.run_evolution(generations=config['generations'])
    
    print("\n🎉 Sistema de especiação concluído!")
    print("📊 Verifique os arquivos de estado gerados")

if __name__ == "__main__":
    main() 
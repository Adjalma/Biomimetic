#!/usr/bin/env python3
"""
SISTEMA DE INTEGRAÇÃO COMPLETA
=============================
Integra todos os componentes do sistema IA evolutiva
"""

import os
import sys
import json
import time
import logging
import subprocess
import threading
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntegratedSystem:
    """Sistema integrado completo"""
    
    def __init__(self):
        self.knowledge_base = []
        self.population_size = 25
        self.generation = 0
        self.evolution_history = []
        self.species_count = 0
        self.best_fitness = 0.0
        self.avg_fitness = 0.0
        
    def load_knowledge(self):
        """Carrega conhecimento consolidado"""
        logger.info("📚 Carregando conhecimento consolidado...")
        
        # Procurar arquivo consolidado
        consolidated_files = [f for f in os.listdir('.') if f.startswith('consolidated_knowledge_')]
        
        if consolidated_files:
            latest_file = max(consolidated_files)
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    self.knowledge_base = json.load(f)
                logger.info(f"✅ {len(self.knowledge_base):,} itens de conhecimento carregados")
                return len(self.knowledge_base)
            except Exception as e:
                logger.error(f"❌ Erro ao carregar conhecimento: {e}")
        
        return 0
    
    def initialize_population(self):
        """Inicializa população com especiação"""
        logger.info(f"🧬 Inicializando população com {self.population_size} indivíduos...")
        
        # Criar indivíduos diversos
        population = []
        for i in range(self.population_size):
            individual = {
                'id': f"ind_{i}_{int(time.time())}",
                'layers': [
                    {'type': 'dense', 'units': 64 + i * 16, 'activation': 'relu'},
                    {'type': 'dense', 'units': 32 + i * 8, 'activation': 'tanh'}
                ],
                'connections': [(0, 1)],
                'hyperparameters': {
                    'learning_rate': 0.001 * (1 + i * 0.1),
                    'dropout': 0.1 + (i * 0.02) % 0.3
                },
                'fitness_score': 0.0,
                'generation': 0,
                'species_id': f"species_{i % 5}"  # 5 espécies iniciais
            }
            population.append(individual)
        
        self.population = population
        self.species_count = 5
        logger.info("✅ População inicializada com especiação")
    
    def evaluate_fitness(self, individual):
        """Avalia fitness baseado no conhecimento"""
        try:
            base_score = 0.3
            
            # Score baseado na arquitetura
            num_layers = len(individual.get('layers', []))
            if 2 <= num_layers <= 6:
                base_score += 0.2
            
            # Score baseado no conhecimento
            if self.knowledge_base:
                knowledge_factor = min(0.3, len(self.knowledge_base) / 100000)
                base_score += knowledge_factor
            
            # Score baseado na espécie
            species_id = individual.get('species_id', 'unknown')
            species_bonus = hash(species_id) % 100 / 1000  # Pequena variação por espécie
            base_score += species_bonus
            
            # Variação aleatória
            random_factor = (hash(str(individual['id'])) % 100) / 1000
            final_score = max(0.0, min(1.0, base_score + random_factor))
            
            individual['fitness_score'] = final_score
            return final_score
            
        except Exception as e:
            logger.warning(f"Erro na avaliação: {e}")
            return 0.1
    
    def evolve_generation(self):
        """Evolui uma geração"""
        logger.info(f"🔄 Evoluindo geração {self.generation}")
        
        # Avaliar população
        for individual in self.population:
            self.evaluate_fitness(individual)
        
        # Calcular estatísticas
        fitness_scores = [ind.get('fitness_score', 0) for ind in self.population]
        self.best_fitness = max(fitness_scores)
        self.avg_fitness = sum(fitness_scores) / len(fitness_scores)
        
        # Simular evolução com especiação
        new_population = []
        
        # Manter elite (20% melhores)
        elite_size = max(1, self.population_size // 5)
        elite = sorted(self.population, key=lambda x: x.get('fitness_score', 0), reverse=True)[:elite_size]
        new_population.extend(elite)
        
        # Gerar descendentes
        while len(new_population) < self.population_size:
            # Seleção por torneio
            parent1 = max(np.random.choice(self.population, 3), key=lambda x: x.get('fitness_score', 0))
            parent2 = max(np.random.choice(self.population, 3), key=lambda x: x.get('fitness_score', 0))
            
            # Crossover
            child = {
                'id': f"child_{len(new_population)}_{int(time.time())}",
                'layers': parent1.get('layers', []).copy(),
                'connections': parent1.get('connections', []).copy(),
                'hyperparameters': parent1.get('hyperparameters', {}).copy(),
                'fitness_score': 0.0,
                'generation': self.generation + 1,
                'species_id': parent1.get('species_id', 'unknown')
            }
            
            # Mutação
            if np.random.random() < 0.1:
                if child['layers']:
                    layer_idx = np.random.randint(0, len(child['layers']))
                    child['layers'][layer_idx]['units'] = max(1, child['layers'][layer_idx]['units'] + np.random.randint(-10, 11))
            
            new_population.append(child)
        
        self.population = new_population[:self.population_size]
        self.generation += 1
        
        # Registrar história
        evolution_data = {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'avg_fitness': self.avg_fitness,
            'population_size': len(self.population),
            'species_count': self.species_count,
            'knowledge_count': len(self.knowledge_base),
            'timestamp': datetime.now().isoformat()
        }
        
        self.evolution_history.append(evolution_data)
        
        logger.info(f"✅ Geração {self.generation}: Melhor={self.best_fitness:.4f}, Média={self.avg_fitness:.4f}")
    
    def save_state(self):
        """Salva estado do sistema"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        state = {
            'system_info': {
                'name': 'Integrated Evolutionary System',
                'version': '2.0.0',
                'timestamp': datetime.now().isoformat()
            },
            'generation': self.generation,
            'population': self.population,
            'evolution_history': self.evolution_history,
            'knowledge_count': len(self.knowledge_base),
            'species_count': self.species_count,
            'best_fitness': self.best_fitness,
            'avg_fitness': self.avg_fitness
        }
        
        filename = f"integrated_system_state_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
            logger.info(f"💾 Estado salvo em: {filename}")
            return filename
        except Exception as e:
            logger.error(f"❌ Erro ao salvar estado: {e}")
            return None
    
    def run_continuous_evolution(self):
        """Executa evolução contínua"""
        logger.info("🚀 Iniciando evolução contínua...")
        
        # Carregar conhecimento
        knowledge_count = self.load_knowledge()
        
        # Inicializar população
        self.initialize_population()
        
        # Loop de evolução
        generation_count = 0
        while True:
            try:
                self.evolve_generation()
                generation_count += 1
                
                # Salvar estado periodicamente
                if generation_count % 5 == 0:
                    self.save_state()
                
                # Pausa entre gerações
                time.sleep(2)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Evolução interrompida pelo usuário")
                break
            except Exception as e:
                logger.error(f"❌ Erro na geração {generation_count}: {e}")
                time.sleep(5)
                continue
        
        # Salvar estado final
        self.save_state()
        logger.info("✅ Evolução concluída!")

def main():
    """Função principal"""
    print("🧬 SISTEMA INTEGRADO DE IA EVOLUTIVA")
    print("=" * 50)
    
    # Criar sistema
    system = IntegratedSystem()
    
    # Executar evolução contínua
    system.run_continuous_evolution()

if __name__ == "__main__":
    import numpy as np
    main()

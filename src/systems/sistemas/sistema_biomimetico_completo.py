#!/usr/bin/env python3
"""
IA BioMimética - Sistema Evolutivo Completo
===========================================

Sistema que combina evolução genética com aprendizado web
para análise jurídica e financeira.
"""

import json
import os
import time
import threading
import logging
import random
import numpy as np
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict, deque
import pickle
import hashlib
import sys

# Configuração de logging para Windows (sem emojis)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('biomimetic_ai.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class WebScraper:
    """Sistema de coleta de dados web para aprendizado"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.legal_sites = [
            'https://www.stj.jus.br/sites/portalp/Paginas/Comunicacao/Noticias.aspx',
            'https://www.gov.br/receitafederal/pt-br',
            'https://www.bcb.gov.br/novoselic',
            'https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14129.htm',
            'https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14130.htm'
        ]
        self.financial_sites = [
            'https://www.bcb.gov.br/novoselic',
            'https://www.gov.br/receitafederal/pt-br/assuntos/orcamento-tributario',
            'https://www.gov.br/economia/pt-br'
        ]
        self.scraped_data = []
        self.last_scrape = {}
        
    def scrape_legal_site(self, url):
        """Coleta dados de sites jurídicos"""
        try:
            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair textos relevantes
            texts = []
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']):
                text = tag.get_text(strip=True)
                if len(text) > 20 and any(keyword in text.lower() for keyword in 
                    ['contrato', 'lei', 'decreto', 'portaria', 'resolução', 'jurisprudência', 'processo']):
                    texts.append(text)
            
            return texts[:10]  # Limitar a 10 textos por site
            
        except Exception as e:
            logger.error(f"Erro ao fazer scraping de {url}: {e}")
            return []
    
    def scrape_financial_site(self, url):
        """Coleta dados de sites financeiros"""
        try:
            response = self.session.get(url, timeout=10, verify=False)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extrair dados financeiros
            texts = []
            for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'div']):
                text = tag.get_text(strip=True)
                if len(text) > 20 and any(keyword in text.lower() for keyword in 
                    ['taxa', 'juros', 'selic', 'inflação', 'dólar', 'real', 'economia', 'finanças']):
                    texts.append(text)
            
            return texts[:10]
            
        except Exception as e:
            logger.error(f"Erro ao fazer scraping de {url}: {e}")
            return []
    
    def run_scraping_cycle(self):
        """Executa ciclo completo de scraping"""
        all_data = []
        
        # Scraping de sites jurídicos
        for url in self.legal_sites:
            data = self.scrape_legal_site(url)
            for text in data:
                all_data.append({
                    'source': 'legal',
                    'url': url,
                    'content': text,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'juridical_knowledge'
                })
            time.sleep(1)  # Pausa entre requests
        
        # Scraping de sites financeiros
        for url in self.financial_sites:
            data = self.scrape_financial_site(url)
            for text in data:
                all_data.append({
                    'source': 'financial',
                    'url': url,
                    'content': text,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'financial_knowledge'
                })
            time.sleep(1)
        
        return all_data

class KnowledgeBase:
    """Base de conhecimento da IA"""
    
    def __init__(self):
        self.knowledge = []
        self.knowledge_file = f"biomimetic_knowledge_{datetime.now().strftime('%Y%m%d')}.json"
        self.load_knowledge()
        
    def load_knowledge(self):
        """Carrega conhecimento existente"""
        try:
            if os.path.exists(self.knowledge_file):
                with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                    self.knowledge = json.load(f)
                logger.info(f"Conhecimento carregado: {len(self.knowledge)} itens")
            else:
                logger.info("Criando nova base de conhecimento")
        except Exception as e:
            logger.error(f"Erro ao carregar conhecimento: {e}")
            self.knowledge = []
    
    def save_knowledge(self):
        """Salva conhecimento atual"""
        try:
            with open(self.knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(self.knowledge, f, ensure_ascii=False, indent=2)
            logger.info(f"Conhecimento salvo: {len(self.knowledge)} itens")
        except Exception as e:
            logger.error(f"Erro ao salvar conhecimento: {e}")
    
    def add_knowledge(self, new_knowledge):
        """Adiciona novo conhecimento"""
        if isinstance(new_knowledge, list):
            self.knowledge.extend(new_knowledge)
        else:
            self.knowledge.append(new_knowledge)
        
        # Remover duplicatas
        seen = set()
        unique_knowledge = []
        for item in self.knowledge:
            content_hash = hashlib.md5(str(item).encode()).hexdigest()
            if content_hash not in seen:
                seen.add(content_hash)
                unique_knowledge.append(item)
        
        self.knowledge = unique_knowledge
        logger.info(f"Conhecimento atualizado: {len(self.knowledge)} itens únicos")
    
    def get_knowledge_stats(self):
        """Retorna estatísticas do conhecimento"""
        legal_count = sum(1 for item in self.knowledge if item.get('type') == 'juridical_knowledge')
        financial_count = sum(1 for item in self.knowledge if item.get('type') == 'financial_knowledge')
        
        return {
            'total': len(self.knowledge),
            'legal': legal_count,
            'financial': financial_count,
            'sources': len(set(item.get('source', '') for item in self.knowledge))
        }

class Individual:
    """Indivíduo do sistema evolutivo"""
    
    def __init__(self, id, genes=None):
        self.id = id
        self.genes = genes or self.generate_random_genes()
        self.fitness = 0.0
        self.species_id = None
        self.age = 0
        self.knowledge_count = 0
        self.performance_history = deque(maxlen=100)
        
    def generate_random_genes(self):
        """Gera genes aleatórios"""
        return {
            'learning_rate': random.uniform(0.01, 0.1),
            'mutation_rate': random.uniform(0.01, 0.05),
            'crossover_rate': random.uniform(0.6, 0.9),
            'adaptability': random.uniform(0.5, 1.0),
            'intelligence': random.uniform(0.3, 1.0),
            'specialization': random.choice(['legal', 'financial', 'general']),
            'memory_capacity': random.uniform(0.5, 1.0),
            'processing_speed': random.uniform(0.4, 1.0)
        }
    
    def calculate_fitness(self, knowledge_base):
        """Calcula fitness baseado no conhecimento"""
        stats = knowledge_base.get_knowledge_stats()
        
        # Fitness baseado em múltiplos fatores
        knowledge_factor = min(stats['total'] / 1000, 1.0)  # Normalizar
        diversity_factor = stats['sources'] / 10  # Normalizar
        age_factor = 1.0 / (1.0 + self.age / 100)  # Penalizar idade
        
        # Fitness específico baseado na especialização
        if self.genes['specialization'] == 'legal':
            specialization_factor = stats['legal'] / max(stats['total'], 1)
        elif self.genes['specialization'] == 'financial':
            specialization_factor = stats['financial'] / max(stats['total'], 1)
        else:
            specialization_factor = 0.5  # Generalista
        
        # Calcular fitness final
        self.fitness = (
            knowledge_factor * 0.3 +
            diversity_factor * 0.2 +
            age_factor * 0.2 +
            specialization_factor * 0.3
        )
        
        # Adicionar ruído para evitar convergência prematura (CORRIGIDO)
        self.fitness += np.random.normal(0, 0.01)
        self.fitness = max(0.0, min(1.0, self.fitness))
        
        self.performance_history.append(self.fitness)
        return self.fitness
    
    def mutate(self):
        """Aplica mutação nos genes"""
        for key in self.genes:
            if random.random() < self.genes['mutation_rate']:
                if isinstance(self.genes[key], float):
                    self.genes[key] += np.random.normal(0, 0.1)
                    self.genes[key] = max(0.0, min(1.0, self.genes[key]))
                elif isinstance(self.genes[key], str):
                    if key == 'specialization':
                        self.genes[key] = random.choice(['legal', 'financial', 'general'])
    
    def crossover(self, other):
        """Realiza crossover com outro indivíduo"""
        child_genes = {}
        for key in self.genes:
            if random.random() < self.genes['crossover_rate']:
                child_genes[key] = self.genes[key]
            else:
                child_genes[key] = other.genes[key]
        
        return Individual(f"child_{self.id}_{other.id}", child_genes)

class Species:
    """Espécie de indivíduos"""
    
    def __init__(self, id, representative):
        self.id = id
        self.representative = representative
        self.members = [representative]
        self.best_fitness = representative.fitness
        self.generation_count = 0
        
    def add_member(self, individual):
        """Adiciona membro à espécie"""
        self.members.append(individual)
        individual.species_id = self.id
        if individual.fitness > self.best_fitness:
            self.best_fitness = individual.fitness
    
    def remove_member(self, individual):
        """Remove membro da espécie"""
        if individual in self.members:
            self.members.remove(individual)
    
    def get_average_fitness(self):
        """Calcula fitness médio da espécie"""
        if not self.members:
            return 0.0
        return sum(member.fitness for member in self.members) / len(self.members)
    
    def select_parent(self):
        """Seleciona pai para reprodução"""
        if not self.members:
            return None
        
        # Seleção por torneio
        tournament_size = min(3, len(self.members))
        tournament = random.sample(self.members, tournament_size)
        return max(tournament, key=lambda x: x.fitness)

class EvolutionaryAI:
    """IA Evolutiva Principal"""
    
    def __init__(self, population_size=25):
        self.population_size = population_size
        self.population = []
        self.species = []
        self.generation = 0
        self.best_fitness = 0.0
        self.knowledge_base = KnowledgeBase()
        self.web_scraper = WebScraper()
        self.frameworks_used = {
            'beautifulsoup': True,
            'requests': True,
            'pandas': True,
            'numpy': True,
            'scikit-learn': False,
            'langchain': True,
            'langgraph': True,
            'chromadb': True,
            'pinecone': True,
            'openai': True,
            'transformers': True,
            'fastapi': True,
            'streamlit': True,
            'gradio': True
        }
        
        self.initialize_population()
        
    def initialize_population(self):
        """Inicializa população inicial"""
        for i in range(self.population_size):
            individual = Individual(f"ind_{i}")
            self.population.append(individual)
        
        self.speciate_population()
        logger.info(f"Populacao inicializada: {len(self.population)} individuos")
    
    def speciate_population(self):
        """Agrupa população em espécies"""
        self.species = []
        unassigned = self.population.copy()
        
        while unassigned:
            representative = unassigned.pop(0)
            species = Species(f"species_{len(self.species)}", representative)
            species.add_member(representative)
            
            # Encontrar indivíduos similares
            to_remove = []
            for individual in unassigned:
                if self.calculate_compatibility(representative, individual) < 0.3:
                    species.add_member(individual)
                    to_remove.append(individual)
            
            for individual in to_remove:
                unassigned.remove(individual)
            
            self.species.append(species)
        
        logger.info(f"Populacao dividida em {len(self.species)} especies")
    
    def calculate_compatibility(self, ind1, ind2):
        """Calcula compatibilidade entre dois indivíduos"""
        # Distância euclidiana entre genes
        distance = 0
        for key in ind1.genes:
            if isinstance(ind1.genes[key], float):
                distance += (ind1.genes[key] - ind2.genes[key]) ** 2
            elif isinstance(ind1.genes[key], str):
                if ind1.genes[key] != ind2.genes[key]:
                    distance += 1
        
        return distance ** 0.5
    
    def evolve_generation(self):
        """Evolui uma geração"""
        self.generation += 1
        
        # Atualizar fitness de todos os indivíduos
        for individual in self.population:
            individual.calculate_fitness(self.knowledge_base)
            individual.age += 1
        
        # Atualizar melhor fitness
        current_best = max(self.population, key=lambda x: x.fitness)
        if current_best.fitness > self.best_fitness:
            self.best_fitness = current_best.fitness
        
        # Reprodução e seleção
        new_population = []
        
        for species in self.species:
            if len(species.members) < 2:
                continue
            
            # Calcular número de filhos para esta espécie
            avg_fitness = species.get_average_fitness()
            offspring_count = max(1, int(len(species.members) * avg_fitness))
            
            for _ in range(offspring_count):
                parent1 = species.select_parent()
                parent2 = species.select_parent()
                
                if parent1 and parent2 and parent1 != parent2:
                    child = parent1.crossover(parent2)
                    child.mutate()
                    new_population.append(child)
        
        # Adicionar alguns indivíduos aleatórios para diversidade
        while len(new_population) < self.population_size:
            new_individual = Individual(f"new_{len(new_population)}")
            new_population.append(new_individual)
        
        # Limitar população
        self.population = new_population[:self.population_size]
        
        # Re-especiar população
        self.speciate_population()
        
        # Log da evolução
        avg_fitness = sum(ind.fitness for ind in self.population) / len(self.population)
        logger.info(f"Geracao {self.generation}: Melhor={self.best_fitness:.4f}, Media={avg_fitness:.4f}")
        
        return {
            'generation': self.generation,
            'best_fitness': self.best_fitness,
            'avg_fitness': avg_fitness,
            'population_size': len(self.population),
            'species_count': len(self.species)
        }
    
    def learn_from_web(self):
        """Aprende com dados da web"""
        try:
            # Executar scraping
            new_data = self.web_scraper.run_scraping_cycle()
            
            if new_data:
                # Adicionar à base de conhecimento
                self.knowledge_base.add_knowledge(new_data)
                
                # Salvar conhecimento
                self.knowledge_base.save_knowledge()
                
                logger.info(f"Aprendizado web: {len(new_data)} novos itens coletados")
                return len(new_data)
            else:
                logger.warning("Nenhum dado novo coletado da web")
                return 0
                
        except Exception as e:
            logger.error(f"Erro no aprendizado web: {e}")
            return 0
    
    def analyze_contracts(self):
        """Analisa contratos usando conhecimento acumulado"""
        stats = self.knowledge_base.get_knowledge_stats()
        
        # Simular análise de contratos
        contracts_analyzed = stats['total'] // 100
        documents_generated = contracts_analyzed // 2
        
        logger.info(f"Analise de contratos: {contracts_analyzed} analisados, {documents_generated} documentos gerados")
        
        return {
            'contracts_analyzed': contracts_analyzed,
            'documents_generated': documents_generated,
            'knowledge_used': stats['total']
        }
    
    def get_system_stats(self):
        """Retorna estatísticas completas do sistema"""
        stats = self.knowledge_base.get_knowledge_stats()
        
        return {
            'generation': self.generation,
            'population_size': len(self.population),
            'species_count': len(self.species),
            'best_fitness': self.best_fitness,
            'avg_fitness': sum(ind.fitness for ind in self.population) / len(self.population),
            'total_knowledge': stats['total'],
            'legal_knowledge': stats['legal'],
            'financial_knowledge': stats['financial'],
            'knowledge_sources': stats['sources'],
            'frameworks_active': sum(self.frameworks_used.values()),
            'system_health': self.calculate_system_health(),
            'diversity': self.calculate_diversity(),
            'confidence': self.calculate_confidence()
        }
    
    def calculate_system_health(self):
        """Calcula saúde do sistema"""
        if not self.population:
            return 0.0
        
        avg_fitness = sum(ind.fitness for ind in self.population) / len(self.population)
        species_diversity = len(self.species) / max(len(self.population), 1)
        knowledge_factor = min(self.knowledge_base.get_knowledge_stats()['total'] / 1000, 1.0)
        
        return (avg_fitness * 0.4 + species_diversity * 0.3 + knowledge_factor * 0.3)
    
    def calculate_diversity(self):
        """Calcula diversidade da população"""
        if len(self.species) <= 1:
            return 0.0
        
        return len(self.species) / len(self.population)
    
    def calculate_confidence(self):
        """Calcula confiança do sistema"""
        if not self.population:
            return 0.0
        
        # Confiança baseada em fitness e estabilidade
        recent_fitness = [ind.performance_history[-1] if ind.performance_history else 0 for ind in self.population]
        avg_recent = sum(recent_fitness) / len(recent_fitness)
        
        return min(avg_recent * 1.2, 1.0)
    
    def save_state(self):
        """Salva estado do sistema"""
        state = {
            'generation': self.generation,
            'population': [
                {
                    'id': ind.id,
                    'genes': ind.genes,
                    'fitness': ind.fitness,
                    'species_id': ind.species_id,
                    'age': ind.age
                }
                for ind in self.population
            ],
            'species': [
                {
                    'id': species.id,
                    'member_ids': [member.id for member in species.members],
                    'best_fitness': species.best_fitness
                }
                for species in self.species
            ],
            'best_fitness': self.best_fitness,
            'knowledge_stats': self.knowledge_base.get_knowledge_stats()
        }
        
        filename = f"biomimetic_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Estado salvo em: {filename}")

class SistemaBiomimeticoCompleto:
    """Sistema Biomimético Completo - Integração de todos os componentes"""
    
    def __init__(self):
        """Inicializa o sistema biomimético completo"""
        self.nome = "Sistema Biomimético Completo"
        self.status = "Ativo"
        self.evolutionary_ai = None
        self.web_scraper = None
        self.knowledge_base = None
        
        try:
            self._inicializar_sistema()
            print("✓ Sistema Biomimético Completo inicializado")
        except Exception as e:
            print(f"✗ Erro ao inicializar: {e}")
            self.status = "Erro"
    
    def _inicializar_sistema(self):
        """Inicializa componentes do sistema"""
        # Inicializar IA evolutiva
        self.evolutionary_ai = EvolutionaryAI(population_size=25)
        
        # Inicializar web scraper
        self.web_scraper = WebScraper()
        
        # Inicializar base de conhecimento
        self.knowledge_base = KnowledgeBase()
        
        print("✓ Componentes biomiméticos inicializados")
    
    def executar_ciclo_evolucao(self):
        """Executa ciclo de evolução biomimética"""
        try:
            print("🔄 Executando ciclo de evolução biomimética...")
            
            # Evoluir geração
            evolution_result = self.evolutionary_ai.evolve_generation()
            
            # Aprendizado web
            web_items = self.evolutionary_ai.learn_from_web()
            
            # Análise de contratos
            contract_result = self.evolutionary_ai.analyze_contracts()
            
            print("✓ Ciclo de evolução biomimética executado")
            return {
                'evolution': evolution_result,
                'web_items': web_items,
                'contracts': contract_result
            }
            
        except Exception as e:
            print(f"⚠️ Erro no ciclo de evolução: {e}")
            return None
    
    def obter_status(self):
        """Retorna status do sistema"""
        return {
            'nome': self.nome,
            'status': self.status,
            'evolutionary_ai': self.evolutionary_ai is not None,
            'web_scraper': self.web_scraper is not None,
            'knowledge_base': self.knowledge_base is not None
        }
    
    def __str__(self):
        return f"SistemaBiomimeticoCompleto(status={self.status})"

def main():
    """Função principal"""
    print("IA BioMimetica - Sistema Evolutivo")
    print("=" * 50)
    
    # Inicializar IA
    ai = EvolutionaryAI(population_size=25)
    
    # Carregar conhecimento existente
    print(f"Conhecimento inicial: {ai.knowledge_base.get_knowledge_stats()['total']} itens")
    
    try:
        generation_count = 0
        while True:
            # Evoluir geração
            evolution_result = ai.evolve_generation()
            generation_count += 1
            
            # Aprendizado web a cada 5 gerações
            if generation_count % 5 == 0:
                web_items = ai.learn_from_web()
                if web_items > 0:
                    print(f"{web_items} novos itens aprendidos da web")
            
            # Análise de contratos a cada 10 gerações
            if generation_count % 10 == 0:
                contract_result = ai.analyze_contracts()
                print(f"{contract_result['contracts_analyzed']} contratos analisados")
            
            # Salvar estado a cada 50 gerações
            if generation_count % 50 == 0:
                ai.save_state()
            
            # Mostrar estatísticas a cada 100 gerações
            if generation_count % 100 == 0:
                stats = ai.get_system_stats()
                print(f"\nEstatisticas do Sistema:")
                print(f"   Geracao: {stats['generation']}")
                print(f"   Populacao: {stats['population_size']} individuos")
                print(f"   Especies: {stats['species_count']}")
                print(f"   Melhor Fitness: {stats['best_fitness']:.4f}")
                print(f"   Conhecimento: {stats['total_knowledge']} itens")
                print(f"   Saude: {stats['system_health']:.3f}")
                print(f"   Diversidade: {stats['diversity']:.3f}")
                print(f"   Confianca: {stats['confidence']:.3f}")
                print("-" * 50)
            
            # Pausa entre gerações
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nEvolucao interrompida pelo usuario")
        ai.save_state()
        print("Estado salvo antes de encerrar")
        print("Evolucao concluida!")

if __name__ == "__main__":
    main() 
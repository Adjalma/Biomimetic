"""
Motor de Evolução - Implementa Meta-Learning de Custo e Curiosidade
Versão: 1.0.0
Insights: 2 (Custo de Inferência) e 3 (Curiosidade Intrínseca)
"""

import yaml
import json
import numpy as np
import random
import copy
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional
import logging
from pathlib import Path
import torch
import torch.nn as nn
import torch.optim as optim

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelemetryTracker:
    """Sistema de telemetria para rastrear custos computacionais"""
    
    def __init__(self):
        self.metrics = {
            'time_taken_ms': {},
            'tokens_used': {},
            'gpu_memory_peak_mb': {},
            'cpu_usage_percent': {},
            'confidence_scores': {},
            'anomaly_detections': []
        }
    
    def track_execution(self, agent_id: str):
        """Decorador para rastrear execução de funções"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                start_time = datetime.now()
                
                # Simular métricas (em implementação real, seria monitoramento real)
                initial_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
                
                # Executar função
                result = func(*args, **kwargs)
                
                # Calcular métricas
                end_time = datetime.now()
                time_taken = (end_time - start_time).total_seconds() * 1000
                final_memory = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
                memory_used = (final_memory - initial_memory) / (1024 * 1024)  # MB
                
                # Simular tokens (em implementação real, seria do LLM)
                tokens_used = len(str(result)) // 4
                
                # Registrar métricas
                if agent_id not in self.metrics['time_taken_ms']:
                    self.metrics['time_taken_ms'][agent_id] = []
                    self.metrics['tokens_used'][agent_id] = []
                    self.metrics['gpu_memory_peak_mb'][agent_id] = []
                
                self.metrics['time_taken_ms'][agent_id].append(time_taken)
                self.metrics['tokens_used'][agent_id].append(tokens_used)
                self.metrics['gpu_memory_peak_mb'][agent_id].append(memory_used)
                
                return result
            return wrapper
        return decorator
    
    def get_agent_metrics(self, agent_id: str) -> Dict[str, float]:
        """Retorna métricas médias de um agente"""
        if agent_id not in self.metrics['time_taken_ms']:
            return {'time_taken_ms': 0, 'tokens_used': 0, 'gpu_memory_mb': 0}
        
        return {
            'time_taken_ms': np.mean(self.metrics['time_taken_ms'][agent_id]),
            'tokens_used': np.mean(self.metrics['tokens_used'][agent_id]),
            'gpu_memory_mb': np.mean(self.metrics['gpu_memory_peak_mb'][agent_id])
        }

class ConfidenceModule:
    """Módulo de confiança e detecção de anomalias (Insight 3)"""
    
    def __init__(self, anomaly_threshold: float = 0.3):
        self.anomaly_threshold = anomaly_threshold
        self.confidence_history = {}
        self.anomaly_history = []
        self.hypothesis_history = []
    
    def evaluate_confidence(self, agent_id: str, prediction: Any, confidence_score: float) -> Dict[str, Any]:
        """Avalia confiança e detecta anomalias"""
        if agent_id not in self.confidence_history:
            self.confidence_history[agent_id] = []
        
        # Adicionar à história
        self.confidence_history[agent_id].append(confidence_score)
        
        # Calcular confiança média histórica
        avg_confidence = np.mean(self.confidence_history[agent_id])
        
        # Detectar anomalia
        is_anomaly = abs(confidence_score - avg_confidence) > self.anomaly_threshold
        
        result = {
            'agent_id': agent_id,
            'current_confidence': confidence_score,
            'avg_confidence': avg_confidence,
            'is_anomaly': is_anomaly,
            'anomaly_magnitude': abs(confidence_score - avg_confidence)
        }
        
        if is_anomaly:
            self.anomaly_history.append(result)
            logger.info(f"🚨 Anomalia detectada no agente {agent_id}: confiança {confidence_score:.3f} vs média {avg_confidence:.3f}")
        
        return result
    
    def generate_hypothesis(self, anomaly_data: Dict) -> str:
        """Gera hipótese sobre anomalia detectada"""
        agent_id = anomaly_data['agent_id']
        confidence_diff = anomaly_data['anomaly_magnitude']
        
        # Gerar hipótese baseada no tipo de anomalia
        if confidence_diff > 0.5:
            hypothesis = f"O agente {agent_id} pode estar enfrentando um novo tipo de problema ou dados fora da distribuição de treinamento."
        elif confidence_diff > 0.3:
            hypothesis = f"O agente {agent_id} pode estar se adaptando a uma mudança gradual no padrão dos dados."
        else:
            hypothesis = f"O agente {agent_id} pode estar experimentando variação normal na confiança."
        
        self.hypothesis_history.append({
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'hypothesis': hypothesis,
            'anomaly_data': anomaly_data
        })
        
        return hypothesis

class EvolutionEngine:
    """Motor de evolução que opera no nível do genoma (Insight 1)"""
    
    def __init__(self, genome_path: str = "genome_master.yaml"):
        self.genome_path = genome_path
        self.genome_data = None
        self.telemetry = TelemetryTracker()
        self.confidence_module = ConfidenceModule()
        self.evolution_history = []
        self.generation = 0
        
        # Carregar genoma inicial
        self.load_genome()
    
    def load_genome(self):
        """Carrega o genoma do arquivo YAML"""
        with open(self.genome_path, 'r', encoding='utf-8') as file:
            self.genome_data = yaml.safe_load(file)
        logger.info(f"✅ Genoma carregado: {self.genome_data['metadata']['name']}")
    
    def save_genome(self, version_suffix: str = ""):
        """Salva o genoma com versionamento"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        version = self.genome_data['metadata']['version']
        
        if version_suffix:
            new_version = f"{version}_{version_suffix}"
        else:
            new_version = f"{version}_v{timestamp}"
        
        # Atualizar metadados
        self.genome_data['metadata']['version'] = new_version
        self.genome_data['metadata']['last_modified'] = datetime.now().isoformat()
        
        # Salvar genoma
        genome_dir = Path("genomes")
        genome_dir.mkdir(exist_ok=True)
        
        genome_file = genome_dir / f"genome_{new_version}.yaml"
        with open(genome_file, 'w', encoding='utf-8') as file:
            yaml.dump(self.genome_data, file, default_flow_style=False, indent=2)
        
        logger.info(f"💾 Genoma salvo: {genome_file}")
        return str(genome_file)
    
    def calculate_fitness(self, agent_id: str, accuracy: float, 
                         time_taken: float, tokens_used: float,
                         knowledge_gain: float = 0.0) -> float:
        """Calcula fitness multi-objetivo com pesos dinâmicos"""
        weights = self.genome_data['fitness_weights']
        
        # Normalizar valores
        normalized_time = max(0, 1 - (time_taken / 10000))  # Penalizar tempo alto
        normalized_tokens = max(0, 1 - (tokens_used / 5000))  # Penalizar tokens altos
        
        # Fitness ponderado
        fitness = (
            weights['accuracy'] * accuracy +
            weights['time_efficiency'] * normalized_time +
            weights['token_efficiency'] * normalized_tokens +
            weights['knowledge_gain'] * knowledge_gain
        )
        
        return fitness
    
    def mutate_genome(self, mutation_type: str = "parameter"):
        """Muta o genoma (não o código!)"""
        mutation_config = self.genome_data['evolution']['mutation_types']
        
        for mutation in mutation_config:
            if mutation['name'] == mutation_type and random.random() < mutation['probability']:
                intensity = mutation['intensity']
                
                if mutation_type == "parameter_mutation":
                    # Mutar pesos de fitness
                    for weight_key in self.genome_data['fitness_weights']:
                        if random.random() < 0.3:  # 30% chance de mutar cada peso
                            current_weight = self.genome_data['fitness_weights'][weight_key]
                            mutation_amount = random.gauss(0, intensity)
                            new_weight = max(0.0, min(1.0, current_weight + mutation_amount))
                            self.genome_data['fitness_weights'][weight_key] = new_weight
                    
                    # Mutar configurações de especialistas
                    for specialist_id, specialist in self.genome_data['specialists'].items():
                        if random.random() < 0.2:
                            current_threshold = specialist['confidence_threshold']
                            mutation_amount = random.gauss(0, intensity * 0.1)
                            new_threshold = max(0.1, min(1.0, current_threshold + mutation_amount))
                            specialist['confidence_threshold'] = new_threshold
                
                elif mutation_type == "structural_mutation":
                    # Mutar estrutura do grafo de agentes
                    if random.random() < 0.1:  # 10% chance de adicionar novo nó
                        new_node = {
                            'name': f"new_node_{len(self.genome_data['agent_graph']['nodes'])}",
                            'type': 'specialist',
                            'specialist': random.choice(list(self.genome_data['specialists'].keys())),
                            'dependencies': ['input_processor']
                        }
                        self.genome_data['agent_graph']['nodes'].append(new_node)
                
                elif mutation_type == "behavioral_mutation":
                    # Mutar comportamentos de curiosidade
                    curiosity_config = self.genome_data['curiosity']
                    if random.random() < 0.3:
                        curiosity_config['anomaly_threshold'] += random.gauss(0, intensity * 0.1)
                        curiosity_config['anomaly_threshold'] = max(0.1, min(0.9, curiosity_config['anomaly_threshold']))
                
                logger.info(f"🔄 Genoma mutado: {mutation_type}")
                break
    
    def crossover_genomes(self, genome_a_path: str, genome_b_path: str) -> str:
        """Crossover entre dois genomas"""
        # Carregar genomas pais
        with open(genome_a_path, 'r') as file:
            genome_a = yaml.safe_load(file)
        with open(genome_b_path, 'r') as file:
            genome_b = yaml.safe_load(file)
        
        # Criar genoma filho
        child_genome = copy.deepcopy(genome_a)
        
        # Crossover de especialistas
        for specialist_id in child_genome['specialists']:
            if random.random() < 0.5 and specialist_id in genome_b['specialists']:
                child_genome['specialists'][specialist_id] = genome_b['specialists'][specialist_id]
        
        # Crossover de pesos de fitness
        for weight_key in child_genome['fitness_weights']:
            if random.random() < 0.5:
                child_genome['fitness_weights'][weight_key] = genome_b['fitness_weights'][weight_key]
        
        # Crossover de configurações de curiosidade
        if random.random() < 0.5:
            child_genome['curiosity'] = genome_b['curiosity']
        
        # Salvar genoma filho
        child_genome['metadata']['version'] = f"crossover_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        child_genome['metadata']['parent_a'] = genome_a['metadata']['version']
        child_genome['metadata']['parent_b'] = genome_b['metadata']['version']
        
        genome_dir = Path("genomes")
        genome_dir.mkdir(exist_ok=True)
        
        child_file = genome_dir / f"genome_{child_genome['metadata']['version']}.yaml"
        with open(child_file, 'w') as file:
            yaml.dump(child_genome, file, default_flow_style=False, indent=2)
        
        logger.info(f"🔄 Crossover realizado: {child_file}")
        return str(child_file)
    
    def evolve_generation(self) -> Dict[str, Any]:
        """Evolui uma geração completa"""
        logger.info(f"🧬 Evoluindo geração {self.generation + 1}...")
        
        # Simular execução de agentes para coletar métricas
        agent_results = {}
        total_knowledge_gain = 0
        
        for specialist_id in self.genome_data['specialists']:
            # Simular execução do agente
            accuracy = random.uniform(0.6, 0.95)
            time_taken = random.uniform(100, 2000)
            tokens_used = random.uniform(100, 3000)
            confidence = random.uniform(0.5, 0.95)
            
            # Avaliar confiança e detectar anomalias
            confidence_result = self.confidence_module.evaluate_confidence(
                specialist_id, None, confidence
            )
            
            # Gerar hipótese se houver anomalia
            knowledge_gain = 0.0
            if confidence_result['is_anomaly']:
                hypothesis = self.confidence_module.generate_hypothesis(confidence_result)
                knowledge_gain = confidence_result['anomaly_magnitude'] * 0.5
                total_knowledge_gain += knowledge_gain
            
            # Calcular fitness
            fitness = self.calculate_fitness(
                specialist_id, accuracy, time_taken, tokens_used, knowledge_gain
            )
            
            agent_results[specialist_id] = {
                'fitness': fitness,
                'accuracy': accuracy,
                'time_taken': time_taken,
                'tokens_used': tokens_used,
                'confidence': confidence,
                'knowledge_gain': knowledge_gain,
                'is_anomaly': confidence_result['is_anomaly']
            }
        
        # Aplicar mutações
        mutation_types = [m['name'] for m in self.genome_data['evolution']['mutation_types']]
        for mutation_type in mutation_types:
            self.mutate_genome(mutation_type)
        
        # Selecionar melhores agentes para crossover
        best_agents = sorted(
            agent_results.items(), 
            key=lambda x: x[1]['fitness'], 
            reverse=True
        )[:3]
        
        # Registrar histórico
        evolution_record = {
            'generation': self.generation,
            'best_fitness': best_agents[0][1]['fitness'],
            'avg_fitness': np.mean([r['fitness'] for r in agent_results.values()]),
            'total_knowledge_gain': total_knowledge_gain,
            'anomalies_detected': len([r for r in agent_results.values() if r['is_anomaly']]),
            'agent_results': agent_results,
            'genome_version': self.genome_data['metadata']['version']
        }
        
        self.evolution_history.append(evolution_record)
        self.generation += 1
        
        # Salvar genoma evoluído
        self.save_genome(f"gen_{self.generation}")
        
        logger.info(f"✅ Geração {self.generation} completada")
        logger.info(f"   Melhor fitness: {best_agents[0][1]['fitness']:.4f}")
        logger.info(f"   Anomalias detectadas: {evolution_record['anomalies_detected']}")
        logger.info(f"   Ganho de conhecimento: {total_knowledge_gain:.4f}")
        
        return evolution_record
    
    def get_evolution_stats(self) -> Dict[str, Any]:
        """Retorna estatísticas completas da evolução"""
        return {
            'current_generation': self.generation,
            'evolution_history': self.evolution_history,
            'telemetry_summary': {
                agent_id: self.telemetry.get_agent_metrics(agent_id)
                for agent_id in self.genome_data['specialists']
            },
            'anomaly_summary': {
                'total_anomalies': len(self.confidence_module.anomaly_history),
                'total_hypotheses': len(self.confidence_module.hypothesis_history),
                'recent_anomalies': self.confidence_module.anomaly_history[-10:] if self.confidence_module.anomaly_history else []
            },
            'genome_metadata': self.genome_data['metadata']
        }
    
    def calculate_cost_efficiency(self, task: Dict[str, Any]) -> float:
        """Calcula eficiência de custo de uma tarefa"""
        cost = task.get('cost', 1)
        reward = task.get('reward', 1)
        complexity = task.get('complexity', 0.5)
        
        # Eficiência = (Recompensa - Custo) / Complexidade
        efficiency = (reward - cost) / max(complexity, 0.1)
        return max(0.0, efficiency)
    
    def select_optimal_task(self, tasks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Seleciona a tarefa mais eficiente em termos de custo"""
        efficiencies = []
        for task in tasks:
            efficiency = self.calculate_cost_efficiency(task)
            efficiencies.append(efficiency)
        
        # Retornar tarefa com maior eficiência
        best_index = np.argmax(efficiencies)
        return tasks[best_index]
    
    def learn_with_cost_constraints(self, task: Dict[str, Any], max_cost: float, learning_steps: int) -> Dict[str, Any]:
        """Aprende com restrições de custo"""
        total_cost = 0
        learning_progress = []
        
        for step in range(learning_steps):
            step_cost = task.get('cost', 1) / learning_steps
            if total_cost + step_cost <= max_cost:
                total_cost += step_cost
                progress = (step + 1) / learning_steps
                learning_progress.append({
                    'step': step + 1,
                    'cost': step_cost,
                    'progress': progress
                })
            else:
                break
        
        return {
            'success': total_cost <= max_cost,
            'total_cost': total_cost,
            'steps_completed': len(learning_progress),
            'learning_progress': learning_progress
        }
    
    def calculate_curiosity(self, environment: Dict[str, Any]) -> float:
        """Calcula nível de curiosidade baseado na novidade do ambiente"""
        novelty = environment.get('novelty', 0.5)
        exploration_value = environment.get('exploration_value', 0.5)
        
        # Curiosidade = Novidade * Valor de Exploração
        curiosity = novelty * exploration_value
        return min(1.0, curiosity)
    
    def decide_exploration(self, environment: Dict[str, Any]) -> bool:
        """Decide se deve explorar baseado na curiosidade"""
        curiosity = self.calculate_curiosity(environment)
        threshold = 0.3  # Threshold para decidir explorar
        
        return curiosity > threshold
    
    def explore_environment(self, environment: Dict[str, Any]) -> Dict[str, Any]:
        """Explora o ambiente e coleta informações"""
        curiosity = self.calculate_curiosity(environment)
        
        # Simular exploração
        discoveries = []
        if curiosity > 0.5:
            discoveries.append("Novo padrão detectado")
        if curiosity > 0.7:
            discoveries.append("Anomalia interessante encontrada")
        if curiosity > 0.9:
            discoveries.append("Descoberta revolucionária!")
        
        return {
            'environment': environment['name'],
            'curiosity_level': curiosity,
            'discoveries': discoveries,
            'exploration_time': curiosity * 100,  # Tempo proporcional à curiosidade
            'knowledge_gained': len(discoveries) * 0.2
        }
    
    def learn_from_discovery(self, exploration_result: Dict[str, Any]) -> Dict[str, Any]:
        """Aprende a partir de descobertas feitas"""
        knowledge_gained = exploration_result.get('knowledge_gained', 0)
        discoveries = exploration_result.get('discoveries', [])
        
        # Simular aprendizado
        learning_efficiency = min(1.0, knowledge_gained * 2)
        
        return {
            'learning_success': learning_efficiency > 0.1,
            'learning_efficiency': learning_efficiency,
            'new_knowledge': discoveries,
            'adaptation_rate': learning_efficiency * 0.5
        }

def create_evolution_engine() -> EvolutionEngine:
    """Cria e retorna o motor de evolução"""
    return EvolutionEngine()

if __name__ == "__main__":
    # Teste do motor de evolução
    engine = create_evolution_engine()
    
    print("🚀 Motor de Evolução iniciado!")
    print(f"📊 Genoma: {engine.genome_data['metadata']['name']} v{engine.genome_data['metadata']['version']}")
    
    # Executar algumas gerações
    for i in range(5):
        result = engine.evolve_generation()
        print(f"Geração {i+1}: Fitness={result['best_fitness']:.4f}, Anomalias={result['anomalies_detected']}")
    
    # Mostrar estatísticas finais
    stats = engine.get_evolution_stats()
    print(f"\n📈 Estatísticas finais:")
    print(f"   Gerações: {stats['current_generation']}")
    print(f"   Anomalias detectadas: {stats['anomaly_summary']['total_anomalies']}")
    print(f"   Hipóteses geradas: {stats['anomaly_summary']['total_hypotheses']}")
    print(f"   Melhor fitness: {stats['evolution_history'][-1]['best_fitness']:.4f}") 
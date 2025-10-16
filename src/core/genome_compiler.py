"""
Compilador Genômico - Transforma o Genoma Mestre em IA Funcional
Versão: 1.0.1 - Corrigido
Descrição: Compila o YAML do genoma em código Python executável
"""

import yaml
import json
import os
import shutil
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import copy
from pathlib import Path

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenomeCompiler:
    """Compilador que transforma o Genoma Mestre em IA funcional"""
    
    def __init__(self, genome_path: str = "genome_master.yaml"):
        self.genome_path = genome_path
        self.genome_data = None
        self.compiled_ai = None
        self.backup_dir = "backups"
        self.ensure_backup_dir()
        
    def ensure_backup_dir(self):
        """Garante que o diretório de backup existe"""
        Path(self.backup_dir).mkdir(exist_ok=True)
        
    def load_genome(self) -> Dict[str, Any]:
        """Carrega o genoma do arquivo YAML"""
        try:
            with open(self.genome_path, 'r', encoding='utf-8') as file:
                self.genome_data = yaml.safe_load(file)
            logger.info(f"✅ Genoma carregado: {self.genome_data['metadata']['name']} v{self.genome_data['metadata']['version']}")
            return self.genome_data
        except Exception as e:
            logger.error(f"❌ Erro ao carregar genoma: {e}")
            raise
    
    def create_backup(self) -> str:
        """Cria backup da IA atual antes da evolução"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"ai_backup_{timestamp}"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # Backup dos arquivos principais
        files_to_backup = [
            "ia_pipeline/ai_engine.py",
            "config-feedforward.txt",
            "testar_ia_completa.py"
        ]
        
        os.makedirs(backup_path, exist_ok=True)
        
        for file_path in files_to_backup:
            if os.path.exists(file_path):
                shutil.copy2(file_path, backup_path)
        
        # Salvar estado do genoma atual
        with open(os.path.join(backup_path, "genome_state.json"), 'w') as f:
            json.dump(self.genome_data, f, indent=2)
        
        logger.info(f"✅ Backup criado: {backup_path}")
        return backup_path
    
    def compile_collaborative_ai(self) -> 'CollaborativeBiomimeticAI':
        """Compila a IA colaborativa baseada no genoma"""
        
        class CollaborativeBiomimeticAI:
            """IA Biomimética Colaborativa com Especialistas"""
            
            def __init__(self, genome_data: Dict):
                self.genome_data = genome_data
                self.base_config = genome_data['base_config']
                self.fitness_weights = genome_data['fitness_weights']
                self.specialists_config = genome_data['specialists']
                
                # Dispositivo
                self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                logger.info(f"Usando dispositivo: {self.device}")
                
                # Inicializar especialistas
                self.specialists = {}
                self.initialize_specialists()
                
                # Sistema de telemetria
                self.telemetry = {
                    'time_taken': {},
                    'tokens_used': {},
                    'confidence_scores': {},
                    'collaboration_history': []
                }
                
                # Histórico de evolução
                self.evolution_history = []
                self.generation = 0
                
                logger.info("✅ IA Colaborativa Biomimética inicializada")
            
            def compile_specialist_network(self, specialist_config: Dict) -> nn.Module:
                """Compila uma rede neural especializada"""
                base_config = self.genome_data['base_config']
                
                class SpecialistNetwork(nn.Module):
                    def __init__(self, specialist_type: str, config: Dict):
                        super().__init__()
                        self.specialist_type = specialist_type
                        self.confidence_threshold = config.get('confidence_threshold', 0.8)
                        self.max_tokens = config.get('max_tokens', 2000)
                        
                        # Arquitetura baseada no tipo de especialista
                        if specialist_type == "jurist":
                            self.hidden_size = base_config['hidden_size'] + 32  # Mais complexo para análise legal
                        elif specialist_type == "financial":
                            self.hidden_size = base_config['hidden_size'] + 16  # Foco em precisão numérica
                        elif specialist_type == "reviewer":
                            self.hidden_size = base_config['hidden_size'] - 16  # Mais simples para revisão
                        elif specialist_type == "skeptic":
                            self.hidden_size = base_config['hidden_size'] + 8   # Análise crítica
                        else:  # maestro
                            self.hidden_size = base_config['hidden_size'] + 64  # Mais complexo para coordenação
                        
                        # Garantir que seja divisível por 4
                        if self.hidden_size % 4 != 0:
                            self.hidden_size = ((self.hidden_size // 4) + 1) * 4
                        
                        # Camadas da rede
                        self.layers = nn.ModuleList([
                            nn.Linear(base_config['input_size'], self.hidden_size),
                            nn.ReLU(),
                            nn.Dropout(0.1),
                            nn.Linear(self.hidden_size, self.hidden_size // 2),
                            nn.ReLU(),
                            nn.Dropout(0.1),
                            nn.Linear(self.hidden_size // 2, base_config['output_size'])
                        ])
                        
                        # Mecanismo de atenção para especialistas complexos
                        if specialist_type in ["jurist", "maestro"]:
                            self.attention = nn.MultiheadAttention(
                                self.hidden_size, 
                                num_heads=4, 
                                batch_first=True
                            )
                            self.use_attention = True
                        else:
                            self.use_attention = False
                        
                        # Camada de confiança
                        self.confidence_layer = nn.Linear(base_config['output_size'], 1)
                        self.confidence_activation = nn.Sigmoid()
                    
                    def forward(self, x):
                        # Processamento através das camadas
                        for i, layer in enumerate(self.layers):
                            if isinstance(layer, nn.Linear) and i == 0 and self.use_attention:
                                # Aplicar atenção na primeira camada para especialistas complexos
                                x = x.unsqueeze(1) if x.dim() == 2 else x
                                attn_output, _ = self.attention(x, x, x)
                                x = attn_output.squeeze(1) if attn_output.size(1) == 1 else attn_output
                            
                            x = layer(x)
                        
                        # Calcular confiança
                        confidence = self.confidence_activation(self.confidence_layer(x))
                        
                        return x, confidence
                
                return SpecialistNetwork(specialist_config['name'].lower().replace(' ', '_'), specialist_config)
            
            def initialize_specialists(self):
                """Inicializa todos os especialistas"""
                for specialist_id, config in self.specialists_config.items():
                    if specialist_id != 'maestro':  # Maestro é tratado separadamente
                        network = self.compile_specialist_network(config).to(self.device)
                        self.specialists[specialist_id] = {
                            'network': network,
                            'config': config,
                            'fitness': 0.0,
                            'confidence_history': [],
                            'performance_history': []
                        }
                        logger.info(f"✅ Especialista inicializado: {config['name']}")
            
            def telemetry_tracker(self, specialist_id: str):
                """Decorador para rastrear telemetria"""
                def decorator(func):
                    def wrapper(*args, **kwargs):
                        start_time = datetime.now()
                        
                        # Executar função
                        result = func(*args, **kwargs)
                        
                        # Calcular telemetria
                        end_time = datetime.now()
                        time_taken = (end_time - start_time).total_seconds() * 1000  # ms
                        
                        # Simular tokens usados (em uma implementação real, seria do LLM)
                        tokens_used = len(str(result)) // 4  # Aproximação
                        
                        # Registrar telemetria
                        if specialist_id not in self.telemetry['time_taken']:
                            self.telemetry['time_taken'][specialist_id] = []
                            self.telemetry['tokens_used'][specialist_id] = []
                        
                        self.telemetry['time_taken'][specialist_id].append(time_taken)
                        self.telemetry['tokens_used'][specialist_id].append(tokens_used)
                        
                        return result
                    return wrapper
                return decorator
            
            def calculate_fitness(self, specialist_id: str, accuracy: float, 
                                time_taken: float, tokens_used: float, 
                                knowledge_gain: float = 0.0) -> float:
                """Calcula fitness multi-objetivo"""
                weights = self.fitness_weights
                
                # Normalizar valores
                normalized_time = max(0, 1 - (time_taken / 10000))  # Penalizar tempo alto
                normalized_tokens = max(0, 1 - (tokens_used / 5000))  # Penalizar tokens altos
                
                fitness = (
                    weights['accuracy'] * accuracy +
                    weights['time_efficiency'] * normalized_time +
                    weights['token_efficiency'] * normalized_tokens +
                    weights['knowledge_gain'] * knowledge_gain
                )
                
                return fitness
            
            def process_with_specialists(self, input_data: torch.Tensor) -> Dict[str, Any]:
                """Processa dados através de todos os especialistas"""
                results = {}
                
                for specialist_id, specialist in self.specialists.items():
                    try:
                        # Processar com o especialista
                        output, confidence = specialist['network'](input_data)
                        
                        # Calcular métricas
                        accuracy = torch.mean(torch.abs(output)).item()
                        time_taken = self.telemetry['time_taken'].get(specialist_id, [0])[-1]
                        tokens_used = self.telemetry['tokens_used'].get(specialist_id, [0])[-1]
                        
                        # Calcular fitness
                        fitness = self.calculate_fitness(
                            specialist_id, accuracy, time_taken, tokens_used
                        )
                        
                        # Atualizar especialista
                        specialist['fitness'] = fitness
                        specialist['confidence_history'].append(confidence.item())
                        specialist['performance_history'].append(accuracy)
                        
                        results[specialist_id] = {
                            'output': output,
                            'confidence': confidence.item(),
                            'fitness': fitness,
                            'accuracy': accuracy,
                            'time_taken': time_taken,
                            'tokens_used': tokens_used
                        }
                        
                    except Exception as e:
                        logger.error(f"Erro no especialista {specialist_id}: {e}")
                        results[specialist_id] = {
                            'error': str(e),
                            'fitness': 0.0
                        }
                
                return results
            
            def evolve_specialists(self):
                """Evolui os especialistas"""
                logger.info(f"🔄 Evoluindo especialistas - Geração {self.generation + 1}")
                
                # Avaliar todos os especialistas
                test_input = torch.randn(10, self.base_config['input_size']).to(self.device)
                results = self.process_with_specialists(test_input)
                
                # Selecionar melhores especialistas
                best_specialists = sorted(
                    results.items(), 
                    key=lambda x: x[1]['fitness'], 
                    reverse=True
                )[:3]
                
                # Mutação dos especialistas
                for specialist_id, specialist in self.specialists.items():
                    if random.random() < self.genome_data['evolution']['innovation_rate']:
                        self.mutate_specialist(specialist_id)
                
                # Crossover entre melhores especialistas
                if len(best_specialists) >= 2:
                    self.crossover_specialists(
                        best_specialists[0][0], 
                        best_specialists[1][0]
                    )
                
                self.generation += 1
                
                # Registrar histórico
                self.evolution_history.append({
                    'generation': self.generation,
                    'best_fitness': max(r['fitness'] for r in results.values()),
                    'avg_fitness': np.mean([r['fitness'] for r in results.values()]),
                    'specialist_performance': results
                })
                
                logger.info(f"✅ Evolução completada - Melhor fitness: {max(r['fitness'] for r in results.values()):.4f}")
            
            def mutate_specialist(self, specialist_id: str):
                """Muta um especialista"""
                specialist = self.specialists[specialist_id]
                network = specialist['network']
                
                # Mutação de pesos
                for param in network.parameters():
                    if random.random() < 0.1:  # 10% chance de mutação
                        noise = torch.randn_like(param) * 0.01
                        param.data += noise
                
                logger.info(f"🔄 Especialista {specialist_id} mutado")
            
            def crossover_specialists(self, specialist1_id: str, specialist2_id: str):
                """Crossover entre dois especialistas"""
                spec1 = self.specialists[specialist1_id]['network']
                spec2 = self.specialists[specialist2_id]['network']
                
                # Trocar alguns parâmetros
                for param1, param2 in zip(spec1.parameters(), spec2.parameters()):
                    if random.random() < 0.5:
                        param1.data, param2.data = param2.data.clone(), param1.data.clone()
                
                logger.info(f"🔄 Crossover entre {specialist1_id} e {specialist2_id}")
            
            def get_evolution_stats(self) -> Dict:
                """Retorna estatísticas da evolução"""
                return {
                    'generation': self.generation,
                    'evolution_history': self.evolution_history,
                    'telemetry': self.telemetry,
                    'specialists_performance': {
                        spec_id: {
                            'fitness': spec['fitness'],
                            'avg_confidence': np.mean(spec['confidence_history']) if spec['confidence_history'] else 0,
                            'avg_performance': np.mean(spec['performance_history']) if spec['performance_history'] else 0
                        }
                        for spec_id, spec in self.specialists.items()
                    }
                }
        
        return CollaborativeBiomimeticAI(self.genome_data)
    
    def compile_genome(self, genome_path: str = None) -> 'CollaborativeBiomimeticAI':
        """Compila o genoma em IA funcional"""
        if genome_path:
            self.genome_path = genome_path
        
        # Carregar genoma
        self.load_genome()
        
        # Compilar IA
        self.compiled_ai = self.compile_collaborative_ai()
        
        # Criar backup
        self.create_backup()
        
        logger.info("✅ Genoma compilado com sucesso")
        return self.compiled_ai

    def compile(self) -> 'CollaborativeBiomimeticAI':
        """Compila o genoma em IA funcional"""
        logger.info("🧬 Iniciando compilação do Genoma Mestre...")
        
        # Carregar genoma
        self.load_genome()
        
        # Criar backup da versão atual
        backup_path = self.create_backup()
        logger.info(f"💾 Backup da versão atual: {backup_path}")
        
        # Compilar IA colaborativa
        self.compiled_ai = self.compile_collaborative_ai()
        
        logger.info("✅ Compilação concluída com sucesso!")
        return self.compiled_ai
    
    def save_compiled_state(self, path: str = "compiled_ai_state.json"):
        """Salva o estado da IA compilada"""
        if self.compiled_ai:
            state = {
                'genome_metadata': self.genome_data['metadata'],
                'compilation_timestamp': datetime.now().isoformat(),
                'evolution_stats': self.compiled_ai.get_evolution_stats()
            }
            
            with open(path, 'w') as f:
                json.dump(state, f, indent=2)
            
            logger.info(f"💾 Estado da IA salvo: {path}")

def create_evolved_ai() -> 'CollaborativeBiomimeticAI':
    """Função principal para criar a IA evoluída"""
    compiler = GenomeCompiler()
    return compiler.compile()

if __name__ == "__main__":
    # Teste do compilador
    ai = create_evolved_ai()
    print("🚀 IA Biomimética Colaborativa criada com sucesso!")
    
    # Teste de evolução
    for i in range(3):
        ai.evolve_specialists()
    
    # Mostrar estatísticas
    stats = ai.get_evolution_stats()
    print(f"📊 Estatísticas finais:")
    print(f"   Gerações: {stats['generation']}")
    print(f"   Melhor fitness: {stats['evolution_history'][-1]['best_fitness']:.4f}")
    print(f"   Fitness médio: {stats['evolution_history'][-1]['avg_fitness']:.4f}") 
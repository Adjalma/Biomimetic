"""
BrainEvolver - Evolução do Cérebro (Llama/Modelos)
==================================================

Implementa evolução do componente de IA local:
1. Substituição de modelos Llama por outros modelos
2. Criação de ensembles automáticos de modelos
3. Otimização de parâmetros do Llama
4. Evolução do sistema de orquestração de modelos

Versão: 1.0.0
Data: 2026-04-14
Autor: Jarvis (OpenClaw)
"""

import os
import json
import random
import copy
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BrainEvolver:
    """Evolui o componente de IA local (Llama/Ollama)"""
    
    # Modelos disponíveis para evolução
    AVAILABLE_MODELS = {
        'llama': {
            'llama3.1:8b': {
                'description': 'Llama 3.1 8B - Equilíbrio entre performance e recursos',
                'context_window': 8192,
                'parameter_count': '8B',
                'recommended_tasks': ['conversation', 'analysis', 'summarization'],
                'estimated_vram_mb': 8000
            },
            'llama3.2:3b': {
                'description': 'Llama 3.2 3B - Leve e rápido',
                'context_window': 8192,
                'parameter_count': '3B',
                'recommended_tasks': ['quick_answers', 'classification', 'simple_reasoning'],
                'estimated_vram_mb': 3000
            },
            'mistral:7b': {
                'description': 'Mistral 7B - Excelente para instruções',
                'context_window': 32768,
                'parameter_count': '7B',
                'recommended_tasks': ['instruction_following', 'coding', 'creative_writing'],
                'estimated_vram_mb': 7000
            },
            'gemma2:9b': {
                'description': 'Gemma 2 9B - Focado em segurança e qualidade',
                'context_window': 8192,
                'parameter_count': '9B',
                'recommended_tasks': ['safe_generation', 'reasoning', 'educational'],
                'estimated_vram_mb': 9000
            }
        },
        'ensemble': {
            'llama3.1:8b+mistral:7b': {
                'description': 'Ensemble Llama 3.1 + Mistral - Melhor dos dois mundos',
                'models': ['llama3.1:8b', 'mistral:7b'],
                'strategy': 'weighted_voting',
                'estimated_vram_mb': 15000
            },
            'llama3.2:3b+gemma2:9b': {
                'description': 'Ensemble Leve + Seguro - Eficiência com segurança',
                'models': ['llama3.2:3b', 'gemma2:9b'],
                'strategy': 'confidence_based',
                'estimated_vram_mb': 12000
            }
        }
    }
    
    def __init__(self, config_path: str = None, config_data: Dict = None):
        """Inicializa BrainEvolver com configuração atual"""
        if config_path:
            # Carregar do bio_console_api ou configuração similar
            self.config = self._load_config_from_path(config_path)
        elif config_data:
            self.config = copy.deepcopy(config_data)
        else:
            # Configuração padrão
            self.config = {
                'use_local_brain': True,
                'local_brain_type': 'ollama',
                'ollama_model': 'llama3.1:8b',
                'ollama_base_url': 'http://localhost:11434',
                'brain_evolution': {
                    'enabled': True,
                    'mutation_rate': 0.1,
                    'ensemble_strategies': ['weighted_voting', 'confidence_based', 'task_routing'],
                    'parameter_optimization': True
                }
            }
        
        self.original_config = copy.deepcopy(self.config)
        self.evolution_history = []
        logger.info(f"🧠 BrainEvolver inicializado com modelo: {self.config.get('ollama_model', 'N/A')}")
    
    def _load_config_from_path(self, config_path: str) -> Dict[str, Any]:
        """Carrega configuração do arquivo"""
        # Em produção, carregaria de bio_console_api.py ou .env
        # Por enquanto, retorna configuração padrão
        return {
            'use_local_brain': True,
            'local_brain_type': 'ollama',
            'ollama_model': 'llama3.1:8b',
            'ollama_base_url': 'http://localhost:11434'
        }
    
    def get_brain_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do cérebro atual"""
        current_model = self.config.get('ollama_model', 'unknown')
        model_info = None
        
        # Buscar informações do modelo atual
        for category, models in self.AVAILABLE_MODELS.items():
            if current_model in models:
                model_info = models[current_model]
                break
        
        return {
            'current_model': current_model,
            'model_info': model_info,
            'use_local_brain': self.config.get('use_local_brain', False),
            'local_brain_type': self.config.get('local_brain_type', 'unknown'),
            'base_url': self.config.get('ollama_base_url', 'http://localhost:11434'),
            'evolution_enabled': self.config.get('brain_evolution', {}).get('enabled', False)
        }
    
    def mutate_model_selection(self) -> str:
        """Muta a seleção do modelo (substitui por outro)"""
        current_model = self.config.get('ollama_model', 'llama3.1:8b')
        
        # Listar todos os modelos disponíveis (exceto o atual)
        all_models = []
        for category, models in self.AVAILABLE_MODELS.items():
            if category != 'ensemble':  # Por enquanto, só modelos individuais
                for model_name in models.keys():
                    if model_name != current_model:
                        all_models.append(model_name)
        
        if not all_models:
            logger.warning("⚠️ Nenhum modelo alternativo disponível")
            return current_model
        
        # Escolher novo modelo
        new_model = random.choice(all_models)
        
        # Atualizar configuração
        self.config['ollama_model'] = new_model
        
        logger.info(f"🔄 Modelo mutado: {current_model} → {new_model}")
        
        # Registrar na história
        self.evolution_history.append({
            'timestamp': datetime.now().isoformat(),
            'mutation_type': 'model_selection',
            'from_model': current_model,
            'to_model': new_model,
            'reason': 'random_mutation'
        })
        
        return new_model
    
    def create_ensemble(self, model_count: int = 2) -> Dict[str, Any]:
        """Cria ensemble de modelos"""
        
        # Escolher modelos para o ensemble
        available_individual = []
        for model_name in self.AVAILABLE_MODELS.get('llama', {}).keys():
            available_individual.append(model_name)
        
        if len(available_individual) < model_count:
            logger.warning(f"⚠️ Não há modelos suficientes para ensemble ({len(available_individual)} disponíveis)")
            return {}
        
        selected_models = random.sample(available_individual, model_count)
        
        # Escolher estratégia do ensemble
        strategies = ['weighted_voting', 'confidence_based', 'task_routing', 'sequential']
        strategy = random.choice(strategies)
        
        # Criar nome do ensemble
        ensemble_name = '+'.join(sorted(selected_models))
        
        # Configurar ensemble
        ensemble_config = {
            'enabled': True,
            'ensemble_name': ensemble_name,
            'models': selected_models,
            'strategy': strategy,
            'weights': {model: random.uniform(0.3, 0.7) for model in selected_models},
            'fallback_model': selected_models[0]
        }
        
        # Normalizar pesos
        total_weight = sum(ensemble_config['weights'].values())
        for model in ensemble_config['weights']:
            ensemble_config['weights'][model] /= total_weight
        
        # Atualizar configuração
        if 'ensemble' not in self.config:
            self.config['ensemble'] = {}
        
        self.config['ensemble'] = ensemble_config
        self.config['use_ensemble'] = True
        
        logger.info(f"🧩 Ensemble criado: {ensemble_name} (estratégia: {strategy})")
        
        # Registrar na história
        self.evolution_history.append({
            'timestamp': datetime.now().isoformat(),
            'mutation_type': 'create_ensemble',
            'ensemble_name': ensemble_name,
            'models': selected_models,
            'strategy': strategy,
            'weights': ensemble_config['weights']
        })
        
        return ensemble_config
    
    def optimize_parameters(self) -> Dict[str, Any]:
        """Otimiza parâmetros do modelo atual"""
        
        current_model = self.config.get('ollama_model', 'llama3.1:8b')
        
        # Parâmetros que podem ser otimizados
        optimizable_params = {
            'temperature': (0.1, 1.0),  # Aleatoriedade
            'top_p': (0.7, 0.95),      # Nucleus sampling
            'top_k': (20, 100),        # Top-k sampling
            'repeat_penalty': (1.0, 1.3),  # Penalidade de repetição
            'num_predict': (100, 2048),  # Tokens máximos a gerar
        }
        
        # Gerar novos valores otimizados
        optimized = {}
        for param, (min_val, max_val) in optimizable_params.items():
            # Pequena mutação aleatória
            current_val = self.config.get(param, (min_val + max_val) / 2)
            mutation = random.gauss(0, (max_val - min_val) * 0.1)
            new_val = current_val + mutation
            # Garantir dentro dos limites
            new_val = max(min_val, min(max_val, new_val))
            optimized[param] = round(new_val, 3)
        
        # Aplicar otimizações
        self.config.update(optimized)
        
        logger.info(f"⚙️ Parâmetros otimizados para {current_model}: {optimized}")
        
        # Registrar na história
        self.evolution_history.append({
            'timestamp': datetime.now().isoformat(),
            'mutation_type': 'parameter_optimization',
            'model': current_model,
            'optimized_parameters': optimized
        })
        
        return optimized
    
    def evolve_routing_strategy(self) -> Dict[str, Any]:
        """Evolui a estratégia de roteamento entre modelos"""
        
        strategies = [
            {
                'name': 'task_based',
                'description': 'Roteia baseado no tipo de tarefa',
                'rules': {
                    'conversation': 'llama3.1:8b',
                    'analysis': 'mistral:7b',
                    'creative': 'gemma2:9b',
                    'quick': 'llama3.2:3b'
                }
            },
            {
                'name': 'confidence_based',
                'description': 'Roteia baseado na confiança do modelo',
                'threshold': 0.7,
                'fallback': 'llama3.1:8b'
            },
            {
                'name': 'performance_based',
                'description': 'Roteia baseado em histórico de performance',
                'window_size': 100,
                'metric': 'accuracy'
            },
            {
                'name': 'hybrid',
                'description': 'Combinação de múltiplas estratégias',
                'components': ['task_based', 'confidence_based'],
                'weights': [0.6, 0.4]
            }
        ]
        
        # Escolher ou criar estratégia
        if random.random() < 0.3:
            # Criar nova estratégia híbrida
            selected_strategies = random.sample(strategies, 2)
            hybrid_strategy = {
                'name': f'hybrid_{datetime.now().strftime("%H%M%S")}',
                'description': f'Híbrido de {selected_strategies[0]["name"]} e {selected_strategies[1]["name"]}',
                'components': [s['name'] for s in selected_strategies],
                'weights': [random.uniform(0.3, 0.7) for _ in range(2)],
                'created_by': 'evolution'
            }
            # Normalizar pesos
            total = sum(hybrid_strategy['weights'])
            hybrid_strategy['weights'] = [w/total for w in hybrid_strategy['weights']]
            
            strategy = hybrid_strategy
        else:
            # Escolher estratégia existente
            strategy = random.choice(strategies)
        
        # Configurar roteamento
        if 'routing' not in self.config:
            self.config['routing'] = {}
        
        self.config['routing']['strategy'] = strategy
        self.config['routing']['last_updated'] = datetime.now().isoformat()
        
        logger.info(f"🔄 Estratégia de roteamento evoluída: {strategy['name']}")
        
        # Registrar na história
        self.evolution_history.append({
            'timestamp': datetime.now().isoformat(),
            'mutation_type': 'routing_strategy',
            'strategy_name': strategy['name'],
            'strategy_details': strategy
        })
        
        return strategy
    
    def perform_brain_evolution(self, evolution_type: str = None) -> Dict[str, Any]:
        """Executa evolução completa do cérebro"""
        
        if not evolution_type:
            evolution_type = random.choice([
                'mutate_model', 'create_ensemble', 
                'optimize_parameters', 'evolve_routing',
                'combined'
            ])
        
        evolution_log = {
            'timestamp': datetime.now().isoformat(),
            'evolution_type': evolution_type,
            'changes': [],
            'metrics_before': self.get_brain_metrics()
        }
        
        try:
            if evolution_type == 'mutate_model':
                new_model = self.mutate_model_selection()
                evolution_log['changes'].append(f"Model mutated to: {new_model}")
            
            elif evolution_type == 'create_ensemble':
                ensemble_config = self.create_ensemble()
                if ensemble_config:
                    evolution_log['changes'].append(f"Ensemble created: {ensemble_config.get('ensemble_name', 'N/A')}")
                else:
                    evolution_log['changes'].append("Ensemble creation failed")
            
            elif evolution_type == 'optimize_parameters':
                optimized = self.optimize_parameters()
                evolution_log['changes'].append(f"Parameters optimized: {optimized}")
            
            elif evolution_type == 'evolve_routing':
                strategy = self.evolve_routing_strategy()
                evolution_log['changes'].append(f"Routing strategy evolved: {strategy['name']}")
            
            elif evolution_type == 'combined':
                # Combinar múltiplas evoluções
                num_evolutions = random.randint(2, 3)
                evolutions = random.sample([
                    'mutate_model', 'optimize_parameters', 'evolve_routing'
                ], min(num_evolutions, 3))
                
                for evol in evolutions:
                    if evol == 'mutate_model':
                        self.mutate_model_selection()
                        evolution_log['changes'].append("Model mutated (combined)")
                    elif evol == 'optimize_parameters':
                        self.optimize_parameters()
                        evolution_log['changes'].append("Parameters optimized (combined)")
                    elif evol == 'evolve_routing':
                        self.evolve_routing_strategy()
                        evolution_log['changes'].append("Routing evolved (combined)")
            
            # Atualizar métricas
            evolution_log['metrics_after'] = self.get_brain_metrics()
            evolution_log['success'] = True
            
            logger.info(f"🧠 Evolução cerebral executada: {evolution_type}")
            
        except Exception as e:
            evolution_log['error'] = str(e)
            evolution_log['success'] = False
            logger.error(f"❌ Erro na evolução cerebral: {e}")
        
        return evolution_log
    
    def save_evolution_config(self, suffix: str = "evolved") -> str:
        """Salva configuração evolvida"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        config_dir = Path("configs/brain_evolution")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Salvar configuração
        config_file = config_dir / f"brain_config_{suffix}_{timestamp}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, default=str)
        
        # Salvar histórico
        history_file = config_dir / f"evolution_history_{suffix}_{timestamp}.json"
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(self.evolution_history, f, indent=2, default=str)
        
        logger.info(f"💾 Configuração cerebral salva: {config_file}")
        
        return str(config_file)
    
    def apply_to_environment(self):
        """Aplica configuração evoluída ao ambiente (variáveis de ambiente)"""
        # Em produção, atualizaria .env ou configuração do bio_console_api
        # Por enquanto, apenas log
        logger.info("🔧 Aplicando configuração cerebral evoluída ao ambiente")
        logger.info(f"   Modelo: {self.config.get('ollama_model')}")
        logger.info(f"   Ensemble: {self.config.get('ensemble', {}).get('enabled', False)}")
        logger.info(f"   Routing: {self.config.get('routing', {}).get('strategy', {}).get('name', 'N/A')}")
        
        # Sugerir comando para aplicar manualmente
        print("\n💡 Para aplicar esta configuração, adicione ao seu .env ou bio_console_api.py:")
        print(f"   OLLAMA_MODEL={self.config.get('ollama_model', 'llama3.1:8b')}")
        if self.config.get('ensemble', {}).get('enabled'):
            print(f"   OLLAMA_ENSEMBLE=true")
            print(f"   OLLAMA_ENSEMBLE_MODELS={','.join(self.config['ensemble'].get('models', []))}")


# Função de teste
def test_brain_evolver():
    """Testa o BrainEvolver"""
    try:
        evolver = BrainEvolver()
        
        print("🧠 TESTE BRAIN EVOLVER")
        print("=" * 50)
        
        # Métricas iniciais
        metrics = evolver.get_brain_metrics()
        print(f"Métricas iniciais:")
        print(f"  Modelo atual: {metrics['current_model']}")
        print(f"  Tipo: {metrics['local_brain_type']}")
        print(f"  Evolution enabled: {metrics['evolution_enabled']}")
        
        # Executar evolução
        print("\n🔀 Executando evolução cerebral...")
        evolution_log = evolver.perform_brain_evolution()
        
        print(f"\n📊 Resultado da evolução:")
        print(f"Tipo: {evolution_log['evolution_type']}")
        print(f"Mudanças: {evolution_log.get('changes', [])}")
        print(f"Sucesso: {evolution_log.get('success', False)}")
        
        # Métricas finais
        metrics_final = evolver.get_brain_metrics()
        print(f"\n✅ Métricas finais:")
        print(f"  Modelo atual: {metrics_final['current_model']}")
        if metrics_final.get('model_info'):
            print(f"  Descrição: {metrics_final['model_info'].get('description', 'N/A')}")
        
        # Salvar configuração
        saved_path = evolver.save_evolution_config()
        print(f"\n💾 Configuração salva em: {saved_path}")
        
        # Aplicar ao ambiente
        evolver.apply_to_environment()
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_brain_evolver()
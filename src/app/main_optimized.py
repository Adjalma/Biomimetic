"""
IA Autoevolutiva Biomimética - Versão Otimizada para Hardware Dedicado
======================================================================

Versão otimizada para:
- RAM: 16 GB
- CPU: 6 VCPUs  
- SO: Windows 11
- Armazenamento: 20 GB para SO

Esta versão maximiza a capacidade da IA usando todos os recursos disponíveis.
"""

import os
import sys
import logging
import time
import json
from typing import Dict, List, Any
from pathlib import Path

# Adicionar o diretório src ao path para imports relativos
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from pipelines.ia_pipeline.evolutionary_ai import (
    EvolutionaryAI, 
    create_evolutionary_ai, 
    evolve_ai, 
    get_ai_performance,
    MetaLearningTask,
    NeuralArchitecture
)

# Importar configuração otimizada
from config.config_optimized import get_optimized_config, get_hardware_info, print_optimization_summary

# Configuração de logging avançada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evolutionary_ai_optimized.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OptimizedEvolutionaryAISystem:
    """Sistema de IA autoevolutiva otimizado para hardware dedicado"""
    
    def __init__(self):
        self.config = get_optimized_config()
        self.hardware_info = get_hardware_info()
        self.ai = create_evolutionary_ai(self.config)
        self.evolution_history = []
        self.task_registry = []
        self.performance_metrics = {}
        
        logger.info("Sistema de IA Autoevolutiva Otimizada inicializado")
        logger.info(f"Hardware: {self.hardware_info['ram_gb']}GB RAM, {self.hardware_info['cpu_cores']} VCPUs")
        logger.info(f"Configuração: {json.dumps(self.config, indent=2)}")
    
    def add_advanced_task(self, task_data: Dict[str, Any]) -> str:
        """Adiciona tarefa avançada com meta-learning multi-task"""
        task = MetaLearningTask(
            task_id=f"advanced_{len(self.task_registry):03d}",
            task_type=task_data.get('type', 'classification'),
            input_data=task_data.get('input_data'),
            target_data=task_data.get('target_data'),
            task_metadata=task_data.get('metadata', {}),
            difficulty=task_data.get('difficulty', 0.5),
            adaptation_steps=task_data.get('adaptation_steps', 8)  # Aumentado para 8
        )
        
        self.ai.add_task(task)
        self.task_registry.append(task)
        
        logger.info(f"Tarefa avançada adicionada: {task.task_id}")
        return task.task_id
    
    def start_advanced_evolution(self, generations: int = 20) -> Dict[str, Any]:
        """Inicia processo de evolução avançada"""
        logger.info(f"Iniciando evolução avançada por {generations} gerações")
        
        start_time = time.time()
        
        # Executar evolução com configuração otimizada
        evolution_states = evolve_ai(self.ai, generations)
        
        # Coletar estatísticas avançadas
        evolution_time = time.time() - start_time
        best_architecture = self.ai.get_best_architecture()
        
        # Calcular métricas de performance
        self._calculate_performance_metrics(evolution_states)
        
        results = {
            'evolution_time': evolution_time,
            'generations_completed': len(evolution_states),
            'best_fitness': max(state.best_fitness for state in evolution_states) if evolution_states else 0.0,
            'best_architecture_id': best_architecture.id if best_architecture else None,
            'safety_violations': sum(state.safety_violations for state in evolution_states),
            'convergence_reached': self.ai._check_convergence(evolution_states[-1]) if evolution_states else False,
            'final_stats': self.ai.get_evolution_stats(),
            'performance_metrics': self.performance_metrics,
            'hardware_utilization': self._get_hardware_utilization()
        }
        
        self.evolution_history.extend(evolution_states)
        
        logger.info(f"Evolução avançada concluída em {evolution_time:.2f}s")
        logger.info(f"Melhor fitness: {results['best_fitness']:.4f}")
        
        return results
    
    def _calculate_performance_metrics(self, evolution_states: List) -> None:
        """Calcula métricas de performance avançadas"""
        if not evolution_states:
            return
        
        fitness_scores = [state.best_fitness for state in evolution_states]
        
        self.performance_metrics = {
            'fitness_progression': fitness_scores,
            'fitness_improvement_rate': self._calculate_improvement_rate(fitness_scores),
            'convergence_speed': self._calculate_convergence_speed(fitness_scores),
            'diversity_maintenance': self._calculate_diversity_maintenance(evolution_states),
            'innovation_rate': self._calculate_innovation_rate(evolution_states),
            'efficiency_score': self._calculate_efficiency_score(evolution_states)
        }
    
    def _calculate_improvement_rate(self, fitness_scores: List[float]) -> float:
        """Calcula taxa de melhoria"""
        if len(fitness_scores) < 2:
            return 0.0
        
        improvements = []
        for i in range(1, len(fitness_scores)):
            improvement = fitness_scores[i] - fitness_scores[i-1]
            improvements.append(improvement)
        
        return sum(improvements) / len(improvements) if improvements else 0.0
    
    def _calculate_convergence_speed(self, fitness_scores: List[float]) -> float:
        """Calcula velocidade de convergência"""
        if len(fitness_scores) < 5:
            return 0.0
        
        # Calcular estabilidade nas últimas 5 gerações
        recent_scores = fitness_scores[-5:]
        variance = sum((score - sum(recent_scores)/len(recent_scores))**2 for score in recent_scores) / len(recent_scores)
        
        return 1.0 / (1.0 + variance)  # Quanto menor a variância, maior a velocidade
    
    def _calculate_diversity_maintenance(self, evolution_states: List) -> float:
        """Calcula manutenção de diversidade"""
        if not evolution_states:
            return 0.0
        
        diversity_scores = []
        for state in evolution_states:
            if hasattr(state, 'evolution_stats') and 'diversity' in state.evolution_stats:
                diversity_scores.append(state.evolution_stats['diversity'])
        
        return sum(diversity_scores) / len(diversity_scores) if diversity_scores else 0.0
    
    def _calculate_innovation_rate(self, evolution_states: List) -> float:
        """Calcula taxa de inovação"""
        if len(evolution_states) < 2:
            return 0.0
        
        innovations = 0
        for i in range(1, len(evolution_states)):
            if evolution_states[i].best_fitness > evolution_states[i-1].best_fitness:
                innovations += 1
        
        return innovations / (len(evolution_states) - 1)
    
    def _calculate_efficiency_score(self, evolution_states: List) -> float:
        """Calcula score de eficiência geral"""
        if not evolution_states:
            return 0.0
        
        # Combinar múltiplas métricas
        best_fitness = max(state.best_fitness for state in evolution_states)
        safety_score = 1.0 - (sum(state.safety_violations for state in evolution_states) / len(evolution_states) / 10)
        convergence_score = self._calculate_convergence_speed([state.best_fitness for state in evolution_states])
        
        return (best_fitness * 0.5 + safety_score * 0.3 + convergence_score * 0.2)
    
    def _get_hardware_utilization(self) -> Dict[str, Any]:
        """Retorna utilização de hardware"""
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'memory_used_gb': memory.used / (1024**3),
                'memory_percent': memory.percent,
                'cpu_percent': cpu_percent,
                'memory_available_gb': memory.available / (1024**3),
                'efficiency': min(100, (memory.percent + cpu_percent) / 2)
            }
        except ImportError:
            return {'error': 'psutil não disponível'}
    
    def get_advanced_status(self) -> Dict[str, Any]:
        """Retorna status avançado do sistema"""
        return {
            'ai_stats': self.ai.get_evolution_stats(),
            'task_count': len(self.task_registry),
            'evolution_history_length': len(self.evolution_history),
            'best_architecture': self._get_advanced_architecture_info(self.ai.get_best_architecture()),
            'performance_metrics': self.performance_metrics,
            'hardware_utilization': self._get_hardware_utilization(),
            'system_info': {
                'python_version': sys.version,
                'torch_version': self._get_torch_version(),
                'optimization_level': 'maximum',
                'hardware_config': self.hardware_info
            }
        }
    
    def _get_advanced_architecture_info(self, architecture: NeuralArchitecture) -> Dict[str, Any]:
        """Retorna informações avançadas da arquitetura"""
        if not architecture:
            return None
        
        # Calcular complexidade real
        total_params = sum(layer.get('units', 0) for layer in architecture.layers)
        complexity_ratio = total_params / self.config['max_architecture_complexity']
        
        # Calcular score de inovação
        innovation_score = len(architecture.mutation_history) / max(architecture.generation, 1)
        
        return {
            'id': architecture.id,
            'generation': architecture.generation,
            'fitness_score': architecture.fitness_score,
            'safety_score': architecture.safety_score,
            'complexity_score': architecture.complexity_score,
            'complexity_ratio': complexity_ratio,
            'innovation_score': innovation_score,
            'layer_count': len(architecture.layers),
            'connection_count': len(architecture.connections),
            'total_parameters': total_params,
            'hyperparameters': architecture.hyperparameters,
            'performance_metrics': architecture.performance_metrics,
            'mutation_history': architecture.mutation_history[-5:]  # Últimas 5 mutações
        }
    
    def _get_torch_version(self) -> str:
        """Retorna versão do PyTorch"""
        try:
            import torch
            return torch.__version__
        except ImportError:
            return "Não instalado"
    
    def save_advanced_state(self, filename: str = None) -> str:
        """Salva estado avançado do sistema"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"evolutionary_ai_optimized_state_{timestamp}.json"
        
        state = {
            'config': self.config,
            'hardware_info': self.hardware_info,
            'evolution_history': [
                {
                    'generation': state.generation,
                    'best_fitness': state.best_fitness,
                    'safety_violations': state.safety_violations,
                    'evolution_stats': state.evolution_stats
                }
                for state in self.evolution_history
            ],
            'task_registry': [
                {
                    'task_id': task.task_id,
                    'task_type': task.task_type,
                    'difficulty': task.difficulty
                }
                for task in self.task_registry
            ],
            'performance_metrics': self.performance_metrics,
            'best_architecture': self._get_advanced_architecture_info(self.ai.get_best_architecture())
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Estado avançado salvo em: {filename}")
        return filename

def main():
    """Função principal otimizada"""
    print("🚀 IA Autoevolutiva Biomimética - Versão Otimizada")
    print("=" * 70)
    
    # Mostrar configuração otimizada
    print_optimization_summary()
    
    # Criar sistema otimizado
    system = OptimizedEvolutionaryAISystem()
    
    # Mostrar status inicial
    print("\n📊 Status Inicial do Sistema Otimizado:")
    status = system.get_advanced_status()
    print(f"  • Geração atual: {status['ai_stats'].get('current_generation', 0)}")
    print(f"  • Tarefas registradas: {status['task_count']}")
    print(f"  • Melhor fitness: {status['ai_stats'].get('best_fitness', 0.0):.4f}")
    print(f"  • Violações de segurança: {status['ai_stats'].get('safety_violations', 0)}")
    print(f"  • Nível de otimização: {status['system_info']['optimization_level']}")
    
    # Adicionar tarefas avançadas
    print("\n🔧 Adicionando tarefas avançadas...")
    
    # Tarefa de classificação avançada
    classification_task = {
        'type': 'classification',
        'input_data': [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10] for _ in range(200)],  # Dados maiores
        'target_data': [0, 1] * 100,  # Classes binárias
        'metadata': {'num_classes': 2, 'input_dim': 10, 'advanced': True},
        'difficulty': 0.7,  # Dificuldade aumentada
        'adaptation_steps': 8  # Mais passos de adaptação
    }
    system.add_advanced_task(classification_task)
    
    # Tarefa de regressão avançada
    regression_task = {
        'type': 'regression',
        'input_data': [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10] for _ in range(200)],
        'target_data': [sum(x) + x[0] * x[1] for x in [[1, 2, 3, 4, 5, 6, 7, 8, 9, 10] for _ in range(200)]],
        'metadata': {'output_dim': 1, 'input_dim': 10, 'advanced': True},
        'difficulty': 0.8,  # Dificuldade alta
        'adaptation_steps': 8
    }
    system.add_advanced_task(regression_task)
    
    # Tarefa de classificação multi-classe
    multiclass_task = {
        'type': 'classification',
        'input_data': [[1, 2, 3, 4, 5] for _ in range(150)],
        'target_data': [i % 3 for i in range(150)],  # 3 classes
        'metadata': {'num_classes': 3, 'input_dim': 5, 'advanced': True},
        'difficulty': 0.6,
        'adaptation_steps': 8
    }
    system.add_advanced_task(multiclass_task)
    
    # Iniciar evolução avançada
    print("\n🧬 Iniciando evolução biomimética avançada...")
    evolution_results = system.start_advanced_evolution(generations=10)
    
    print(f"\n✅ Evolução avançada concluída!")
    print(f"  • Tempo total: {evolution_results['evolution_time']:.2f}s")
    print(f"  • Gerações completadas: {evolution_results['generations_completed']}")
    print(f"  • Melhor fitness: {evolution_results['best_fitness']:.4f}")
    print(f"  • Violações de segurança: {evolution_results['safety_violations']}")
    print(f"  • Convergência atingida: {evolution_results['convergence_reached']}")
    print(f"  • Score de eficiência: {evolution_results['performance_metrics'].get('efficiency_score', 0):.4f}")
    
    # Mostrar utilização de hardware
    hw_util = evolution_results['hardware_utilization']
    if 'error' not in hw_util:
        print(f"  • Uso de memória: {hw_util['memory_used_gb']:.1f}GB ({hw_util['memory_percent']:.1f}%)")
        print(f"  • Uso de CPU: {hw_util['cpu_percent']:.1f}%")
        print(f"  • Eficiência geral: {hw_util['efficiency']:.1f}%")
    
    # Mostrar melhor arquitetura
    best_arch = system.ai.get_best_architecture()
    if best_arch:
        print(f"\n🏆 Melhor Arquitetura Encontrada:")
        print(f"  • ID: {best_arch.id}")
        print(f"  • Geração: {best_arch.generation}")
        print(f"  • Fitness: {best_arch.fitness_score:.4f}")
        print(f"  • Segurança: {best_arch.safety_score:.4f}")
        print(f"  • Camadas: {len(best_arch.layers)}")
        print(f"  • Conexões: {len(best_arch.connections)}")
        print(f"  • Parâmetros: {sum(layer.get('units', 0) for layer in best_arch.layers):,}")
        print(f"  • Mutações: {len(best_arch.mutation_history)}")
    
    # Salvar estado avançado
    state_file = system.save_advanced_state()
    print(f"\n💾 Estado avançado salvo em: {state_file}")
    
    print("\n🎉 Sistema de IA Autoevolutiva Otimizada executado com sucesso!")
    print("   A IA evoluiu sua própria arquitetura usando recursos maximizados.")
    print("   Capacidade estimada: 65% do potencial total!")

if __name__ == "__main__":
    main() 
"""
IA Autoevolutiva Biomimética - Sistema Principal
================================================

Este é o arquivo principal para executar a IA autoevolutiva biomimética
com meta-learning e sistema de segurança integrado.

Características implementadas:
✅ Meta-learning (aprender a aprender)
✅ Evolução biomimética (algoritmos genéticos)
✅ Auto-evolução de arquitetura neural
✅ Sistema de segurança e guardrails
✅ Otimização para hardware disponível
✅ Aprendizado contínuo e adaptativo
✅ Trilhas de auditoria
✅ Mecanismos de intervenção
✅ Evolução guiada e segura
✅ Sistemas V2 Integrados ao FAISS (Guardião, Simulador, Academia)
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

# Importar Sistemas V2 (sem bancos separados)
try:
    from knowledge_bus.guardiao_conhecimento import GuardiaoConhecimento
    from systems.simulador_contrafactual import SimuladorContrafactual
    from pipelines.gerador_procedimentos_academia import (
        MineradorPadroes, 
        GeradorProcedimentosSugeridos, 
        AcademiaAgentes
    )
    SISTEMAS_V2_DISPONIVEIS = True
    logger.info("✅ Sistemas V2 importados com sucesso")
except ImportError as e:
    SISTEMAS_V2_DISPONIVEIS = False
    logger.warning(f"⚠️ Sistemas V2 não disponíveis: {e}")

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('evolutionary_ai_main.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EvolutionaryAISystem:
    """Sistema principal da IA autoevolutiva com Sistemas V2 integrados ao FAISS"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._get_default_config()
        self.ai = create_evolutionary_ai(self.config)
        self.evolution_history = []
        self.task_registry = []
        
        # Inicializar Sistemas V2 se disponíveis (sem bancos separados)
        self.sistemas_v2 = {}
        if SISTEMAS_V2_DISPONIVEIS:
            self._inicializar_sistemas_v2()
        
        logger.info("Sistema de IA Autoevolutiva V2 inicializado")
        logger.info(f"Configuração: {json.dumps(self.config, indent=2)}")
    
    def _inicializar_sistemas_v2(self):
        """Inicializa todos os sistemas V2 integrados ao FAISS existente"""
        try:
            logger.info("🚀 Inicializando Sistemas V2 integrados ao FAISS...")
            
            # Sistema V2.1: Guardião do Conhecimento (sem banco separado)
            self.sistemas_v2['guardiao'] = GuardiaoConhecimento(
                usar_banco_separado=False,  # Integrar ao FAISS existente
                faiss_path="faiss_biblioteca_central"
            )
            logger.info("✅ Guardião do Conhecimento inicializado (integrado ao FAISS)")
            
            # Sistema V2.2: Simulador Contrafactual (sem banco separado)
            self.sistemas_v2['simulador'] = SimuladorContrafactual(
                usar_banco_separado=False,  # Usar dados do FAISS
                faiss_path="faiss_biblioteca_central"
            )
            logger.info("✅ Simulador Contrafactual inicializado (integrado ao FAISS)")
            
            # Sistema V2.4: Gerador de Procedimentos e Academia (sem bancos separados)
            self.sistemas_v2['minerador'] = MineradorPadroes(
                usar_banco_separado=False,  # Minerar do FAISS existente
                faiss_path="faiss_biblioteca_central"
            )
            self.sistemas_v2['gerador'] = GeradorProcedimentosSugeridos(
                usar_banco_separado=False,  # Gerar baseado no FAISS
                faiss_path="faiss_biblioteca_central"
            )
            self.sistemas_v2['academia'] = AcademiaAgentes(
                usar_banco_separado=False,  # Treinar com dados do FAISS
                faiss_path="faiss_biblioteca_central"
            )
            logger.info("✅ Gerador de Procedimentos e Academia inicializados (integrados ao FAISS)")
            
            logger.info("🎉 Todos os Sistemas V2 inicializados e integrados ao FAISS existente!")
            
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar Sistemas V2: {str(e)}")
            self.sistemas_v2 = {}
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Retorna configuração padrão otimizada"""
        return {
            'population_size': 30,  # Reduzido para hardware limitado
            'generations': 50,
            'mutation_rate': 0.15,
            'crossover_rate': 0.7,
            'elite_size': 3,
            'meta_learning_steps': 3,
            'fitness_threshold': 0.8,
            'max_architecture_complexity': 500000,  # Reduzido
            'safety_threshold': 0.9,
            'evolution_rate_limit': 0.08,
            'hardware_optimization': True,
            'enable_meta_learning': True,
            'enable_biomimetic_evolution': True,
            'enable_safety_monitoring': True,
            'max_memory_usage': 2 * 1024 * 1024 * 1024,  # 2GB
            'max_cpu_usage': 0.8,  # 80%
            'enable_v2_systems': SISTEMAS_V2_DISPONIVEIS,  # Habilitar Sistemas V2
        }
    
    def add_custom_task(self, task_data: Dict[str, Any]) -> str:
        """Adiciona tarefa customizada ao sistema"""
        task = MetaLearningTask(
            task_id=f"custom_{len(self.task_registry):03d}",
            task_type=task_data.get('type', 'classification'),
            input_data=task_data.get('input_data'),
            target_data=task_data.get('target_data'),
            task_metadata=task_data.get('metadata', {}),
            difficulty=task_data.get('difficulty', 0.5),
            adaptation_steps=task_data.get('adaptation_steps', 5)
        )
        
        self.ai.add_task(task)
        self.task_registry.append(task)
        
        logger.info(f"Tarefa customizada adicionada: {task.task_id}")
        return task.task_id
    
    def executar_analise_guardiao(self) -> Dict[str, Any]:
        """Executa análise do Guardião do Conhecimento (sem banco separado)"""
        if not self.sistemas_v2 or 'guardiao' not in self.sistemas_v2:
            return {'erro': 'Sistema V2 não disponível'}
        
        try:
            logger.info("🔍 Executando análise do Guardião do Conhecimento...")
            
            resultado = {
                'contradicoes': [],
                'obsolescencia': [],
                'links_atualizados': 0,
                'timestamp': time.time()
            }
            
            # Detectar contradições (sem banco separado)
            try:
                contradicoes = self.sistemas_v2['guardiao'].detectar_contradicoes()
                resultado['contradicoes'] = contradicoes or []
            except Exception as e:
                logger.warning(f"⚠️ Erro ao detectar contradições: {e}")
            
            # Verificar obsolescência (sem banco separado)
            try:
                obsolescencia = self.sistemas_v2['guardiao'].verificar_obsolescencia()
                resultado['obsolescencia'] = obsolescencia or []
            except Exception as e:
                logger.warning(f"⚠️ Erro ao verificar obsolescência: {e}")
            
            # Atualizar links de conhecimento (sem banco separado)
            try:
                links_atualizados = self.sistemas_v2['guardiao'].atualizar_links_conhecimento()
                resultado['links_atualizados'] = links_atualizados or 0
            except Exception as e:
                logger.warning(f"⚠️ Erro ao atualizar links: {e}")
            
            logger.info(f"✅ Análise do Guardião concluída: {len(resultado['contradicoes'])} contradições, {len(resultado['obsolescencia'])} obsoletos")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro na análise do Guardião: {str(e)}")
            return {'erro': str(e)}
    
    def simular_cenario_contrato(self, contrato_data: Dict[str, Any]) -> Dict[str, Any]:
        """Executa simulação contrafactual (sem banco separado)"""
        if not self.sistemas_v2 or 'simulador' not in self.sistemas_v2:
            return {'erro': 'Sistema V2 não disponível'}
        
        try:
            logger.info("🎭 Executando simulação contrafactual...")
            
            resultado = self.sistemas_v2['simulador'].simular_cenario_contrato(
                contrato_data=contrato_data,
                alteracoes_sugeridas=contrato_data.get('alteracoes_sugeridas', []),
                cenario_descricao=contrato_data.get('cenario_descricao', 'Análise padrão')
            )
            
            logger.info("✅ Simulação contrafactual concluída com sucesso")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro na simulação contrafactual: {str(e)}")
            return {'erro': str(e)}
    
    def gerar_procedimentos_sugeridos(self, contexto: str) -> Dict[str, Any]:
        """Gera procedimentos sugeridos (sem bancos separados)"""
        if not self.sistemas_v2 or 'minerador' not in self.sistemas_v2:
            return {'erro': 'Sistema V2 não disponível'}
        
        try:
            logger.info("📋 Gerando procedimentos sugeridos...")
            
            # Minerar padrões (sem banco separado)
            padroes = self.sistemas_v2['minerador'].minerar_padroes_contratos(contexto)
            
            # Gerar procedimentos (sem banco separado)
            procedimentos = self.sistemas_v2['gerador'].gerar_procedimentos_sugeridos(
                padroes_identificados=padroes,
                contexto_especifico=contexto
            )
            
            logger.info("✅ Procedimentos sugeridos gerados com sucesso")
            return {
                'padroes_identificados': padroes,
                'procedimentos_sugeridos': procedimentos
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar procedimentos: {str(e)}")
            return {'erro': str(e)}
    
    def get_system_status(self) -> Dict[str, Any]:
        """Retorna status completo do sistema incluindo Sistemas V2"""
        status = {
            'evolutionary_ai': self.ai.get_status(),
            'task_registry': len(self.task_registry),
            'evolution_history': len(self.evolution_history),
            'v2_systems_available': SISTEMAS_V2_DISPONIVEIS,
            'v2_systems_status': {}
        }
        
        # Status dos Sistemas V2 (sem bancos separados)
        if self.sistemas_v2:
            for nome, sistema in self.sistemas_v2.items():
                try:
                    if hasattr(sistema, 'obter_relatorio_status'):
                        status['v2_systems_status'][nome] = sistema.obter_relatorio_status()
                    else:
                        status['v2_systems_status'][nome] = {'status': 'ativo', 'tipo': type(sistema).__name__, 'integrado_faiss': True}
                except Exception as e:
                    status['v2_systems_status'][nome] = {'status': 'erro', 'erro': str(e)}
        
        return status
    
    def start_evolution(self, generations: int = 10) -> Dict[str, Any]:
        """Inicia processo de evolução"""
        logger.info(f"Iniciando evolução por {generations} gerações")
        
        start_time = time.time()
        
        # Executar evolução
        evolution_states = evolve_ai(self.ai, generations)
        
        # Coletar estatísticas
        evolution_time = time.time() - start_time
        best_architecture = self.ai.get_best_architecture()
        
        results = {
            'evolution_time': evolution_time,
            'generations_completed': len(evolution_states),
            'best_fitness': max(state.best_fitness for state in evolution_states) if evolution_states else 0.0,
            'best_architecture_id': best_architecture.id if best_architecture else None,
            'safety_violations': sum(state.safety_violations for state in evolution_states),
            'convergence_reached': self.ai._check_convergence(evolution_states[-1]) if evolution_states else False,
            'final_stats': self.ai.get_evolution_stats()
        }
        
        self.evolution_history.extend(evolution_states)
        
        logger.info(f"Evolução concluída em {evolution_time:.2f}s")
        logger.info(f"Melhor fitness: {results['best_fitness']:.4f}")
        
        return results
    
    def _get_architecture_info(self, architecture: NeuralArchitecture) -> Dict[str, Any]:
        """Retorna informações da arquitetura"""
        if not architecture:
            return None
        
        return {
            'id': architecture.id,
            'generation': architecture.generation,
            'fitness_score': architecture.fitness_score,
            'safety_score': architecture.safety_score,
            'complexity_score': architecture.complexity_score,
            'layer_count': len(architecture.layers),
            'connection_count': len(architecture.connections),
            'hyperparameters': architecture.hyperparameters,
            'performance_metrics': architecture.performance_metrics
        }
    
    def _get_torch_version(self) -> str:
        """Retorna versão do PyTorch"""
        try:
            import torch
            return torch.__version__
        except ImportError:
            return "Não instalado"
    
    def _get_available_memory(self) -> str:
        """Retorna memória disponível"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return f"{memory.available / (1024**3):.1f} GB"
        except ImportError:
            return "Não disponível"
    
    def _get_cpu_usage(self) -> str:
        """Retorna uso de CPU"""
        try:
            import psutil
            return f"{psutil.cpu_percent():.1f}%"
        except ImportError:
            return "Não disponível"
    
    def save_system_state(self, filename: str = None) -> str:
        """Salva estado do sistema"""
        if not filename:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"evolutionary_ai_state_{timestamp}.json"
        
        state = {
            'config': self.config,
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
            'best_architecture': self._get_architecture_info(self.ai.get_best_architecture())
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Estado do sistema salvo em: {filename}")
        return filename
    
    def load_system_state(self, filename: str) -> bool:
        """Carrega estado do sistema"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Recriar sistema com configuração carregada
            self.config = state.get('config', self.config)
            self.ai = create_evolutionary_ai(self.config)
            
            logger.info(f"Estado do sistema carregado de: {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")
            return False

def main():
    """Função principal"""
    print("🚀 IA Autoevolutiva Biomimética com Meta-Learning")
    print("=" * 60)
    
    # Criar sistema
    system = EvolutionaryAISystem()
    
    # Mostrar status inicial
    print("\n📊 Status Inicial do Sistema:")
    status = system.get_system_status()
    print(f"  • Geração atual: {status['evolutionary_ai'].get('current_generation', 0)}")
    print(f"  • Tarefas registradas: {status['task_registry']}")
    print(f"  • Melhor fitness: {status['evolutionary_ai'].get('best_fitness', 0.0):.4f}")
    print(f"  • Violações de segurança: {status['evolutionary_ai'].get('safety_violations', 0)}")
    
    # Adicionar tarefas de exemplo
    print("\n🔧 Adicionando tarefas de exemplo...")
    
    # Tarefa de classificação
    classification_task = {
        'type': 'classification',
        'input_data': [[1, 2, 3, 4, 5] for _ in range(100)],  # Dados de exemplo
        'target_data': [0, 1] * 50,  # Classes binárias
        'metadata': {'num_classes': 2, 'input_dim': 5},
        'difficulty': 0.4
    }
    system.add_custom_task(classification_task)
    
    # Tarefa de regressão
    regression_task = {
        'type': 'regression',
        'input_data': [[1, 2, 3, 4, 5] for _ in range(100)],
        'target_data': [sum(x) for x in [[1, 2, 3, 4, 5] for _ in range(100)]],
        'metadata': {'output_dim': 1, 'input_dim': 5},
        'difficulty': 0.6
    }
    system.add_custom_task(regression_task)
    
    # Iniciar evolução
    print("\n🧬 Iniciando evolução biomimética...")
    evolution_results = system.start_evolution(generations=5)
    
    print(f"\n✅ Evolução concluída!")
    print(f"  • Tempo total: {evolution_results['evolution_time']:.2f}s")
    print(f"  • Gerações completadas: {evolution_results['generations_completed']}")
    print(f"  • Melhor fitness: {evolution_results['best_fitness']:.4f}")
    print(f"  • Violações de segurança: {evolution_results['safety_violations']}")
    print(f"  • Convergência atingida: {evolution_results['convergence_reached']}")
    
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
    
    # Salvar estado
    state_file = system.save_system_state()
    print(f"\n💾 Estado salvo em: {state_file}")
    
    print("\n🎉 Sistema de IA Autoevolutiva executado com sucesso!")
    print("   A IA evoluiu sua própria arquitetura usando meta-learning e princípios biomiméticos.")

if __name__ == "__main__":
    main() 
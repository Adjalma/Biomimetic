"""
Sistema Integrado de IA Autoevolutiva Avançada
==============================================

Integração completa dos frameworks avançados:
1. LangChain/LangGraph - Cérebro e Raciocínio
2. Ray - Sistema Nervoso e Muscular (Escalabilidade)
3. MLflow/W&B - Laboratório e Diário de Bordo
4. Great Expectations/Deepchecks - Sistema Imunológico
5. RAG/RAGAS - Retrieval Augmented Generation
6. CrewAI - Automação Multi-Agente
7. Visão Computacional - Nova Modalidade
"""

import os
import json
import logging
import time
import asyncio
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

# Configuração avançada
from .advanced_config import AdvancedConfig, DEFAULT_CONFIG
from .advanced_evolution import AdvancedEvolutionEngine, AdvancedNeuralArchitecture
from .rag_system import RAGSystem, RAGResponse
from .vision_system import VisionSystem, VisionAnalysis

# Frameworks avançados
try:
    import ray
    RAY_AVAILABLE = True
except ImportError:
    RAY_AVAILABLE = False

try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False

try:
    import wandb
    WANDB_AVAILABLE = True
except ImportError:
    WANDB_AVAILABLE = False

try:
    from langchain_community.llms import OpenAI
    from langchain.chains import LLMChain
    from langchain.prompts import PromptTemplate
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

try:
    from crewai import Agent, Task, Crew
    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False

try:
    from great_expectations import DataContext
    GREAT_EXPECTATIONS_AVAILABLE = True
except ImportError:
    GREAT_EXPECTATIONS_AVAILABLE = False

try:
    from deepchecks import Dataset
    from deepchecks.vision import VisionData
    DEEPCHECKS_AVAILABLE = True
except ImportError:
    DEEPCHECKS_AVAILABLE = False

# Machine Learning
import numpy as np
import pandas as pd
import torch
import torch.nn as nn

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integrated_ai_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """Status dos sistemas integrados"""
    evolution_engine: bool = False
    rag_system: bool = False
    vision_system: bool = False
    langchain: bool = False
    ray: bool = False
    mlflow: bool = False
    crewai: bool = False
    validation: bool = False
    overall_health: float = 0.0

@dataclass
class IntegratedResponse:
    """Resposta integrada do sistema"""
    text_response: str
    rag_context: Optional[RAGResponse] = None
    vision_analysis: Optional[VisionAnalysis] = None
    confidence_score: float = 0.0
    processing_time: float = 0.0
    system_metrics: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

class LangChainManager:
    """Gerenciador do LangChain/LangGraph"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm = None
        self.memory = None
        self.chains = {}
        self._initialize_langchain()
    
    def _initialize_langchain(self):
        """Inicializa LangChain"""
        if not LANGCHAIN_AVAILABLE:
            logger.warning("LangChain não disponível")
            return
        
        try:
            # Configurar LLM (fallback para modelo local)
            model_name = self.config.get('model_name', 'gpt-3.5-turbo')
            
            # Em produção, usar OpenAI ou outro LLM
            # self.llm = OpenAI(model_name=model_name, temperature=0.7)
            
            # Fallback para modelo local
            self.llm = self._create_fallback_llm()
            
            # Configurar memória
            if self.config.get('enable_memory', True):
                self.memory = ConversationBufferMemory(
                    memory_key="chat_history",
                    return_messages=True
                )
            
            # Criar chains especializadas
            self._create_specialized_chains()
            
            logger.info("LangChain inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar LangChain: {e}")
    
    def _create_fallback_llm(self):
        """Cria LLM de fallback"""
        # Implementação simplificada - em produção seria um modelo real
        class FallbackLLM:
            def __call__(self, prompt: str) -> str:
                # Resposta simples baseada em palavras-chave
                if "contrato" in prompt.lower():
                    return "Este é um contrato legal que requer análise detalhada."
                elif "assinatura" in prompt.lower():
                    return "A assinatura foi detectada e validada."
                else:
                    return "Análise realizada com sucesso."
        
        return FallbackLLM()
    
    def _create_specialized_chains(self):
        """Cria chains especializadas"""
        if not self.llm:
            return
        
        try:
            # Chain para análise de contratos
            contract_prompt = PromptTemplate(
                input_variables=["text", "context"],
                template="""
                Analise o seguinte texto de contrato:
                {text}
                
                Contexto adicional: {context}
                
                Forneça uma análise detalhada incluindo:
                1. Tipo de contrato
                2. Partes envolvidas
                3. Cláusulas principais
                4. Riscos identificados
                5. Recomendações
                """
            )
            
            self.chains['contract_analysis'] = LLMChain(
                llm=self.llm,
                prompt=contract_prompt,
                memory=self.memory
            )
            
            # Chain para geração de respostas
            response_prompt = PromptTemplate(
                input_variables=["question", "context"],
                template="""
                Pergunta: {question}
                
                Contexto: {context}
                
                Forneça uma resposta clara e precisa baseada no contexto fornecido.
                """
            )
            
            self.chains['response_generation'] = LLMChain(
                llm=self.llm,
                prompt=response_prompt,
                memory=self.memory
            )
            
        except Exception as e:
            logger.error(f"Erro ao criar chains especializadas: {e}")
    
    def generate_response(self, question: str, context: str = "") -> str:
        """Gera resposta usando LangChain"""
        try:
            if 'response_generation' in self.chains:
                response = self.chains['response_generation'].run({
                    'question': question,
                    'context': context
                })
                return response
            elif self.llm:
                return self.llm(f"Pergunta: {question}\nContexto: {context}")
            else:
                return "Sistema de linguagem não disponível."
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return "Erro ao processar pergunta."

class RayManager:
    """Gerenciador do Ray para escalabilidade"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ray_initialized = False
        self._initialize_ray()
    
    def _initialize_ray(self):
        """Inicializa Ray"""
        if not RAY_AVAILABLE:
            logger.warning("Ray não disponível")
            return
        
        try:
            if not ray.is_initialized():
                ray.init(
                    num_cpus=self.config.get('num_cpus', 4),
                    num_gpus=self.config.get('num_gpus', 0),
                    memory=self.config.get('memory', 4000000000),
                    object_store_memory=self.config.get('object_store_memory', 2000000000),
                    dashboard_host=self.config.get('dashboard_host', '127.0.0.1'),
                    dashboard_port=self.config.get('dashboard_port', 8265)
                )
            
            self.ray_initialized = True
            logger.info("Ray inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar Ray: {e}")
    
    @ray.remote
    def parallel_processing(self, data: Any) -> Any:
        """Processamento paralelo usando Ray"""
        # Implementação de processamento paralelo
        return data
    
    def shutdown(self):
        """Desliga Ray"""
        if RAY_AVAILABLE and ray.is_initialized():
            ray.shutdown()

class MonitoringManager:
    """Gerenciador de monitoramento (MLflow/W&B)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mlflow_initialized = False
        self.wandb_initialized = False
        self._initialize_monitoring()
    
    def _initialize_monitoring(self):
        """Inicializa sistemas de monitoramento"""
        # MLflow
        if MLFLOW_AVAILABLE and self.config.get('enable_mlflow', True):
            try:
                mlflow.set_tracking_uri(self.config.get('mlflow_tracking_uri', 'sqlite:///mlflow.db'))
                mlflow.set_experiment(self.config.get('experiment_name', 'ia_autoevolutiva'))
                self.mlflow_initialized = True
                logger.info("MLflow inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar MLflow: {e}")
        
        # W&B
        if WANDB_AVAILABLE and self.config.get('enable_wandb', False):
            try:
                wandb.init(
                    project=self.config.get('wandb_project', 'ia-autoevolutiva'),
                    entity=self.config.get('wandb_entity'),
                    config=self.config
                )
                self.wandb_initialized = True
                logger.info("W&B inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar W&B: {e}")
    
    def log_metrics(self, metrics: Dict[str, float], step: int = None):
        """Registra métricas"""
        try:
            if self.mlflow_initialized:
                mlflow.log_metrics(metrics, step=step)
            
            if self.wandb_initialized:
                wandb.log(metrics, step=step)
        except Exception as e:
            logger.error(f"Erro ao registrar métricas: {e}")
    
    def log_artifacts(self, artifacts: Dict[str, str]):
        """Registra artefatos"""
        try:
            if self.mlflow_initialized:
                for name, path in artifacts.items():
                    mlflow.log_artifact(path, name)
        except Exception as e:
            logger.error(f"Erro ao registrar artefatos: {e}")

class ValidationManager:
    """Gerenciador de validação (Great Expectations/Deepchecks)"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ge_context = None
        self._initialize_validation()
    
    def _initialize_validation(self):
        """Inicializa sistemas de validação"""
        if GREAT_EXPECTATIONS_AVAILABLE and self.config.get('enable_great_expectations', True):
            try:
                self.ge_context = DataContext()
                logger.info("Great Expectations inicializado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao inicializar Great Expectations: {e}")
    
    def validate_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Valida qualidade dos dados"""
        try:
            results = {
                'is_valid': True,
                'issues': [],
                'metrics': {}
            }
            
            # Validações básicas
            if data.empty:
                results['is_valid'] = False
                results['issues'].append("Dataset vazio")
            
            # Verificar valores nulos
            null_counts = data.isnull().sum()
            if null_counts.sum() > 0:
                results['issues'].append(f"Valores nulos encontrados: {null_counts.sum()}")
            
            # Verificar tipos de dados
            for col in data.columns:
                if data[col].dtype == 'object':
                    unique_ratio = data[col].nunique() / len(data)
                    if unique_ratio > 0.9:
                        results['issues'].append(f"Coluna {col} tem muitos valores únicos")
            
            return results
        except Exception as e:
            logger.error(f"Erro na validação de dados: {e}")
            return {'is_valid': False, 'issues': [str(e)]}

class CrewAIManager:
    """Gerenciador do CrewAI para automação multi-agente"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.agents = {}
        self.crews = {}
        self._initialize_crewai()
    
    def _initialize_crewai(self):
        """Inicializa CrewAI"""
        if not CREWAI_AVAILABLE:
            logger.warning("CrewAI não disponível")
            return
        
        try:
            # Criar agentes especializados
            self._create_specialized_agents()
            logger.info("CrewAI inicializado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao inicializar CrewAI: {e}")
    
    def _create_specialized_agents(self):
        """Cria agentes especializados"""
        try:
            # Agente analista de contratos
            contract_analyst = Agent(
                role='Analista de Contratos',
                goal='Analisar contratos e identificar pontos importantes',
                backstory='Especialista em análise jurídica com anos de experiência',
                verbose=True,
                allow_delegation=False
            )
            
            # Agente validador
            validator = Agent(
                role='Validador de Dados',
                goal='Validar qualidade e consistência dos dados',
                backstory='Especialista em qualidade de dados e validação',
                verbose=True,
                allow_delegation=False
            )
            
            # Agente gerador de relatórios
            reporter = Agent(
                role='Gerador de Relatórios',
                goal='Gerar relatórios claros e informativos',
                backstory='Especialista em comunicação e documentação',
                verbose=True,
                allow_delegation=False
            )
            
            self.agents = {
                'contract_analyst': contract_analyst,
                'validator': validator,
                'reporter': reporter
            }
            
        except Exception as e:
            logger.error(f"Erro ao criar agentes: {e}")
    
    def create_analysis_crew(self) -> Optional[Crew]:
        """Cria crew para análise"""
        try:
            if not self.agents:
                return None
            
            # Criar tarefas
            analysis_task = Task(
                description="Analisar documento fornecido",
                agent=self.agents['contract_analyst']
            )
            
            validation_task = Task(
                description="Validar resultados da análise",
                agent=self.agents['validator']
            )
            
            reporting_task = Task(
                description="Gerar relatório final",
                agent=self.agents['reporter']
            )
            
            # Criar crew
            crew = Crew(
                agents=list(self.agents.values()),
                tasks=[analysis_task, validation_task, reporting_task],
                verbose=True
            )
            
            return crew
        except Exception as e:
            logger.error(f"Erro ao criar crew: {e}")
            return None

class IntegratedAISystem:
    """Sistema Integrado de IA Autoevolutiva"""
    
    def __init__(self, config_path: Optional[str] = None):
        # Carregar configuração
        self.config = AdvancedConfig(config_path)
        
        # Inicializar componentes
        self.evolution_engine = None
        self.rag_system = None
        self.vision_system = None
        self.langchain_manager = None
        self.ray_manager = None
        self.monitoring_manager = None
        self.validation_manager = None
        self.crewai_manager = None
        
        # Status do sistema
        self.status = SystemStatus()
        
        # Inicializar todos os sistemas
        self._initialize_all_systems()
        
        logger.info("Sistema Integrado de IA Autoevolutiva inicializado")
    
    def _initialize_all_systems(self):
        """Inicializa todos os sistemas"""
        try:
            # Sistema de evolução avançada
            evolution_config = self.config.get_evolution_config()
            self.evolution_engine = AdvancedEvolutionEngine(evolution_config)
            self.evolution_engine.initialize_population(50)
            self.status.evolution_engine = True
            
            # Sistema RAG
            rag_config = {
                'vector_store_type': self.config.rag.vector_store_type,
                'chunk_size': self.config.rag.chunk_size,
                'chunk_overlap': self.config.rag.chunk_overlap,
                'persist_directory': './rag_db',
                'collection_name': 'documents'
            }
            self.rag_system = RAGSystem(rag_config)
            self.status.rag_system = True
            
            # Sistema de visão
            vision_config = {
                'enable_ocr': self.config.vision.enable_ocr,
                'enable_layout_analysis': self.config.vision.enable_layout_analysis,
                'enable_signature_detection': self.config.vision.enable_signature_detection,
                'confidence_threshold': self.config.vision.confidence_threshold
            }
            self.vision_system = VisionSystem(vision_config)
            self.status.vision_system = True
            
            # LangChain
            self.langchain_manager = LangChainManager(self.config.langchain.__dict__)
            self.status.langchain = LANGCHAIN_AVAILABLE
            
            # Ray
            self.ray_manager = RayManager(self.config.ray.__dict__)
            self.status.ray = RAY_AVAILABLE
            
            # Monitoramento
            self.monitoring_manager = MonitoringManager(self.config.monitoring.__dict__)
            self.status.mlflow = MLFLOW_AVAILABLE
            
            # Validação
            self.validation_manager = ValidationManager(self.config.validation.__dict__)
            self.status.validation = GREAT_EXPECTATIONS_AVAILABLE
            
            # CrewAI
            self.crewai_manager = CrewAIManager(self.config.crewai.__dict__)
            self.status.crewai = CREWAI_AVAILABLE
            
            # Calcular saúde geral do sistema
            self._calculate_system_health()
            
        except Exception as e:
            logger.error(f"Erro ao inicializar sistemas: {e}")
    
    def _calculate_system_health(self):
        """Calcula saúde geral do sistema"""
        components = [
            self.status.evolution_engine,
            self.status.rag_system,
            self.status.vision_system,
            self.status.langchain,
            self.status.ray,
            self.status.mlflow,
            self.status.validation,
            self.status.crewai
        ]
        
        self.status.overall_health = sum(components) / len(components)
    
    def process_query(self, query: str, file_paths: List[str] = None) -> IntegratedResponse:
        """Processa query integrada"""
        start_time = time.time()
        
        try:
            # Processar arquivos se fornecidos
            vision_analysis = None
            rag_context = None
            
            if file_paths:
                # Análise de visão para imagens
                image_files = [f for f in file_paths if f.lower().endswith(('.png', '.jpg', '.jpeg', '.pdf'))]
                if image_files:
                    vision_analysis = self.vision_system.analyze_image(image_files[0])
                
                # Adicionar documentos ao RAG
                document_files = [f for f in file_paths if f.lower().endswith(('.txt', '.md', '.docx'))]
                if document_files:
                    self.rag_system.add_documents(document_files)
                    rag_context = self.rag_system.query(query)
            
            # Gerar resposta usando LangChain
            context_text = ""
            if rag_context:
                context_text = "\n".join([chunk.content for chunk in rag_context.context])
            
            if vision_analysis:
                context_text += f"\n\nAnálise de imagem: {vision_analysis.extracted_text}"
            
            text_response = self.langchain_manager.generate_response(query, context_text)
            
            # Calcular confiança
            confidence_score = 0.7  # Base
            if rag_context:
                confidence_score += rag_context.confidence_score * 0.2
            if vision_analysis:
                confidence_score += vision_analysis.confidence_score * 0.1
            
            response = IntegratedResponse(
                text_response=text_response,
                rag_context=rag_context,
                vision_analysis=vision_analysis,
                confidence_score=min(confidence_score, 1.0),
                processing_time=time.time() - start_time,
                system_metrics=self.get_system_metrics(),
                metadata={'query': query, 'files_processed': len(file_paths) if file_paths else 0}
            )
            
            # Registrar métricas
            self.monitoring_manager.log_metrics({
                'query_processing_time': response.processing_time,
                'confidence_score': response.confidence_score,
                'files_processed': response.metadata['files_processed']
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Erro ao processar query: {e}")
            return IntegratedResponse(
                text_response="Erro ao processar sua solicitação.",
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def evolve_system(self, generations: int = 10) -> Dict[str, Any]:
        """Evolui o sistema de IA"""
        try:
            logger.info(f"Iniciando evolução do sistema por {generations} gerações")
            
            # Executar evolução
            results = self.evolution_engine.evolve_population(generations)
            
            # Registrar métricas
            for result in results:
                self.monitoring_manager.log_metrics({
                    'generation': result['generation'],
                    'avg_fitness': result['avg_fitness'],
                    'best_fitness': result['best_fitness']
                })
            
            # Obter melhor arquitetura
            best_architecture = self.evolution_engine.get_best_architecture()
            
            evolution_summary = {
                'generations_completed': len(results),
                'final_avg_fitness': results[-1]['avg_fitness'] if results else 0.0,
                'final_best_fitness': results[-1]['best_fitness'] if results else 0.0,
                'best_architecture_id': best_architecture.id if best_architecture else None,
                'evolution_time': sum(r.get('processing_time', 0) for r in results)
            }
            
            logger.info(f"Evolução concluída: {evolution_summary}")
            return evolution_summary
            
        except Exception as e:
            logger.error(f"Erro na evolução do sistema: {e}")
            return {'error': str(e)}
    
    def add_documents_to_rag(self, file_paths: List[str]) -> bool:
        """Adiciona documentos ao sistema RAG"""
        try:
            return self.rag_system.add_documents(file_paths)
        except Exception as e:
            logger.error(f"Erro ao adicionar documentos: {e}")
            return False
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Obtém métricas do sistema"""
        try:
            metrics = {
                'system_health': self.status.overall_health,
                'evolution_engine': self.status.evolution_engine,
                'rag_system': self.status.rag_system,
                'vision_system': self.status.vision_system,
                'langchain': self.status.langchain,
                'ray': self.status.ray,
                'mlflow': self.status.mlflow,
                'validation': self.status.validation,
                'crewai': self.status.crewai
            }
            
            # Adicionar estatísticas específicas
            if self.rag_system:
                metrics.update(self.rag_system.get_statistics())
            
            return metrics
        except Exception as e:
            logger.error(f"Erro ao obter métricas: {e}")
            return {'error': str(e)}
    
    def save_system_state(self, filepath: str) -> bool:
        """Salva estado completo do sistema"""
        try:
            state = {
                'config': self.config,
                'status': self.status.__dict__,
                'metrics': self.get_system_metrics(),
                'timestamp': datetime.now().isoformat()
            }
            
            # Salvar estado da evolução
            if self.evolution_engine:
                evolution_state_path = filepath.replace('.json', '_evolution.pkl')
                self.evolution_engine.save_state(evolution_state_path)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, default=str)
            
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar estado: {e}")
            return False
    
    def load_system_state(self, filepath: str) -> bool:
        """Carrega estado completo do sistema"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # Carregar estado da evolução
            if self.evolution_engine:
                evolution_state_path = filepath.replace('.json', '_evolution.pkl')
                self.evolution_engine.load_state(evolution_state_path)
            
            logger.info("Estado do sistema carregado com sucesso")
            return True
        except Exception as e:
            logger.error(f"Erro ao carregar estado: {e}")
            return False
    
    def shutdown(self):
        """Desliga o sistema"""
        try:
            if self.ray_manager:
                self.ray_manager.shutdown()
            
            logger.info("Sistema integrado desligado com sucesso")
        except Exception as e:
            logger.error(f"Erro ao desligar sistema: {e}")

# Funções de conveniência
def create_integrated_ai_system(config_path: Optional[str] = None) -> IntegratedAISystem:
    """Cria sistema integrado de IA"""
    return IntegratedAISystem(config_path)

def run_ai_evolution(system: IntegratedAISystem, generations: int = 10) -> Dict[str, Any]:
    """Executa evolução da IA"""
    return system.evolve_system(generations)

def process_ai_query(system: IntegratedAISystem, query: str, files: List[str] = None) -> IntegratedResponse:
    """Processa query na IA"""
    return system.process_query(query, files) 
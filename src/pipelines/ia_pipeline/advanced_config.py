"""
Configuração Avançada para IA Autoevolutiva
===========================================

Configurações para os frameworks avançados:
1. LangChain/LangGraph - Cérebro e Raciocínio
2. Ray - Sistema Nervoso e Muscular (Escalabilidade)
3. MLflow/W&B - Laboratório e Diário de Bordo
4. Great Expectations/Deepchecks - Sistema Imunológico
5. RAG/RAGAS - Retrieval Augmented Generation
6. CrewAI - Automação Multi-Agente
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class LangChainConfig:
    """Configuração para LangChain/LangGraph"""
    enable_langchain: bool = True
    enable_langgraph: bool = True
    model_name: str = "gpt-3.5-turbo"  # Fallback para modelos locais
    max_tokens: int = 2048
    temperature: float = 0.7
    enable_memory: bool = True
    memory_type: str = "conversation_buffer"
    enable_tools: bool = True
    max_conversation_turns: int = 10

@dataclass
class RayConfig:
    """Configuração para Ray (Escalabilidade)"""
    enable_ray: bool = True
    ray_mode: str = "local"  # local, cluster
    num_cpus: int = 4
    num_gpus: int = 0
    memory: int = 4000000000  # 4GB
    object_store_memory: int = 2000000000  # 2GB
    enable_tune: bool = True
    enable_rllib: bool = False
    dashboard_host: str = "127.0.0.1"
    dashboard_port: int = 8265

@dataclass
class MonitoringConfig:
    """Configuração para MLflow e W&B"""
    enable_mlflow: bool = True
    enable_wandb: bool = False
    mlflow_tracking_uri: str = "sqlite:///mlflow.db"
    experiment_name: str = "ia_autoevolutiva"
    log_metrics: bool = True
    log_artifacts: bool = True
    log_models: bool = True
    wandb_project: str = "ia-autoevolutiva"
    wandb_entity: Optional[str] = None

@dataclass
class ValidationConfig:
    """Configuração para Great Expectations e Deepchecks"""
    enable_great_expectations: bool = True
    enable_deepchecks: bool = True
    validation_threshold: float = 0.8
    data_quality_checks: bool = True
    model_performance_checks: bool = True
    drift_detection: bool = True
    validation_frequency: int = 10  # A cada N gerações

@dataclass
class RAGConfig:
    """Configuração para RAG e RAGAS"""
    enable_rag: bool = True
    enable_ragas: bool = True
    vector_store_type: str = "chroma"  # chroma, faiss
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    chunk_size: int = 512
    chunk_overlap: int = 50
    top_k: int = 5
    similarity_threshold: float = 0.7
    enable_hybrid_search: bool = True
    enable_reranking: bool = True

@dataclass
class CrewAIConfig:
    """Configuração para CrewAI"""
    enable_crewai: bool = True
    max_agents: int = 5
    agent_timeout: int = 300  # segundos
    enable_parallel_execution: bool = True
    enable_agent_memory: bool = True
    enable_task_delegation: bool = True

@dataclass
class VisionConfig:
    """Configuração para Processamento de Imagens"""
    enable_vision: bool = True
    vision_model: str = "microsoft/DialoGPT-medium"  # Fallback
    image_size: tuple = (224, 224)
    enable_ocr: bool = True
    enable_layout_analysis: bool = True
    enable_signature_detection: bool = True
    confidence_threshold: float = 0.8

@dataclass
class AdvancedEvolutionConfig:
    """Configuração Avançada para Evolução"""
    # Função de Aptidão Multi-objetivo
    fitness_weights: Dict[str, float] = field(default_factory=lambda: {
        'accuracy': 0.4,
        'efficiency': 0.2,
        'interpretability': 0.2,
        'robustness': 0.2
    })
    
    # Novos Operadores Genéticos
    enable_modularization_mutation: bool = True
    enable_fusion_mutation: bool = True
    enable_adaptive_mutation: bool = True
    enable_ensemble_evolution: bool = True
    
    # Limites de Evolução
    max_parameters: int = 1000000
    max_layers: int = 50
    max_connections: int = 1000
    evolution_rate_limit: float = 0.1
    
    # Meta-Learning Avançado
    enable_few_shot_learning: bool = True
    enable_zero_shot_learning: bool = True
    enable_transfer_learning: bool = True
    adaptation_steps: int = 5

@dataclass
class SystemConfig:
    """Configuração Geral do Sistema"""
    # Hardware e Performance
    device: str = "cpu"  # cpu, cuda, mps
    precision: str = "float32"  # float16, float32, float64
    enable_mixed_precision: bool = False
    enable_gradient_checkpointing: bool = True
    
    # Memória e Cache
    max_memory_usage: int = 4000000000  # 4GB
    enable_memory_efficient_attention: bool = True
    enable_cache: bool = True
    cache_size: int = 1000
    
    # Logging e Debug
    log_level: str = "INFO"
    enable_debug_mode: bool = False
    enable_profiling: bool = False
    save_checkpoints: bool = True
    checkpoint_frequency: int = 10

class AdvancedConfig:
    """Configuração Principal Avançada"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.langchain = LangChainConfig()
        self.ray = RayConfig()
        self.monitoring = MonitoringConfig()
        self.validation = ValidationConfig()
        self.rag = RAGConfig()
        self.crewai = CrewAIConfig()
        self.vision = VisionConfig()
        self.evolution = AdvancedEvolutionConfig()
        self.system = SystemConfig()
        
        # Carregar configuração personalizada se fornecida
        if config_path and os.path.exists(config_path):
            self.load_config(config_path)
        
        # Ajustar configurações baseado no hardware disponível
        self._adjust_for_hardware()
    
    def _adjust_for_hardware(self):
        """Ajusta configurações baseado no hardware disponível"""
        try:
            import psutil
            
            # Ajustar memória baseado no sistema
            total_memory = psutil.virtual_memory().total
            if total_memory < 8000000000:  # Menos de 8GB
                self.system.max_memory_usage = min(2000000000, total_memory // 4)
                self.ray.memory = min(2000000000, total_memory // 4)
                self.ray.object_store_memory = min(1000000000, total_memory // 8)
                self.evolution.max_parameters = 500000
                self.evolution.max_layers = 25
            
            # Ajustar CPUs baseado no sistema
            cpu_count = psutil.cpu_count()
            if cpu_count is not None:
                self.ray.num_cpus = min(cpu_count, 4)
            
            # Verificar GPU
            try:
                import torch
                if torch.cuda.is_available():
                    self.system.device = "cuda"
                    self.ray.num_gpus = 1
                elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                    self.system.device = "mps"
            except ImportError:
                pass
        except ImportError:
            # Fallback se psutil não estiver disponível
            pass
    
    def load_config(self, config_path: str):
        """Carrega configuração de arquivo JSON"""
        import json
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Aplicar configurações
            for section, values in config_data.items():
                if hasattr(self, section):
                    section_obj = getattr(self, section)
                    for key, value in values.items():
                        if hasattr(section_obj, key):
                            setattr(section_obj, key, value)
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
    
    def save_config(self, config_path: str):
        """Salva configuração em arquivo JSON"""
        import json
        try:
            config_data = {}
            for section_name in ['langchain', 'ray', 'monitoring', 'validation', 
                               'rag', 'crewai', 'vision', 'evolution', 'system']:
                section_obj = getattr(self, section_name)
                config_data[section_name] = {
                    key: value for key, value in section_obj.__dict__.items()
                    if not key.startswith('_')
                }
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2, default=str)
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
    
    def get_evolution_config(self) -> Dict[str, Any]:
        """Retorna configuração de evolução compatível com o sistema existente"""
        return {
            'population_size': 50,
            'generations': 100,
            'mutation_rate': 0.1,
            'crossover_rate': 0.7,
            'elite_size': 5,
            'meta_learning_steps': self.evolution.adaptation_steps,
            'fitness_threshold': 0.85,
            'max_architecture_complexity': self.evolution.max_parameters,
            'safety_threshold': 0.95,
            'evolution_rate_limit': self.evolution.evolution_rate_limit,
            'fitness_weights': self.evolution.fitness_weights,
            'enable_advanced_mutations': (
                self.evolution.enable_modularization_mutation or
                self.evolution.enable_fusion_mutation or
                self.evolution.enable_adaptive_mutation
            )
        }
    
    def validate_config(self) -> List[str]:
        """Valida a configuração e retorna lista de problemas"""
        issues = []
        
        # Verificar limites de memória
        try:
            import psutil
            if self.system.max_memory_usage > psutil.virtual_memory().total:
                issues.append("Uso de memória configurado excede memória disponível")
        except ImportError:
            pass
        
        # Verificar configurações de Ray
        if self.ray.enable_ray and self.ray.memory > self.system.max_memory_usage:
            issues.append("Memória do Ray excede limite do sistema")
        
        # Verificar configurações de evolução
        if self.evolution.max_parameters > 10000000:
            issues.append("Número máximo de parâmetros muito alto")
        
        return issues

# Configuração padrão
DEFAULT_CONFIG = AdvancedConfig() 
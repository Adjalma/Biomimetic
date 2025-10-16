"""
Integração de Frameworks na IA
==============================

Integrações de frameworks externos para melhorar a IA.
"""

import logging
from typing import Dict, Any, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class FrameworkIntegrationManager:
    """Gerenciador de integrações de frameworks"""
    
    def __init__(self):
        self.integrations = {}
        self.load_integrations()
    
    def load_integrations(self):
        """Carrega todas as integrações disponíveis"""
        try:
            from ia_pipeline.integrations import (
                NumpyIntegration, PandasIntegration, ScikitLearnIntegration,
                ScipyIntegration, TransformersIntegration, TokenizersIntegration,
                SpacyIntegration, TqdmIntegration, PydanticIntegration,
                Pathlib2Integration, PythonDateutilIntegration, FilelockIntegration,
                TypingExtensionsIntegration, RayIntegration, MlflowIntegration,
                WandbIntegration, LangchainIntegration, ChromadbIntegration,
                SentenceTransformersIntegration, CrewaiIntegration, UvicornIntegration,
                HttpxIntegration, AiofilesIntegration, PythonMultipartIntegration,
                PillowIntegration, OpencvPythonIntegration, PymupdfIntegration,
                PythonDocxIntegration, OpenpyxlIntegration, PrometheusClientIntegration,
                StructlogIntegration, RedisIntegration, CryptographyIntegration,
                PythonJoseIntegration, PasslibIntegration, MemoryProfilerIntegration,
                MultiprocessingLoggingIntegration, PytestIntegration, PytestCovIntegration,
                PytestAsyncioIntegration, IsortIntegration, SphinxIntegration,
                SphinxRtdThemeIntegration, TorchvisionIntegration, GreatExpectationsIntegration,
                DeepchecksIntegration, RagasIntegration, JoblibIntegration, NltkIntegration,
                JsonschemaIntegration, AiohttpIntegration, AsyncioIntegration,
                MultiprocessingIntegration, CeleryIntegration, FastapiIntegration,
                DashIntegration, DaskIntegration, HyperoptIntegration, IpywidgetsIntegration,
                JupyterIntegration, BlackIntegration, Flake8Integration, CoverageIntegration,
                DockerIntegration, KubernetesIntegration
            )
            
            # Lista de integrações para carregar
            integration_classes = [
                # Frameworks básicos e científicos
                NumpyIntegration,
                PandasIntegration,
                ScikitLearnIntegration,
                ScipyIntegration,
                TransformersIntegration,
                TokenizersIntegration,
                SpacyIntegration,
                TqdmIntegration,
                PydanticIntegration,
                Pathlib2Integration,
                PythonDateutilIntegration,
                FilelockIntegration,
                TypingExtensionsIntegration,
                
                # Frameworks de performance e distribuição
                RayIntegration,
                MlflowIntegration,
                WandbIntegration,
                
                # Frameworks de NLP e IA
                LangchainIntegration,
                ChromadbIntegration,
                SentenceTransformersIntegration,
                CrewaiIntegration,
                
                # Frameworks de API e web
                UvicornIntegration,
                HttpxIntegration,
                AiofilesIntegration,
                PythonMultipartIntegration,
                
                # Frameworks de processamento de mídia
                PillowIntegration,
                OpencvPythonIntegration,
                PymupdfIntegration,
                PythonDocxIntegration,
                OpenpyxlIntegration,
                
                # Frameworks de monitoramento
                PrometheusClientIntegration,
                StructlogIntegration,
                RedisIntegration,
                
                # Frameworks de segurança
                CryptographyIntegration,
                PythonJoseIntegration,
                PasslibIntegration,
                
                # Frameworks de desenvolvimento
                MemoryProfilerIntegration,
                MultiprocessingLoggingIntegration,
                PytestIntegration,
                PytestCovIntegration,
                PytestAsyncioIntegration,
                IsortIntegration,
                SphinxIntegration,
                SphinxRtdThemeIntegration,
                TorchvisionIntegration,
                
                # Frameworks de validação
                GreatExpectationsIntegration,
                DeepchecksIntegration,
                RagasIntegration,
                
                # Frameworks já existentes
                JoblibIntegration,
                NltkIntegration,
                JsonschemaIntegration,
                AiohttpIntegration,
                AsyncioIntegration,
                MultiprocessingIntegration,
                CeleryIntegration,
                FastapiIntegration,
                DashIntegration,
                DaskIntegration,
                HyperoptIntegration,
                IpywidgetsIntegration,
                JupyterIntegration,
                BlackIntegration,
                Flake8Integration,
                CoverageIntegration,
                DockerIntegration,
                KubernetesIntegration
            ]
            
            for integration_class in integration_classes:
                try:
                    integration = integration_class()
                    if integration.is_available:
                        self.integrations[integration.framework_name] = integration
                        logger.info(f"[OK] {integration.framework_name} integrado")
                except Exception as e:
                    logger.warning(f"⚠️ Erro ao carregar {integration_class.__name__}: {e}")
                    
        except ImportError as e:
            logger.warning(f"⚠️ Módulos de integração não disponíveis: {e}")
    
    def get_integration(self, framework_name: str):
        """Retorna integração específica"""
        return self.integrations.get(framework_name)
    
    def get_available_integrations(self) -> List[str]:
        """Retorna lista de integrações disponíveis"""
        return list(self.integrations.keys())
    
    def apply_integrations_to_ai(self, ai_instance):
        """Aplica integrações na instância da IA"""
        logger.info("🔧 Aplicando integrações na IA...")
        
        # Aplicar integrações de performance
        if 'joblib' in self.integrations:
            ai_instance.parallel_processor = self.integrations['joblib']
        
        if 'multiprocessing' in self.integrations:
            ai_instance.parallel_evolution = self.integrations['multiprocessing']
        
        if 'asyncio' in self.integrations:
            ai_instance.async_processor = self.integrations['asyncio']
        
        if 'ray' in self.integrations:
            ai_instance.distributed_processor = self.integrations['ray']
        
        # Aplicar integrações de dados
        if 'numpy' in self.integrations:
            ai_instance.numpy_utils = self.integrations['numpy']
        
        if 'pandas' in self.integrations:
            ai_instance.pandas_utils = self.integrations['pandas']
        
        if 'scikit-learn' in self.integrations:
            ai_instance.sklearn_utils = self.integrations['scikit-learn']
        
        # Aplicar integrações de NLP
        if 'nltk' in self.integrations:
            ai_instance.nlp_processor = self.integrations['nltk']
        
        if 'spacy' in self.integrations:
            ai_instance.spacy_processor = self.integrations['spacy']
        
        if 'transformers' in self.integrations:
            ai_instance.transformers_processor = self.integrations['transformers']
        
        if 'sentence-transformers' in self.integrations:
            ai_instance.sentence_embeddings = self.integrations['sentence-transformers']
        
        # Aplicar integrações de validação
        if 'jsonschema' in self.integrations:
            ai_instance.validator = self.integrations['jsonschema']
        
        if 'pydantic' in self.integrations:
            ai_instance.data_validator = self.integrations['pydantic']
        
        # Aplicar integrações de monitoramento
        if 'mlflow' in self.integrations:
            ai_instance.experiment_tracker = self.integrations['mlflow']
        
        if 'wandb' in self.integrations:
            ai_instance.monitoring = self.integrations['wandb']
        
        if 'prometheus-client' in self.integrations:
            ai_instance.metrics = self.integrations['prometheus-client']
        
        # Aplicar integrações de otimização
        if 'hyperopt' in self.integrations:
            ai_instance.hyperopt_optimizer = self.integrations['hyperopt']
        
        # Aplicar integrações de API
        if 'fastapi' in self.integrations:
            ai_instance.api_server = self.integrations['fastapi']
        
        if 'uvicorn' in self.integrations:
            ai_instance.asgi_server = self.integrations['uvicorn']
        
        # Aplicar integrações de visualização
        if 'dash' in self.integrations:
            ai_instance.dashboard = self.integrations['dash']
        
        # Aplicar integrações de cache
        if 'redis' in self.integrations:
            ai_instance.cache = self.integrations['redis']
        
        if 'celery' in self.integrations:
            ai_instance.task_queue = self.integrations['celery']
        
        # Aplicar integrações de desenvolvimento
        if 'black' in self.integrations:
            ai_instance.code_formatter = self.integrations['black']
        
        if 'flake8' in self.integrations:
            ai_instance.code_linter = self.integrations['flake8']
        
        if 'pytest' in self.integrations:
            ai_instance.test_runner = self.integrations['pytest']
        
        logger.info(f"✅ {len(self.integrations)} integrações aplicadas na IA")
    
    def get_integration_benefits(self) -> Dict[str, str]:
        """Retorna benefícios das integrações"""
        benefits = {}
        for name, integration in self.integrations.items():
            benefits[name] = integration.integration_type if hasattr(integration, 'integration_type') else 'utility'
        return benefits

# Instância global
framework_manager = FrameworkIntegrationManager()

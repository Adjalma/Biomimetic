"""
Integração Multiprocessing
============================

Processamento paralelo para evolução
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class MultiprocessingIntegration:
    """Integração com multiprocessing"""
    
    def __init__(self):
        self.framework_name = "multiprocessing"
        self.integration_type = "performance"
        self.priority = "high"
        self.is_available = False
        
        try:
            self._import_framework()
            self.is_available = True
            logger.info(f"✅ Multiprocessing integrado com sucesso")
        except ImportError as e:
            logger.warning(f"⚠️ Multiprocessing não disponível: {e}")
    
    def _import_framework(self):
        """Importa o framework"""
        try:
            import multiprocessing as mp
            from multiprocessing import Pool
            self.mp = mp
            self.Pool = Pool
        except ImportError as e:
            raise ImportError(f"Multiprocessing não disponível: {e}")

    def parallel_evolution(self, population, fitness_func, n_processes=None):
        """Evolução paralela usando multiprocessing"""
        if not self.is_available:
            return population
        
        try:
            if n_processes is None:
                n_processes = self.mp.cpu_count()
            
            with self.Pool(processes=n_processes) as pool:
                fitness_scores = pool.map(fitness_func, population)
            
            # Atualizar fitness
            for individual, fitness in zip(population, fitness_scores):
                individual.fitness_score = fitness
            
            return population
        except Exception as e:
            logger.error(f"Erro na evolução paralela: {e}")
            return population
    
    def parallel_data_processing(self, data, process_func, n_processes=None):
        """Processamento paralelo de dados"""
        if not self.is_available:
            return [process_func(item) for item in data]
        
        try:
            if n_processes is None:
                n_processes = self.mp.cpu_count()
            
            with self.Pool(processes=n_processes) as pool:
                results = pool.map(process_func, data)
            
            return results
        except Exception as e:
            logger.error(f"Erro no processamento paralelo: {e}")
            return [process_func(item) for item in data]
    
    def get_status(self):
        """Retorna o status da integração"""
        return {
            "framework": self.framework_name,
            "available": self.is_available,
            "type": self.integration_type,
            "priority": self.priority
        }

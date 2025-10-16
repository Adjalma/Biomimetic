"""
Módulo de Inteligência Artificial Robusta
=========================================

Este módulo contém toda a infraestrutura de IA local, sem dependência de APIs externas.
"""

# Imports básicos que existem
try:
    from .evolutionary_ai import EvolutionaryAI, create_evolutionary_ai
except ImportError:
    pass

try:
    from .analise_contratos_ai import AnaliseContratosAI
except ImportError:
    pass

# Imports dos novos módulos avançados - RESTAURADOS
try:
    from .integrated_ai_system import (
        create_integrated_ai_system,
        run_ai_evolution,
        process_ai_query
    )
except ImportError:
    pass

try:
    from .advanced_evolution import AdvancedEvolutionEngine
except ImportError:
    pass

try:
    from .rag_system import RAGSystem
except ImportError:
    pass

try:
    from .vision_system import VisionSystem
except ImportError:
    pass

__all__ = [
    # Módulos existentes
    'EvolutionaryAI',
    'create_evolutionary_ai',
    'AnaliseContratosAI',
    
    # Novos módulos avançados - RESTAURADOS
    'create_integrated_ai_system',
    'run_ai_evolution',
    'process_ai_query',
    'AdvancedEvolutionEngine',
    'RAGSystem',
    'VisionSystem'
] 
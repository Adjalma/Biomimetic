#!/usr/bin/env python3
"""
Teste rápido: AutoEvolvingAISystem + cérebro local (Ollama em localhost:11434).

Pré-requisitos:
  - Ollama a correr (`ollama serve` ou serviço em background)
  - Modelo puxado, ex.: `ollama pull llama3` (ou o nome em OLLAMA_MODEL)
  - pip install -r requirements/requirements_local_brain.txt
  - Stack completo do projeto (inclui torch), ex. requirements_core + pipelines conforme uso

Se ainda não tem torch: use `python scripts/test_ollama_brain_light.py` (só cérebro + Ollama).

Variáveis opcionais:
  OLLAMA_MODEL      (default: llama3)
  OLLAMA_BASE_URL   (default: http://localhost:11434)

Uso (na pasta AI-Biomimetica):
  python scripts/test_cerebro_ollama.py
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("test_cerebro")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))

    try:
        from src.systems.sistemas.sistema_meta_learning_biomimetico import (
            AutoEvolvingAISystem,
        )
    except ImportError as e:
        logger.error("Falha ao importar o sistema (dependências como torch?): %s", e)
        return 1

    logger.info("A inicializar AutoEvolvingAISystem com use_local_brain=True, tipo=ollama...")
    system = AutoEvolvingAISystem(use_local_brain=True, local_brain_type="ollama")

    task = {
        "task_type": "code_generation",
        "text_length": 400,
        "context": {
            "budget": "balanced",
            "latency": "standard",
            "quality": "high",
            "description": "Gerar módulo Python pequeno para validação de JSON",
        },
    }

    logger.info("A pedir recomendação de provedor (via Ollama se disponível)...")
    out = system.recommend_provider(task)
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

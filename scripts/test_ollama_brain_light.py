#!/usr/bin/env python3
"""
Teste leve: só HybridBiomimeticSystem + Ollama (sem torch / AutoEvolvingAISystem).

Use quando ainda não instalou o stack completo do meta-learning.

Uso (na pasta AI-Biomimetica):
  pip install -r requirements/requirements_local_brain.txt numpy
  python scripts/test_ollama_brain_light.py
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(root))

    from src.systems.sistemas.local_brain import HybridBiomimeticSystem

    model = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")
    base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    brain = HybridBiomimeticSystem(brain_type="ollama", model=model, base_url=base_url)
    task = {
        "task_type": "text_completion",
        "text_length": 120,
        "context": {"budget": "low", "latency": "standard"},
    }
    out = asyncio.run(brain.recommend_provider(task))
    print(json.dumps(out, indent=2, ensure_ascii=False, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Sobe a API do Bio Console (FastAPI) na porta 8000.

Uso (na pasta AI-Biomimetica, com venv ativo):
  pip install -r requirements/requirements_web.txt
  python scripts/run_bio_console_api.py

Variáveis opcionais:
  USE_LOCAL_BRAIN=true|false   (default: true)
  LOCAL_BRAIN_TYPE=ollama|mock
  OLLAMA_MODEL, OLLAMA_BASE_URL
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("BIO_CONSOLE_HOST", "0.0.0.0")
    port = int(os.environ.get("BIO_CONSOLE_PORT", "8000"))
    uvicorn.run(
        "app.bio_console_api:app",
        host=host,
        port=port,
        reload=os.environ.get("BIO_CONSOLE_RELOAD", "1") == "1",
    )

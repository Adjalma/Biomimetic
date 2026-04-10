#!/usr/bin/env python3
"""Smoke: Captum + shap + lime importáveis (exit 0) ou erro claro (exit 1)."""
import sys

def main() -> int:
    try:
        from captum.attr import IntegratedGradients  # noqa: F401
        import shap  # noqa: F401
        import lime  # noqa: F401
    except ImportError as e:
        print("FAIL:", e, file=sys.stderr)
        return 1
    print("XAI ok")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

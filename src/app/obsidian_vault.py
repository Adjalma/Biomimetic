"""
Escrita segura de notas Markdown num cofre Obsidian (fase 1: sistema de ficheiros).

Variáveis de ambiente:
- OBSIDIAN_VAULT_ROOT: caminho absoluto da pasta do cofre Obsidian.
- OBSIDIAN_CHOKMAH_RELATIVE: subpasta dentro do cofre (default: CHOKMAH).
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_REL_PATH_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_\-./]*\.md$")


def vault_root_from_env() -> Optional[Path]:
    raw = os.environ.get("OBSIDIAN_VAULT_ROOT", "").strip()
    if not raw:
        return None
    p = Path(raw).expanduser()
    if not p.is_absolute():
        return None
    return p


def chokmah_subdir() -> str:
    s = os.environ.get("OBSIDIAN_CHOKMAH_RELATIVE", "CHOKMAH").strip() or "CHOKMAH"
    s = s.replace("\\", "/").strip("/")
    if not s or ".." in s.split("/"):
        return "CHOKMAH"
    return s


def chokmah_base(vault: Path) -> Path:
    return (vault / chokmah_subdir()).resolve()


def validate_relative_md(relative_path: str) -> str:
    rel = relative_path.strip().replace("\\", "/").lstrip("/")
    if not rel or ".." in rel.split("/"):
        raise ValueError("caminho relativo inválido")
    if not _REL_PATH_PATTERN.match(rel):
        raise ValueError(
            "use apenas .md, letras, números, _ - . / ; deve começar com alfanumérico"
        )
    return rel


def resolve_note_path(vault: Path, relative_md: str) -> Path:
    base = chokmah_base(vault)
    target = (base / relative_md).resolve()
    try:
        target.relative_to(base)
    except ValueError as e:
        raise ValueError("caminho fora da pasta CHOKMAH do cofre") from e
    return target


def build_frontmatter(tags: List[str], extra: Optional[Dict[str, Any]] = None) -> str:
    tags = [t.strip() for t in tags if t and str(t).strip()]
    lines = ["---"]
    lines.append(f"created: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    lines.append('source: "bio-console-api"')
    if tags:
        lines.append("tags: [" + ", ".join(json_escape_tag(t) for t in tags) + "]")
    if extra:
        for k, v in extra.items():
            if isinstance(v, str):
                lines.append(f"{k}: {yaml_quote_if_needed(v)}")
            elif isinstance(v, (int, float, bool)):
                lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def json_escape_tag(t: str) -> str:
    s = t.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{s}"'


def yaml_quote_if_needed(s: str) -> str:
    if any(c in s for c in (":", "#", "\n", '"')):
        esc = s.replace('"', '\\"')
        return f'"{esc}"'
    return s if s else '""'


def compose_note_markdown(
    *,
    frontmatter: str,
    title: Optional[str],
    body: str,
) -> str:
    parts: List[str] = []
    if frontmatter.strip():
        parts.append(frontmatter.rstrip() + "\n")
    if title and title.strip():
        parts.append(f"# {title.strip()}\n\n")
    parts.append(body.strip())
    parts.append("\n")
    return "".join(parts)


def append_section(markdown_body: str) -> str:
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"\n\n---\n\n## {ts}\n\n{markdown_body.strip()}\n"


def write_note(
    *,
    vault: Path,
    relative_md: str,
    title: Optional[str],
    body: str,
    tags: List[str],
    append: bool,
    frontmatter_extra: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    rel = validate_relative_md(relative_md)
    path = resolve_note_path(vault, rel)
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = build_frontmatter(tags, frontmatter_extra)
    full = compose_note_markdown(frontmatter=fm, title=title, body=body)

    if append and path.is_file():
        existing = path.read_text(encoding="utf-8")
        path.write_text(existing + append_section(body), encoding="utf-8")
        return {"path": str(path), "relative": rel, "mode": "append", "bytes": path.stat().st_size}

    path.write_text(full, encoding="utf-8")
    return {"path": str(path), "relative": rel, "mode": "create", "bytes": path.stat().st_size}

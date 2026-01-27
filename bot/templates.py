from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from jinja2 import Environment

_TEXTS_DIR = Path(__file__).parent / "texts"
_env = Environment(autoescape=False)

_BLOCK_RE = re.compile(
    r"\{%[-\s]*block\s+(\w+)\s*[-\s]*%\}(.*?)\{%[-\s]*endblock\s*[-\s]*%\}",
    re.DOTALL,
)

_blocks: dict[str, str] = {}


def _load_blocks() -> None:
    src = (_TEXTS_DIR / "messages.html").read_text("utf-8")
    for m in _BLOCK_RE.finditer(src):
        _blocks[m.group(1)] = m.group(2)


_load_blocks()


def render(block_name: str, **kwargs: Any) -> str:
    source = _blocks.get(block_name)
    if source is None:
        return f"[missing block: {block_name}]"
    tpl = _env.from_string(source)
    return tpl.render(**kwargs).strip()

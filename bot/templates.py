from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

_TEXTS_DIR = Path(__file__).parent / "texts"

_env = Environment(loader=FileSystemLoader(str(_TEXTS_DIR)), autoescape=False)
_template = _env.get_template("messages.html")
_module = _template.module  # type: ignore[attr-defined]


def render(block_name: str, **kwargs: Any) -> str:
    block = getattr(_module, block_name, None)
    if block is None:
        return f"[missing block: {block_name}]"
    # Jinja2 module blocks are strings — but we need variable rendering,
    # so we use the environment to render a sub-template.
    source = _get_block_source(block_name)
    tpl = _env.from_string(source)
    return tpl.render(**kwargs).strip()


def _get_block_source(block_name: str) -> str:
    src = (_TEXTS_DIR / "messages.html").read_text("utf-8")
    start_tag = f"{{% block {block_name} %}}"
    end_tag = f"{{% endblock %}}"
    start = src.index(start_tag) + len(start_tag)
    end = src.index(end_tag, start)
    return src[start:end]

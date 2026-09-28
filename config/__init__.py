"""Chargement de config/config.yaml avec substitution ${VAR:-défaut}."""

import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv

load_dotenv()

CONFIG_FILE = Path(__file__).parent / "config.yaml"
_ENV_PATTERN = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)(?::-([^}]*))?\}")


def _expand(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _expand(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand(v) for v in value]
    if isinstance(value, str):
        return _ENV_PATTERN.sub(lambda m: os.getenv(m.group(1), m.group(2) or ""), value)
    return value


def load_config() -> dict[str, Any]:
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return _expand(yaml.safe_load(f))


@lru_cache(maxsize=1)
def get_config() -> dict[str, Any]:
    """Config mise en cache. `get_config.cache_clear()` pour relire l'environnement."""
    return load_config()

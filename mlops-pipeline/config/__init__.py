"""Configuration management for MLOps pipeline"""
from pathlib import Path
import yaml
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

CONFIG_DIR = Path(__file__).parent
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def load_config() -> Dict[str, Any]:
    """Charge la configuration depuis le fichier YAML"""
    with open(CONFIG_FILE, 'r') as f:
        config = yaml.safe_load(f)
    
    # Remplacer les variables d'environnement (syntaxe ${VAR:-default})
    def replace_env_vars(obj):
        if isinstance(obj, dict):
            return {k: replace_env_vars(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [replace_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and ":-" in obj:
            # Format: ${VAR:-default}
            import re
            match = re.match(r'\$\{([^:]+):-([^}]+)\}', obj)
            if match:
                var_name = match.group(1)
                default = match.group(2)
                return os.getenv(var_name, default)
            else:
                # Format simple: ${VAR}
                var_name = obj[2:-1]
                return os.getenv(var_name, obj)
        elif isinstance(obj, str) and obj.startswith("${"):
            # Format simple: ${VAR}
            var_name = obj[2:-1]
            return os.getenv(var_name, obj)
        else:
            return obj
    
    config = replace_env_vars(config)
    
    return config


def get_config(key: str = None, default: Any = None) -> Any:
    """Récupère une valeur de configuration"""
    config = load_config()
    
    if key is None:
        return config
    
    keys = key.split('.')
    value = config
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value


# Configuration globale
_config = None

def get_global_config() -> Dict[str, Any]:
    """Récupère la configuration globale (singleton)"""
    global _config
    if _config is None:
        _config = load_config()
    return _config


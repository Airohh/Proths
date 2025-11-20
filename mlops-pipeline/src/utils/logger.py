"""
Logging structuré pour le pipeline MLOps
"""
import logging
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Any, Dict
import os


class JSONFormatter(logging.Formatter):
    """Formatter JSON pour les logs structurés"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }
        
        # Ajouter les champs personnalisés
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
        
        # Ajouter l'exception si présente
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


def setup_logger(
    name: str,
    level: str = None,
    log_file: str = None,
    json_format: bool = True
) -> logging.Logger:
    """
    Configure un logger avec format structuré
    
    Args:
        name: Nom du logger
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Chemin vers le fichier de log (optionnel)
        json_format: Utiliser le format JSON (défaut: True)
    
    Returns:
        Logger configuré
    """
    logger = logging.getLogger(name)
    
    # Niveau de log depuis l'environnement ou paramètre
    log_level = level or os.getenv('LOG_LEVEL', 'INFO')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Éviter les handlers dupliqués
    if logger.handlers:
        return logger
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler pour fichier si spécifié
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Récupère un logger (créé s'il n'existe pas)
    
    Args:
        name: Nom du logger (défaut: nom du module appelant)
    
    Returns:
        Logger
    """
    if name is None:
        import inspect
        frame = inspect.currentframe().f_back
        name = frame.f_globals.get('__name__', 'root')
    
    return setup_logger(name)


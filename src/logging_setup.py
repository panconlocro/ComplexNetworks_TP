"""
Configuración centralizada de logging para el proyecto.
Logger estándar con formato timestamp, nivel y módulo.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logger(
    name: str = "etl_pipeline",
    log_file: Optional[Path] = None,
    level: int = logging.INFO,
    console: bool = True
) -> logging.Logger:
    """
    Configura un logger con formato estándar.
    
    Args:
        name: Nombre del logger.
        log_file: Ruta al archivo de log. Si es None, solo salida a consola.
        level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        console: Si True, también imprime a consola.
        
    Returns:
        Logger configurado.
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicación de handlers
    if logger.handlers:
        logger.handlers.clear()
    
    # Formato estándar: timestamp | nivel | módulo | mensaje
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo
    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Handler para consola
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


def get_etl_logger(config: dict) -> logging.Logger:
    """
    Crea el logger estándar para el pipeline ETL.
    
    Args:
        config: Diccionario de configuración.
        
    Returns:
        Logger configurado con archivo en reports/etl.log
    """
    # Import sin relative para compatibilidad con notebooks
    import config_loader
    
    reports_path = config_loader.get_absolute_path(config, 'reports')
    log_file = reports_path / config['outputs']['etl_log']
    
    return setup_logger(
        name="etl_pipeline",
        log_file=log_file,
        level=logging.INFO,
        console=True
    )


def log_separator(logger: logging.Logger, char: str = "=", length: int = 80) -> None:
    """
    Imprime una línea separadora en el log.
    
    Args:
        logger: Logger a usar.
        char: Carácter para la línea.
        length: Longitud de la línea.
    """
    logger.info(char * length)


def log_section(logger: logging.Logger, title: str) -> None:
    """
    Imprime un título de sección en el log.
    
    Args:
        logger: Logger a usar.
        title: Título de la sección.
    """
    log_separator(logger)
    logger.info(f"  {title}")
    log_separator(logger)

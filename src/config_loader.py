"""
Cargador y validador de configuración central.
Lectura de config.yaml con validación de estructura.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """
    Obtiene la ruta raíz del proyecto.
    Asume que este módulo está en src/ y la raíz está un nivel arriba.
    
    Returns:
        Path: Ruta absoluta a la raíz del proyecto.
    """
    return Path(__file__).parent.parent


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Carga el archivo de configuración YAML.
    
    Args:
        config_path: Ruta al archivo config.yaml. Si es None, usa la ruta por defecto.
        
    Returns:
        Dict con la configuración completa.
        
    Raises:
        FileNotFoundError: Si no se encuentra el archivo de configuración.
        yaml.YAMLError: Si hay errores de parseo en el YAML.
    """
    if config_path is None:
        project_root = get_project_root()
        config_path = project_root / "config" / "config.yaml"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
    
    logger.info(f"Cargando configuración desde: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Validar estructura básica
    _validate_config_structure(config)
    
    logger.info("Configuración cargada y validada correctamente")
    return config


def _validate_config_structure(config: Dict[str, Any]) -> None:
    """
    Valida que el diccionario de configuración tenga la estructura esperada.
    
    Args:
        config: Diccionario de configuración.
        
    Raises:
        ValueError: Si falta alguna sección obligatoria.
    """
    required_sections = ['paths', 'columns_expected', 'domains', 'time', 'random_seed', 'outputs', 'plots']
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Sección obligatoria '{section}' no encontrada en config.yaml")
    
    # Validar subsecciones críticas
    required_paths = ['data_raw', 'data_processed', 'figures', 'reports', 'notebooks']
    for path_key in required_paths:
        if path_key not in config['paths']:
            raise ValueError(f"Ruta '{path_key}' no definida en paths")

    required_domains = ['MODALIDAD', 'COMPLEJIDAD']
    for domain in required_domains:
        if domain not in config['domains']:
            raise ValueError(f"Dominio '{domain}' no definido en domains")
    
    logger.debug("Estructura de configuración validada")


def get_absolute_path(config: Dict[str, Any], path_key: str) -> Path:
    """
    Convierte una ruta relativa del config a ruta absoluta.
    
    Args:
        config: Diccionario de configuración.
        path_key: Clave de la ruta en config['paths'].
        
    Returns:
        Path absoluto.
    """
    project_root = get_project_root()
    relative_path = config['paths'][path_key]
    return project_root / relative_path


def get_columns_expected(config: Dict[str, Any]) -> List[str]:
    """
    Obtiene la lista de columnas esperadas.
    
    Args:
        config: Diccionario de configuración.
        
    Returns:
        Lista de nombres de columnas.
    """
    return config['columns_expected']


def get_domain_values(config: Dict[str, Any], domain: str) -> List[str]:
    """
    Obtiene los valores permitidos para un dominio específico.
    
    Args:
        config: Diccionario de configuración.
        domain: Nombre del dominio (ej: 'Modalidad', 'Complejidad').
        
    Returns:
        Lista de valores permitidos.
    """
    return config['domains'].get(domain, [])

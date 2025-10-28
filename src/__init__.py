"""
Paquete src: Módulos reutilizables para análisis de redes.
Hito 1: Ingesta, limpieza, EDA básico.
"""

__version__ = "0.1.0"

from . import config_loader
from . import logging_setup
from . import io_utils
from . import validate
from . import cleaning
from . import network_prep
from . import eda_basic

__all__ = [
    'config_loader',
    'logging_setup',
    'io_utils',
    'validate',
    'cleaning',
    'network_prep',
    'eda_basic'
]

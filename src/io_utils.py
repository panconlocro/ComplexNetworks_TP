"""
Utilidades de entrada/salida para el proyecto.
Lectura y escritura segura de datos, detección automática de archivos.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


def find_data_file(
    data_dir: Path,
    extensions: List[str] = ['.csv', '.xlsx', '.xls'],
    pattern: str = None
) -> Path:
    """
    Detecta automáticamente un archivo de datos en un directorio.
    Si hay múltiples archivos, selecciona el primero o aplica un patrón.
    
    Args:
        data_dir: Directorio donde buscar.
        extensions: Extensiones permitidas.
        pattern: Patrón opcional para filtrar por nombre.
        
    Returns:
        Path al archivo encontrado.
        
    Raises:
        FileNotFoundError: Si no se encuentra ningún archivo.
        ValueError: Si hay múltiples archivos sin patrón específico.
    """
    data_dir = Path(data_dir)
    
    if not data_dir.exists():
        raise FileNotFoundError(f"Directorio no encontrado: {data_dir}")
    
    # Buscar archivos con las extensiones permitidas
    files = []
    for ext in extensions:
        if pattern:
            files.extend(data_dir.glob(f"*{pattern}*{ext}"))
        else:
            files.extend(data_dir.glob(f"*{ext}"))
    
    if len(files) == 0:
        raise FileNotFoundError(f"No se encontraron archivos en {data_dir} con extensiones {extensions}")
    
    if len(files) == 1:
        logger.info(f"Archivo detectado: {files[0].name}")
        return files[0]
    
    # Si hay múltiples archivos, usar el primero y advertir
    logger.warning(f"Múltiples archivos encontrados en {data_dir}. Usando: {files[0].name}")
    return files[0]


def read_data_file(
    file_path: Path,
    expected_columns: Optional[List[str]] = None,
    dtype: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Lee un archivo de datos (CSV o Excel) con validación básica.
    
    Args:
        file_path: Ruta al archivo.
        expected_columns: Columnas esperadas (opcional, para validación).
        dtype: Diccionario de tipos de datos por columna.
        
    Returns:
        DataFrame con los datos.
        
    Raises:
        ValueError: Si faltan columnas esperadas.
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
    
    logger.info(f"Leyendo archivo: {file_path.name}")
    
    # Leer según extensión
    if file_path.suffix == '.csv':
        df = pd.read_csv(file_path, dtype=dtype)
    elif file_path.suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path, dtype=dtype)
    else:
        raise ValueError(f"Extensión no soportada: {file_path.suffix}")
    
    logger.info(f"Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
    
    # Validar columnas si se especifican
    if expected_columns:
        missing_cols = set(expected_columns) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Columnas faltantes en el archivo: {missing_cols}")
        logger.debug(f"Validación de columnas exitosa")
    
    return df


def write_data_file(
    df: pd.DataFrame,
    file_path: Path,
    index: bool = False,
    create_dirs: bool = True
) -> None:
    """
    Escribe un DataFrame a archivo CSV de forma segura.
    
    Args:
        df: DataFrame a escribir.
        file_path: Ruta de destino.
        index: Si True, incluye el índice en el CSV.
        create_dirs: Si True, crea directorios si no existen.
    """
    file_path = Path(file_path)
    
    if create_dirs:
        file_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Escribiendo archivo: {file_path.name} ({df.shape[0]} filas, {df.shape[1]} columnas)")
    
    df.to_csv(file_path, index=index, encoding='utf-8')
    
    logger.info(f"Archivo guardado exitosamente: {file_path}")


def get_data_snapshot_path(original_path: Path, suffix: str = "_snapshot") -> Path:
    """
    Genera la ruta para un archivo snapshot.
    Los snapshots siempre se guardan como CSV.
    
    Args:
        original_path: Ruta del archivo original.
        suffix: Sufijo a añadir antes de la extensión.
        
    Returns:
        Path con el sufijo añadido y extensión .csv
    """
    stem = original_path.stem
    parent = original_path.parent
    
    # Siempre usar .csv para snapshots (write_data_file guarda como CSV)
    return parent / f"{stem}{suffix}.csv"


def profile_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Genera un perfil básico de un DataFrame.
    
    Args:
        df: DataFrame a perfilar.
        
    Returns:
        Diccionario con información de perfil.
    """
    profile = {
        'n_rows': len(df),
        'n_cols': len(df.columns),
        'columns': list(df.columns),
        'dtypes': df.dtypes.to_dict(),
        'missing_counts': df.isnull().sum().to_dict(),
        'missing_pcts': (df.isnull().sum() / len(df) * 100).to_dict(),
        'duplicated_rows': df.duplicated().sum(),
        'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2
    }
    
    return profile


def print_profile(profile: Dict[str, Any], logger: logging.Logger = None) -> None:
    """
    Imprime un resumen del perfil de datos.
    
    Args:
        profile: Diccionario de perfil generado por profile_dataframe.
        logger: Logger opcional. Si es None, usa print.
    """
    log_func = logger.info if logger else print
    
    log_func(f"  Filas: {profile['n_rows']:,}")
    log_func(f"  Columnas: {profile['n_cols']}")
    log_func(f"  Filas duplicadas: {profile['duplicated_rows']}")
    log_func(f"  Memoria: {profile['memory_usage_mb']:.2f} MB")
    log_func(f"\n  Columnas y tipos:")
    for col, dtype in profile['dtypes'].items():
        missing = profile['missing_counts'][col]
        missing_pct = profile['missing_pcts'][col]
        log_func(f"    - {col}: {dtype} (nulos: {missing}, {missing_pct:.1f}%)")

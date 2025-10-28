"""
Funciones de limpieza y normalización de datos.
Transformaciones seguras, trazables y reproducibles.
"""

import pandas as pd
import numpy as np
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class CleaningLog:
    """Registro detallado de operaciones de limpieza."""
    
    def __init__(self):
        self.operations: List[Dict[str, Any]] = []
        self.before_stats: Dict[str, int] = {}
        self.after_stats: Dict[str, int] = {}
    
    def log_operation(self, operation: str, details: Dict[str, Any]):
        """Registra una operación de limpieza."""
        self.operations.append({
            'operation': operation,
            'details': details
        })
    
    def set_before_stats(self, df: pd.DataFrame):
        """Captura estadísticas antes de limpieza."""
        self.before_stats = {
            'n_rows': len(df),
            'n_cols': len(df.columns),
            'duplicados': df.duplicated().sum(),
            'nulos_totales': df.isnull().sum().sum()
        }
    
    def set_after_stats(self, df: pd.DataFrame):
        """Captura estadísticas después de limpieza."""
        self.after_stats = {
            'n_rows': len(df),
            'n_cols': len(df.columns),
            'duplicados': df.duplicated().sum(),
            'nulos_totales': df.isnull().sum().sum()
        }
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convierte el log a DataFrame para exportar."""
        records = []
        for op in self.operations:
            record = {
                'operacion': op['operation'],
                **op['details']
            }
            records.append(record)
        return pd.DataFrame(records)
    
    def to_markdown(self) -> str:
        """Genera reporte en formato Markdown."""
        lines = []
        lines.append("# Log de Limpieza de Datos\n")
        
        lines.append("## Estadísticas Antes de Limpieza")
        for key, val in self.before_stats.items():
            lines.append(f"- **{key}**: {val:,}")
        
        lines.append("\n## Operaciones Realizadas\n")
        for i, op in enumerate(self.operations, 1):
            lines.append(f"### {i}. {op['operation']}")
            for key, val in op['details'].items():
                lines.append(f"- **{key}**: {val}")
            lines.append("")
        
        lines.append("## Estadísticas Después de Limpieza")
        for key, val in self.after_stats.items():
            lines.append(f"- **{key}**: {val:,}")
        
        # Calcular cambios
        lines.append("\n## Resumen de Cambios")
        rows_removed = self.before_stats.get('n_rows', 0) - self.after_stats.get('n_rows', 0)
        lines.append(f"- **Registros removidos**: {rows_removed:,}")
        
        return "\n".join(lines)


def remove_accents(text: str) -> str:
    """
    Elimina acentos y diacríticos de un string.
    
    Args:
        text: String a normalizar.
        
    Returns:
        String sin acentos.
    """
    if pd.isna(text):
        return text
    
    # Normalizar a NFD (descomponer caracteres con diacríticos)
    nfd = unicodedata.normalize('NFD', str(text))
    # Filtrar solo caracteres que no son marcas diacríticas
    return ''.join(char for char in nfd if unicodedata.category(char) != 'Mn')


def normalize_string_column(series: pd.Series, remove_acc: bool = True) -> pd.Series:
    """
    Normaliza una columna de strings: espacios, mayúsculas, acentos.
    
    Args:
        series: Serie de pandas a normalizar.
        remove_acc: Si True, elimina acentos.
        
    Returns:
        Serie normalizada.
    """
    # Convertir a string
    result = series.astype(str)
    
    # Eliminar espacios extra al inicio/fin
    result = result.str.strip()
    
    # Eliminar múltiples espacios consecutivos
    result = result.str.replace(r'\s+', ' ', regex=True)
    
    # Capitalizar primera letra de cada palabra
    result = result.str.title()
    
    # Eliminar acentos si se especifica
    if remove_acc:
        result = result.apply(remove_accents)
    
    # Reemplazar 'Nan' por NaN real
    result = result.replace('Nan', np.nan)
    
    return result


def normalize_categorical_columns(
    df: pd.DataFrame,
    columns: List[str],
    remove_accents_flag: bool = False
) -> Tuple[pd.DataFrame, Dict[str, int]]:
    """
    Normaliza múltiples columnas categóricas.
    
    Args:
        df: DataFrame a procesar.
        columns: Lista de columnas a normalizar.
        remove_accents_flag: Si True, elimina acentos.
        
    Returns:
        Tupla (DataFrame procesado, diccionario con conteos de cambios).
    """
    df_clean = df.copy()
    changes = {}
    
    for col in columns:
        if col not in df_clean.columns:
            logger.warning(f"Columna {col} no existe, se omite normalización")
            continue
        
        original = df_clean[col].copy()
        df_clean[col] = normalize_string_column(df_clean[col], remove_acc=remove_accents_flag)
        
        # Contar cambios
        n_changed = (original != df_clean[col]).sum()
        changes[col] = n_changed
        
        if n_changed > 0:
            logger.info(f"  Columna {col}: {n_changed} valores normalizados")
    
    return df_clean, changes


def remove_duplicates(
    df: pd.DataFrame,
    subset: List[str] = None,
    keep: str = 'first'
) -> Tuple[pd.DataFrame, int]:
    """
    Elimina filas duplicadas.
    
    Args:
        df: DataFrame a procesar.
        subset: Columnas a considerar para duplicados. Si None, usa todas.
        keep: Qué duplicado mantener ('first', 'last', False).
        
    Returns:
        Tupla (DataFrame sin duplicados, número de duplicados removidos).
    """
    n_before = len(df)
    df_clean = df.drop_duplicates(subset=subset, keep=keep)
    n_removed = n_before - len(df_clean)
    
    if n_removed > 0:
        logger.info(f"  Duplicados removidos: {n_removed}")
    
    return df_clean, n_removed


def handle_missing_values(
    df: pd.DataFrame,
    strategy: str = 'drop',
    columns: List[str] = None
) -> Tuple[pd.DataFrame, int]:
    """
    Maneja valores faltantes.
    
    Args:
        df: DataFrame a procesar.
        strategy: Estrategia ('drop', 'fill_mode', 'fill_value').
        columns: Columnas específicas. Si None, aplica a todas.
        
    Returns:
        Tupla (DataFrame procesado, número de filas removidas).
    """
    n_before = len(df)
    df_clean = df.copy()
    
    cols_to_check = columns if columns else df.columns
    
    if strategy == 'drop':
        df_clean = df_clean.dropna(subset=cols_to_check)
    elif strategy == 'fill_mode':
        for col in cols_to_check:
            if col in df_clean.columns and df_clean[col].dtype == 'object':
                mode_val = df_clean[col].mode()
                if len(mode_val) > 0:
                    df_clean[col].fillna(mode_val[0], inplace=True)
    
    n_removed = n_before - len(df_clean)
    
    if n_removed > 0:
        logger.info(f"  Filas con nulos removidas: {n_removed}")
    
    return df_clean, n_removed


def filter_by_domain(
    df: pd.DataFrame,
    column: str,
    allowed_values: List[str]
) -> Tuple[pd.DataFrame, int]:
    """
    Filtra registros que no cumplan con un dominio permitido.
    
    Args:
        df: DataFrame a filtrar.
        column: Columna a validar.
        allowed_values: Valores permitidos.
        
    Returns:
        Tupla (DataFrame filtrado, número de filas removidas).
    """
    if column not in df.columns:
        logger.warning(f"Columna {column} no existe")
        return df, 0
    
    n_before = len(df)
    df_clean = df[df[column].isin(allowed_values) | df[column].isna()].copy()
    n_removed = n_before - len(df_clean)
    
    if n_removed > 0:
        invalid_vals = df[~df[column].isin(allowed_values) & ~df[column].isna()][column].unique()
        logger.warning(f"  Columna {column}: {n_removed} filas removidas por valores fuera del dominio: {list(invalid_vals)}")
    
    return df_clean, n_removed


def clean_data_pipeline(
    df: pd.DataFrame,
    config: Dict[str, Any],
    key_columns: List[str] = None
) -> Tuple[pd.DataFrame, CleaningLog]:
    """
    Pipeline completo de limpieza de datos.
    
    Args:
        df: DataFrame crudo.
        config: Diccionario de configuración.
        key_columns: Columnas clave para detección de duplicados.
        
    Returns:
        Tupla (DataFrame limpio, CleaningLog con trazabilidad).
    """
    logger.info("Iniciando pipeline de limpieza")
    
    cleaning_log = CleaningLog()
    cleaning_log.set_before_stats(df)
    
    df_clean = df.copy()
    
    # 1. Normalizar columnas de texto
    logger.info("Paso 1: Normalizando columnas de texto")
    text_columns = [col for col in df_clean.columns if df_clean[col].dtype == 'object']
    df_clean, changes = normalize_categorical_columns(df_clean, text_columns, remove_accents_flag=False)
    cleaning_log.log_operation('Normalización de texto', {
        'columnas_procesadas': len(text_columns),
        'valores_modificados': sum(changes.values())
    })
    
    # 2. Validar y filtrar dominios
    logger.info("Paso 2: Validando dominios")
    total_removed_domain = 0
    for domain_col, allowed_vals in config['domains'].items():
        if domain_col in df_clean.columns:
            df_clean, n_removed = filter_by_domain(df_clean, domain_col, allowed_vals)
            total_removed_domain += n_removed
    
    cleaning_log.log_operation('Filtrado por dominios', {
        'registros_removidos': total_removed_domain
    })
    
    # 3. Eliminar duplicados
    logger.info("Paso 3: Eliminando duplicados")
    if key_columns:
        df_clean, n_dup = remove_duplicates(df_clean, subset=key_columns)
    else:
        df_clean, n_dup = remove_duplicates(df_clean)
    
    cleaning_log.log_operation('Eliminación de duplicados', {
        'registros_removidos': n_dup,
        'columnas_clave': key_columns if key_columns else 'todas'
    })
    
    # 4. Manejar valores faltantes
    logger.info("Paso 4: Manejando valores faltantes")
    df_clean, n_nulls = handle_missing_values(df_clean, strategy='drop')
    cleaning_log.log_operation('Eliminación de nulos', {
        'registros_removidos': n_nulls
    })
    
    cleaning_log.set_after_stats(df_clean)
    
    logger.info(f"Pipeline de limpieza finalizado: {len(df)} -> {len(df_clean)} registros")
    
    return df_clean, cleaning_log


def export_cleaning_log(
    cleaning_log: CleaningLog,
    reports_path: Path,
    config: Dict[str, Any]
) -> None:
    """
    Exporta el log de limpieza a CSV y Markdown.
    
    Args:
        cleaning_log: Objeto CleaningLog con información.
        reports_path: Ruta al directorio de reportes.
        config: Diccionario de configuración.
    """
    reports_path = Path(reports_path)
    reports_path.mkdir(parents=True, exist_ok=True)
    
    # Exportar CSV
    csv_path = reports_path / config['outputs']['limpieza_log_csv']
    df_log = cleaning_log.to_dataframe()
    df_log.to_csv(csv_path, index=False, encoding='utf-8')
    logger.info(f"Log CSV exportado: {csv_path}")
    
    # Exportar Markdown
    md_path = reports_path / config['outputs']['limpieza_log_md']
    md_content = cleaning_log.to_markdown()
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    logger.info(f"Log Markdown exportado: {md_path}")

"""
Validación de esquema y dominios de datos.
Contratos de calidad: tipos, dominios, unicidad.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class ValidationReport:
    """Reporte estructurado de validación de datos."""
    
    def __init__(self):
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        self.passed: bool = True
    
    def add_error(self, category: str, message: str, details: Any = None):
        """Añade un error crítico."""
        self.errors.append({
            'category': category,
            'message': message,
            'details': details
        })
        self.passed = False
    
    def add_warning(self, category: str, message: str, details: Any = None):
        """Añade una advertencia."""
        self.warnings.append({
            'category': category,
            'message': message,
            'details': details
        })
    
    def get_summary(self) -> str:
        """Genera resumen del reporte."""
        summary = []
        summary.append(f"Estado: {'✓ APROBADO' if self.passed else '✗ RECHAZADO'}")
        summary.append(f"Errores: {len(self.errors)}")
        summary.append(f"Advertencias: {len(self.warnings)}")
        return "\n".join(summary)
    
    def print_report(self, logger_obj: logging.Logger = None):
        """Imprime el reporte completo."""
        log_func = logger_obj.info if logger_obj else print
        
        log_func(self.get_summary())
        
        if self.errors:
            log_func("\nErrores detectados:")
            for err in self.errors:
                log_func(f"  [{err['category']}] {err['message']}")
                if err['details']:
                    log_func(f"    Detalles: {err['details']}")
        
        if self.warnings:
            log_func("\nAdvertencias:")
            for warn in self.warnings:
                log_func(f"  [{warn['category']}] {warn['message']}")
                if warn['details']:
                    log_func(f"    Detalles: {warn['details']}")


def validate_schema(
    df: pd.DataFrame,
    expected_columns: List[str],
    required_types: Dict[str, type] = None
) -> ValidationReport:
    """
    Valida el esquema del DataFrame: columnas y tipos.
    
    Args:
        df: DataFrame a validar.
        expected_columns: Lista de columnas esperadas.
        required_types: Diccionario columna -> tipo esperado.
        
    Returns:
        ValidationReport con resultados.
    """
    report = ValidationReport()
    
    # Validar columnas presentes
    missing_cols = set(expected_columns) - set(df.columns)
    extra_cols = set(df.columns) - set(expected_columns)
    
    if missing_cols:
        report.add_error(
            'SCHEMA',
            f'Columnas faltantes: {missing_cols}',
            list(missing_cols)
        )
    
    if extra_cols:
        report.add_warning(
            'SCHEMA',
            f'Columnas extras no esperadas: {extra_cols}',
            list(extra_cols)
        )
    
    # Validar tipos si se especifican
    if required_types:
        for col, expected_type in required_types.items():
            if col in df.columns:
                actual_dtype = df[col].dtype
                # Validación flexible de tipos numéricos
                if expected_type in [int, np.int64] and not pd.api.types.is_integer_dtype(actual_dtype):
                    report.add_warning(
                        'DTYPE',
                        f'Columna {col}: esperado tipo entero, encontrado {actual_dtype}'
                    )
                elif expected_type == str and not pd.api.types.is_object_dtype(actual_dtype):
                    report.add_warning(
                        'DTYPE',
                        f'Columna {col}: esperado tipo string, encontrado {actual_dtype}'
                    )
    
    logger.info(f"Validación de esquema: {len(report.errors)} errores, {len(report.warnings)} advertencias")
    return report


def validate_domains(
    df: pd.DataFrame,
    domain_config: Dict[str, List[str]]
) -> ValidationReport:
    """
    Valida que las columnas categóricas tengan valores dentro de dominios permitidos.
    
    Args:
        df: DataFrame a validar.
        domain_config: Diccionario columna -> lista de valores permitidos.
        
    Returns:
        ValidationReport con resultados.
    """
    report = ValidationReport()
    
    for col, allowed_values in domain_config.items():
        if col not in df.columns:
            report.add_warning('DOMAIN', f'Columna {col} no existe en el DataFrame')
            continue
        
        # Valores únicos presentes (excluyendo nulos)
        unique_vals = df[col].dropna().unique()
        invalid_vals = set(unique_vals) - set(allowed_values)
        
        if invalid_vals:
            count = df[col].isin(invalid_vals).sum()
            report.add_error(
                'DOMAIN',
                f'Columna {col}: {count} registros con valores fuera del dominio',
                {
                    'valores_invalidos': list(invalid_vals),
                    'valores_permitidos': allowed_values,
                    'registros_afectados': count
                }
            )
    
    logger.info(f"Validación de dominios: {len(report.errors)} errores")
    return report


def validate_duplicates(
    df: pd.DataFrame,
    key_columns: List[str]
) -> ValidationReport:
    """
    Valida que no existan duplicados en la combinación de columnas clave.
    
    Args:
        df: DataFrame a validar.
        key_columns: Columnas que forman la clave única.
        
    Returns:
        ValidationReport con resultados.
    """
    report = ValidationReport()
    
    # Verificar que existan las columnas
    missing_keys = set(key_columns) - set(df.columns)
    if missing_keys:
        report.add_error('DUPLICATES', f'Columnas clave faltantes: {missing_keys}')
        return report
    
    # Detectar duplicados
    duplicated = df.duplicated(subset=key_columns, keep=False)
    n_duplicated = duplicated.sum()
    
    if n_duplicated > 0:
        report.add_error(
            'DUPLICATES',
            f'{n_duplicated} registros duplicados en clave {key_columns}',
            {'n_duplicados': n_duplicated}
        )
    
    logger.info(f"Validación de duplicados: {n_duplicated} registros duplicados encontrados")
    return report


def validate_nulls(
    df: pd.DataFrame,
    required_columns: List[str] = None
) -> ValidationReport:
    """
    Valida valores nulos en columnas requeridas.
    
    Args:
        df: DataFrame a validar.
        required_columns: Columnas que no deben tener nulos. Si None, aplica a todas.
        
    Returns:
        ValidationReport con resultados.
    """
    report = ValidationReport()
    
    cols_to_check = required_columns if required_columns else df.columns
    
    for col in cols_to_check:
        if col not in df.columns:
            continue
        
        n_nulls = df[col].isnull().sum()
        if n_nulls > 0:
            pct = (n_nulls / len(df)) * 100
            report.add_error(
                'NULLS',
                f'Columna {col}: {n_nulls} valores nulos ({pct:.1f}%)',
                {'n_nulos': n_nulls, 'porcentaje': pct}
            )
    
    logger.info(f"Validación de nulos: {len(report.errors)} columnas con nulos")
    return report


def full_validation(
    df: pd.DataFrame,
    config: Dict[str, Any],
    key_columns: List[str] = None
) -> ValidationReport:
    """
    Ejecuta todas las validaciones según configuración.
    
    Args:
        df: DataFrame a validar.
        config: Diccionario de configuración del proyecto.
        key_columns: Columnas clave para detección de duplicados.
        
    Returns:
        ValidationReport combinado con todos los resultados.
    """
    logger.info("Iniciando validación completa")
    
    combined_report = ValidationReport()
    
    # 1. Validar esquema
    schema_report = validate_schema(df, config['columns_expected'])
    combined_report.errors.extend(schema_report.errors)
    combined_report.warnings.extend(schema_report.warnings)
    combined_report.passed = combined_report.passed and schema_report.passed
    
    # 2. Validar dominios
    domain_report = validate_domains(df, config['domains'])
    combined_report.errors.extend(domain_report.errors)
    combined_report.warnings.extend(domain_report.warnings)
    combined_report.passed = combined_report.passed and domain_report.passed
    
    # 3. Validar duplicados si se especifican columnas clave
    if key_columns:
        dup_report = validate_duplicates(df, key_columns)
        combined_report.errors.extend(dup_report.errors)
        combined_report.warnings.extend(dup_report.warnings)
        combined_report.passed = combined_report.passed and dup_report.passed
    
    # 4. Validar nulos en columnas críticas
    null_report = validate_nulls(df, config['columns_expected'])
    combined_report.errors.extend(null_report.errors)
    combined_report.warnings.extend(null_report.warnings)
    combined_report.passed = combined_report.passed and null_report.passed
    
    logger.info(f"Validación completa finalizada: {combined_report.get_summary()}")
    return combined_report

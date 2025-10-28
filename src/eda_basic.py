"""
Análisis exploratorio básico y métricas de red.
Funciones para métricas del Hito 1: sin comunidades ni centralidades costosas.
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


def compute_basic_metrics(G: nx.Graph) -> Dict[str, Any]:
    """
    Calcula métricas básicas de red (Hito 1).
    
    Args:
        G: Grafo de NetworkX.
        
    Returns:
        Diccionario con métricas.
    """
    logger.info("Calculando métricas básicas de red")
    
    metrics = {}
    
    # Métricas básicas de tamaño
    metrics['n_nodes'] = G.number_of_nodes()
    metrics['n_edges'] = G.number_of_edges()
    
    # Densidad
    if metrics['n_nodes'] > 1:
        metrics['density'] = nx.density(G)
    else:
        metrics['density'] = 0.0
    
    # Grado medio
    degrees = dict(G.degree())
    if degrees:
        metrics['avg_degree'] = np.mean(list(degrees.values()))
        metrics['max_degree'] = np.max(list(degrees.values()))
        metrics['min_degree'] = np.min(list(degrees.values()))
    else:
        metrics['avg_degree'] = 0.0
        metrics['max_degree'] = 0
        metrics['min_degree'] = 0
    
    # Nodos aislados
    metrics['isolated_nodes'] = nx.number_of_isolates(G)
    metrics['pct_isolated'] = (metrics['isolated_nodes'] / metrics['n_nodes'] * 100) if metrics['n_nodes'] > 0 else 0
    
    # Componentes conectados
    if G.number_of_nodes() > 0:
        components = list(nx.connected_components(G))
        metrics['n_components'] = len(components)
        
        if components:
            lcc_size = len(max(components, key=len))
            metrics['lcc_size'] = lcc_size
            metrics['lcc_pct'] = (lcc_size / metrics['n_nodes'] * 100)
        else:
            metrics['lcc_size'] = 0
            metrics['lcc_pct'] = 0.0
    else:
        metrics['n_components'] = 0
        metrics['lcc_size'] = 0
        metrics['lcc_pct'] = 0.0
    
    # Clustering global (solo si hay suficientes nodos)
    try:
        if metrics['n_nodes'] > 2:
            metrics['clustering_global'] = nx.transitivity(G)
        else:
            metrics['clustering_global'] = 0.0
    except:
        metrics['clustering_global'] = 0.0
    
    logger.info(f"  N={metrics['n_nodes']}, E={metrics['n_edges']}, densidad={metrics['density']:.4f}")
    
    return metrics


def compute_weighted_metrics(G: nx.Graph) -> Dict[str, Any]:
    """
    Calcula métricas para grafos ponderados.
    
    Args:
        G: Grafo ponderado.
        
    Returns:
        Diccionario con métricas.
    """
    logger.info("Calculando métricas ponderadas")
    
    metrics = {}
    
    # Fuerza (strength): suma de pesos de aristas incidentes
    strength = dict(G.degree(weight='weight'))
    
    if strength:
        metrics['avg_strength'] = np.mean(list(strength.values()))
        metrics['max_strength'] = np.max(list(strength.values()))
        metrics['min_strength'] = np.min(list(strength.values()))
        metrics['std_strength'] = np.std(list(strength.values()))
    else:
        metrics['avg_strength'] = 0.0
        metrics['max_strength'] = 0.0
        metrics['min_strength'] = 0.0
        metrics['std_strength'] = 0.0
    
    # Peso total de la red
    weights = [d.get('weight', 1) for _, _, d in G.edges(data=True)]
    metrics['total_weight'] = sum(weights)
    metrics['avg_edge_weight'] = np.mean(weights) if weights else 0.0
    
    logger.info(f"  Fuerza media={metrics['avg_strength']:.2f}, peso total={metrics['total_weight']}")
    
    return metrics


def plot_degree_distribution(
    G: nx.Graph,
    output_path: Path,
    config: Dict[str, Any],
    title: str = "Distribución de Grado"
) -> None:
    """
    Genera histograma de distribución de grado.
    
    Args:
        G: Grafo.
        output_path: Ruta para guardar la figura.
        config: Configuración.
        title: Título del gráfico.
    """
    logger.info(f"Generando gráfico: {title}")
    
    degrees = [d for n, d in G.degree()]
    
    plt.figure(figsize=config['plots']['figsize_hist'])
    plt.hist(degrees, bins=30, edgecolor='black', alpha=0.7)
    plt.xlabel('Grado')
    plt.ylabel('Frecuencia')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=config['plots']['dpi'], format=config['plots']['format'])
    plt.close()
    
    logger.info(f"  Guardado: {output_path}")


def plot_strength_distribution(
    G: nx.Graph,
    output_path: Path,
    config: Dict[str, Any],
    title: str = "Distribución de Fuerza (Strength)"
) -> None:
    """
    Genera histograma de distribución de fuerza para grafos ponderados.
    
    Args:
        G: Grafo ponderado.
        output_path: Ruta para guardar la figura.
        config: Configuración.
        title: Título del gráfico.
    """
    logger.info(f"Generando gráfico: {title}")
    
    strengths = [d for n, d in G.degree(weight='weight')]
    
    plt.figure(figsize=config['plots']['figsize_hist'])
    plt.hist(strengths, bins=30, edgecolor='black', alpha=0.7, color='orange')
    plt.xlabel('Fuerza (Strength)')
    plt.ylabel('Frecuencia')
    plt.title(title)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=config['plots']['dpi'], format=config['plots']['format'])
    plt.close()
    
    logger.info(f"  Guardado: {output_path}")


def plot_categorical_by_year(
    df: pd.DataFrame,
    column: str,
    output_path: Path,
    config: Dict[str, Any],
    year_col: str = 'AÑO',
    title: str = None
) -> None:
    """
    Genera gráfico de barras de una variable categórica por año.
    
    Args:
        df: DataFrame con datos.
        column: Columna categórica a graficar.
        output_path: Ruta para guardar la figura.
        config: Configuración.
        year_col: Nombre de columna de año.
        title: Título del gráfico.
    """
    if title is None:
        title = f"{column} por {year_col}"
    
    logger.info(f"Generando gráfico: {title}")
    
    # Crear tabla de contingencia
    ct = pd.crosstab(df[year_col], df[column])
    
    plt.figure(figsize=config['plots']['figsize_bar'])
    ct.plot(kind='bar', ax=plt.gca(), edgecolor='black', alpha=0.8)
    plt.xlabel(year_col)
    plt.ylabel('Frecuencia')
    plt.title(title)
    plt.legend(title=column, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=config['plots']['dpi'], format=config['plots']['format'])
    plt.close()
    
    logger.info(f"  Guardado: {output_path}")


def generate_all_plots(
    df_clean: pd.DataFrame,
    G_proyeccion: nx.Graph,
    figures_path: Path,
    config: Dict[str, Any]
) -> None:
    """
    Genera todos los gráficos del EDA básico.
    
    Args:
        df_clean: DataFrame con datos limpios.
        G_proyeccion: Grafo de proyección cliente-cliente.
        figures_path: Ruta al directorio de figuras.
        config: Configuración.
    """
    logger.info("Generando todas las figuras")
    
    figures_path = Path(figures_path)
    figures_path.mkdir(parents=True, exist_ok=True)
    
    # 1. Histograma de grado
    plot_degree_distribution(
        G_proyeccion,
        figures_path / 'hist_grado.png',
        config,
        title='Distribución de Grado - Red Cliente-Cliente'
    )
    
    # 2. Histograma de fuerza
    plot_strength_distribution(
        G_proyeccion,
        figures_path / 'hist_fuerza.png',
        config,
        title='Distribución de Fuerza - Red Cliente-Cliente'
    )
    
    # 3. Modalidad por año
    if 'MODALIDAD' in df_clean.columns and 'AÑO' in df_clean.columns:
        plot_categorical_by_year(
            df_clean,
            'MODALIDAD',
            figures_path / 'barras_modalidad_por_anio.png',
            config,
            year_col='AÑO',
            title='Modalidad de Servicio por Año'
        )
    
    # 4. Complejidad por año
    if 'COMPLEJIDAD' in df_clean.columns and 'AÑO' in df_clean.columns:
        plot_categorical_by_year(
            df_clean,
            'COMPLEJIDAD',
            figures_path / 'barras_complejidad_por_anio.png',
            config,
            year_col='AÑO',
            title='Complejidad por Año'
        )
    
    logger.info("Todas las figuras generadas exitosamente")


def export_metrics_summary(
    metrics_basic: Dict[str, Any],
    metrics_weighted: Dict[str, Any],
    reports_path: Path
) -> None:
    """
    Exporta resumen de métricas a CSV.
    
    Args:
        metrics_basic: Métricas básicas.
        metrics_weighted: Métricas ponderadas.
        reports_path: Ruta al directorio de reportes.
    """
    reports_path = Path(reports_path)
    reports_path.mkdir(parents=True, exist_ok=True)
    
    # Combinar métricas
    all_metrics = {**metrics_basic, **metrics_weighted}
    
    # Convertir a DataFrame
    df_metrics = pd.DataFrame([all_metrics])
    
    # Exportar
    output_path = reports_path / 'metricas_resumen.csv'
    df_metrics.to_csv(output_path, index=False, encoding='utf-8')
    
    logger.info(f"Resumen de métricas exportado: {output_path}")


def print_metrics_summary(
    metrics_basic: Dict[str, Any],
    metrics_weighted: Dict[str, Any] = None
) -> None:
    """
    Imprime resumen de métricas en formato legible.
    
    Args:
        metrics_basic: Métricas básicas.
        metrics_weighted: Métricas ponderadas (opcional).
    """
    print("\n" + "="*60)
    print("RESUMEN DE MÉTRICAS DE RED")
    print("="*60)
    
    print("\nMétricas Básicas:")
    print(f"  Nodos (N):              {metrics_basic['n_nodes']:,}")
    print(f"  Aristas (E):            {metrics_basic['n_edges']:,}")
    print(f"  Densidad:               {metrics_basic['density']:.6f}")
    print(f"  Grado medio:            {metrics_basic['avg_degree']:.2f}")
    print(f"  Grado máximo:           {metrics_basic['max_degree']}")
    print(f"  Grado mínimo:           {metrics_basic['min_degree']}")
    print(f"  Nodos aislados:         {metrics_basic['isolated_nodes']} ({metrics_basic['pct_isolated']:.1f}%)")
    print(f"  Componentes conectados: {metrics_basic['n_components']}")
    print(f"  Tamaño del LCC:         {metrics_basic['lcc_size']} ({metrics_basic['lcc_pct']:.1f}%)")
    print(f"  Clustering global:      {metrics_basic['clustering_global']:.4f}")
    
    if metrics_weighted:
        print("\nMétricas Ponderadas:")
        print(f"  Fuerza media:           {metrics_weighted['avg_strength']:.2f}")
        print(f"  Fuerza máxima:          {metrics_weighted['max_strength']:.2f}")
        print(f"  Fuerza mínima:          {metrics_weighted['min_strength']:.2f}")
        print(f"  Desv. std. fuerza:      {metrics_weighted['std_strength']:.2f}")
        print(f"  Peso total red:         {metrics_weighted['total_weight']:.0f}")
        print(f"  Peso medio arista:      {metrics_weighted['avg_edge_weight']:.2f}")
    
    print("="*60 + "\n")

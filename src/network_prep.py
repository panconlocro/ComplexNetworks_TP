"""
Preparación de datos de red.
Construcción de redes bipartitas y proyecciones cliente-cliente.
"""

import pandas as pd
import networkx as nx
from pathlib import Path
from typing import Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


def create_bipartite_edges(
    df: pd.DataFrame,
    person_col: str = 'PERSONA',
    service_col: str = 'TIPO DE SERVICIO',
    year_col: str = 'AÑO'
) -> pd.DataFrame:
    """
    Crea lista de aristas para red bipartita Persona-Servicio.
    
    Args:
        df: DataFrame con datos limpios.
        person_col: Nombre de columna de personas.
        service_col: Nombre de columna de servicios.
        year_col: Nombre de columna de año.
        
    Returns:
        DataFrame con aristas (persona, servicio, año).
    """
    logger.info("Creando aristas bipartitas Persona-Servicio")
    
    # Verificar columnas
    required_cols = [person_col, service_col, year_col]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Columnas faltantes: {missing}")
    
    # Crear aristas únicas
    edges = df[[person_col, service_col, year_col]].copy()
    edges = edges.drop_duplicates()
    
    # Renombrar para claridad
    edges.columns = ['persona', 'servicio', 'anio']
    
    logger.info(f"Aristas bipartitas creadas: {len(edges)} conexiones únicas")
    
    return edges


def create_bipartite_graph(edges_df: pd.DataFrame) -> nx.Graph:
    """
    Crea un grafo bipartito a partir de la lista de aristas.
    
    Args:
        edges_df: DataFrame con columnas (persona, servicio, anio).
        
    Returns:
        Grafo bipartito de NetworkX.
    """
    logger.info("Construyendo grafo bipartito")
    
    G = nx.Graph()
    
    # Añadir nodos de personas
    personas = edges_df['persona'].unique()
    G.add_nodes_from(personas, bipartite=0, node_type='persona')
    
    # Añadir nodos de servicios
    servicios = edges_df['servicio'].unique()
    G.add_nodes_from(servicios, bipartite=1, node_type='servicio')
    
    # Añadir aristas
    for _, row in edges_df.iterrows():
        G.add_edge(row['persona'], row['servicio'], anio=row['anio'])
    
    logger.info(f"Grafo bipartito: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")
    logger.info(f"  Personas: {len(personas)}, Servicios: {len(servicios)}")
    
    return G


def project_client_client(
    bipartite_graph: nx.Graph
) -> Tuple[nx.Graph, pd.DataFrame]:
    """
    Proyecta el grafo bipartito a una red cliente-cliente ponderada.
    El peso es el número de servicios compartidos.
    
    Args:
        bipartite_graph: Grafo bipartito.
        
    Returns:
        Tupla (grafo proyectado, DataFrame de aristas con pesos).
    """
    logger.info("Proyectando red cliente-cliente")
    
    # Obtener nodos de personas (bipartite=0)
    personas = {n for n, d in bipartite_graph.nodes(data=True) if d.get('bipartite') == 0}
    
    # Crear proyección ponderada
    # El peso es el número de vecinos (servicios) compartidos
    G_proj = nx.Graph()
    G_proj.add_nodes_from(personas)
    
    # Calcular pesos
    edges_with_weights = []
    
    personas_list = list(personas)
    for i, p1 in enumerate(personas_list):
        # Servicios de p1
        servicios_p1 = set(bipartite_graph.neighbors(p1))
        
        for p2 in personas_list[i+1:]:
            # Servicios de p2
            servicios_p2 = set(bipartite_graph.neighbors(p2))
            
            # Servicios compartidos
            shared = servicios_p1.intersection(servicios_p2)
            
            if len(shared) > 0:
                weight = len(shared)
                G_proj.add_edge(p1, p2, weight=weight)
                edges_with_weights.append({
                    'persona1': p1,
                    'persona2': p2,
                    'peso': weight,
                    'servicios_compartidos': list(shared)
                })
    
    logger.info(f"Proyección cliente-cliente: {G_proj.number_of_nodes()} nodos, {G_proj.number_of_edges()} aristas")
    
    edges_df = pd.DataFrame(edges_with_weights)
    
    return G_proj, edges_df


def export_network_data(
    edges_bipartita: pd.DataFrame,
    edges_proyeccion: pd.DataFrame,
    processed_path: Path,
    config: Dict[str, Any]
) -> None:
    """
    Exporta los datos de red a archivos CSV.
    
    Args:
        edges_bipartita: DataFrame con aristas bipartitas.
        edges_proyeccion: DataFrame con aristas de proyección.
        processed_path: Ruta al directorio de datos procesados.
        config: Diccionario de configuración.
    """
    processed_path = Path(processed_path)
    processed_path.mkdir(parents=True, exist_ok=True)
    
    # Exportar aristas bipartitas
    bipartita_path = processed_path / config['outputs']['edges_bipartita']
    edges_bipartita.to_csv(bipartita_path, index=False, encoding='utf-8')
    logger.info(f"Aristas bipartitas exportadas: {bipartita_path}")
    
    # Exportar proyección
    proyeccion_path = processed_path / config['outputs']['proyeccion_cc_ponderada']
    
    # Simplificar formato de proyección para exportar
    edges_export = edges_proyeccion[['persona1', 'persona2', 'peso']].copy()
    edges_export.to_csv(proyeccion_path, index=False, encoding='utf-8')
    logger.info(f"Proyección cliente-cliente exportada: {proyeccion_path}")


def prepare_networks(
    df_clean: pd.DataFrame,
    config: Dict[str, Any],
    processed_path: Path
) -> Tuple[nx.Graph, nx.Graph, pd.DataFrame, pd.DataFrame]:
    """
    Pipeline completo de preparación de redes.
    
    Args:
        df_clean: DataFrame con datos limpios.
        config: Diccionario de configuración.
        processed_path: Ruta para exportar archivos.
        
    Returns:
        Tupla (grafo_bipartito, grafo_proyeccion, edges_bipartita, edges_proyeccion).
    """
    logger.info("Iniciando preparación de redes")
    
    # 1. Crear aristas bipartitas
    edges_bipartita = create_bipartite_edges(df_clean)
    
    # 2. Crear grafo bipartito
    G_bipartito = create_bipartite_graph(edges_bipartita)
    
    # 3. Proyectar cliente-cliente
    G_proyeccion, edges_proyeccion = project_client_client(G_bipartito)
    
    # 4. Exportar datos
    export_network_data(edges_bipartita, edges_proyeccion, processed_path, config)
    
    logger.info("Preparación de redes completada")
    
    return G_bipartito, G_proyeccion, edges_bipartita, edges_proyeccion

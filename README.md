# Análisis de Redes y Consumo de Servicios - Hito 1

Proyecto de análisis de redes complejas aplicado al consumo de servicios. Este repositorio contiene el pipeline completo de ingesta, limpieza, EDA y métricas básicas de red.

## 🎯 Alcance del Hito 1

Este hito se enfoca en:
- ✅ Ingesta y profiling de datos
- ✅ Limpieza y validación con trazabilidad
- ✅ Construcción de redes bipartitas y proyecciones
- ✅ Métricas básicas: N, E, densidad, grado, fuerza, LCC, clustering
- ✅ Visualizaciones descriptivas

**NO incluye** (para hitos posteriores):
- ❌ Comunidades (Louvain, GN)
- ❌ Centralidades costosas (betweenness, closeness, eigenvector)
- ❌ Filtros avanzados o Jaccard
- ❌ Comparativas interanuales complejas

## 📁 Estructura del Proyecto

```
ComplexNetworks_TP/
├── config/
│   └── config.yaml              # Configuración central (rutas, dominios, parámetros)
├── data/
│   ├── raw/                     # Datos crudos (no modificar)
│   └── processed/               # Datos procesados y limpios
│       ├── *_snapshot.csv       # Snapshot para trazabilidad
│       ├── datos_limpios.csv    # Dataset limpio final
│       ├── edges_bipartita.csv  # Aristas Persona-Servicio
│       └── proyeccion_cc_ponderada.csv  # Red cliente-cliente
├── notebooks/
│   ├── 01_ingesta.ipynb         # Ingesta y profiling inicial
│   ├── 02_limpieza.ipynb        # Limpieza y validación
│   └── 03_eda.ipynb             # EDA y métricas de red
├── reports/
│   ├── figures/                 # Gráficos generados
│   │   ├── hist_grado.png
│   │   ├── hist_fuerza.png
│   │   ├── barras_modalidad_por_anio.png
│   │   └── barras_complejidad_por_anio.png
│   ├── etl.log                  # Log del pipeline
│   ├── limpieza_log.csv         # Log de limpieza (CSV)
│   ├── limpieza_log.md          # Log de limpieza (Markdown)
│   └── metricas_resumen.csv     # Resumen de métricas
├── src/                         # Paquete Python reutilizable
│   ├── __init__.py
│   ├── config_loader.py         # Carga y validación de config.yaml
│   ├── logging_setup.py         # Configuración de logging
│   ├── io_utils.py              # Lectura/escritura de archivos
│   ├── validate.py              # Validación de esquema y dominios
│   ├── cleaning.py              # Pipeline de limpieza
│   ├── network_prep.py          # Construcción de redes
│   └── eda_basic.py             # Métricas y visualizaciones
├── requirements.txt             # Dependencias Python
├── .gitignore
└── README.md                    # Este archivo
```

## 🚀 Instalación y Uso

### 1. Clonar el repositorio

```bash
git clone <repository-url>
cd ComplexNetworks_TP
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Colocar datos crudos

Coloca tu archivo de datos (CSV o Excel) en `data/raw/`. El pipeline detectará automáticamente el archivo.

### 4. Ejecutar notebooks en orden

```bash
jupyter notebook
```

Ejecuta los notebooks en secuencia:
1. `01_ingesta.ipynb` - Carga datos y genera snapshot
2. `02_limpieza.ipynb` - Limpia y valida datos
3. `03_eda.ipynb` - Análisis exploratorio y métricas de red

Cada notebook es **idempotente**: puedes ejecutar "Run All" múltiples veces y regenerará todos los artefactos.

## ⚙️ Configuración

Toda la configuración está centralizada en `config/config.yaml`:

- **Rutas**: Directorios de entrada/salida (relativas)
- **Columnas esperadas**: Esquema del dataset
- **Dominios**: Valores permitidos para variables categóricas
- **Semilla aleatoria**: Para reproducibilidad
- **Parámetros de gráficos**: DPI, tamaño, formato

**No hardcodees rutas**: todo debe salir del config.

## 📊 Artefactos Generados

### Datos

- `datos_limpios.csv`: Dataset validado y normalizado
- `edges_bipartita.csv`: Aristas de la red bipartita Persona-Servicio
- `proyeccion_cc_ponderada.csv`: Red cliente-cliente con pesos (servicios compartidos)

### Figuras

- `hist_grado.png`: Distribución de grado
- `hist_fuerza.png`: Distribución de fuerza (strength)
- `barras_modalidad_por_anio.png`: Modalidad por año
- `barras_complejidad_por_anio.png`: Complejidad por año

### Logs y Reportes

- `etl.log`: Log completo del pipeline
- `limpieza_log.md` / `.csv`: Documentación de transformaciones
- `metricas_resumen.csv`: Métricas de red exportadas

## 🔍 Métricas Calculadas

**Red Bipartita Persona-Servicio:**
- N (nodos), E (aristas)
- Densidad
- Grado medio/máx/mín
- Nodos aislados
- Componentes conectados
- Tamaño del LCC
- Clustering global

**Red Proyección Cliente-Cliente:**
- Todas las anteriores, más:
- Fuerza (strength) media/máx/mín
- Peso total de la red
- Peso medio por arista

## 🧪 Validaciones

El pipeline incluye validaciones automáticas:

✅ **Esquema**: Columnas esperadas presentes  
✅ **Dominios**: Valores dentro de rangos permitidos  
✅ **Duplicados**: Detección en clave (Persona, Tipo_Servicio, Año)  
✅ **Nulos**: Identificación y manejo  

Los reportes de validación se generan pre y post limpieza.

## 📝 Logs y Trazabilidad

Cada paso del pipeline genera logs:

- **Snapshots**: Copia "as-is" de datos crudos
- **Cleaning Log**: Contadores antes/después, operaciones realizadas
- **ETL Log**: Eventos timestamped con niveles (INFO, WARNING, ERROR)

## 🛠️ Módulos del Paquete `src/`

| Módulo | Descripción |
|--------|-------------|
| `config_loader.py` | Carga y valida configuración YAML |
| `logging_setup.py` | Logger estándar con formato consistente |
| `io_utils.py` | Lectura/escritura segura, detección automática de archivos |
| `validate.py` | Contratos de calidad: esquema, dominios, duplicados |
| `cleaning.py` | Normalización, deduplicación, pipeline completo |
| `network_prep.py` | Construcción de redes bipartitas y proyecciones |
| `eda_basic.py` | Métricas básicas de red y visualizaciones |

Todos los módulos tienen:
- ✅ Type hints
- ✅ Docstrings
- ✅ Funciones puras y testables
- ✅ Logging integrado

## 📋 Requisitos

Ver `requirements.txt` para versiones específicas. Principales dependencias:

- Python 3.8+
- pandas
- numpy
- networkx
- matplotlib
- PyYAML
- openpyxl (para archivos Excel)

## 🤝 Contribución

Este es un proyecto académico. Para contribuir:

1. Crea una rama desde `develop`
2. Mantén el estilo de código consistente
3. Actualiza documentación si es necesario
4. Asegúrate de que los notebooks sean reproducibles

## 📄 Licencia

Ver archivo `LICENSE` en el repositorio.

---

**Proyecto**: Análisis de Redes Complejas  
**Hito**: 1 - Ingesta, Limpieza y EDA Básico  
**Estado**: ✅ Completado
-----
## Instalar dependencias en un .venv

pip install -r requirements.txt


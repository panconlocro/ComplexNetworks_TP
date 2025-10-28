# Guía de Ejecución Rápida - Hito 1

## ⚡ Quick Start

### 1. Preparar el entorno

```bash
# Clonar y entrar al proyecto
cd ComplexNetworks_TP

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Verificar estructura

Asegúrate de que existe:
- `config/config.yaml` ✅
- `data/raw/` con tu archivo de datos ✅
- `src/` con los módulos Python ✅

### 3. Ejecutar notebooks

```bash
# Iniciar Jupyter
jupyter notebook

# O usar VS Code con la extensión de Jupyter
```

**Orden de ejecución:**

1. **`01_ingesta.ipynb`**
   - Detecta automáticamente el archivo en `data/raw/`
   - Genera snapshot en `data/processed/`
   - Output: `*_snapshot.csv`

2. **`02_limpieza.ipynb`**
   - Lee el snapshot
   - Aplica validaciones y limpieza
   - Output: `datos_limpios.csv`, logs de limpieza

3. **`03_eda.ipynb`**
   - Construye redes
   - Calcula métricas
   - Genera visualizaciones
   - Output: aristas, figuras, resumen de métricas

## 📋 Checklist de Verificación

Después de ejecutar los 3 notebooks, deberías tener:

### En `data/processed/`:
- [ ] `*_snapshot.csv` (copia cruda)
- [ ] `datos_limpios.csv`
- [ ] `edges_bipartita.csv`
- [ ] `proyeccion_cc_ponderada.csv`

### En `reports/`:
- [ ] `etl.log`
- [ ] `limpieza_log.csv`
- [ ] `limpieza_log.md`
- [ ] `metricas_resumen.csv`

### En `reports/figures/`:
- [ ] `hist_grado.png`
- [ ] `hist_fuerza.png`
- [ ] `barras_modalidad_por_anio.png`
- [ ] `barras_complejidad_por_anio.png`

## 🔧 Troubleshooting

### Error: "Archivo de configuración no encontrado"

**Solución**: Verifica que `config/config.yaml` existe y estás ejecutando los notebooks desde `notebooks/`

### Error: "No se encontraron archivos en data/raw/"

**Solución**: Coloca tu archivo `.csv` o `.xlsx` en `data/raw/`

### Error: "Import 'yaml' could not be resolved"

**Solución**: 
```bash
pip install PyYAML
```

### Error: Columnas faltantes en validación

**Solución**: Verifica que tu dataset tenga las columnas esperadas en `config.yaml`:
- PERSONA
- TIPO DE SERVICIO
- NOMBRE DE LA TAREA
- AÑO
- MODALIDAD
- COMPLEJIDAD

Si tus columnas tienen otros nombres, actualiza `config.yaml` o renombra las columnas.

### Los notebooks no encuentran los módulos de `src/`

**Solución**: Los notebooks añaden `src/` al path automáticamente. Si persiste:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd().parent / 'src'))
```

## 🎯 Validación de Resultados

### Test rápido en Python:

```python
import pandas as pd
from pathlib import Path

# Verificar datos limpios
df = pd.read_csv('data/processed/datos_limpios.csv')
print(f"✓ Datos limpios: {df.shape}")

# Verificar aristas
edges = pd.read_csv('data/processed/edges_bipartita.csv')
print(f"✓ Aristas bipartitas: {len(edges)}")

# Verificar figuras
figures = list(Path('reports/figures').glob('*.png'))
print(f"✓ Figuras generadas: {len(figures)}")
```

## 🔄 Re-ejecutar el Pipeline

Para regenerar todo desde cero:

1. **Opción conservadora** (mantiene logs):
   - Ejecuta "Run All" en cada notebook

2. **Opción completa** (limpia todo):
```bash
# Limpiar outputs (¡cuidado!)
rm data/processed/*.csv
rm reports/*.log
rm reports/*.csv
rm reports/*.md
rm reports/figures/*.png

# Re-ejecutar notebooks
```

## 📊 Interpretar los Resultados

### Métricas clave:

- **Densidad**: Qué tan conectada está la red (0 a 1)
- **Grado medio**: Promedio de conexiones por nodo
- **LCC %**: Porcentaje de nodos en la componente gigante
- **Clustering**: Tendencia a formar triángulos

### Valores esperados (red social):
- Densidad: < 0.1 (redes grandes son sparse)
- LCC: > 50% (mayoría conectada)
- Clustering: > 0 (estructura social)

## 💡 Tips

1. **Reproducibilidad**: La semilla aleatoria está fija en `config.yaml`
2. **Idempotencia**: Ejecutar múltiples veces da el mismo resultado
3. **Trazabilidad**: Revisa `reports/etl.log` para debug
4. **Limpieza**: El log detalla qué se modificó y por qué

## 📞 Soporte

Si encuentras problemas:
1. Revisa `reports/etl.log`
2. Verifica que todos los imports funcionan
3. Asegúrate de ejecutar los notebooks en orden
4. Valida que `config.yaml` esté bien formateado (sintaxis YAML)

---

**¡Listo para ejecutar! 🚀**

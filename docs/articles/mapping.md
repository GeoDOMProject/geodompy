# Funciones de Mapeo en geodompy

Este artículo explora las capacidades de mapeo de geodompy, mostrando cómo crear mapas coropléticos profesionales de la República Dominicana.

## Introducción

geodompy proporciona una interfaz simple pero poderosa para crear mapas temáticos de la República Dominicana. Con una sola línea de código, puedes visualizar datos a cualquier nivel administrativo.

## Preparación de datos

Para crear un mapa, necesitas un DataFrame con:

1. Una columna con nombres geográficos (provincias, municipios, etc.)
2. Una o más columnas con valores a visualizar

```python
import pandas as pd
import geodompy as gd

# Datos de ejemplo: población por provincia
datos_poblacion = pd.DataFrame({
    'provincia': [
        'Santo Domingo', 'Distrito Nacional', 'Santiago', 
        'San Cristóbal', 'La Vega', 'Puerto Plata',
        'Duarte', 'La Altagracia', 'San Pedro de Macorís'
    ],
    'poblacion_2020': [
        3_339_410, 1_029_110, 1_049_530,
        660_000, 404_000, 332_000,
        297_000, 337_000, 301_000
    ],
    'densidad_km2': [
        2582, 10701, 388,
        461, 169, 173,
        189, 128, 218
    ]
})
```

## Mapa básico

```python
# Crear mapa - geodompy detecta automáticamente el nivel y la variable
gd.map(datos_poblacion)
```

Por defecto, geodompy:
- Detecta que los datos son de nivel provincial
- Selecciona la variable numérica más apropiada para fill
- Aplica una paleta de colores predeterminada

## Personalización del mapa

### Seleccionar variable de fill

```python
# Mapear densidad en lugar de población
gd.map(datos_poblacion, fill='densidad_km2')
```

### Cambiar paleta de colores

```python
# Paleta de rojos
gd.map(datos_poblacion, fill='poblacion_2020', cmap='Reds')

# Paleta inversa
gd.map(datos_poblacion, fill='poblacion_2020', cmap='Reds_r')
```

### Agregar título y personalizar apariencia

```python
gd.map(
    datos_poblacion,
    fill='poblacion_2020',
    title='Población por Provincia (2020)',
    cmap='YlOrRd',
    figsize=(14, 10),
    edgecolor='darkgray',
    linewidth=0.8
)
```

## Trabajo avanzado con map_data()

Para mayor control, usa `map_data()` para obtener el GeoDataFrame:

```python
import matplotlib.pyplot as plt

# Obtener GeoDataFrame con datos unidos
gdf = gd.map_data(datos_poblacion)

# Crear figura personalizada
fig, ax = plt.subplots(1, 1, figsize=(12, 10))

# Plotear con opciones avanzadas
gdf.plot(
    column='poblacion_2020',
    ax=ax,
    cmap='YlOrRd',
    legend=True,
    legend_kwds={
        'label': 'Población',
        'orientation': 'horizontal',
        'shrink': 0.6,
        'pad': 0.05
    },
    missing_kwds={
        'color': 'lightgray',
        'label': 'Sin datos'
    }
)

# Personalizar
ax.set_title('Población de República Dominicana por Provincia', fontsize=16, fontweight='bold')
ax.axis('off')

# Agregar anotación
ax.annotate(
    'Fuente: ONE (2020)', 
    xy=(0.02, 0.02), 
    xycoords='axes fraction',
    fontsize=8, 
    style='italic'
)

plt.tight_layout()
plt.savefig('mapa_poblacion.png', dpi=300, bbox_inches='tight')
plt.show()
```

## Mapas comparativos

```python
fig, axes = plt.subplots(1, 2, figsize=(18, 8))

# Mapa 1: Población
gdf = gd.map_data(datos_poblacion, fill='poblacion_2020')
gdf.plot(column='poblacion_2020', ax=axes[0], cmap='Blues', legend=True)
axes[0].set_title('Población Total')
axes[0].axis('off')

# Mapa 2: Densidad
gdf.plot(column='densidad_km2', ax=axes[1], cmap='Reds', legend=True)
axes[1].set_title('Densidad (hab/km²)')
axes[1].axis('off')

plt.suptitle('Comparación: Población vs Densidad', fontsize=16, fontweight='bold')
plt.tight_layout()
plt.show()
```

## Mapas a diferentes niveles

### Nivel de regiones

```python
datos_regiones = pd.DataFrame({
    'region': ['Ozama', 'Cibao Norte', 'Cibao Sur', 'Valdesia'],
    'pib_2020': [45.2, 22.1, 8.5, 12.3]
})

gd.map(datos_regiones, fill='pib_2020', title='PIB por Región (miles de millones RD$)')
```

### Nivel municipal

```python
datos_municipios = pd.DataFrame({
    'municipio': ['Santo Domingo Este', 'Santiago', 'Santo Domingo Norte'],
    'empresas': [15000, 8500, 7200]
})

gd.map(datos_municipios, fill='empresas', title='Número de Empresas')
```

## Integración con otros análisis

### Análisis de correlación espacial

```python
import geopandas as gpd
from libpysal.weights import Queen
import esda

# Obtener datos unidos
gdf = gd.map_data(datos_poblacion, fill='densidad_km2')

# Crear matriz de pesos espaciales
w = Queen.from_dataframe(gdf)

# Calcular I de Moran
mi = esda.Moran(gdf['densidad_km2'].fillna(0), w)
print(f"I de Moran: {mi.I:.4f}")
print(f"p-value: {mi.p_sim:.4f}")
```

## Conclusión

geodompy simplifica significativamente el proceso de crear mapas de República Dominicana, desde visualizaciones rápidas hasta mapas publicables. La integración con el ecosistema de Python (matplotlib, geopandas) permite personalización ilimitada.

## Recursos adicionales

- [Guía de paletas de colores de matplotlib](https://matplotlib.org/stable/tutorials/colors/colormaps.html)
- [Documentación de geopandas](https://geopandas.org/)
- [geodomR (versión R)](https://drdsdaniel.github.io/geodomR/)

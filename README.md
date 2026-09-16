# geodompy

Version actual: `1.2.0`.

Acceso a datos geoespaciales estandarizados de República Dominicana en Python.

## Instalación

```bash
pip install https://github.com/GeoDOMProject/geodompy/releases/download/v1.2.0/geodompy-1.2.0-py3-none-any.whl
```

## Uso Rápido

```python
import geodompy as gd
import pandas as pd

# Obtener provincias como GeoDataFrame
provincias = gd.provinces()

# Crear mapa automático
datos = pd.DataFrame({
    "provincia": ["Santo Domingo", "Santiago", "La Vega"],
    "poblacion": [2500000, 1000000, 400000],
})

gd.map(datos)  # Detecta nivel y variable automáticamente
```

Las categorías aceptan colores exactos y un fondo personalizado:

```python
colores = {
    "DAVID COLLADO": "#1565c0",
    "CAROLINA MEJÍA": "#ffffff",
    "WELLINGTON ARNAUD": "#f1d7a3",
    "LEONEL FERNÁNDEZ": "#2e7d32",
}
gd.map(datos, fill="preferencia", colors=colores, background_color="#526860")
```

También puedes usar aliases con prefijo `gd_*` para acercarte a la API de
`geodomR`:

```python
provincias = gd.gd_provinces()
gd.gd_map(datos, labels=True)
```

## Alcance

`geodompy` cubre datos, detección, limpieza, mapeo y jerarquía territorial:

- Limpieza: `clean_prov_name()`, `clean_region_name()`,
  `clean_municipality_name()`, `clean_dm_name()`, `clean_section_name()`,
  `clean_bparaje_name()` y `clean_zone_name()`.
- Jerarquía: `add_parent_cols()` agrega columnas superiores como `Region`,
  `Provincia`, `Municipio`, `Distrito_Municipal` y `Seccion`.
- Mapeo: `map()`, `map_data()`, `gd_mpl_plot()` y `gd_geom_sf()`.

## Interoperabilidad con R

Los paquetes usan las mismas fuentes públicas, con cachés separadas para evitar
mezclar objetos RDS de R y Parquet de Python. Python guarda sus pines en
`~/.geodom/python-v1` (en Windows, dentro de Documents). `GEODOM_CACHE_DIR`
permite cambiar la raíz. La caché anterior se conserva sin modificar.

## Desarrollo

```bash
pytest
```

## Licencia

MIT

## Mapas interactivos (1.2.0)

```python
import pandas as pd
import geodompy as gd
data = pd.DataFrame({'PROV_CODE': ['01', '25'], 'valor': [0, 34]})
mapa = gd.map_interactive(data, fill='valor', level='provinces',
                         name='PROV_CODE', key='PROV_CODE', file='mapa.html')
mapa  # Vista integrada en notebooks.
# mapa.save('otra-copia.html')
```

`map_interactive` devuelve un `InteractiveMap`, compatible con texto HTML, `.save()`
y visualización en notebooks. `context=False` omite las capas adicionales.
No requiere Plotly ni una conexión a un servicio de mapas para abrir el HTML sin fondo.

El HTML incluye el visor, los estilos y las geometrías. Permite zoom, desplazamiento,
búsqueda por nombre o código, consulta de atributos y filtros por provincia y municipio.
Las capas de contexto se identifican como límites sin datos: no se reparten las cifras
de una provincia entre sus municipios. La leyenda conserva su escala al filtrar.

El fondo predeterminado funciona sin internet después de generar el archivo.
El fondo opcional de calles OpenStreetMap requiere conexión y conserva la atribución.
Las etiquetas permanentes se muestran hasta 300 territorios; en capas mayores se
consultan al señalar o tras filtrar. Los resultados de búsqueda muestran hasta 30
territorios a la vez; el mapa conserva todos los que coinciden.

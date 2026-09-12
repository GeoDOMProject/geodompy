# geodompy

Version actual: `1.0.0`.

Acceso a datos geoespaciales estandarizados de República Dominicana en Python.

## Instalación

```bash
pip install https://github.com/GeoDOMProject/geodompy/releases/download/v1.0.0/geodompy-1.0.0-py3-none-any.whl
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

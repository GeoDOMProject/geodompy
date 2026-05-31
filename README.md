# geodompy

Version actual: `0.2.0`.

Acceso a datos geoespaciales estandarizados de República Dominicana en Python.

## Instalación

```bash
pip install geodompy
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

Este paquete usa `pins` para caché local, lo que permite compartir datos
descargados entre Python y R (`geodomR`).

## Desarrollo

```bash
pytest
```

## Licencia

MIT

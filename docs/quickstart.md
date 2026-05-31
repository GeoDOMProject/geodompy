# Inicio Rápido

Esta guía te mostrará cómo empezar a usar geodompy en 5 minutos.

## Paso 1: Importar geodompy

```python
import geodompy as gd
import pandas as pd
```

## Paso 2: Obtener datos geográficos

```python
# Provincias de República Dominicana
provincias = gd.provinces()
print(provincias.head())
```

Salida:
```
   PROV  PROV_CODE      TOPONIMIA                                           geometry
0    01         01          Azua  MULTIPOLYGON (((-70.73889 18.34861, -70.73806 ...
1    02         02       Bahoruco  MULTIPOLYGON (((-71.70833 18.51111, -71.70556 ...
2    03         03       Barahona  MULTIPOLYGON (((-71.09167 18.02500, -71.08889 ...
...
```

## Paso 3: Crear un mapa básico

```python
# Tus datos
datos = pd.DataFrame({
    'provincia': ['Santo Domingo', 'Santiago', 'La Vega', 'Puerto Plata'],
    'poblacion': [2500000, 1000000, 400000, 350000]
})

# Crear mapa (detecta automáticamente nivel y variable)
gd.map(datos)
```

## Paso 4: Limpiar nombres

Cuando tus datos tienen nombres con variaciones:

```python
# Nombres con errores o variaciones
nombres_sucios = ['sto dgo', 'stgo', 'la vegas', 'pto plata']

# Limpiar y estandarizar
nombres_limpios = gd.clean_prov_name(nombres_sucios, tolerance=0.5)
print(nombres_limpios)
# ['Santo Domingo', 'Santiago', 'La Vega', 'Puerto Plata']
```

## Paso 5: Detectar nivel automáticamente

```python
datos = pd.DataFrame({
    'nombre': ['Azua', 'Bahoruco', 'Barahona'],
    'valor': [100, 200, 300]
})

# ¿Qué nivel geográfico son estos datos?
info = gd.detect_level(datos)
print(f"Nivel: {info['level']}")        # 'provinces'
print(f"Columna: {info['name']}")       # 'nombre'
print(f"Clave: {info['key']}")          # 'TOPONIMIA'
```

## Funciones principales

| Categoría | Funciones |
|-----------|-----------|
| **Datos** | `provinces()`, `regions()`, `municipalities()`, `dm()`, `sections()`, `zones()`, `bparajes()`, `macroregions()` |
| **Limpieza** | `clean_prov_name()`, `clean_region_name()`, `clean_municipality_name()`, `clean_zone_name()` |
| **Detección** | `detect_level()`, `detect_fill()`, `detect_column_type()`, `analyze_columns()` |
| **Mapeo** | `map()`, `map_data()` |

## Próximos pasos

- [Funciones de Datos](guides/data-functions.md) - Explora todos los datasets disponibles
- [Funciones de Limpieza](guides/cleaning-functions.md) - Aprende sobre fuzzy matching
- [Detección Automática](guides/detection.md) - Cómo funciona la magia
- [Mapeo](guides/mapping.md) - Personaliza tus mapas

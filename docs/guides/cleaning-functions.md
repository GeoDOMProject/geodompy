# Funciones de Limpieza

Las funciones de limpieza en geodompy permiten estandarizar nombres de unidades administrativas que pueden tener variaciones, errores tipográficos o abreviaturas.

## ¿Por qué limpiar nombres?

Los datos del mundo real frecuentemente contienen inconsistencias:

| Original | Problema | Correcto |
|----------|----------|----------|
| "sto dgo" | Abreviatura | "Santo Domingo" |
| "SANTIAGO" | Mayúsculas | "Santiago" |
| "la vegas" | Typo | "La Vega" |
| "Pto. Plata" | Puntuación | "Puerto Plata" |

## clean_prov_name

Limpia y estandariza nombres de provincias.

```python
import geodompy as gd

# Nombres con variaciones
nombres_sucios = ['azua', 'barahona', 'stgo', 'sto dgo', 'Pto Plata']

# Limpiar
nombres_limpios = gd.clean_prov_name(nombres_sucios)
print(nombres_limpios)
# ['Azua', 'Barahona', 'Santiago', 'Santo Domingo', 'Puerto Plata']
```

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `names` | list[str] | - | Nombres a limpiar |
| `tolerance` | float | 0.25 | Tolerancia para fuzzy matching (0-1) |
| `on_error` | str | "fail" | Qué hacer si no hay match: "fail", "na", "omit" |

### Control de tolerancia

```python
# Más estricto (menos falsos positivos)
gd.clean_prov_name(['stgo'], tolerance=0.1)

# Más permisivo (más matches)
gd.clean_prov_name(['stgo'], tolerance=0.5)
```

### Manejo de errores

```python
# Fallar si no hay match (default)
gd.clean_prov_name(['nombre_invalido'], on_error='fail')
# ValueError: No se pudo emparejar 'nombre_invalido'...

# Retornar None para no matches
gd.clean_prov_name(['nombre_invalido'], on_error='na')
# [None]

# Mantener original si no hay match
gd.clean_prov_name(['nombre_invalido'], on_error='omit')
# ['nombre_invalido']
```

## clean_region_name

Limpia nombres de regiones de planificación.

```python
regiones = ['cibao norte', 'valdesia', 'enriquillo']
limpios = gd.clean_region_name(regiones)
print(limpios)
# ['Cibao Norte', 'Valdesia', 'Enriquillo']
```

## clean_municipality_name

Limpia nombres de municipios.

```python
municipios = ['santo domingo este', 'stgo de los cab', 'la romana']
limpios = gd.clean_municipality_name(municipios)
print(limpios)
# ['Santo Domingo Este', 'Santiago de los Caballeros', 'La Romana']
```

## clean_zone_name

Limpia nombres de zonas (urbana/rural).

```python
zonas = ['zona urbana', 'campo', 'ciudad', 'rural']
limpios = gd.clean_zone_name(zonas)
print(limpios)
# ['Urbana', 'Rural', 'Urbana', 'Rural']
```

## Sistema de Alias

Las funciones de limpieza utilizan datasets de alias que contienen variaciones comunes de nombres. Esto proporciona mejor matching que el fuzzy matching simple.

```python
# El sistema internamente carga alias como:
# PROV_ID | PROV_NAME
# 25      | Santiago
# 25      | Stgo
# 25      | Santiago de los Caballeros
```

## Ejemplo: Limpieza en pipeline

```python
import pandas as pd
import geodompy as gd

# Datos sucios
datos = pd.DataFrame({
    'prov': ['sto dgo', 'stgo', 'la vega', 'pto pta'],
    'ventas': [1000, 800, 500, 300]
})

# Limpiar antes de mapear
datos['prov_limpia'] = gd.clean_prov_name(
    datos['prov'].tolist(),
    tolerance=0.5,
    on_error='na'
)

# Ahora podemos mapear con confianza
gd.map(datos[['prov_limpia', 'ventas']].rename(columns={'prov_limpia': 'provincia'}))
```

## Casos especiales

### Valores None o NaN

```python
import numpy as np

nombres = ['Santiago', None, np.nan, 'La Vega']
limpios = gd.clean_prov_name(nombres, on_error='na')
# ['Santiago', None, None, 'La Vega']
```

### Duplicados

Las funciones manejan duplicados correctamente:

```python
nombres = ['stgo', 'stgo', 'stgo']
limpios = gd.clean_prov_name(nombres)
# ['Santiago', 'Santiago', 'Santiago']
```

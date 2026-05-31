# Funciones de Datos

geodompy proporciona acceso a datos geoespaciales estandarizados de la República Dominicana en varios niveles administrativos.

## Provincias

La República Dominicana está dividida en 31 provincias más el Distrito Nacional.

```python
import geodompy as gd

# Obtener todas las provincias
provincias = gd.provinces()
print(f"Total de provincias: {len(provincias)}")

# Con columna de región administrativa (Ley 345-22)
provincias_reg = gd.provinces(reg="rup")
```

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `id` | str | "RD_PROV" | Nombre del dataset |
| `sf` | bool | True | Si True, retorna GeoDataFrame con geometría |
| `reg` | str | None | Si "rup", agrega columna de región |
| `verbose` | bool | False | Mostrar mensajes de progreso |

## Regiones de Planificación

Las regiones de planificación facilitan la administración y planificación territorial.

```python
# Regiones Únicas de Planificación (Ley 345-22)
regiones = gd.regions()

# Regiones según Decreto 710-04
regiones_710 = gd.regions(id="RD_REG71004")
```

### Datasets disponibles

- `"RD_RUP"` (default): Regiones Únicas de Planificación (Ley 345-22)
- `"RD_REG71004"`: Regiones según Decreto 710-04

## Municipios

La división municipal de la República Dominicana.

```python
# 158 Municipios
municipios = gd.municipalities()

# Versión alternativa con 155 municipios
mun155 = gd.municipalities(id="RD_MUN155")
```

## Distritos Municipales

Los distritos municipales son subdivisiones de los municipios.

```python
dm = gd.dm()
print(f"Total de distritos municipales: {len(dm)}")
```

## Secciones

Las secciones son divisiones censales del territorio.

```python
secciones = gd.sections()
```

!!! warning "Nota"
    El dataset de secciones puede no estar disponible en algunos momentos.
    Usa `verbose=True` para ver mensajes de error.

## Zonas de Residencia

Clasificación urbana/rural.

```python
zonas = gd.zones()
print(zonas)
```

Salida:
```
  ZONE_ID ZONE_CODE ZONE_NAME TOPONIMIA
0      01       URB    Urbana    Urbana
1      02       RUR     Rural     Rural
```

!!! note "Nota"
    `zones()` no tiene geometría - es un dataset de referencia.

## Barrios y Parajes

El nivel más granular de división territorial.

```python
bp = gd.bparajes()
print(f"Total de barrios y parajes: {len(bp)}")
```

## Macro-regiones

Las tres macro-regiones de planificación.

```python
mreg = gd.macroregions()
print(mreg[['MREG_CODE', 'TOPONIMIA']])
```

## Trabajar sin geometría

Todas las funciones de datos aceptan `sf=False` para obtener solo atributos:

```python
# Solo datos, sin geometría
provincias_df = gd.provinces(sf=False)
print(type(provincias_df))  # pandas.DataFrame
```

## Caché y actualizaciones

Los datos se descargan una sola vez y se almacenan en caché local:

```python
# Primera llamada: descarga
provincias = gd.provinces(verbose=True)

# Segunda llamada: usa caché
provincias = gd.provinces(verbose=True)  # "Usando datos en caché..."
```

El caché se encuentra en:

- **Windows**: `~/Documents/.geodom`
- **Linux/Mac**: `~/.geodom`

Esta ubicación es compatible con el paquete R `geodomR`.

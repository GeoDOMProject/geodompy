# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Versionado Semántico](https://semver.org/lang/es/).

## [0.2.0] - 2026

### AÃ±adido

- Aliases publicos `gd_*` para acercar la API Python a `geodomR`.
- `clean_dm_name()`, `clean_section_name()` y `clean_bparaje_name()`.
- `add_parent_cols()` para agregar columnas superiores de la jerarquia territorial.
- `gd_mpl_plot()` y `gd_geom_sf()` como helpers Matplotlib.
- Soporte de labels en `map()`.

### Cambiado

- `sections()` usa `RD_SECCIONES` por defecto.
- `map_data()` y deteccion incluyen barrios/parajes.
- `get_dataset()` lee pins R como DataFrame y usa cache local cuando no hay red.

## [0.1.0] - 2024

### Añadido

#### Funciones de Datos
- `provinces()` - Obtener límites de provincias
- `regions()` - Obtener regiones de planificación
- `municipalities()` - Obtener límites de municipios
- `dm()` - Obtener distritos municipales
- `sections()` - Obtener secciones censales
- `zones()` - Obtener zonas de residencia (urbana/rural)
- `bparajes()` - Obtener barrios y parajes
- `macroregions()` - Obtener macro-regiones

#### Funciones de Limpieza
- `clean_prov_name()` - Limpiar nombres de provincias
- `clean_region_name()` - Limpiar nombres de regiones
- `clean_municipality_name()` - Limpiar nombres de municipios
- `clean_zone_name()` - Limpiar nombres de zonas

#### Funciones de Detección
- `detect_level()` - Detectar nivel administrativo automáticamente
- `detect_fill()` - Detectar mejor variable para fill
- `detect_column_type()` - Detectar tipo de columna geográfica
- `analyze_columns()` - Analizar todas las columnas de un DataFrame

#### Funciones de Mapeo
- `map()` - Crear mapa coroplético
- `map_data()` - Preparar datos para mapeo

#### Sistema de Caché
- `get_dataset()` - Obtener dataset genérico del servidor
- Sistema de caché local usando `pins`
- Compatibilidad con geodomR (directorio compartido)

### Interoperabilidad
- Caché compartido con geodomR en `~/Documents/.geodom` (Windows) o `~/.geodom` (Unix)
- Formato de datos compatible con pins de R

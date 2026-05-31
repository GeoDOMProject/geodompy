# Detección Automática

geodompy puede detectar automáticamente el nivel geográfico de tus datos y la mejor variable para visualización.

## detect_level

Detecta el nivel administrativo de un DataFrame.

```python
import pandas as pd
import geodompy as gd

datos = pd.DataFrame({
    'nombre': ['Azua', 'Bahoruco', 'Barahona', 'Dajabón'],
    'poblacion': [214311, 91480, 187105, 63955]
})

# Detectar nivel
info = gd.detect_level(datos)
print(info)
```

Salida:
```python
{
    'level': 'provinces',      # Nivel detectado
    'name': 'nombre',          # Columna en tus datos
    'key': 'TOPONIMIA',        # Columna en datos de referencia
    'match_count': 4,          # Valores que coinciden
    'total_count': 4           # Total de valores únicos
}
```

### ¿Cómo funciona?

1. Obtiene datos de referencia de todos los niveles administrativos
2. Para cada columna de texto en tus datos:
   - Compara con cada columna de referencia
   - Cuenta coincidencias (case-insensitive)
3. Retorna el nivel con mejor coincidencia

### Especificar parámetros

Puedes guiar la detección:

```python
# Solo buscar en nivel específico
info = gd.detect_level(datos, level='provinces')

# Especificar columna en tus datos
info = gd.detect_level(datos, name='nombre')

# Todo especificado (sin detección)
info = gd.detect_level(datos, level='provinces', name='nombre', key='TOPONIMIA')
```

## detect_fill

Detecta la mejor variable para fill en un mapa.

```python
datos = pd.DataFrame({
    'provincia': ['Santo Domingo', 'Santiago', 'La Vega'],
    'poblacion': [2500000, 1000000, 400000],
    'codigo': ['A', 'B', 'C'],
    'constante': [1, 1, 1]
})

# Detectar mejor variable para fill
fill_var = gd.detect_fill(datos, exclude=['provincia'])
print(fill_var)  # 'poblacion'
```

### Criterios de selección

| Tipo | Métrica | Preferencia |
|------|---------|-------------|
| Numéricas | Coeficiente de variación | Preferidas (x1.5) |
| Categóricas | Entropía de Shannon | Menor preferencia |

### Exclusiones

```python
# Excluir columnas geográficas
fill = gd.detect_fill(datos, exclude=['provincia', 'codigo'])
```

## detect_column_type

Analiza una columna específica.

```python
provincias = ['Santo Domingo', 'Santiago', 'La Vega', 'Azua']
result = gd.detect_column_type(provincias, 'mi_columna')
print(result)
```

Salida:
```python
{
    'level': 'provinces',
    'name': 'mi_columna',
    'key': 'TOPONIMIA',
    'match_count': 4,
    'total_count': 4
}
```

## analyze_columns

Analiza todas las columnas de un DataFrame.

```python
mis_datos = pd.DataFrame({
    'provincia': ['Santo Domingo', 'Santiago'],
    'municipio': ['Santo Domingo Este', 'Santiago'],
    'region': ['Ozama', 'Cibao Norte'],
    'valor': [100, 200],
    'texto': ['Hola', 'Mundo']
})

resultados = gd.analyze_columns(mis_datos, threshold=0.7)
print(resultados)
```

Salida:
```
  column_name detected_level key_variable  match_count  total_count  match_ratio  is_geographic
0   provincia      provinces    TOPONIMIA            2            2          1.0           True
1   municipio  municipalities    TOPONIMIA            2            2          1.0           True
2      region        regions    TOPONIMIA            2            2          1.0           True
3       texto           None         None            0            2          0.0          False
```

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `data` | DataFrame | - | DataFrame a analizar |
| `threshold` | float | 0.7 | Umbral mínimo para considerar geográfico |

## Uso en pipeline

```python
import pandas as pd
import geodompy as gd

# Datos de ejemplo
datos = pd.read_csv('mis_datos.csv')

# Paso 1: Analizar columnas
analisis = gd.analyze_columns(datos)
print("Columnas geográficas detectadas:")
print(analisis[analisis['is_geographic']])

# Paso 2: Detectar nivel
info = gd.detect_level(datos)
print(f"\nNivel detectado: {info['level']}")

# Paso 3: Detectar fill
geo_cols = analisis[analisis['is_geographic']]['column_name'].tolist()
fill_var = gd.detect_fill(datos, exclude=geo_cols)
print(f"Variable de fill: {fill_var}")

# Paso 4: Crear mapa
gd.map(datos, fill=fill_var)
```

## Limitaciones

!!! warning "Casos ambiguos"
    - Si una columna tiene valores que existen en múltiples niveles, el algoritmo elige el nivel con mayor coincidencia.
    - Nombres muy genéricos pueden causar falsos positivos.
    - Valores con typos no serán detectados (usa `clean_*` primero).

!!! tip "Mejores prácticas"
    1. Limpia tus datos primero con `clean_prov_name()` etc.
    2. Usa `analyze_columns()` para verificar detección
    3. Especifica parámetros manualmente si conoces tus datos

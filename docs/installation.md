# Instalación

## Requisitos

- Python 3.9 o superior
- pip (gestor de paquetes)

## Instalación desde PyPI

La forma más sencilla de instalar geodompy es usando pip:

```bash
pip install geodompy
```

## Instalación desde GitHub (desarrollo)

Para la versión más reciente en desarrollo:

```bash
pip install git+https://github.com/drdsdaniel/geodompy.git
```

## Instalación para desarrollo local

Si deseas contribuir al proyecto o ejecutar las pruebas:

```bash
# Clonar el repositorio
git clone https://github.com/drdsdaniel/geodompy.git
cd geodompy

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# o
venv\Scripts\activate  # Windows

# Instalar en modo editable con dependencias de desarrollo
pip install -e ".[dev]"
```

## Dependencias

geodompy instalará automáticamente las siguientes dependencias:

| Paquete | Propósito |
|---------|-----------|
| `geopandas` | Manipulación de datos geoespaciales |
| `pandas` | Estructuras de datos |
| `pins` | Sistema de caché |
| `pyarrow` | Lectura de archivos parquet |
| `rapidfuzz` | Fuzzy matching para limpieza de nombres |
| `matplotlib` | Visualización de mapas |
| `requests` | Descargas HTTP |

## Verificar instalación

Después de instalar, verifica que todo funciona correctamente:

```python
import geodompy as gd

# Verificar versión
print(f"geodompy versión: {gd.__version__}")

# Probar descarga de datos
provincias = gd.provinces()
print(f"Provincias cargadas: {len(provincias)}")
```

## Ubicación del caché

geodompy usa un directorio de caché para almacenar datos descargados:

- **Windows**: `C:\Users\<usuario>\Documents\.geodom`
- **Linux/Mac**: `~/.geodom`

Esta ubicación es compatible con el paquete R `geodomR`, permitiendo compartir datos entre ambos lenguajes.

## Solución de problemas

### Error de conexión

Si recibes errores de conexión al descargar datos:

1. Verifica tu conexión a internet
2. Intenta nuevamente (el servidor puede estar temporalmente no disponible)
3. El caché local te permitirá trabajar offline una vez descargados los datos

### Error de dependencias

Si tienes problemas con las dependencias geoespaciales:

```bash
# En Ubuntu/Debian
sudo apt-get install libgdal-dev libgeos-dev libproj-dev

# En macOS con Homebrew
brew install gdal geos proj
```

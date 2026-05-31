"""
Funciones para obtener datos geoespaciales de República Dominicana
"""

from typing import Optional, Union
import pandas as pd
import geopandas as gpd

from geodompy.cache import fetch_and_cache, get_dataset


def provinces(
    id: str = "RD_PROV",
    sf: bool = True,
    reg: Optional[str] = None,
    verbose: bool = False
) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Obtener límites de las provincias de República Dominicana.
    
    Parameters
    ----------
    id : str
        Nombre del archivo de datos en el servidor remoto. Por defecto "RD_PROV".
    sf : bool
        Si es True, retorna GeoDataFrame. Si es False, retorna DataFrame sin geometría.
    reg : str, optional
        Si es "rup", agrega columna de región administrativa según Ley 345-22.
    verbose : bool
        Si es True, muestra mensajes de progreso.
    
    Returns
    -------
    GeoDataFrame or DataFrame
        Datos de provincias
    
    Examples
    --------
    >>> import geodompy as gd
    >>> prov = gd.provinces()
    >>> prov.head()
    
    >>> # Con columna de región administrativa
    >>> prov_reg = gd.provinces(reg="rup")
    """
    gdf = fetch_and_cache(id, verbose=verbose)
    
    if reg is not None and reg.lower() == "rup":
        if verbose:
            print("Agregando columna de región administrativa (Ley 345-22)...")
        try:
            datos = get_dataset("division_territorial_rd_ley_345_22", verbose=verbose)
            # Seleccionar columnas relevantes y eliminar duplicados
            reg_data = datos[['PROV_CODE', 'REG_CODE']].drop_duplicates()
            gdf = gdf.merge(reg_data, left_on='PROV', right_on='PROV_CODE', how='left')
        except Exception as e:
            if verbose:
                print(f"No se pudo agregar columna de región: {e}")
    
    if not sf:
        return gdf.drop(columns=['geometry'])
    return gdf


def regions(
    id: str = "RD_RUP",
    sf: bool = True,
    verbose: bool = False
) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Obtener límites de las regiones de planificación de República Dominicana.
    
    Las regionalizaciones disponibles son:
    - "RD_RUP" (por defecto): Regiones Únicas de Planificación según Ley 345-22.
    - "RD_REG71004": Regiones de planificación según el Decreto 710-04.
    
    Parameters
    ----------
    id : str
        Nombre del archivo de datos en el servidor remoto.
    sf : bool
        Si es True, retorna GeoDataFrame.
    verbose : bool
        Si es True, muestra mensajes de progreso.
    
    Returns
    -------
    GeoDataFrame or DataFrame
    """
    gdf = fetch_and_cache(id, verbose=verbose)
    if not sf:
        return gdf.drop(columns=['geometry'])
    return gdf


def municipalities(
    id: str = "RD_MUN158",
    sf: bool = True,
    verbose: bool = False
) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Obtener límites de los municipios de República Dominicana.
    
    Las divisiones disponibles son:
    - "RD_MUN158" (por defecto): 158 Municipios de la República Dominicana.
    - "RD_MUN155": Versión alternativa.
    
    Parameters
    ----------
    id : str
        Nombre del archivo de datos en el servidor remoto.
    sf : bool
        Si es True, retorna GeoDataFrame.
    verbose : bool
        Si es True, muestra mensajes de progreso.
    
    Returns
    -------
    GeoDataFrame or DataFrame
    """
    gdf = fetch_and_cache(id, verbose=verbose)
    if not sf:
        return gdf.drop(columns=['geometry'])
    return gdf


def dm(
    id: str = "RD_DM",
    sf: bool = True,
    verbose: bool = False
) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Obtener límites de los distritos municipales de República Dominicana.
    
    Parameters
    ----------
    id : str
        Nombre del archivo de datos en el servidor remoto.
    sf : bool
        Si es True, retorna GeoDataFrame.
    verbose : bool
        Si es True, muestra mensajes de progreso.
    
    Returns
    -------
    GeoDataFrame or DataFrame
    """
    gdf = fetch_and_cache(id, verbose=verbose)
    if not sf:
        return gdf.drop(columns=['geometry'])
    return gdf


def sections(
    id: str = "RD_SECCIONES",
    sf: bool = True,
    verbose: bool = False
) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Obtener límites de las secciones de República Dominicana.
    
    Parameters
    ----------
    id : str
        Nombre del archivo de datos en el servidor remoto.
    sf : bool
        Si es True, retorna GeoDataFrame.
    verbose : bool
        Si es True, muestra mensajes de progreso.
    
    Returns
    -------
    GeoDataFrame or DataFrame
    """
    gdf = fetch_and_cache(id, verbose=verbose)
    if not sf:
        return gdf.drop(columns=['geometry'])
    return gdf


def zones(
    sf: bool = True,
    verbose: bool = False
) -> pd.DataFrame:
    """
    Obtener datos de zonas de residencia (urbano/rural) de República Dominicana.
    
    Esta función crea un dataset estándar con las zonas de residencia para uso 
    en análisis y estandarización de datos.
    
    Parameters
    ----------
    sf : bool
        Incluido por compatibilidad, pero no aplica para zones (no hay geometría).
    verbose : bool
        Si es True, muestra mensajes de progreso.
    
    Returns
    -------
    DataFrame
        Datos de zonas de residencia.
    """
    # Dataset base con zonas de residencia estándar (igual que R)
    zones_data = pd.DataFrame({
        'ZONE_ID': ['01', '02'],
        'ZONE_CODE': ['URB', 'RUR'],
        'ZONE_NAME': ['Urbana', 'Rural'],
        'TOPONIMIA': ['Urbana', 'Rural']
    })
    return zones_data


def bparajes(
    id: str = "RD_BPARAJES",
    sf: bool = True,
    verbose: bool = False
) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Obtener límites de los barrios y parajes de República Dominicana.
    
    Parameters
    ----------
    id : str
        Nombre del archivo de datos en el servidor remoto.
    sf : bool
        Si es True, retorna GeoDataFrame. Si es False, retorna DataFrame sin geometría.
    verbose : bool
        Si es True, muestra mensajes de progreso.
    
    Returns
    -------
    GeoDataFrame or DataFrame
        Datos de barrios y parajes
    
    Examples
    --------
    >>> import geodompy as gd
    >>> bp = gd.bparajes()
    >>> bp.head()
    """
    gdf = fetch_and_cache(id, verbose=verbose)
    if not sf:
        return gdf.drop(columns=['geometry'])
    return gdf


def macroregions(
    id: str = "RD_MREG",
    sf: bool = True,
    verbose: bool = False
) -> Union[gpd.GeoDataFrame, pd.DataFrame]:
    """
    Obtener límites de las macro-regiones de planificación de República Dominicana.
    
    Descarga (si es necesario) y carga los límites de las tres macro-regiones
    de planificación como un objeto GeoDataFrame.
    
    Parameters
    ----------
    id : str
        Nombre del archivo de datos en el servidor remoto.
    sf : bool
        Si es True, retorna GeoDataFrame. Si es False, retorna DataFrame sin geometría.
    verbose : bool
        Si es True, muestra mensajes de progreso.
    
    Returns
    -------
    GeoDataFrame or DataFrame
        Datos de macro-regiones
    
    Examples
    --------
    >>> import geodompy as gd
    >>> mreg = gd.macroregions()
    >>> mreg.head()
    """
    gdf = fetch_and_cache(id, verbose=verbose)
    if not sf:
        return gdf.drop(columns=['geometry'])
    return gdf


gd_provinces = provinces
gd_regions = regions
gd_municipalities = municipalities
gd_dm = dm
gd_sections = sections
gd_zones = zones
gd_bparajes = bparajes
gd_macroregions = macroregions

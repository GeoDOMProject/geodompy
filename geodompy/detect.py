"""
Funciones de detección automática de nivel geográfico y variable de fill
"""

from typing import Dict, List, Optional, Any, Tuple, Union
import pandas as pd
import numpy as np

from geodompy.data import bparajes, dm, municipalities, provinces, regions, sections, zones


def _get_admin_levels_data() -> Dict[str, pd.DataFrame]:
    """Obtiene datos de referencia de todos los niveles administrativos"""
    levels = {}
    
    try:
        levels["provinces"] = provinces(sf=False)
    except Exception:
        pass
    
    try:
        levels["regions"] = regions(sf=False)
    except Exception:
        pass
    
    try:
        levels["municipalities"] = municipalities(sf=False)
    except Exception:
        pass
    
    try:
        levels["dm"] = dm(sf=False)
    except Exception:
        pass
    
    try:
        levels["sections"] = sections(sf=False)
    except Exception:
        pass
    
    try:
        levels["zones"] = zones(sf=False)
    except Exception:
        pass

    try:
        levels["bparajes"] = bparajes(sf=False)
    except Exception:
        pass
    
    return levels


def detect_level(
    data: pd.DataFrame,
    level: Optional[str] = None,
    name: Optional[str] = None,
    key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Detectar el nivel administrativo de datos geográficos.
    
    Esta función intenta determinar automáticamente el nivel administrativo
    apropiado, el nombre de la variable de enlace, y la variable clave para
    datos relacionados con República Dominicana.
    
    Parameters
    ----------
    data : DataFrame
        Datos a analizar
    level : str, optional
        Nivel administrativo específico a considerar
    name : str, optional
        Nombre de la variable en data con nombres geográficos
    key : str, optional
        Nombre de la variable clave en los datos de referencia
    
    Returns
    -------
    dict
        Diccionario con 'level', 'name', 'key', 'match_count', 'total_count'
    
    Examples
    --------
    >>> import pandas as pd
    >>> import geodompy as gd
    >>> datos = pd.DataFrame({'provincia': ['Santo Domingo', 'Santiago'], 'valor': [1, 2]})
    >>> info = gd.detect_level(datos)
    """
    if level is not None and name is not None and key is not None:
        return {
            'level': level,
            'name': name,
            'key': key,
            'match_count': None,
            'total_count': None
        }
    
    code_levels = {"BP_CODE": "bparajes", "SEC_CODE": "sections", "DM_CODE": "dm", "MUN_CODE": "municipalities", "PROV_CODE": "provinces", "REG_CODE": "regions"}
    for candidate, candidate_level in code_levels.items():
        if candidate in data and (name is None or name == candidate) and (key is None or key == candidate) and (level is None or level == candidate_level):
            return {"level": candidate_level, "name": candidate, "key": candidate, "match_count": None, "total_count": None}
    # Obtener datos de referencia
    admin_data = _get_admin_levels_data()
    
    if level is not None:
        admin_data = {k: v for k, v in admin_data.items() if k == level}
    
    best_match = {
        'level': None,
        'name': None,
        'key': None,
        'match_count': 0,
        'total_count': 0
    }
    
    # Buscar coincidencias
    for level_name, ref_df in admin_data.items():
        for ref_col in ref_df.columns:
            # Saltar columnas numéricas o de ID
            if ref_col.lower() in ['fid', 'objectid', 'objectid_1', 'id', 'geometry']:
                continue
            
            # Convertir a mayúsculas para comparación case-insensitive
            ref_values = set(str(v).upper() for v in ref_df[ref_col].dropna().unique())
            if len(ref_values) == 0:
                continue
            
            for data_col in data.columns:
                # Solo considerar columnas de texto
                if data[data_col].dtype == 'object' or pd.api.types.is_string_dtype(data[data_col]):
                    # Convertir a mayúsculas para comparación
                    unique_values = set(str(v).upper() for v in data[data_col].dropna().unique())
                    
                    if len(unique_values) == 0:
                        continue
                    
                    # Contar coincidencias (case-insensitive)
                    matches = len(unique_values & ref_values)
                    total = len(unique_values)
                    
                    # Si todas coinciden, es match perfecto - retornar inmediatamente
                    if matches == total and matches > 0:
                        return {
                            'level': level_name,
                            'name': data_col,
                            'key': ref_col,
                            'match_count': matches,
                            'total_count': total
                        }
                    
                    # Guardar mejor coincidencia parcial (por ratio, no solo count)
                    current_ratio = matches / total if total > 0 else 0
                    best_ratio = best_match['match_count'] / best_match['total_count'] if best_match['total_count'] > 0 else 0
                    
                    if current_ratio > best_ratio:
                        best_match = {
                            'level': level_name,
                            'name': data_col,
                            'key': ref_col,
                            'match_count': matches,
                            'total_count': total
                        }
    
    return best_match


def detect_fill(
    data: pd.DataFrame,
    exclude: Optional[List[str]] = None
) -> str:
    """
    Detectar automáticamente la mejor variable para fill en un mapa.
    
    Usa varianza normalizada para numéricas y entropía de Shannon para categóricas.
    
    Parameters
    ----------
    data : DataFrame
        Datos a analizar
    exclude : list of str, optional
        Columnas a excluir de la consideración
    
    Returns
    -------
    str
        Nombre de la variable seleccionada
    
    Examples
    --------
    >>> import pandas as pd
    >>> import geodompy as gd
    >>> datos = pd.DataFrame({
    ...     'provincia': ['Santo Domingo', 'Santiago'],
    ...     'poblacion': [2500000, 1000000]
    ... })
    >>> fill_var = gd.detect_fill(datos, exclude=['provincia'])
    """
    exclude = exclude or []
    candidates = [col for col in data.columns if col not in exclude]
    
    if len(candidates) == 0:
        raise ValueError("No hay variables candidatas para fill")
    
    scores = {}
    
    for col in candidates:
        series = data[col]
        
        # Proporción de NA
        na_ratio = series.isna().sum() / len(series)
        if na_ratio > 0.2:
            scores[col] = 0
            continue
        
        clean_series = series.dropna()
        if len(clean_series) == 0 or clean_series.nunique() == 1:
            scores[col] = 0
            continue
        
        if pd.api.types.is_numeric_dtype(clean_series):
            # Coeficiente de variación para numéricas
            mean_val = clean_series.mean()
            if mean_val == 0:
                score = clean_series.std() / abs(clean_series).max() if abs(clean_series).max() > 0 else 0
            else:
                cv = clean_series.std() / abs(mean_val)
                score = 1 - np.exp(-cv)
            # Preferir numéricas
            scores[col] = score * 1.5 * (1 - na_ratio)
        else:
            # Entropía de Shannon para categóricas
            freq = clean_series.value_counts(normalize=True)
            entropy = -np.sum(freq * np.log2(freq + 1e-10))
            max_entropy = np.log2(len(freq))
            if max_entropy > 0:
                normalized_entropy = entropy / max_entropy
            else:
                normalized_entropy = 0
            scores[col] = normalized_entropy * (1 - na_ratio)
    
    if not scores or max(scores.values()) == 0:
        raise ValueError("No se pudo detectar una variable apropiada para fill")
    
    return max(scores, key=scores.get)


def detect_column_type(
    column: Union[pd.Series, List, np.ndarray],
    column_name: str = "columna"
) -> Dict[str, Any]:
    """
    Detectar el tipo de columna geográfica específico.
    
    Esta función analiza una columna específica para determinar
    qué tipo de información geográfica contiene.
    
    Parameters
    ----------
    column : Series, list, or array
        Vector con los valores a analizar
    column_name : str
        Nombre de la columna (opcional, para mensajes informativos)
    
    Returns
    -------
    dict
        Diccionario con información sobre el tipo detectado:
        - level: Nivel administrativo detectado
        - name: Nombre de la columna
        - key: Variable clave en datos de referencia
        - match_count: Número de valores que coincidieron
        - total_count: Total de valores únicos
    
    Examples
    --------
    >>> import geodompy as gd
    >>> provincias = ['Santo Domingo', 'Santiago', 'La Vega']
    >>> resultado = gd.detect_column_type(provincias, 'provincia')
    """
    # Crear DataFrame temporal
    temp_df = pd.DataFrame({column_name: column})
    
    # Usar la función principal de detección
    result = detect_level(temp_df)
    
    return result


def analyze_columns(
    data: pd.DataFrame,
    threshold: float = 0.7
) -> pd.DataFrame:
    """
    Analizar todas las columnas de un DataFrame.
    
    Esta función analiza todas las columnas de un DataFrame para identificar
    cuáles contienen información geográfica y de qué tipo.
    
    Parameters
    ----------
    data : DataFrame
        DataFrame a analizar
    threshold : float
        Umbral mínimo de coincidencias para considerar una detección válida.
        Por defecto es 0.7 (70% de coincidencias).
    
    Returns
    -------
    DataFrame
        Resultados del análisis para cada columna con las columnas:
        - column_name: Nombre de la columna
        - detected_level: Nivel administrativo detectado
        - key_variable: Variable clave en datos de referencia
        - match_count: Número de valores que coincidieron
        - total_count: Total de valores únicos
        - match_ratio: Proporción de coincidencias
        - is_geographic: Si la columna es geográfica según el threshold
    
    Examples
    --------
    >>> import pandas as pd
    >>> import geodompy as gd
    >>> mis_datos = pd.DataFrame({
    ...     'provincia': ['Santo Domingo', 'Santiago'],
    ...     'municipio': ['Santo Domingo Este', 'Santiago'],
    ...     'valor': [100, 200]
    ... })
    >>> resultados = gd.analyze_columns(mis_datos)
    """
    results = []
    
    for col_name in data.columns:
        col = data[col_name]
        
        # Solo analizar columnas de tipo texto
        if col.dtype == 'object' or pd.api.types.is_string_dtype(col):
            result = detect_column_type(col.tolist(), col_name)
            
            match_count = result.get('match_count', 0) or 0
            total_count = result.get('total_count', 0) or 0
            
            if total_count > 0:
                match_ratio = match_count / total_count
            else:
                match_ratio = 0.0
            
            is_geographic = result.get('level') is not None and match_ratio >= threshold
            
            results.append({
                'column_name': col_name,
                'detected_level': result.get('level'),
                'key_variable': result.get('key'),
                'match_count': match_count,
                'total_count': total_count,
                'match_ratio': match_ratio,
                'is_geographic': is_geographic
            })
    
    return pd.DataFrame(results)


gd_detect_level = detect_level
gd_detect_fill = detect_fill
gd_detect_column_type = detect_column_type
gd_analyze_columns = analyze_columns

"""
Sistema de cache usando pins para interoperabilidad con geodomR.
"""

import os
from io import BytesIO
import warnings
from pathlib import Path
from typing import Optional

import geopandas as gpd
import pandas as pd
import pins
import requests

from geodompy._constants import BASE_DATA_URL, CACHE_DIR_NAME
from geodompy._codes import add_codes, restore_crs


def _get_cache_dir() -> Path:
    """
    Obtiene el directorio de cache compatible con R pins.

    Los pines Python se aíslan de los pines R, cuyos formatos no son intercambiables.
    GEODOM_CACHE_DIR permite elegir la raíz sin modificar la caché anterior.
    """
    if os.name == "nt":
        documents = Path(os.environ.get("USERPROFILE", Path.home())) / "Documents"
    else:
        documents = Path.home()

    cache_root = Path(os.environ.get("GEODOM_CACHE_DIR", documents / f".{CACHE_DIR_NAME}"))
    cache_dir = cache_root / "python-v1"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir


def _get_board() -> pins.board:
    """Obtiene el board de pins para cache."""
    return pins.board_folder(str(_get_cache_dir()))


def _pin_exists(pin_name: str, board: pins.board) -> bool:
    """Verifica si un pin existe en el board."""
    try:
        return pin_name in board.pin_list()
    except Exception:
        return False


def _pin_read(board: pins.board, pin_name: str):
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message="Missing constructor for R class")
        return board.pin_read(pin_name)


def _coerce_r_geometry(value):
    try:
        from shapely.geometry import MultiPolygon, Polygon
        from shapely.geometry.base import BaseGeometry
    except Exception:
        return value

    if isinstance(value, BaseGeometry):
        return value

    def ring_to_coords(ring):
        try:
            return [(float(x), float(y)) for x, y in ring]
        except Exception:
            return []

    def polygon_from_rings(rings):
        coords = [ring_to_coords(ring) for ring in rings]
        coords = [ring for ring in coords if len(ring) >= 4]
        if not coords:
            return None
        return Polygon(coords[0], holes=coords[1:] or None)

    if isinstance(value, list):
        polygons = []
        for polygon in value:
            if isinstance(polygon, list):
                converted = polygon_from_rings(polygon)
            else:
                converted = polygon_from_rings([polygon])
            if converted is not None:
                polygons.append(converted)

        if len(polygons) == 1:
            return polygons[0]
        if len(polygons) > 1:
            return MultiPolygon(polygons)
        return None

    return value


def _check_remote_file_changed(
    url: str,
    pin_name: str,
    board: pins.board,
    verbose: bool = False,
) -> bool:
    """
    Verifica si el archivo remoto cambio comparando ETag o Last-Modified.

    Si la red no esta disponible y existe cache local, se usa el cache.
    """
    if not _pin_exists(pin_name, board):
        return True

    try:
        local_meta = board.pin_meta(pin_name)
        local_user = getattr(local_meta, "user", None) or {}
        local_etag = local_user.get("etag")
        local_last_modified = local_user.get("last_modified")
    except Exception:
        local_etag = None
        local_last_modified = None

    try:
        resp = requests.head(url, timeout=10)
        remote_etag = resp.headers.get("etag")
        remote_last_modified = resp.headers.get("last-modified")
    except requests.RequestException:
        if verbose:
            print(f"No se pudo verificar '{pin_name}' remotamente; usando cache local.")
        return False

    if local_etag and remote_etag:
        return local_etag != remote_etag

    if local_last_modified and remote_last_modified:
        return local_last_modified != remote_last_modified

    return False


def _read_cached_geodataframe(data_id: str, board: pins.board) -> Optional[gpd.GeoDataFrame]:
    """Lee un GeoDataFrame del cache, restaurando geometria si es necesario."""
    try:
        cached_data = _pin_read(board, data_id)
    except Exception:
        return None

    if isinstance(cached_data, gpd.GeoDataFrame):
        return cached_data

    if isinstance(cached_data, pd.DataFrame):
        if "geometry" in cached_data.columns:
            cached_data = cached_data.copy()
            geom_col = cached_data["geometry"]
            if len(geom_col) > 0 and isinstance(geom_col.iloc[0], bytes):
                from shapely import wkb

                cached_data["geometry"] = geom_col.apply(
                    lambda x: wkb.loads(x) if isinstance(x, bytes) else x
                )
            else:
                cached_data["geometry"] = geom_col.apply(_coerce_r_geometry)
            return gpd.GeoDataFrame(cached_data, geometry="geometry")
        return gpd.GeoDataFrame(cached_data)

    return None


def _dataset_to_dataframe(data) -> pd.DataFrame:
    if isinstance(data, pd.DataFrame):
        return data
    if isinstance(data, dict) and "data" in data:
        return pd.DataFrame(data["data"])
    if isinstance(data, list):
        return pd.DataFrame(data)
    return pd.DataFrame([data])


def fetch_and_cache(
    data_id: str,
    data_type: str = "TopoJSON",
    force_download: bool = False,
    verbose: bool = False,
) -> gpd.GeoDataFrame:
    """
    Descarga y cachea datos geoespaciales.
    """
    board = _get_board()

    if data_type == "TopoJSON":
        url = f"{BASE_DATA_URL}TopoJSON/{data_id}.json"
    else:
        url = f"{BASE_DATA_URL}datasets/{data_id}.json"

    if not force_download and _pin_exists(data_id, board):
        if not _check_remote_file_changed(url, data_id, board, verbose):
            if verbose:
                print(f"Cargando '{data_id}' desde cache local.")
            gdf = _read_cached_geodataframe(data_id, board)
            if gdf is not None:
                return add_codes(restore_crs(gdf, data_id))
        elif verbose:
            print(f"Pin '{data_id}' encontrado, pero el remoto cambio. Actualizando.")

    if verbose and not _pin_exists(data_id, board):
        print(f"Pin '{data_id}' no encontrado localmente. Descargando.")

    remote_meta = {"etag": None, "last_modified": None}
    try:
        resp = requests.head(url, timeout=10)
        remote_meta["etag"] = resp.headers.get("etag")
        remote_meta["last_modified"] = resp.headers.get("last-modified")
    except requests.RequestException:
        pass

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        gdf = gpd.read_file(BytesIO(response.content))
    except Exception as e:
        if _pin_exists(data_id, board):
            if verbose:
                print(f"Fallo al descargar datos remotos. Usando cache local: {e}")
            gdf = _read_cached_geodataframe(data_id, board)
            if gdf is not None:
                return add_codes(restore_crs(gdf, data_id))
        raise RuntimeError(f"Error descargando '{data_id}': {e}") from e

    try:
        board.pin_write(gdf, name=data_id, type="parquet", metadata=remote_meta)
        if verbose:
            print(f"Pin '{data_id}' guardado en cache.")
    except Exception as cache_error:
        if verbose:
            print(f"Aviso: No se pudo guardar en cache: {cache_error}")

    return add_codes(restore_crs(gdf, data_id))


def get_dataset(
    data_id: str,
    force_download: bool = False,
    verbose: bool = False,
) -> pd.DataFrame:
    """Obtiene un dataset JSON no geoespacial."""
    board = _get_board()
    url = f"{BASE_DATA_URL}datasets/{data_id}.json"

    if not force_download and _pin_exists(data_id, board):
        if not _check_remote_file_changed(url, data_id, board, verbose):
            if verbose:
                print(f"Cargando '{data_id}' desde cache.")
            try:
                return _dataset_to_dataframe(_pin_read(board, data_id))
            except Exception:
                pass

    if verbose:
        print(f"Descargando dataset '{data_id}'.")

    remote_meta = {"etag": None, "last_modified": None}
    try:
        resp = requests.head(url, timeout=10)
        remote_meta["etag"] = resp.headers.get("etag")
        remote_meta["last_modified"] = resp.headers.get("last-modified")
    except requests.RequestException:
        pass

    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except requests.RequestException as e:
        if _pin_exists(data_id, board):
            if verbose:
                print(f"Fallo al descargar '{data_id}'. Usando cache local: {e}")
            try:
                return _dataset_to_dataframe(_pin_read(board, data_id))
            except Exception as cache_error:
                raise RuntimeError(
                    f"Error descargando '{data_id}' y leyendo cache local: {cache_error}"
                ) from e
        raise

    df = _dataset_to_dataframe(data)

    try:
        board.pin_write(df, name=data_id, type="parquet", metadata=remote_meta)
    except Exception:
        pass

    return df


gd_get_dataset = get_dataset

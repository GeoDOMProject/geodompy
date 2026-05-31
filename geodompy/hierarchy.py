"""
Funciones para enriquecer datos con columnas de jerarquia administrativa.
"""

from __future__ import annotations

import warnings
from typing import Optional, Sequence

import pandas as pd

from geodompy.clean import (
    clean_bparaje_name,
    clean_dm_name,
    clean_municipality_name,
    clean_prov_name,
    clean_region_name,
    clean_section_name,
)
from geodompy.data import bparajes, dm, municipalities, provinces, regions, sections
from geodompy.detect import detect_level

ADMIN_HIERARCHY = ["regions", "provinces", "municipalities", "dm", "sections", "bparajes"]
LEVEL_COL_NAMES = {
    "regions": "Region",
    "provinces": "Provincia",
    "municipalities": "Municipio",
    "dm": "Distrito_Municipal",
    "sections": "Seccion",
    "bparajes": "Barrio_Paraje",
}

_CODE_WIDTHS = {"PROV": 2, "MUN": 2, "DM": 2, "SEC": 2, "SECC": 2, "BP": 3}


def _code_series(df: pd.DataFrame, column: str) -> pd.Series:
    values = df[column].astype(str).str.strip().str.replace(r"\.0$", "", regex=True)
    width = _CODE_WIDTHS.get(column)
    if width:
        values = values.str.zfill(width)
    return values


def _key(df: pd.DataFrame, columns: Sequence[str]) -> pd.Series:
    parts = [_code_series(df, column) for column in columns]
    result = parts[0]
    for part in parts[1:]:
        result = result + part
    return result


def _sec_col(df: pd.DataFrame) -> Optional[str]:
    if "SEC" in df.columns:
        return "SEC"
    if "SECC" in df.columns:
        return "SECC"
    return None


def _get_clean_fn(level: str):
    clean_fns = {
        "regions": clean_region_name,
        "provinces": clean_prov_name,
        "municipalities": clean_municipality_name,
        "dm": clean_dm_name,
        "sections": clean_section_name,
        "bparajes": clean_bparaje_name,
    }
    try:
        return clean_fns[level]
    except KeyError as e:
        raise ValueError(f"Nivel no reconocido: {level}") from e


def _get_data_fn(level: str):
    data_fns = {
        "regions": regions,
        "provinces": provinces,
        "municipalities": municipalities,
        "dm": dm,
        "sections": sections,
        "bparajes": bparajes,
    }
    try:
        return data_fns[level]
    except KeyError as e:
        raise ValueError(f"Nivel no reconocido: {level}") from e


def _series_map(
    source_df: pd.DataFrame,
    key_series: pd.Series,
    value_series: Sequence[object],
) -> dict[str, object]:
    return dict(zip(key_series.astype(str), value_series))


def _build_parent_lookup(current_level: str, parent_levels: Sequence[str]) -> pd.DataFrame:
    current_df = _get_data_fn(current_level)(sf=False)
    current_clean_fn = _get_clean_fn(current_level)
    lookup = pd.DataFrame(
        {
            "current_name": current_clean_fn(
                current_df["TOPONIMIA"].tolist(),
                on_error="na",
            )
        }
    )

    if "regions" in parent_levels and "REG" in current_df.columns:
        reg_df = regions(sf=False)
        reg_map = _series_map(
            reg_df,
            _code_series(reg_df, "CODREG"),
            clean_region_name(reg_df["TOPONIMIA"].tolist(), on_error="na"),
        )
        lookup["Region"] = _code_series(current_df, "REG").map(reg_map)

    if "provinces" in parent_levels and "PROV" in current_df.columns:
        prov_df = provinces(sf=False)
        prov_map = _series_map(
            prov_df,
            _code_series(prov_df, "PROV"),
            clean_prov_name(prov_df["TOPONIMIA"].tolist(), on_error="na"),
        )
        lookup["Provincia"] = _code_series(current_df, "PROV").map(prov_map)

    if {"municipalities"}.intersection(parent_levels) and {"PROV", "MUN"}.issubset(current_df.columns):
        mun_df = municipalities(sf=False)
        mun_map = _series_map(
            mun_df,
            _key(mun_df, ["PROV", "MUN"]),
            clean_municipality_name(mun_df["TOPONIMIA"].tolist(), on_error="na"),
        )
        lookup["Municipio"] = _key(current_df, ["PROV", "MUN"]).map(mun_map)

    if "dm" in parent_levels and {"PROV", "MUN", "DM"}.issubset(current_df.columns):
        dm_df = dm(sf=False)
        dm_map = _series_map(
            dm_df,
            _key(dm_df, ["PROV", "MUN", "DM"]),
            clean_dm_name(dm_df["TOPONIMIA"].tolist(), on_error="na"),
        )
        lookup["Distrito_Municipal"] = _key(current_df, ["PROV", "MUN", "DM"]).map(dm_map)

    if "sections" in parent_levels:
        current_sec_col = _sec_col(current_df)
        if current_sec_col and {"PROV", "MUN", "DM"}.issubset(current_df.columns):
            sec_df = sections(sf=False)
            sec_col = _sec_col(sec_df)
            if sec_col:
                sec_map = _series_map(
                    sec_df,
                    _key(sec_df, ["PROV", "MUN", "DM", sec_col]),
                    clean_section_name(sec_df["TOPONIMIA"].tolist(), on_error="na"),
                )
                lookup["Seccion"] = _key(
                    current_df,
                    ["PROV", "MUN", "DM", current_sec_col],
                ).map(sec_map)

    return lookup.drop_duplicates()


def add_parent_cols(
    data: pd.DataFrame,
    levels: Optional[Sequence[str]] = None,
    level: Optional[str] = None,
    name: Optional[str] = None,
    key: Optional[str] = None,
    clean: bool = True,
    tolerance: float = 0.25,
    on_error: str = "na",
) -> pd.DataFrame:
    """
    Agrega columnas de niveles superiores a un DataFrame.
    """
    info = detect_level(data, level=level, name=name, key=key)
    if info.get("level") is None:
        raise ValueError(
            "No se pudo detectar el nivel administrativo de los datos. "
            "Especifique level, name y key manualmente."
        )

    current_level = info["level"]
    current_col = info["name"]
    if current_level not in ADMIN_HIERARCHY:
        raise ValueError(f"Nivel '{current_level}' no es parte de la jerarquia estandar.")

    current_idx = ADMIN_HIERARCHY.index(current_level)
    if current_idx == 0:
        return data.copy()

    available_parents = ADMIN_HIERARCHY[:current_idx]
    if levels is None:
        parent_levels = available_parents
    else:
        requested_levels = [levels] if isinstance(levels, str) else list(levels)
        parent_levels = [level_name for level_name in requested_levels if level_name in available_parents]
        invalid = sorted(set(requested_levels) - set(parent_levels))
        if invalid:
            warnings.warn(
                f"Los niveles {invalid} no son superiores a '{current_level}' y se ignoraron.",
                stacklevel=2,
            )

    if not parent_levels:
        return data.copy()

    result = data.copy()
    if clean:
        clean_fn = _get_clean_fn(current_level)
        result[current_col] = clean_fn(
            result[current_col].tolist(),
            tolerance=tolerance,
            on_error=on_error,
        )

    lookup = _build_parent_lookup(current_level, parent_levels)
    return result.merge(lookup, left_on=current_col, right_on="current_name", how="left").drop(
        columns=["current_name"]
    )


gd_add_parent_cols = add_parent_cols

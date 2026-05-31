"""
Funciones para limpieza y estandarizacion de nombres geograficos.
"""

from __future__ import annotations

import re
import unicodedata
from typing import Iterable, Optional, Sequence, Union

import pandas as pd
from rapidfuzz.distance import JaroWinkler

from geodompy.cache import get_dataset
from geodompy.data import bparajes, dm, municipalities, provinces, regions, sections, zones

NameInput = Union[str, Sequence[object], pd.Series]

_CODE_WIDTHS = {
    "PROV": 2,
    "REG": 2,
    "CODREG": 2,
    "MUN": 2,
    "DM": 2,
    "SEC": 2,
    "SECC": 2,
    "BP": 3,
}

_NON_GEOGRAPHIC_NAMES = {
    "otros",
    "otras",
    "other",
    "others",
    "resto",
    "demas",
    "demas provincias",
    "no especificado",
    "sin especificar",
    "no aplica",
    "nacional",
    "total",
}


def _is_missing(value: object) -> bool:
    try:
        result = pd.isna(value)
    except Exception:
        return False
    if isinstance(result, bool):
        return result
    if result is pd.NA:
        return True
    return False


def _as_list(names: NameInput) -> tuple[list[object], bool]:
    if isinstance(names, str) or names is None or _is_missing(names):
        return [names], True
    if isinstance(names, pd.Series):
        return names.tolist(), False
    if isinstance(names, Iterable):
        return list(names), False
    return [names], True


def _restore_shape(values: list[Optional[str]], scalar: bool):
    return values[0] if scalar else values


def _text_cleaning(names: NameInput):
    """
    Limpieza y normalizacion de texto compatible con geodomR.
    """
    values, scalar = _as_list(names)
    cleaned = [_clean_single_name(value) for value in values]
    return _restore_shape(cleaned, scalar)


def _clean_single_name(name: object) -> str:
    if _is_missing(name):
        return "_na_"

    text = str(name).lower().strip()
    text = " ".join(text.split())
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")

    prefixes = [
        r"^region[ ]?",
        r"^provincia[ ]?de[ ]?",
        r"^provincia[ ]?",
        r"^municipio[ ]?",
        r"^ayuntamiento[ ]?de[ ]?",
        r" \(d\.?[ ]?m\.?\)",
        r" [(]?zona urbana[)]?",
        r"^el[ ]",
        r"^la[s]?[ ]?",
        r"^los[ ]?",
        r"^de[l]?[ ]?",
    ]
    for prefix in prefixes:
        text = re.sub(prefix, "", text, flags=re.IGNORECASE)

    text = re.sub(r"\bde\b", "", text, flags=re.IGNORECASE)
    text = " ".join(text.split())
    if text != "_na_":
        text = re.sub(r"[^0-9a-z ]", "", text, flags=re.IGNORECASE)
    return " ".join(text.split())


def _validate_clean_params(tolerance: float, on_error: str) -> None:
    if not isinstance(tolerance, (int, float)) or tolerance < 0 or tolerance > 1:
        raise ValueError("tolerance debe ser un numero entre 0 y 1")
    if on_error not in {"fail", "na", "omit"}:
        raise ValueError("on_error debe ser uno de: 'fail', 'na', 'omit'")


def _as_dataframe(raw: object) -> Optional[pd.DataFrame]:
    if raw is None:
        return None
    if isinstance(raw, pd.DataFrame):
        return raw.copy()
    if isinstance(raw, dict) and "data" in raw:
        return pd.DataFrame(raw["data"])
    if isinstance(raw, list):
        return pd.DataFrame(raw)
    return None


def _get_alias_dataset(alias_id: str, verbose: bool = False) -> Optional[pd.DataFrame]:
    try:
        return _as_dataframe(get_dataset(alias_id, verbose=verbose))
    except Exception:
        return None


def _code_value(value: object, column: str) -> str:
    if _is_missing(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0"):
        text = text[:-2]
    width = _CODE_WIDTHS.get(column)
    return text.zfill(width) if width and text.isdigit() else text


def _compose_id(row: pd.Series, columns: Sequence[str]) -> str:
    return "".join(_code_value(row[col], col) for col in columns)


def _first_existing(columns: Sequence[str], choices: Sequence[str]) -> Optional[str]:
    for choice in choices:
        if choice in columns:
            return choice
    return None


def _fallback_alias_data(
    fallback_data: Optional[pd.DataFrame],
    id_col: str,
    name_col: str,
    official_col: str,
    id_parts: Sequence[str],
) -> pd.DataFrame:
    if fallback_data is None or fallback_data.empty:
        return pd.DataFrame(columns=[id_col, name_col])

    source = fallback_data.copy()
    available_parts = []
    for part in id_parts:
        if part in {"SEC", "SECC"}:
            sec_col = _first_existing(source.columns, ["SEC", "SECC"])
            if sec_col:
                available_parts.append(sec_col)
        elif part in source.columns:
            available_parts.append(part)

    if available_parts:
        ids = source.apply(lambda row: _compose_id(row, available_parts), axis=1)
    elif id_col in source.columns:
        ids = source[id_col].astype(str)
    else:
        ids = source.index.astype(str)

    if official_col in source.columns:
        names = source[official_col]
    elif name_col in source.columns:
        names = source[name_col]
    else:
        names = source.iloc[:, 0]

    return pd.DataFrame({id_col: ids, name_col: names}).dropna(subset=[name_col])


def _load_alias_data(
    alias_id: str,
    id_col: str,
    name_col: str,
    fallback_data: Optional[pd.DataFrame] = None,
    official_col: str = "TOPONIMIA",
    id_parts: Sequence[str] = (),
) -> pd.DataFrame:
    alias_data = _get_alias_dataset(alias_id)
    if alias_data is not None and {id_col, name_col}.issubset(alias_data.columns):
        return alias_data[[id_col, name_col]].copy()
    return _fallback_alias_data(fallback_data, id_col, name_col, official_col, id_parts)


def _handle_no_match(
    current_name: object,
    level_label: str,
    on_error: str,
    msg: Optional[str] = None,
    hint: Optional[str] = None,
) -> Optional[str]:
    if on_error == "na":
        return None
    if on_error == "omit":
        return current_name
    detail = msg or f"{level_label} name '{current_name}' not matched"
    if hint:
        detail = f"{detail}. {hint}"
    raise ValueError(detail)


def _handle_ambiguous(
    current_name: object,
    officials: Sequence[str],
    level_label: str,
    parent_hint: Optional[str],
    on_error: str,
) -> Optional[str]:
    if on_error == "na":
        return None
    if on_error == "omit":
        return current_name
    sample = "', '".join(list(officials)[:3])
    detail = f"{level_label} '{current_name}' is ambiguous: {len(officials)} matches found"
    if sample:
        detail += f". Matches include: '{sample}'"
    if parent_hint:
        detail += f". {parent_hint}"
    raise ValueError(detail)


def _resolve_parent_ids(
    parent_name: Optional[str],
    alias_data: pd.DataFrame,
    id_col: str,
    name_col: str,
) -> Optional[list[str]]:
    if parent_name is None or alias_data is None or alias_data.empty:
        return None

    parent_clean = _clean_single_name(parent_name)
    lookup = alias_data[[id_col, name_col]].dropna().copy()
    lookup["_CLEAN"] = lookup[name_col].map(_clean_single_name)

    exact = lookup[lookup["_CLEAN"] == parent_clean]
    if not exact.empty:
        return exact[id_col].astype(str).drop_duplicates().tolist()

    lookup["_DIST"] = lookup["_CLEAN"].map(
        lambda value: JaroWinkler.normalized_distance(parent_clean, value)
    )
    fuzzy = lookup[lookup["_DIST"] <= 0.25].sort_values("_DIST")
    if not fuzzy.empty:
        return fuzzy[id_col].astype(str).drop_duplicates().tolist()
    return None


def _generic_clean_names(
    names: NameInput,
    alias_data: pd.DataFrame,
    id_col: str,
    name_col: str,
    level_label: str,
    prefix_regex: Optional[str] = None,
    code_regex: Optional[str] = None,
    parent_filter_ids: Optional[Sequence[str]] = None,
    parent_prefix_len: Optional[int] = None,
    parent_hint: Optional[str] = None,
    tolerance: float = 0.25,
    on_error: str = "fail",
):
    _validate_clean_params(tolerance, on_error)
    values, scalar = _as_list(names)
    if not values:
        return _restore_shape([], scalar)

    alias_data = alias_data[[id_col, name_col]].dropna(subset=[id_col, name_col]).copy()
    alias_data[id_col] = alias_data[id_col].astype(str)

    official_names = alias_data.drop_duplicates(subset=[id_col], keep="first").copy()
    official_col = "_OFFICIAL"
    official_names[official_col] = official_names[name_col]

    alias_lookup = alias_data.merge(
        official_names[[id_col, official_col]],
        on=id_col,
        how="left",
    )
    alias_lookup["_CLEAN"] = alias_lookup[name_col].map(_clean_single_name)
    alias_lookup["_RAW_LOWER"] = alias_lookup[name_col].astype(str).str.lower()
    alias_lookup["_ID"] = alias_lookup[id_col].astype(str)
    alias_lookup = alias_lookup[["_ID", "_CLEAN", "_RAW_LOWER", official_col]].drop_duplicates()

    if parent_filter_ids and parent_prefix_len:
        parent_filter_ids = [str(value) for value in parent_filter_ids]
        alias_lookup = alias_lookup[
            alias_lookup["_ID"].str[:parent_prefix_len].isin(parent_filter_ids)
        ]
        official_names = official_names[
            official_names[id_col].str[:parent_prefix_len].isin(parent_filter_ids)
        ]

    results: list[Optional[str]] = []

    for current_name in values:
        if _is_missing(current_name):
            results.append(None)
            continue

        current_raw = str(current_name)
        current_clean = _clean_single_name(current_raw)

        if current_clean in {"", "_na_"}:
            results.append(
                _handle_no_match(
                    current_name,
                    level_label,
                    on_error,
                    msg=f"{level_label} name is empty",
                )
            )
            continue

        if current_clean in _NON_GEOGRAPHIC_NAMES:
            results.append(
                _handle_no_match(
                    current_name,
                    level_label,
                    on_error,
                    msg=f"{level_label} name '{current_name}' is an aggregate or non-geographic label",
                )
            )
            continue

        if code_regex and re.fullmatch(code_regex, current_raw.strip()):
            code_match = official_names[official_names[id_col] == current_raw.strip()]
            if not code_match.empty:
                results.append(code_match[official_col].iloc[0])
                continue
            results.append(
                _handle_no_match(
                    current_name,
                    level_label,
                    on_error,
                    msg=f"{level_label} code '{current_name}' not found",
                )
            )
            continue

        exact_matches = alias_lookup[alias_lookup["_CLEAN"] == current_clean]
        if not exact_matches.empty:
            officials = exact_matches[official_col].dropna().drop_duplicates().tolist()
            if len(officials) == 1:
                results.append(officials[0])
                continue

            raw_exact = exact_matches[exact_matches["_RAW_LOWER"] == current_raw.lower()]
            raw_officials = raw_exact[official_col].dropna().drop_duplicates().tolist()
            if len(raw_officials) == 1:
                results.append(raw_officials[0])
                continue

            results.append(
                _handle_ambiguous(current_name, officials, level_label, parent_hint, on_error)
            )
            continue

        current_no_prefix = current_clean
        if prefix_regex:
            current_no_prefix = re.sub(prefix_regex, "", current_clean, flags=re.IGNORECASE)

        if current_no_prefix != current_clean:
            prefix_exact = alias_lookup[alias_lookup["_CLEAN"] == current_no_prefix]
            if not prefix_exact.empty:
                officials = prefix_exact[official_col].dropna().drop_duplicates().tolist()
                if len(officials) == 1:
                    results.append(officials[0])
                    continue
                results.append(
                    _handle_ambiguous(current_name, officials, level_label, parent_hint, on_error)
                )
                continue

        prefix_matches = alias_lookup[alias_lookup["_CLEAN"].str.startswith(current_no_prefix)]
        if not prefix_matches.empty:
            prefix_matches = prefix_matches.assign(_LEN=prefix_matches["_CLEAN"].str.len())
            prefix_matches = prefix_matches.sort_values("_LEN")
            officials = prefix_matches[official_col].dropna().drop_duplicates().tolist()
            results.append(officials[0] if officials else None)
            continue

        reverse_matches = alias_lookup[
            alias_lookup["_CLEAN"].map(lambda value: current_no_prefix.startswith(value))
        ]
        if not reverse_matches.empty:
            reverse_matches = reverse_matches.assign(_LEN=reverse_matches["_CLEAN"].str.len())
            reverse_matches = reverse_matches.sort_values("_LEN", ascending=False)
            officials = reverse_matches[official_col].dropna().drop_duplicates().tolist()
            results.append(officials[0] if officials else None)
            continue

        fuzzy_pool = alias_lookup[alias_lookup["_CLEAN"] != "_na_"].copy()
        if not fuzzy_pool.empty:
            fuzzy_pool["_DIST"] = fuzzy_pool["_CLEAN"].map(
                lambda value: JaroWinkler.normalized_distance(current_no_prefix, value)
            )
            fuzzy_pool["_LEN"] = fuzzy_pool["_CLEAN"].str.len()
            best = fuzzy_pool.sort_values(["_DIST", "_LEN"]).iloc[0]
            if best["_DIST"] <= tolerance:
                results.append(best[official_col])
                continue
            results.append(
                _handle_no_match(
                    current_name,
                    level_label,
                    on_error,
                    msg=f"{level_label} name '{current_name}' could not be matched with tolerance {tolerance}",
                    hint=f"Best match was '{best[official_col]}' with distance {best['_DIST']:.3f}",
                )
            )
        else:
            results.append(
                _handle_no_match(
                    current_name,
                    level_label,
                    on_error,
                    msg=f"{level_label} name '{current_name}' could not be matched",
                )
            )

    return _restore_shape(results, scalar)


def _reference_data(fetcher) -> Optional[pd.DataFrame]:
    try:
        return fetcher(sf=False)
    except Exception:
        return None


def _province_alias_data() -> pd.DataFrame:
    return _load_alias_data(
        "provincias_alias",
        "PROV_ID",
        "PROV_NAME",
        _reference_data(provinces),
        id_parts=("PROV",),
    )


def _region_alias_data() -> pd.DataFrame:
    return _load_alias_data(
        "regiones_alias",
        "REG_ID",
        "REG_NAME",
        _reference_data(regions),
        id_parts=("CODREG",),
    )


def _municipality_alias_data() -> pd.DataFrame:
    return _load_alias_data(
        "municipios_alias",
        "MUN_ID",
        "MUN_NAME",
        _reference_data(municipalities),
        id_parts=("PROV", "MUN"),
    )


def _dm_alias_data() -> pd.DataFrame:
    return _load_alias_data(
        "dm_alias",
        "DM_ID",
        "DM_NAME",
        _reference_data(dm),
        id_parts=("PROV", "MUN", "DM"),
    )


def _section_alias_data() -> pd.DataFrame:
    return _load_alias_data(
        "sections_alias",
        "SEC_ID",
        "SEC_NAME",
        _reference_data(sections),
        id_parts=("PROV", "MUN", "DM", "SEC"),
    )


def _bparaje_alias_data() -> pd.DataFrame:
    return _load_alias_data(
        "bparajes_alias",
        "BP_ID",
        "BP_NAME",
        _reference_data(bparajes),
        id_parts=("PROV", "MUN", "DM", "SEC", "BP"),
    )


def _zone_alias_data() -> pd.DataFrame:
    return _load_alias_data(
        "zones_alias",
        "ZONE_ID",
        "ZONE_NAME",
        zones(),
        id_parts=("ZONE_ID",),
    )


def clean_prov_name(
    names: NameInput,
    tolerance: float = 0.25,
    on_error: str = "fail",
):
    """Limpiar y estandarizar nombres de provincias."""
    return _generic_clean_names(
        names,
        _province_alias_data(),
        id_col="PROV_ID",
        name_col="PROV_NAME",
        level_label="Province",
        prefix_regex=r"^(provincia|prov)\.?\s+",
        code_regex=r"^\d{2}$",
        tolerance=tolerance,
        on_error=on_error,
    )


def clean_region_name(
    names: NameInput,
    tolerance: float = 0.25,
    on_error: str = "fail",
):
    """Limpiar y estandarizar nombres de regiones."""
    return _generic_clean_names(
        names,
        _region_alias_data(),
        id_col="REG_ID",
        name_col="REG_NAME",
        level_label="Region",
        prefix_regex=r"^(region|reg)\.?\s+",
        code_regex=r"^\d{2}$",
        tolerance=tolerance,
        on_error=on_error,
    )


def clean_municipality_name(
    names: NameInput,
    province: Optional[str] = None,
    tolerance: float = 0.25,
    on_error: str = "fail",
):
    """Limpiar y estandarizar nombres de municipios."""
    parent_filter_ids = None
    parent_prefix_len = None
    if province is not None:
        parent_filter_ids = _resolve_parent_ids(province, _province_alias_data(), "PROV_ID", "PROV_NAME")
        if parent_filter_ids:
            parent_prefix_len = 2

    return _generic_clean_names(
        names,
        _municipality_alias_data(),
        id_col="MUN_ID",
        name_col="MUN_NAME",
        level_label="Municipality",
        prefix_regex=r"^(municipio|mun)\.?\s+",
        code_regex=r"^\d{4}$",
        parent_filter_ids=parent_filter_ids,
        parent_prefix_len=parent_prefix_len,
        parent_hint="Use province to disambiguate",
        tolerance=tolerance,
        on_error=on_error,
    )


def clean_dm_name(
    names: NameInput,
    municipality: Optional[str] = None,
    tolerance: float = 0.25,
    on_error: str = "fail",
):
    """Limpiar y estandarizar nombres de distritos municipales."""
    parent_filter_ids = None
    parent_prefix_len = None
    if municipality is not None:
        parent_filter_ids = _resolve_parent_ids(
            municipality,
            _municipality_alias_data(),
            "MUN_ID",
            "MUN_NAME",
        )
        if parent_filter_ids:
            parent_prefix_len = 4

    return _generic_clean_names(
        names,
        _dm_alias_data(),
        id_col="DM_ID",
        name_col="DM_NAME",
        level_label="DM",
        prefix_regex=r"^(distrito\s+municipal|dist\.?\s*mun\.?|d\.?\s*m\.?)\s+",
        code_regex=r"^\d{6}$",
        parent_filter_ids=parent_filter_ids,
        parent_prefix_len=parent_prefix_len,
        parent_hint="Use municipality to disambiguate",
        tolerance=tolerance,
        on_error=on_error,
    )


def clean_section_name(
    names: NameInput,
    dm: Optional[str] = None,
    municipality: Optional[str] = None,
    tolerance: float = 0.25,
    on_error: str = "fail",
):
    """Limpiar y estandarizar nombres de secciones."""
    parent_filter_ids = None
    parent_prefix_len = None
    if dm is not None:
        parent_filter_ids = _resolve_parent_ids(dm, _dm_alias_data(), "DM_ID", "DM_NAME")
        if parent_filter_ids:
            parent_prefix_len = 6
    elif municipality is not None:
        parent_filter_ids = _resolve_parent_ids(
            municipality,
            _municipality_alias_data(),
            "MUN_ID",
            "MUN_NAME",
        )
        if parent_filter_ids:
            parent_prefix_len = 4

    return _generic_clean_names(
        names,
        _section_alias_data(),
        id_col="SEC_ID",
        name_col="SEC_NAME",
        level_label="Section",
        prefix_regex=r"^(seccion|secc?\.?)\s+",
        code_regex=r"^\d{8}$",
        parent_filter_ids=parent_filter_ids,
        parent_prefix_len=parent_prefix_len,
        parent_hint="Use dm or municipality to disambiguate",
        tolerance=tolerance,
        on_error=on_error,
    )


def clean_bparaje_name(
    names: NameInput,
    section: Optional[str] = None,
    dm: Optional[str] = None,
    municipality: Optional[str] = None,
    tolerance: float = 0.25,
    on_error: str = "fail",
):
    """Limpiar y estandarizar nombres de barrios y parajes."""
    parent_filter_ids = None
    parent_prefix_len = None
    if section is not None:
        parent_filter_ids = _resolve_parent_ids(section, _section_alias_data(), "SEC_ID", "SEC_NAME")
        if parent_filter_ids:
            parent_prefix_len = 8
    elif dm is not None:
        parent_filter_ids = _resolve_parent_ids(dm, _dm_alias_data(), "DM_ID", "DM_NAME")
        if parent_filter_ids:
            parent_prefix_len = 6
    elif municipality is not None:
        parent_filter_ids = _resolve_parent_ids(
            municipality,
            _municipality_alias_data(),
            "MUN_ID",
            "MUN_NAME",
        )
        if parent_filter_ids:
            parent_prefix_len = 4

    return _generic_clean_names(
        names,
        _bparaje_alias_data(),
        id_col="BP_ID",
        name_col="BP_NAME",
        level_label="Barrio/paraje",
        prefix_regex=r"^(barrio|paraje|bar\.?)\s+",
        code_regex=r"^\d{11}$",
        parent_filter_ids=parent_filter_ids,
        parent_prefix_len=parent_prefix_len,
        parent_hint="Use section, dm, or municipality to disambiguate",
        tolerance=tolerance,
        on_error=on_error,
    )


def clean_zone_name(
    names: NameInput,
    tolerance: float = 0.25,
    on_error: str = "fail",
):
    """Limpiar y estandarizar nombres de zonas de residencia."""
    return _generic_clean_names(
        names,
        _zone_alias_data(),
        id_col="ZONE_ID",
        name_col="ZONE_NAME",
        level_label="Zone",
        prefix_regex=r"^(zona|area|area)\s+",
        code_regex=r"^\d{2}$",
        tolerance=tolerance,
        on_error=on_error,
    )


gd_clean_prov_name = clean_prov_name
gd_clean_region_name = clean_region_name
gd_clean_municipality_name = clean_municipality_name
gd_clean_dm_name = clean_dm_name
gd_clean_section_name = clean_section_name
gd_clean_bparaje_name = clean_bparaje_name
gd_clean_zone_name = clean_zone_name

"""
Funciones para preparar y crear mapas coropleticos de Republica Dominicana.
"""

from __future__ import annotations

import unicodedata
from collections.abc import Mapping, Sequence
from typing import Any, Optional

import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap, ListedColormap

from geodompy.clean import (
    clean_bparaje_name,
    clean_dm_name,
    clean_municipality_name,
    clean_prov_name,
    clean_region_name,
    clean_section_name,
    clean_zone_name,
)
from geodompy.data import bparajes, dm, municipalities, provinces, regions, sections, zones
from geodompy.detect import detect_fill, detect_level
from geodompy._codes import CODE_PARTS, code
from geodompy.palettes import Palette, discrete_colors, normalize_color, resolve_palette


def _normalize_name(name: object) -> str:
    if pd.isna(name):
        return ""
    text = unicodedata.normalize("NFD", str(name))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return " ".join(text.upper().strip().split())


def _clean_names_for_level(level: str, names: list[object], on_error: str = "na") -> list[object]:
    cleaners = {
        "provinces": clean_prov_name,
        "regions": clean_region_name,
        "municipalities": clean_municipality_name,
        "dm": clean_dm_name,
        "sections": clean_section_name,
        "zones": clean_zone_name,
        "bparajes": clean_bparaje_name,
    }
    cleaner = cleaners.get(level)
    if cleaner is None:
        return names
    return cleaner(names, tolerance=0.5, on_error=on_error)


def map_data(
    data: pd.DataFrame,
    fill: Optional[str] = None,
    level: Optional[str] = None,
    name: Optional[str] = None,
    key: Optional[str] = None,
) -> gpd.GeoDataFrame:
    """
    Prepara datos para mapeo uniendolos con geometrias administrativas.
    """
    info = detect_level(data, level=level, name=name, key=key)

    if info["level"] is None:
        raise ValueError(
            "No se pudo determinar el nivel administrativo. "
            "Especifique level, name y key manualmente."
        )
    if info["name"] is None:
        raise ValueError("No se pudo determinar la variable geografica en data.")
    if info["key"] is None:
        raise ValueError("No se pudo determinar la variable clave de enlace.")

    if fill is None:
        fill = detect_fill(data, exclude=[info["name"]])

    geo_funcs = {
        "provinces": provinces,
        "regions": regions,
        "municipalities": municipalities,
        "dm": dm,
        "sections": sections,
        "zones": zones,
        "bparajes": bparajes,
    }
    if info["level"] not in geo_funcs:
        raise ValueError(f"Nivel administrativo no reconocido: {info['level']}")

    geo_df = geo_funcs[info["level"]]()
    geo_df = geo_df.copy()
    data_copy = data.copy()

    if info["key"] == "TOPONIMIA":
        try:
            data_names = _clean_names_for_level(
                info["level"],
                data_copy[info["name"]].tolist(),
                on_error="na",
            )
            geo_names = _clean_names_for_level(
                info["level"],
                geo_df[info["key"]].tolist(),
                on_error="omit",
            )
        except Exception:
            data_names = data_copy[info["name"]].tolist()
            geo_names = geo_df[info["key"]].tolist()
    else:
        data_names = data_copy[info["name"]].tolist()
        geo_names = geo_df[info["key"]].tolist()
        if info["key"] in CODE_PARTS:
            width = 11 if info["key"] == "BP_CODE" else 2 * len(CODE_PARTS[info["key"]])
            data_names = [code(value, width) for value in data_names]

    data_copy["_join_key"] = [_normalize_name(value) for value in data_names]
    geo_df["_join_key"] = [_normalize_name(value) for value in geo_names]
    if fill not in data_copy:
        raise ValueError("La variable de color no existe en los datos.")
    keys = data_copy.loc[data_copy["_join_key"] != "", "_join_key"]
    if keys.duplicated().any():
        raise ValueError("Hay filas duplicadas por unidad territorial. Agrega los datos antes de mapear.")
    ambiguous = set(geo_df.loc[geo_df["_join_key"].duplicated(), "_join_key"])
    if any(value in ambiguous for value in keys):
        raise ValueError("La clave territorial es ambigua. Usa un codigo compuesto como MUN_CODE o BP_CODE.")

    data_dict = {}
    for _, row in data_copy.iterrows():
        join_key = row["_join_key"]
        if join_key:
            data_dict[join_key] = row

    fill_var = fill
    for column in data_copy.columns:
        if column == "_join_key":
            continue
        output_column = column
        if output_column in geo_df.columns:
            output_column = f"{column}_data"
        if column == fill:
            fill_var = output_column
        geo_df[output_column] = geo_df["_join_key"].map(
            lambda join_key, col=column: data_dict.get(join_key, {}).get(col)
            if join_key in data_dict
            else None
        )

    merged = geo_df.drop(columns=["_join_key"])
    merged.attrs["fill_var"] = fill_var
    merged.attrs["geo_level"] = info["level"]
    return merged


def _plot_map_frame(
    map_df: gpd.GeoDataFrame,
    fill_var: str,
    cmap: str,
    palette: Palette,
    colors: Optional[Mapping[str, str]],
    domain: Optional[Sequence[str]],
    missing: str,
    background_color: str,
    legend: bool,
    edgecolor: str,
    linewidth: float,
    ax: Optional[Any] = None,
    **kwargs,
):
    if "geometry" not in map_df.columns:
        raise ValueError("El nivel detectado no tiene geometria disponible para mapear.")

    if ax is None:
        _, ax = plt.subplots(1, 1)

    missing = normalize_color(missing, "El color sin datos")
    background_color = normalize_color(background_color, "El color de fondo")
    ax.set_facecolor(background_color)
    map_df.plot(
        ax=ax,
        color=missing,
        edgecolor="#a0a0a0",
        linewidth=linewidth * 0.5,
    )
    fill_values = map_df[fill_var]
    numeric_fill = pd.api.types.is_numeric_dtype(fill_values) and not pd.api.types.is_bool_dtype(fill_values)
    palette_value = palette if palette is not None else cmap
    plot_options = dict(
        column=fill_var, ax=ax, legend=legend, edgecolor=edgecolor, linewidth=linewidth,
        missing_kwds={"color": missing, "edgecolor": "grey", "linewidth": linewidth * 0.5},
    )
    if numeric_fill:
        plot_options["cmap"] = LinearSegmentedColormap.from_list("geodom", resolve_palette(palette_value, numeric=True))
    else:
        categories, category_colors = discrete_colors(fill_values, palette_value, colors, domain)
        plot_options.update(cmap=ListedColormap([category_colors[value] for value in categories]), categorical=True, categories=categories)
    plot_options.update(kwargs)
    map_df.plot(**plot_options)
    ax.set_axis_off()
    return ax


def _add_labels(
    ax: Any,
    map_df: gpd.GeoDataFrame,
    labels: Optional[object],
    label_size: float,
    label_color: str,
    fill_var: Optional[str] = None,
) -> None:
    if labels is None or labels is False:
        return
    if labels is True or labels == "name":
        label_col = "TOPONIMIA"
    elif labels == "value":
        label_col = fill_var
    elif labels == "both":
        if fill_var is None or fill_var not in map_df.columns:
            raise ValueError("labels='both' requiere una variable fill valida.")
        label_col = "_geodom_label"
        map_df[label_col] = map_df["TOPONIMIA"].astype(str)
        present = map_df[fill_var].notna()
        map_df.loc[present, label_col] = (
            map_df.loc[present, "TOPONIMIA"].astype(str)
            + ": "
            + map_df.loc[present, fill_var].astype(str)
        )
    elif isinstance(labels, str):
        label_col = labels
    else:
        raise ValueError("labels debe ser True, False, None, 'name', 'value', 'both', o el nombre de una columna.")

    if label_col is None:
        raise ValueError("labels='value' requiere una variable fill valida.")

    if label_col not in map_df.columns:
        available = ", ".join(map_df.columns)
        raise ValueError(f"La columna '{label_col}' no existe. Columnas disponibles: {available}")

    points = map_df.geometry.representative_point()
    for idx, point in points.items():
        label = map_df.loc[idx, label_col]
        if pd.isna(label):
            continue
        ax.text(
            point.x,
            point.y,
            str(label),
            ha="center",
            va="center",
            fontsize=label_size,
            color=label_color,
        )


def map(
    data: pd.DataFrame,
    fill: Optional[str] = None,
    labels: Optional[object] = None,
    label_size: float = 2.5,
    level: Optional[str] = None,
    name: Optional[str] = None,
    key: Optional[str] = None,
    cmap: str = "viridis",
    palette: Palette = None,
    colors: Optional[Mapping[str, str]] = None,
    domain: Optional[Sequence[str]] = None,
    missing: str = "#cbd5e1",
    background_color: str = "#eef4f1",
    figsize: tuple = (10, 8),
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    caption: Optional[str] = None,
    legend: bool = True,
    label_color: str = "black",
    edgecolor: str = "white",
    linewidth: float = 0.3,
    ax: Optional[Any] = None,
    **kwargs,
) -> plt.Figure:
    """
    Crea un mapa coropletico con deteccion automatica de nivel y fill.
    """
    map_df = map_data(data, fill=fill, level=level, name=name, key=key)
    fill_var = map_df.attrs.get("fill_var", fill)

    if ax is None:
        fig, ax = plt.subplots(1, 1, figsize=figsize)
    else:
        fig = ax.figure

    _plot_map_frame(
        map_df,
        fill_var=fill_var,
        cmap=cmap,
        palette=palette,
        colors=colors,
        domain=domain,
        missing=missing,
        background_color=background_color,
        legend=legend,
        edgecolor=edgecolor,
        linewidth=linewidth,
        ax=ax,
        **kwargs,
    )
    _add_labels(ax, map_df, labels, label_size, label_color, fill_var)
    fig.patch.set_facecolor(normalize_color(background_color, "El color de fondo"))

    if title:
        ax.set_title(title, fontsize=14, fontweight="bold")
    if subtitle:
        fig.suptitle(subtitle, y=0.96, fontsize=11)
    if caption:
        fig.text(0.01, 0.01, caption, ha="left", va="bottom", fontsize=9, color="dimgray")

    plt.tight_layout()
    return fig


def gd_mpl_plot(*args, **kwargs) -> plt.Figure:
    """Alias geodom para crear mapas Matplotlib."""
    return map(*args, **kwargs)


def gd_geom_sf(
    data: Optional[pd.DataFrame] = None,
    fill: Optional[str] = None,
    level: Optional[str] = None,
    name: Optional[str] = None,
    key: Optional[str] = None,
    cmap: str = "viridis",
    palette: Palette = None,
    colors: Optional[Mapping[str, str]] = None,
    domain: Optional[Sequence[str]] = None,
    missing: str = "#cbd5e1",
    background_color: str = "#eef4f1",
    legend: bool = True,
    edgecolor: str = "white",
    linewidth: float = 0.3,
    ax: Optional[Any] = None,
    **kwargs,
):
    """
    Helper de capa Matplotlib equivalente al rol de gd_geom_sf en R.
    """
    if data is None:
        if ax is None:
            _, ax = plt.subplots(1, 1)
        ax.set_axis_off()
        return ax

    map_df = map_data(data, fill=fill, level=level, name=name, key=key)
    fill_var = map_df.attrs.get("fill_var", fill)
    return _plot_map_frame(
        map_df,
        fill_var=fill_var,
        cmap=cmap,
        palette=palette,
        colors=colors,
        domain=domain,
        missing=missing,
        background_color=background_color,
        legend=legend,
        edgecolor=edgecolor,
        linewidth=linewidth,
        ax=ax,
        **kwargs,
    )


gd_map_data = map_data
gd_map = map

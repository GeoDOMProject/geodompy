"""Shared GeoDOM color palettes and validation helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Optional, Union

from matplotlib.colors import to_hex
from pandas import isna

PALETTES = {
    "viridis": ["#440154", "#482878", "#3e4989", "#31688e", "#26828e", "#1f9e89", "#35b779", "#6ece58", "#fde725"],
    "plasma": ["#0d0887", "#5b02a3", "#9a179b", "#cb4679", "#ed7953", "#fb9f3a", "#fdca26", "#f0f921"],
    "inferno": ["#000004", "#1b0c41", "#4a0c6b", "#781c6d", "#a52c60", "#cf4446", "#ed6925", "#fb9b06", "#fcffa4"],
    "magma": ["#000004", "#180f3d", "#440f76", "#721f81", "#9e2f7f", "#cd4071", "#f1605d", "#fd9668", "#fcfdbf"],
    "cividis": ["#00224e", "#123570", "#3b496c", "#575d6d", "#707173", "#8a8678", "#a59c74", "#c3b369", "#e1cc55", "#fee838"],
    "blues": ["#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b"],
    "greens": ["#f7fcf5", "#e5f5e0", "#c7e9c0", "#a1d99b", "#74c476", "#41ab5d", "#238b45", "#006d2c", "#00441b"],
    "orangeblue": ["#b35806", "#e08214", "#fdb863", "#fee0b6", "#f7f7f7", "#d8daeb", "#b2abd2", "#8073ac", "#542788"],
    "geodom": ["#4e79a7", "#f28e2b", "#59a14f", "#e15759", "#76b7b2", "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ab", "#2f4b7c", "#a05195", "#d45087", "#f95d6a", "#ff7c43", "#ffa600"],
    "tableau": ["#4e79a7", "#f28e2b", "#e15759", "#76b7b2", "#59a14f", "#edc948", "#b07aa1", "#ff9da7", "#9c755f", "#bab0ab"],
    "set2": ["#66c2a5", "#fc8d62", "#8da0cb", "#e78ac3", "#a6d854", "#ffd92f", "#e5c494", "#b3b3b3"],
    "dark2": ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02", "#a6761d", "#666666"],
    "pastel": ["#b3e2cd", "#fdcdac", "#cbd5e8", "#f4cae4", "#e6f5c9", "#fff2ae", "#f1e2cc", "#cccccc"],
    "highcontrast": ["#004488", "#ddaa33", "#bb5566", "#000000", "#228833", "#aa3377", "#66ccee", "#ee7733"],
}

Palette = Optional[Union[str, Sequence[str]]]


def normalize_color(color: str, label: str = "color") -> str:
    try:
        return to_hex(color, keep_alpha=False).lower()
    except (TypeError, ValueError) as error:
        raise ValueError(f"{label} no es un color valido: {color}.") from error


def resolve_palette(palette: Palette = None, *, numeric: bool = True) -> list[str]:
    value = palette if palette is not None else ("viridis" if numeric else "geodom")
    if isinstance(value, str):
        key = value.strip().lower()
        if key not in PALETTES:
            raise ValueError(f"Paleta desconocida: {value}.")
        result = list(PALETTES[key])
    else:
        result = [normalize_color(color, f"El color {index + 1} de la paleta") for index, color in enumerate(value)]
    minimum = 2 if numeric else 1
    if len(result) < minimum:
        message = "Una paleta continua necesita al menos dos colores." if numeric else "La paleta discreta necesita al menos un color."
        raise ValueError(message)
    return result


def discrete_colors(values, palette: Palette = None, colors: Optional[Mapping[str, str]] = None, domain: Optional[Sequence[str]] = None):
    observed = list(dict.fromkeys(str(value) for value in values if value is not None and not isna(value) and str(value).strip()))
    categories = list(dict.fromkeys([*(str(value) for value in (domain or [])), *observed]))
    palette_values = resolve_palette(palette, numeric=False)
    result = {category: palette_values[index % len(palette_values)] for index, category in enumerate(categories)}
    for category, color in (colors or {}).items():
        key = str(category)
        if key in result:
            result[key] = normalize_color(color, f"El color de {key}")
    return categories, result

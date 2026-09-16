"""Portable interactive maps using GeoDOM's bundled browser renderer."""

import html
import json
import base64
import gzip
from pathlib import Path
from collections.abc import Mapping, Sequence
from typing import Optional, Union

import geopandas as gpd
import pandas as pd

from geodompy.data import provinces, municipalities
from geodompy.map import map_data
from geodompy.palettes import Palette, discrete_colors, normalize_color, resolve_palette


class InteractiveMap(str):
    """An HTML document that can be saved or displayed in a notebook."""

    def save(self, file: Union[str, Path]) -> Path:
        """Write this map as UTF-8 HTML and return its path."""
        path = Path(file)
        path.write_text(self, encoding="utf-8")
        return path

    def _repr_html_(self) -> str:
        return '<iframe title="Mapa interactivo GeoDOM" sandbox="allow-scripts" style="width:100%;height:760px;border:0" srcdoc="' + html.escape(self, quote=True) + '"></iframe>'


def _geojson(frame: gpd.GeoDataFrame) -> dict:
    if not isinstance(frame, gpd.GeoDataFrame) or frame.empty or frame.crs is None:
        raise ValueError("La capa debe contener geometrías con un sistema de referencia conocido.")
    if frame.geometry.isna().any() or frame.geometry.is_empty.any():
        raise ValueError("La capa contiene geometrías vacías.")
    if not frame.geometry.geom_type.isin(["Polygon", "MultiPolygon"]).all():
        raise ValueError("El visor admite polígonos y multipolígonos.")
    result = json.loads(frame.to_crs(4326).to_json(na="null", drop_id=True))
    def rounded(value):
        if isinstance(value[0], (float, int)):
            return [round(v, 6) for v in value[:2]]
        return [rounded(child) for child in value]
    for feature in result['features']:
        feature['geometry']['coordinates'] = rounded(feature['geometry']['coordinates'])
    return result


def map_interactive(
    data: pd.DataFrame,
    fill: Optional[str] = None,
    level: Optional[str] = None,
    name: Optional[str] = None,
    key: Optional[str] = None,
    *,
    title: str = "Mapa GeoDOM",
    subtitle: Optional[str] = None,
    caption: Optional[str] = None,
    labels: Union[str, bool] = False,
    background: str = "none",
    context: bool = True,
    palette: Palette = None,
    colors: Optional[Mapping[str, str]] = None,
    domain: Optional[Sequence[str]] = None,
    missing: str = "#cbd5e1",
    background_color: str = "#eef4f1",
    file: Optional[Union[str, Path]] = None,
) -> InteractiveMap:
    """Create a standalone HTML map with search, selection and hierarchy filters.

    Runtime, styles and polygon data are included in the document. The default
    ``background='none'`` works offline after generation. Optional ``'osm'``
    street tiles need internet access. Context boundaries have no measurements;
    values are never propagated from a province to its municipalities.
    ``file`` optionally saves the document. The return value also supports
    ``.save(path)`` and notebook HTML display. Existing map join checks apply.
    """
    if background not in ("none", "osm"):
        raise ValueError("background debe ser 'none' u 'osm'.")
    if labels not in (False, True, "name", "value", "both", None, ""):
        raise ValueError("labels debe ser False, True, 'name', 'value' o 'both'.")
    joined = map_data(data, fill=fill, level=level, name=name, key=key)
    primary = joined.attrs["geo_level"]
    layers = [{"id": primary, "fillVar": joined.attrs["fill_var"], "measured": True, "geojson": _geojson(joined)}]
    if context:
        for layer_id, getter in (("provinces", provinces), ("municipalities", municipalities)):
            if layer_id != primary:
                layers.append({"id": layer_id, "fillVar": None, "measured": False, "geojson": _geojson(getter())})
    fill_values = joined[joined.attrs["fill_var"]]
    numeric_fill = pd.api.types.is_numeric_dtype(fill_values) and not pd.api.types.is_bool_dtype(fill_values)
    palette_values = resolve_palette(palette, numeric=numeric_fill)
    category_domain = None
    category_colors = None
    if not numeric_fill:
        category_domain, category_colors = discrete_colors(fill_values, palette, colors, domain)
    payload = {"version": "1.2.0", "primary": primary, "layers": layers, "options": {
        "title": title or "Mapa GeoDOM", "subtitle": subtitle or "", "caption": caption or "",
        "labels": labels or False, "background": background,
        "backgroundColor": normalize_color(background_color, "El color de fondo"),
        "palette": palette_values, "colors": category_colors, "domain": category_domain,
        "missing": normalize_color(missing, "El color sin datos"),
    }}
    encoded = json.dumps(payload, ensure_ascii=True, allow_nan=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    encoded = base64.b64encode(gzip.compress(encoded.encode('utf-8'), mtime=0)).decode('ascii')
    assets = Path(__file__).parent / "assets"
    runtime = (assets / "interactive-runtime.js").read_text(encoding="utf-8")
    style = (assets / "interactive.css").read_text(encoding="utf-8")
    result = InteractiveMap('<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="generator" content="GeoDOM 1.2.0"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; img-src data: https://tile.openstreetmap.org; connect-src \'none\'; base-uri \'none\'; form-action \'none\'"><title>' + html.escape(title or "Mapa GeoDOM") + '</title><style>' + style + '</style></head><body><main id="geodom-interactive"></main><script id="geodom-payload" type="application/octet-stream" data-encoding="gzip">' + encoded + '</script><script>' + runtime + '\nGeoDOMInteractive.boot();</script></body></html>')
    if file is not None:
        result.save(file)
    return result


gd_map_interactive = map_interactive

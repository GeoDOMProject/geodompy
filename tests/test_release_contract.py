import pandas as pd
import pytest
from geodompy._codes import add_codes
from geodompy.cache import _get_cache_dir
from geodompy import detect_level, map_data, municipalities

def test_composite_codes_keep_parents_and_leading_zeros():
    data = pd.DataFrame({"PROV": ["01", "02"], "MUN": ["01", "01"], "DM": ["01", "01"], "SECC": ["01", "01"], "BP": ["001", "001"]})
    result = add_codes(data)
    assert result.MUN_CODE.tolist() == ["0101", "0201"]
    assert result.BP_CODE.tolist() == ["01010101001", "02010101001"]
    assert detect_level(pd.DataFrame({"MUN_CODE": ["0101", "0201"]}))["level"] == "municipalities"

def test_python_cache_does_not_overwrite_r_pins(tmp_path, monkeypatch):
    monkeypatch.setenv("GEODOM_CACHE_DIR", str(tmp_path))
    assert _get_cache_dir() == tmp_path / "python-v1"

def test_map_join_rejects_duplicates_and_tracks_fill_collisions():
    data = pd.DataFrame({"PROV_CODE": ["01", "02"], "TOPONIMIA": [10, 20]})
    result = map_data(data, fill="TOPONIMIA", level="provinces", name="PROV_CODE", key="PROV_CODE")
    assert result.attrs["fill_var"] == "TOPONIMIA_data"
    assert result.TOPONIMIA_data.notna().sum() == 2
    with pytest.raises(ValueError, match="duplicadas"):
        map_data(pd.concat([data, data.iloc[:1]]), fill="TOPONIMIA", level="provinces", name="PROV_CODE", key="PROV_CODE")

def test_municipalities_are_transformed_from_utm_to_geographic_coordinates():
    frame = municipalities()
    assert frame.crs.to_epsg() == 4326
    xmin, ymin, xmax, ymax = frame.total_bounds
    assert -73 < xmin < xmax < -68
    assert 17 < ymin < ymax < 21
    assert frame.MUN_CODE.nunique() == 158

def test_cache_reuses_geometry_without_another_download(tmp_path, monkeypatch):
    import geopandas as gpd
    import requests
    from shapely.geometry import Point
    from types import SimpleNamespace
    from geodompy.cache import fetch_and_cache

    monkeypatch.setenv("GEODOM_CACHE_DIR", str(tmp_path))
    original = gpd.GeoDataFrame({"PROV": ["01", "02"]},
        geometry=[Point(-70, 19), Point(-71, 18)], crs=4326)
    response = SimpleNamespace(content=original.to_json().encode(),
        raise_for_status=lambda: None, headers={"etag": '"cache-contract"'})
    monkeypatch.setattr(requests, "head", lambda *a, **kw: response)
    monkeypatch.setattr(requests, "get", lambda *a, **kw: response)
    first = fetch_and_cache("RD_PROV")

    def unexpected_download(*args, **kwargs):
        raise AssertionError("The second read must use the persisted cache")
    monkeypatch.setattr(requests, "get", unexpected_download)
    cached = fetch_and_cache("RD_PROV")
    assert cached.crs.to_epsg() == 4326
    assert cached.geometry.equals(first.geometry)
    assert cached.PROV_CODE.tolist() == ["01", "02"]

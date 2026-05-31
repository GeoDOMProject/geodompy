"""
Tests para las funciones de datos de geodompy
"""

import pytest
import pandas as pd
import geopandas as gpd


class TestProvinces:
    """Tests para la función provinces()"""
    
    def test_provinces_returns_geodataframe(self):
        """provinces() debe retornar un GeoDataFrame por defecto"""
        import geodompy as gd
        result = gd.provinces()
        assert isinstance(result, gpd.GeoDataFrame)
        assert 'geometry' in result.columns
    
    def test_provinces_sf_false(self):
        """provinces(sf=False) debe retornar DataFrame sin geometría"""
        import geodompy as gd
        result = gd.provinces(sf=False)
        assert isinstance(result, pd.DataFrame)
        assert 'geometry' not in result.columns
    
    def test_provinces_has_required_columns(self):
        """provinces() debe tener columnas requeridas"""
        import geodompy as gd
        result = gd.provinces(sf=False)
        # Verificar que tiene alguna columna de nombre
        assert any(col in result.columns for col in ['TOPONIMIA', 'PROV_NAME', 'nombre', 'PROV'])
    
    def test_provinces_has_32_provinces(self):
        """RD tiene 32 provincias"""
        import geodompy as gd
        result = gd.provinces(sf=False)
        assert len(result) >= 31  # Al menos 31 provincias


class TestRegions:
    """Tests para la función regions()"""
    
    def test_regions_returns_geodataframe(self):
        """regions() debe retornar un GeoDataFrame por defecto"""
        import geodompy as gd
        result = gd.regions()
        assert isinstance(result, gpd.GeoDataFrame)
    
    def test_regions_sf_false(self):
        """regions(sf=False) debe retornar DataFrame sin geometría"""
        import geodompy as gd
        result = gd.regions(sf=False)
        assert isinstance(result, pd.DataFrame)
        assert 'geometry' not in result.columns
    
    def test_regions_has_10_regions(self):
        """RD tiene 10 regiones de planificación"""
        import geodompy as gd
        result = gd.regions(sf=False)
        assert len(result) >= 10


class TestMunicipalities:
    """Tests para la función municipalities()"""
    
    def test_municipalities_returns_geodataframe(self):
        """municipalities() debe retornar un GeoDataFrame"""
        import geodompy as gd
        result = gd.municipalities()
        assert isinstance(result, gpd.GeoDataFrame)
    
    def test_municipalities_sf_false(self):
        """municipalities(sf=False) debe retornar DataFrame sin geometría"""
        import geodompy as gd
        result = gd.municipalities(sf=False)
        assert 'geometry' not in result.columns
    
    def test_municipalities_count(self):
        """RD tiene 158 municipios"""
        import geodompy as gd
        result = gd.municipalities(sf=False)
        assert len(result) >= 155


class TestDm:
    """Tests para la función dm()"""
    
    def test_dm_returns_geodataframe(self):
        """dm() debe retornar un GeoDataFrame"""
        import geodompy as gd
        result = gd.dm()
        assert isinstance(result, gpd.GeoDataFrame)


class TestSections:
    """Tests para la función sections()"""
    
    def test_sections_returns_geodataframe(self):
        """sections() debe retornar un GeoDataFrame"""
        import geodompy as gd
        result = gd.sections()
        assert isinstance(result, gpd.GeoDataFrame)

    def test_sections_sf_false(self):
        """sections(sf=False) debe retornar DataFrame sin geometrÃ­a"""
        import geodompy as gd
        result = gd.sections(sf=False)
        assert isinstance(result, pd.DataFrame)
        assert 'geometry' not in result.columns


class TestZones:
    """Tests para la función zones()"""
    
    def test_zones_returns_dataframe(self):
        """zones() debe retornar un DataFrame"""
        import geodompy as gd
        result = gd.zones()
        assert isinstance(result, pd.DataFrame)
    
    def test_zones_has_2_zones(self):
        """Hay 2 zonas: Urbana y Rural"""
        import geodompy as gd
        result = gd.zones()
        assert len(result) == 2
    
    def test_zones_has_required_columns(self):
        """zones() debe tener columnas requeridas"""
        import geodompy as gd
        result = gd.zones()
        assert 'ZONE_ID' in result.columns
        assert 'ZONE_CODE' in result.columns
        assert 'ZONE_NAME' in result.columns
        assert 'TOPONIMIA' in result.columns


class TestBparajes:
    """Tests para la función bparajes()"""
    
    def test_bparajes_returns_geodataframe(self):
        """bparajes() debe retornar un GeoDataFrame"""
        import geodompy as gd
        result = gd.bparajes()
        assert isinstance(result, gpd.GeoDataFrame)
    
    def test_bparajes_sf_false(self):
        """bparajes(sf=False) debe retornar DataFrame sin geometría"""
        import geodompy as gd
        result = gd.bparajes(sf=False)
        assert 'geometry' not in result.columns


class TestMacroregions:
    """Tests para la función macroregions()"""
    
    def test_macroregions_returns_geodataframe(self):
        """macroregions() debe retornar un GeoDataFrame"""
        import geodompy as gd
        result = gd.macroregions()
        assert isinstance(result, gpd.GeoDataFrame)
    
    def test_macroregions_sf_false(self):
        """macroregions(sf=False) debe retornar DataFrame sin geometría"""
        import geodompy as gd
        result = gd.macroregions(sf=False)
        assert 'geometry' not in result.columns
    
    def test_macroregions_has_3_regions(self):
        """Hay 3 macro-regiones"""
        import geodompy as gd
        result = gd.macroregions(sf=False)
        assert len(result) >= 3


class TestGetDataset:
    """Tests para la función get_dataset()"""
    
    def test_get_dataset_returns_dataframe(self):
        """get_dataset() debe retornar un DataFrame"""
        import geodompy as gd
        result = gd.get_dataset("provincias_alias")
        assert isinstance(result, pd.DataFrame)
    
    def test_get_dataset_provincias_alias(self):
        """provincias_alias debe tener las columnas correctas"""
        import geodompy as gd
        result = gd.get_dataset("provincias_alias")
        assert 'PROV_ID' in result.columns
        assert 'PROV_NAME' in result.columns


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

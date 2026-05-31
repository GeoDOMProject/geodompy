"""
Tests de paridad con geodomR

Estos tests verifican que geodompy tiene paridad funcional con geodomR.
"""

import pytest
import pandas as pd
import geopandas as gpd


class TestParidadFuncionesExportadas:
    """Verifica que todas las funciones exportadas en geodomR existen en geodompy"""
    
    def test_provinces_exists(self):
        """gd_provinces -> provinces"""
        import geodompy as gd
        assert hasattr(gd, 'provinces')
        assert callable(gd.provinces)
    
    def test_regions_exists(self):
        """gd_regions -> regions"""
        import geodompy as gd
        assert hasattr(gd, 'regions')
        assert callable(gd.regions)
    
    def test_municipalities_exists(self):
        """gd_municipalities -> municipalities"""
        import geodompy as gd
        assert hasattr(gd, 'municipalities')
        assert callable(gd.municipalities)
    
    def test_dm_exists(self):
        """gd_dm -> dm"""
        import geodompy as gd
        assert hasattr(gd, 'dm')
        assert callable(gd.dm)
    
    def test_sections_exists(self):
        """gd_sections -> sections"""
        import geodompy as gd
        assert hasattr(gd, 'sections')
        assert callable(gd.sections)
    
    def test_zones_exists(self):
        """gd_zones -> zones"""
        import geodompy as gd
        assert hasattr(gd, 'zones')
        assert callable(gd.zones)
    
    def test_bparajes_exists(self):
        """gd_bparajes -> bparajes"""
        import geodompy as gd
        assert hasattr(gd, 'bparajes')
        assert callable(gd.bparajes)
    
    def test_macroregions_exists(self):
        """gd_macroregions -> macroregions"""
        import geodompy as gd
        assert hasattr(gd, 'macroregions')
        assert callable(gd.macroregions)
    
    def test_detect_level_exists(self):
        """gd_detect_level -> detect_level"""
        import geodompy as gd
        assert hasattr(gd, 'detect_level')
        assert callable(gd.detect_level)
    
    def test_detect_fill_exists(self):
        """gd_detect_fill -> detect_fill"""
        import geodompy as gd
        assert hasattr(gd, 'detect_fill')
        assert callable(gd.detect_fill)
    
    def test_detect_column_type_exists(self):
        """gd_detect_column_type -> detect_column_type"""
        import geodompy as gd
        assert hasattr(gd, 'detect_column_type')
        assert callable(gd.detect_column_type)
    
    def test_analyze_columns_exists(self):
        """gd_analyze_columns -> analyze_columns"""
        import geodompy as gd
        assert hasattr(gd, 'analyze_columns')
        assert callable(gd.analyze_columns)
    
    def test_clean_prov_name_exists(self):
        """gd_clean_prov_name -> clean_prov_name"""
        import geodompy as gd
        assert hasattr(gd, 'clean_prov_name')
        assert callable(gd.clean_prov_name)
    
    def test_clean_region_name_exists(self):
        """gd_clean_region_name -> clean_region_name"""
        import geodompy as gd
        assert hasattr(gd, 'clean_region_name')
        assert callable(gd.clean_region_name)
    
    def test_clean_municipality_name_exists(self):
        """gd_clean_municipality_name -> clean_municipality_name"""
        import geodompy as gd
        assert hasattr(gd, 'clean_municipality_name')
        assert callable(gd.clean_municipality_name)
    
    def test_clean_zone_name_exists(self):
        """gd_clean_zone_name -> clean_zone_name"""
        import geodompy as gd
        assert hasattr(gd, 'clean_zone_name')
        assert callable(gd.clean_zone_name)

    def test_clean_dm_name_exists(self):
        """gd_clean_dm_name -> clean_dm_name"""
        import geodompy as gd
        assert hasattr(gd, 'clean_dm_name')
        assert callable(gd.clean_dm_name)

    def test_clean_section_name_exists(self):
        """gd_clean_section_name -> clean_section_name"""
        import geodompy as gd
        assert hasattr(gd, 'clean_section_name')
        assert callable(gd.clean_section_name)

    def test_clean_bparaje_name_exists(self):
        """gd_clean_bparaje_name -> clean_bparaje_name"""
        import geodompy as gd
        assert hasattr(gd, 'clean_bparaje_name')
        assert callable(gd.clean_bparaje_name)

    def test_add_parent_cols_exists(self):
        """gd_add_parent_cols -> add_parent_cols"""
        import geodompy as gd
        assert hasattr(gd, 'add_parent_cols')
        assert callable(gd.add_parent_cols)
    
    def test_map_exists(self):
        """gd_map -> map"""
        import geodompy as gd
        assert hasattr(gd, 'map')
        assert callable(gd.map)
    
    def test_map_data_exists(self):
        """gd_map_data -> map_data"""
        import geodompy as gd
        assert hasattr(gd, 'map_data')
        assert callable(gd.map_data)
    
    def test_get_dataset_exists(self):
        """gd_get_dataset -> get_dataset"""
        import geodompy as gd
        assert hasattr(gd, 'get_dataset')
        assert callable(gd.get_dataset)

    def test_gd_aliases_exist(self):
        """Los aliases gd_* deben existir y ser invocables"""
        import geodompy as gd

        aliases = [
            'gd_provinces', 'gd_regions', 'gd_municipalities', 'gd_dm',
            'gd_sections', 'gd_zones', 'gd_bparajes', 'gd_macroregions',
            'gd_get_dataset', 'gd_detect_level', 'gd_detect_fill',
            'gd_detect_column_type', 'gd_analyze_columns', 'gd_map',
            'gd_map_data', 'gd_geom_sf', 'gd_mpl_plot',
            'gd_clean_prov_name', 'gd_clean_region_name',
            'gd_clean_municipality_name', 'gd_clean_dm_name',
            'gd_clean_section_name', 'gd_clean_bparaje_name',
            'gd_clean_zone_name', 'gd_add_parent_cols',
        ]

        for alias in aliases:
            assert hasattr(gd, alias), f"Falta alias {alias}"
            assert callable(getattr(gd, alias)), f"{alias} no es callable"


class TestParidadParametros:
    """Verifica que las funciones tienen los parámetros equivalentes a geodomR"""
    
    def test_provinces_has_id_param(self):
        """provinces debe tener parámetro id como gd_provinces"""
        import geodompy as gd
        import inspect
        sig = inspect.signature(gd.provinces)
        assert 'id' in sig.parameters
    
    def test_provinces_has_sf_param(self):
        """provinces debe tener parámetro sf como gd_provinces"""
        import geodompy as gd
        import inspect
        sig = inspect.signature(gd.provinces)
        assert 'sf' in sig.parameters
    
    def test_provinces_has_reg_param(self):
        """provinces debe tener parámetro reg como gd_provinces"""
        import geodompy as gd
        import inspect
        sig = inspect.signature(gd.provinces)
        assert 'reg' in sig.parameters
    
    def test_regions_has_id_param(self):
        """regions debe tener parámetro id"""
        import geodompy as gd
        import inspect
        sig = inspect.signature(gd.regions)
        assert 'id' in sig.parameters
    
    def test_municipalities_has_id_param(self):
        """municipalities debe tener parámetro id"""
        import geodompy as gd
        import inspect
        sig = inspect.signature(gd.municipalities)
        assert 'id' in sig.parameters
    
    def test_clean_prov_name_has_tolerance_param(self):
        """clean_prov_name debe tener parámetro tolerance (equiv a .tol)"""
        import geodompy as gd
        import inspect
        sig = inspect.signature(gd.clean_prov_name)
        assert 'tolerance' in sig.parameters
    
    def test_clean_prov_name_has_on_error_param(self):
        """clean_prov_name debe tener parámetro on_error"""
        import geodompy as gd
        import inspect
        sig = inspect.signature(gd.clean_prov_name)
        assert 'on_error' in sig.parameters


class TestParidadComportamiento:
    """Verifica que el comportamiento es equivalente entre geodompy y geodomR"""
    
    def test_zones_has_2_zones(self):
        """zones() debe retornar 2 zonas como gd_zones()"""
        import geodompy as gd
        result = gd.zones()
        assert len(result) == 2
    
    def test_zones_has_urbana_rural(self):
        """zones() debe tener Urbana y Rural"""
        import geodompy as gd
        result = gd.zones()
        zone_names = result['ZONE_NAME'].tolist()
        assert 'Urbana' in zone_names
        assert 'Rural' in zone_names
    
    def test_clean_on_error_fail_raises(self):
        """on_error='fail' debe lanzar excepción como en R"""
        import geodompy as gd
        with pytest.raises(ValueError):
            gd.clean_prov_name(['xxxinvalidxxx'], tolerance=0.1, on_error='fail')
    
    def test_clean_on_error_na_returns_none(self):
        """on_error='na' debe retornar None como NA en R"""
        import geodompy as gd
        result = gd.clean_prov_name(['xxxinvalidxxx'], tolerance=0.1, on_error='na')
        assert result[0] is None
    
    def test_clean_on_error_omit_keeps_original(self):
        """on_error='omit' debe mantener original como en R"""
        import geodompy as gd
        result = gd.clean_prov_name(['xxxinvalidxxx'], tolerance=0.1, on_error='omit')
        assert result[0] == 'xxxinvalidxxx'
    
    def test_detect_level_returns_dict_with_level(self):
        """detect_level debe retornar dict con 'level' como en R"""
        import geodompy as gd
        data = pd.DataFrame({'col': ['A', 'B'], 'val': [1, 2]})
        result = gd.detect_level(data)
        assert 'level' in result
        assert 'name' in result
        assert 'key' in result
        assert 'match_count' in result
        assert 'total_count' in result


class TestParidadAllExports:
    """Verifica que __all__ contiene todas las funciones necesarias"""
    
    def test_all_exports_complete(self):
        """__all__ debe contener todas las funciones de paridad"""
        import geodompy as gd
        
        required_exports = [
            # Data
            'provinces', 'regions', 'municipalities', 'dm', 
            'sections', 'zones', 'bparajes', 'macroregions',
            'get_dataset',
            # Detection
            'detect_level', 'detect_fill', 'detect_column_type', 'analyze_columns',
            # Cleaning
            'clean_prov_name', 'clean_region_name', 
            'clean_municipality_name', 'clean_dm_name',
            'clean_section_name', 'clean_bparaje_name', 'clean_zone_name',
            # Hierarchy
            'add_parent_cols',
            # Mapping
            'map', 'map_data', 'gd_geom_sf', 'gd_mpl_plot',
            # R-style aliases
            'gd_provinces', 'gd_regions', 'gd_municipalities', 'gd_dm',
            'gd_sections', 'gd_zones', 'gd_bparajes', 'gd_macroregions',
            'gd_get_dataset', 'gd_detect_level', 'gd_detect_fill',
            'gd_detect_column_type', 'gd_analyze_columns', 'gd_map',
            'gd_map_data', 'gd_clean_prov_name', 'gd_clean_region_name',
            'gd_clean_municipality_name', 'gd_clean_dm_name',
            'gd_clean_section_name', 'gd_clean_bparaje_name',
            'gd_clean_zone_name', 'gd_add_parent_cols',
        ]
        
        for export in required_exports:
            assert export in gd.__all__, f"'{export}' no está en __all__"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

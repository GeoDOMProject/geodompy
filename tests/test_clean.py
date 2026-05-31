"""
Tests para las funciones de limpieza de nombres de geodompy
"""

import pytest
import pandas as pd


class TestCleanProvName:
    """Tests para clean_prov_name()"""
    
    def test_clean_exact_match(self):
        """Nombres exactos deben coincidir"""
        import geodompy as gd
        # Primero obtenemos los nombres reales
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            name = prov['TOPONIMIA'].iloc[0]
        else:
            name = prov.iloc[0, 0]
        
        result = gd.clean_prov_name([name])
        assert len(result) == 1
        assert result[0] is not None
    
    def test_clean_prov_name_lowercase(self):
        """Nombres en minúsculas deben funcionar"""
        import geodompy as gd
        # Probar con nombres conocidos en minúsculas
        result = gd.clean_prov_name(['azua'], tolerance=0.5, on_error='na')
        assert len(result) == 1
    
    def test_clean_prov_name_on_error_na(self):
        """on_error='na' debe retornar None para no matches"""
        import geodompy as gd
        result = gd.clean_prov_name(['xxxinvalidxxx'], tolerance=0.1, on_error='na')
        assert result[0] is None
    
    def test_clean_prov_name_on_error_omit(self):
        """on_error='omit' debe mantener el nombre original"""
        import geodompy as gd
        result = gd.clean_prov_name(['xxxinvalidxxx'], tolerance=0.1, on_error='omit')
        assert result[0] == 'xxxinvalidxxx'

    def test_clean_prov_name_aggregate_label_returns_none(self):
        """Etiquetas agregadas como Otros no deben hacer fuzzy match con provincias"""
        import geodompy as gd
        result = gd.clean_prov_name(['Otros'], tolerance=0.5, on_error='na')
        assert result[0] is None
    
    def test_clean_prov_name_on_error_fail(self):
        """on_error='fail' debe lanzar excepción"""
        import geodompy as gd
        with pytest.raises(ValueError):
            gd.clean_prov_name(['xxxinvalidxxx'], tolerance=0.1, on_error='fail')
    
    def test_clean_prov_name_preserves_length(self):
        """clean_prov_name debe preservar la longitud del input"""
        import geodompy as gd
        names = ['azua', 'barahona', 'xxx']
        result = gd.clean_prov_name(names, tolerance=0.5, on_error='na')
        assert len(result) == len(names)
    
    def test_clean_prov_name_handles_none(self):
        """clean_prov_name debe manejar None/NaN"""
        import geodompy as gd
        result = gd.clean_prov_name([None, 'azua'], tolerance=0.5, on_error='na')
        assert len(result) == 2
        assert result[0] is None


class TestCleanRegionName:
    """Tests para clean_region_name()"""
    
    def test_clean_region_exact_match(self):
        """Nombres exactos deben coincidir"""
        import geodompy as gd
        reg = gd.regions(sf=False)
        if 'TOPONIMIA' in reg.columns:
            name = reg['TOPONIMIA'].iloc[0]
        else:
            name = reg.iloc[0, 0]
        
        result = gd.clean_region_name([name])
        assert len(result) == 1
        assert result[0] is not None
    
    def test_clean_region_name_on_error_na(self):
        """on_error='na' debe retornar None para no matches"""
        import geodompy as gd
        result = gd.clean_region_name(['xxxinvalidxxx'], tolerance=0.1, on_error='na')
        assert result[0] is None


class TestCleanMunicipalityName:
    """Tests para clean_municipality_name()"""
    
    def test_clean_municipality_exists(self):
        """La función clean_municipality_name debe existir"""
        import geodompy as gd
        assert hasattr(gd, 'clean_municipality_name')
    
    def test_clean_municipality_exact_match(self):
        """Nombres exactos deben coincidir"""
        import geodompy as gd
        mun = gd.municipalities(sf=False)
        if 'TOPONIMIA' in mun.columns:
            name = mun['TOPONIMIA'].iloc[0]
        else:
            name = mun.iloc[0, 0]
        
        result = gd.clean_municipality_name([name], tolerance=0.5, on_error='na')
        assert len(result) == 1
    
    def test_clean_municipality_on_error_na(self):
        """on_error='na' debe retornar None para no matches"""
        import geodompy as gd
        result = gd.clean_municipality_name(['xxxinvalidxxx'], tolerance=0.1, on_error='na')
        assert result[0] is None

    def test_clean_municipality_with_code(self):
        """clean_municipality_name debe aceptar cÃ³digos MUN_ID"""
        import geodompy as gd
        mun = gd.municipalities(sf=False).iloc[0]
        code = f"{mun['PROV']}{mun['MUN']}"
        result = gd.clean_municipality_name([code], on_error='na')
        assert result[0] is not None

    def test_clean_municipality_with_parent_province(self):
        """clean_municipality_name debe aceptar desambiguaciÃ³n por provincia"""
        import geodompy as gd
        result = gd.clean_municipality_name(['Azua'], province='Azua', on_error='na')
        assert result[0] is not None


class TestCleanDmName:
    """Tests para clean_dm_name()"""

    def test_clean_dm_exists(self):
        import geodompy as gd
        assert hasattr(gd, 'clean_dm_name')

    def test_clean_dm_with_code(self):
        import geodompy as gd
        row = gd.dm(sf=False).iloc[0]
        code = f"{row['PROV']}{row['MUN']}{row['DM']}"
        result = gd.clean_dm_name([code], on_error='na')
        assert result[0] is not None

    def test_clean_dm_with_parent_municipality(self):
        import geodompy as gd
        row = gd.dm(sf=False).iloc[0]
        result = gd.clean_dm_name(
            [row['TOPONIMIA']],
            municipality=row['TOPONIMIA'],
            tolerance=0.5,
            on_error='na',
        )
        assert result[0] is not None


class TestCleanSectionName:
    """Tests para clean_section_name()"""

    def test_clean_section_exists(self):
        import geodompy as gd
        assert hasattr(gd, 'clean_section_name')

    def test_clean_section_with_code(self):
        import geodompy as gd
        row = gd.sections(sf=False).iloc[0]
        code = f"{row['PROV']}{row['MUN']}{row['DM']}{row['SEC']}"
        result = gd.clean_section_name([code], on_error='na')
        assert result[0] is not None

    def test_clean_section_with_parent_dm(self):
        import geodompy as gd
        row = gd.sections(sf=False).iloc[0]
        result = gd.clean_section_name(
            [row['TOPONIMIA']],
            dm=row['TOPONIMIA'],
            tolerance=0.5,
            on_error='na',
        )
        assert len(result) == 1


class TestCleanBparajeName:
    """Tests para clean_bparaje_name()"""

    def test_clean_bparaje_exists(self):
        import geodompy as gd
        assert hasattr(gd, 'clean_bparaje_name')

    def test_clean_bparaje_with_code(self):
        import geodompy as gd
        row = gd.bparajes(sf=False).iloc[0]
        code = f"{row['PROV']}{row['MUN']}{row['DM']}{row['SECC']}{row['BP']}"
        result = gd.clean_bparaje_name([code], on_error='na')
        assert result[0] is not None

    def test_clean_bparaje_with_parent_section(self):
        import geodompy as gd
        row = gd.bparajes(sf=False).iloc[0]
        result = gd.clean_bparaje_name(
            [row['TOPONIMIA']],
            section=row['TOPONIMIA'],
            tolerance=0.5,
            on_error='na',
        )
        assert len(result) == 1


class TestCleanZoneName:
    """Tests para clean_zone_name()"""
    
    def test_clean_zone_exists(self):
        """La función clean_zone_name debe existir"""
        import geodompy as gd
        assert hasattr(gd, 'clean_zone_name')
    
    def test_clean_zone_urbana(self):
        """'Urbana' debe coincidir"""
        import geodompy as gd
        result = gd.clean_zone_name(['Urbana'], tolerance=0.5, on_error='na')
        assert len(result) == 1
        assert result[0] is not None
    
    def test_clean_zone_rural(self):
        """'Rural' debe coincidir"""
        import geodompy as gd
        result = gd.clean_zone_name(['Rural'], tolerance=0.5, on_error='na')
        assert len(result) == 1
        assert result[0] is not None
    
    def test_clean_zone_on_error_na(self):
        """on_error='na' debe retornar None para no matches"""
        import geodompy as gd
        result = gd.clean_zone_name(['xxxinvalidxxx'], tolerance=0.1, on_error='na')
        assert result[0] is None


class TestTextCleaning:
    """Tests para la función interna _text_cleaning"""
    
    def test_text_cleaning_removes_accents(self):
        """_text_cleaning debe remover acentos"""
        from geodompy.clean import _text_cleaning
        result = _text_cleaning("Azúa")
        assert 'u' in result  # sin tilde
    
    def test_text_cleaning_lowercase(self):
        """_text_cleaning debe convertir a minúsculas"""
        from geodompy.clean import _text_cleaning
        result = _text_cleaning("AZUA")
        assert result == result.lower()
    
    def test_text_cleaning_removes_prefixes(self):
        """_text_cleaning debe remover prefijos comunes"""
        from geodompy.clean import _text_cleaning
        result = _text_cleaning("Provincia de Azua")
        assert 'provincia' not in result
    
    def test_text_cleaning_handles_na(self):
        """_text_cleaning debe manejar NA"""
        from geodompy.clean import _text_cleaning
        result = _text_cleaning(None)
        assert result == "_na_"
    
    def test_text_cleaning_handles_nan_in_list(self):
        """_text_cleaning debe manejar NaN en lista"""
        from geodompy.clean import _text_cleaning
        import pandas as pd
        result = _text_cleaning([None, pd.NA, 'test'])
        assert result[0] == "_na_"
        assert result[2] == "test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

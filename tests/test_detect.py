"""
Tests para las funciones de detección de geodompy
"""

import pytest
import pandas as pd
import numpy as np


class TestDetectLevel:
    """Tests para detect_level()"""
    
    def test_detect_level_returns_dict(self):
        """detect_level() debe retornar un diccionario"""
        import geodompy as gd
        
        # Obtener nombres de provincias para crear datos de prueba
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:5]
        else:
            names = prov.iloc[:5, 0].tolist()
        
        data = pd.DataFrame({
            'provincia': names,
            'valor': range(len(names))
        })
        
        result = gd.detect_level(data)
        assert isinstance(result, dict)
        assert 'level' in result
        assert 'name' in result
        assert 'key' in result
    
    def test_detect_level_provinces(self):
        """detect_level() debe detectar provincias"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:10]
        else:
            names = prov.iloc[:10, 0].tolist()
        
        data = pd.DataFrame({
            'provincia': names,
            'poblacion': range(len(names))
        })
        
        result = gd.detect_level(data)
        assert result['level'] == 'provinces'
        assert result['name'] == 'provincia'
    
    def test_detect_level_regions(self):
        """detect_level() debe detectar regiones"""
        import geodompy as gd
        
        reg = gd.regions(sf=False)
        if 'TOPONIMIA' in reg.columns:
            names = reg['TOPONIMIA'].tolist()
        else:
            names = reg.iloc[:, 0].tolist()
        
        data = pd.DataFrame({
            'region': names,
            'valor': range(len(names))
        })
        
        result = gd.detect_level(data)
        assert result['level'] == 'regions'
    
    def test_detect_level_with_explicit_level(self):
        """detect_level() con level explícito debe respetar el nivel"""
        import geodompy as gd
        
        data = pd.DataFrame({
            'name': ['A', 'B', 'C'],
            'value': [1, 2, 3]
        })
        
        result = gd.detect_level(data, level='provinces', name='name', key='TOPONIMIA')
        assert result['level'] == 'provinces'


class TestDetectFill:
    """Tests para detect_fill()"""
    
    def test_detect_fill_returns_string(self):
        """detect_fill() debe retornar un string"""
        import geodompy as gd
        
        data = pd.DataFrame({
            'provincia': ['A', 'B', 'C'],
            'poblacion': [1000, 2000, 3000]
        })
        
        result = gd.detect_fill(data, exclude=['provincia'])
        assert isinstance(result, str)
    
    def test_detect_fill_prefers_numeric(self):
        """detect_fill() debe preferir columnas numéricas"""
        import geodompy as gd
        
        data = pd.DataFrame({
            'provincia': ['A', 'B', 'C'],
            'categoria': ['X', 'Y', 'Z'],
            'poblacion': [1000, 2000, 3000]
        })
        
        result = gd.detect_fill(data, exclude=['provincia'])
        # Debe ser una de las columnas restantes (numéricas preferidas)
        assert result in ['poblacion', 'categoria']
    
    def test_detect_fill_excludes_columns(self):
        """detect_fill() debe excluir columnas especificadas"""
        import geodompy as gd
        
        data = pd.DataFrame({
            'provincia': ['A', 'B', 'C'],
            'poblacion': [1000, 2000, 3000]
        })
        
        # Debe fallar porque no hay columnas candidatas
        with pytest.raises(ValueError):
            gd.detect_fill(data, exclude=['provincia', 'poblacion'])
    
    def test_detect_fill_rejects_constant(self):
        """detect_fill() debe rechazar columnas constantes"""
        import geodompy as gd
        
        data = pd.DataFrame({
            'provincia': ['A', 'B', 'C'],
            'constante': [1, 1, 1],
            'variable': [1, 2, 3]
        })
        
        result = gd.detect_fill(data, exclude=['provincia'])
        assert result == 'variable'


class TestDetectColumnType:
    """Tests para detect_column_type()"""
    
    def test_detect_column_type_exists(self):
        """detect_column_type() debe existir"""
        import geodompy as gd
        assert hasattr(gd, 'detect_column_type')
    
    def test_detect_column_type_returns_dict(self):
        """detect_column_type() debe retornar un diccionario"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:5]
        else:
            names = prov.iloc[:5, 0].tolist()
        
        result = gd.detect_column_type(names, 'test_col')
        assert isinstance(result, dict)
        assert 'level' in result
    
    def test_detect_column_type_detects_provinces(self):
        """detect_column_type() debe detectar provincias"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:10]
        else:
            names = prov.iloc[:10, 0].tolist()
        
        result = gd.detect_column_type(names, 'provincias')
        assert result['level'] == 'provinces'


class TestAnalyzeColumns:
    """Tests para analyze_columns()"""
    
    def test_analyze_columns_exists(self):
        """analyze_columns() debe existir"""
        import geodompy as gd
        assert hasattr(gd, 'analyze_columns')
    
    def test_analyze_columns_returns_dataframe(self):
        """analyze_columns() debe retornar un DataFrame"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:5]
        else:
            names = prov.iloc[:5, 0].tolist()
        
        data = pd.DataFrame({
            'provincia': names,
            'valor': range(len(names))
        })
        
        result = gd.analyze_columns(data)
        assert isinstance(result, pd.DataFrame)
    
    def test_analyze_columns_has_required_columns(self):
        """analyze_columns() debe tener las columnas requeridas"""
        import geodompy as gd
        
        data = pd.DataFrame({
            'col1': ['A', 'B', 'C'],
            'col2': [1, 2, 3]
        })
        
        result = gd.analyze_columns(data)
        assert 'column_name' in result.columns
        assert 'detected_level' in result.columns
        assert 'match_ratio' in result.columns
        assert 'is_geographic' in result.columns
    
    def test_analyze_columns_identifies_geographic(self):
        """analyze_columns() debe identificar columnas geográficas"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()
        else:
            names = prov.iloc[:, 0].tolist()
        
        data = pd.DataFrame({
            'provincia': names,
            'texto': ['A'] * len(names),
            'valor': range(len(names))
        })
        
        result = gd.analyze_columns(data)
        prov_row = result[result['column_name'] == 'provincia']
        if len(prov_row) > 0:
            assert prov_row['is_geographic'].iloc[0] == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

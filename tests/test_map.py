"""
Tests para las funciones de mapeo de geodompy
"""

import pytest
import pandas as pd
import geopandas as gpd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


class TestMapData:
    """Tests para map_data()"""
    
    def test_map_data_returns_geodataframe(self):
        """map_data() debe retornar un GeoDataFrame"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:5]
        else:
            names = prov.iloc[:5, 0].tolist()
        
        data = pd.DataFrame({
            'provincia': names,
            'poblacion': [1000, 2000, 3000, 4000, 5000]
        })
        
        result = gd.map_data(data)
        # El resultado debe tener columna geometry (es geodataframe)
        assert 'geometry' in result.columns
    
    def test_map_data_has_geometry(self):
        """map_data() debe tener columna geometry"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:3]
        else:
            names = prov.iloc[:3, 0].tolist()
        
        data = pd.DataFrame({
            'provincia': names,
            'valor': [1, 2, 3]
        })
        
        result = gd.map_data(data)
        assert 'geometry' in result.columns
    
    def test_map_data_with_explicit_fill(self):
        """map_data() con fill explícito"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:3]
        else:
            names = prov.iloc[:3, 0].tolist()
        
        data = pd.DataFrame({
            'provincia': names,
            'poblacion': [1, 2, 3],
            'area': [100, 200, 300]
        })
        
        result = gd.map_data(data, fill='area')
        assert result.attrs.get('fill_var') == 'area'
    
    def test_map_data_merges_data(self):
        """map_data() debe hacer merge correctamente"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:3]
        else:
            names = prov.iloc[:3, 0].tolist()
        
        data = pd.DataFrame({
            'provincia': names,
            'custom_column': ['A', 'B', 'C']
        })
        
        result = gd.map_data(data)
        assert 'custom_column' in result.columns


class TestMap:
    """Tests para map()"""
    
    def test_map_returns_figure(self):
        """map() debe retornar una Figure"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:5]
        else:
            names = prov.iloc[:5, 0].tolist()
        
        data = pd.DataFrame({
            'provincia': names,
            'poblacion': [1000, 2000, 3000, 4000, 5000]
        })
        
        result = gd.map(data)
        assert isinstance(result, plt.Figure)
        plt.close('all')
    
    def test_map_with_custom_cmap(self):
        """map() acepta cmap personalizado"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:3]
        else:
            names = prov.iloc[:3, 0].tolist()
        
        data = pd.DataFrame({
            'provincia': names,
            'valor': [1, 2, 3]
        })
        
        # No debe lanzar excepción
        result = gd.map(data, cmap='plasma')
        assert isinstance(result, plt.Figure)
        plt.close('all')
    
    def test_map_with_title(self):
        """map() acepta título"""
        import geodompy as gd
        
        prov = gd.provinces(sf=False)
        if 'TOPONIMIA' in prov.columns:
            names = prov['TOPONIMIA'].tolist()[:3]
        else:
            names = prov.iloc[:3, 0].tolist()
        
        data = pd.DataFrame({
            'provincia': names,
            'valor': [1, 2, 3]
        })
        
        result = gd.map(data, title='Test Map')
        assert isinstance(result, plt.Figure)
        plt.close('all')

    def test_map_with_labels_true(self):
        """map() acepta labels=True"""
        import geodompy as gd

        prov = gd.provinces(sf=False)
        names = prov['TOPONIMIA'].tolist()[:3]
        data = pd.DataFrame({'provincia': names, 'valor': [1, 2, 3]})

        result = gd.map(data, labels=True, legend=False)
        assert isinstance(result, plt.Figure)
        plt.close('all')

    def test_map_with_new_text_and_label_options(self):
        """map() acepta subtitle, caption y labels compatibles con JS"""
        import geodompy as gd

        prov = gd.provinces(sf=False)
        data = pd.DataFrame({
            'provincia': prov['TOPONIMIA'].tolist()[:3],
            'valor': [1, 2, 3],
        })

        result = gd.map(
            data,
            fill='valor',
            labels='both',
            title='Titulo',
            subtitle='Subtitulo',
            caption='Fuente: GeoDOM',
            legend=False,
        )
        assert isinstance(result, plt.Figure)
        assert result._suptitle is not None
        assert result._suptitle.get_text() == 'Subtitulo'
        assert any(text.get_text() == 'Fuente: GeoDOM' for text in result.texts)
        plt.close('all')

    def test_gd_map_alias_returns_figure(self):
        """gd_map es alias funcional de map()"""
        import geodompy as gd

        prov = gd.provinces(sf=False)
        data = pd.DataFrame({
            'provincia': prov['TOPONIMIA'].tolist()[:3],
            'valor': [1, 2, 3],
        })

        result = gd.gd_map(data, legend=False)
        assert isinstance(result, plt.Figure)
        plt.close('all')

    def test_gd_geom_sf_returns_axes(self):
        """gd_geom_sf agrega una capa Matplotlib y retorna Axes"""
        import geodompy as gd

        prov = gd.provinces(sf=False)
        data = pd.DataFrame({
            'provincia': prov['TOPONIMIA'].tolist()[:3],
            'valor': [1, 2, 3],
        })

        ax = gd.gd_geom_sf(data, legend=False)
        assert ax is not None
        plt.close('all')


class TestMapWithDifferentLevels:
    """Tests para map() con diferentes niveles administrativos"""
    
    def test_map_regions(self):
        """map() con datos de regiones"""
        import geodompy as gd
        
        reg = gd.regions(sf=False)
        if 'TOPONIMIA' in reg.columns:
            names = reg['TOPONIMIA'].tolist()[:5]
        else:
            names = reg.iloc[:5, 0].tolist()
        
        data = pd.DataFrame({
            'region': names,
            'valor': range(len(names))
        })
        
        result = gd.map(data)
        assert isinstance(result, plt.Figure)
        plt.close('all')

    def test_map_data_bparajes(self):
        """map_data() funciona con barrios/parajes"""
        import geodompy as gd

        bp = gd.bparajes(sf=False).head(1)
        data = pd.DataFrame({
            'barrio': bp['TOPONIMIA'].tolist(),
            'valor': [1],
        })

        result = gd.map_data(
            data,
            fill='valor',
            level='bparajes',
            name='barrio',
            key='TOPONIMIA',
        )
        assert 'geometry' in result.columns
        assert result.attrs.get('geo_level') == 'bparajes'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

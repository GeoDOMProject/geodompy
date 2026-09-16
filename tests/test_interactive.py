import importlib
import json
import base64, gzip
import re
import geopandas as gpd
import pandas as pd
import pytest
from shapely.geometry import Polygon
from geodompy import map_interactive, InteractiveMap

module = importlib.import_module('geodompy.interactive')

@pytest.fixture
def prepared(monkeypatch):
    frame = gpd.GeoDataFrame({'PROV_CODE':['01','02'], 'TOPONIMIA':['Azua','Bahoruco'], 'value':[0,None]}, geometry=[Polygon([(-70,18),(-69,18),(-69,19),(-70,18)])]*2, crs=4326)
    frame.attrs.update(geo_level='provinces',fill_var='value')
    monkeypatch.setattr(module, 'map_data', lambda *args,**kwargs:frame)
    monkeypatch.setattr(module, 'municipalities', lambda:frame.drop(columns=['value']).assign(MUN_CODE=['0101','0201']).to_crs(32619))
    return frame

def test_portable_html_encodes_data_safely_and_saves(prepared,tmp_path):
    danger='</script><script>alert(1)</script>'
    prepared.loc[0,'TOPONIMIA']=danger
    path=tmp_path/'mapa.html'
    document=map_interactive(pd.DataFrame(),title=danger,file=path)
    assert isinstance(document,InteractiveMap)
    assert path.read_text(encoding='utf-8')==document
    assert danger not in document
    assert not re.search(r'<script[^>]+src=',document)
    payload=json.loads(gzip.decompress(base64.b64decode(re.search(r'data-encoding="gzip">(.*?)</script>',document,re.S)[1])))
    assert payload['layers'][0]['geojson']['features'][0]['properties']['TOPONIMIA']==danger
    assert payload['layers'][0]['geojson']['features'][0]['properties']['value']==0
    assert payload['layers'][0]['geojson']['features'][1]['properties']['value'] is None
    context=payload['layers'][1]
    assert context['measured'] is False
    assert all('value' not in f['properties'] for f in context['geojson']['features'])
    assert -71<context['geojson']['features'][0]['geometry']['coordinates'][0][0][0]<-68
    assert 'sandbox="allow-scripts"' in document._repr_html_()

def test_context_can_be_excluded(prepared):
    document=map_interactive(pd.DataFrame(),context=False)
    payload=json.loads(gzip.decompress(base64.b64decode(re.search(r'data-encoding="gzip">(.*?)</script>',document,re.S)[1])))
    assert len(payload['layers'])==1

def test_unknown_crs_and_empty_geometries_rejected(prepared):
    prepared.set_crs(None, allow_override=True, inplace=True)
    with pytest.raises(ValueError,match='referencia'):
        map_interactive(pd.DataFrame())

def test_invalid_options_rejected():
    with pytest.raises(ValueError,match='background'):
        map_interactive(pd.DataFrame(),background='unknown')

def test_palette_category_colors_and_background_are_portable(prepared):
    prepared['group']=['A','B']
    prepared.attrs['fill_var']='group'
    document=map_interactive(
        pd.DataFrame(), context=False, palette='set2', colors={'B':'#ff0000'},
        domain=['B','A'], missing='#123456', background_color='#334455'
    )
    payload=json.loads(gzip.decompress(base64.b64decode(re.search(r'data-encoding="gzip">(.*?)</script>',document,re.S)[1])))
    assert payload['options']['domain']==['B','A']
    assert payload['options']['colors']['B']=='#ff0000'
    assert payload['options']['missing']=='#123456'
    assert payload['options']['backgroundColor']=='#334455'
    assert len(payload['options']['palette'])>=1

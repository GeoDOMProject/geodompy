"""
Tests para add_parent_cols().
"""

import pandas as pd


def test_add_parent_cols_provinces_adds_region():
    import geodompy as gd

    prov = gd.provinces(sf=False).iloc[0]
    data = pd.DataFrame({"provincia": [prov["TOPONIMIA"]], "valor": [1]})

    result = gd.add_parent_cols(data, levels=["regions"])

    assert "Region" in result.columns
    assert result["Region"].notna().all()


def test_add_parent_cols_municipalities_adds_province_and_region():
    import geodompy as gd

    mun = gd.municipalities(sf=False).iloc[0]
    data = pd.DataFrame({"municipio": [mun["TOPONIMIA"]], "valor": [1]})

    result = gd.add_parent_cols(data, levels=["regions", "provinces"])

    assert "Region" in result.columns
    assert "Provincia" in result.columns


def test_add_parent_cols_dm_adds_municipality():
    import geodompy as gd

    dm_row = gd.dm(sf=False).iloc[0]
    data = pd.DataFrame({"dm": [dm_row["TOPONIMIA"]], "valor": [1]})

    result = gd.add_parent_cols(
        data,
        levels=["municipalities"],
        level="dm",
        name="dm",
        key="TOPONIMIA",
    )

    assert "Municipio" in result.columns


def test_add_parent_cols_sections_adds_dm():
    import geodompy as gd

    sec = gd.sections(sf=False).iloc[0]
    data = pd.DataFrame({"seccion": [sec["TOPONIMIA"]], "valor": [1]})

    result = gd.add_parent_cols(data, levels=["dm"])

    assert "Distrito_Municipal" in result.columns


def test_add_parent_cols_bparajes_adds_section():
    import geodompy as gd

    bp = gd.bparajes(sf=False).iloc[0]
    data = pd.DataFrame({"barrio": [bp["TOPONIMIA"]], "valor": [1]})

    result = gd.add_parent_cols(data, levels=["sections"])

    assert "Seccion" in result.columns


def test_gd_add_parent_cols_alias():
    import geodompy as gd

    prov = gd.provinces(sf=False).iloc[0]
    data = pd.DataFrame({"provincia": [prov["TOPONIMIA"]], "valor": [1]})

    result = gd.gd_add_parent_cols(data, levels=["regions"])

    assert "Region" in result.columns

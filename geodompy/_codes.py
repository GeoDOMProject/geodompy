"""Canonical territorial codes retain leading zeros and all parent components."""
import pandas as pd
import geopandas as gpd

CODE_PARTS = {
    "REG_CODE": ["CODREG"], "PROV_CODE": ["PROV"],
    "MUN_CODE": ["PROV", "MUN"], "DM_CODE": ["PROV", "MUN", "DM"],
    "SEC_CODE": ["PROV", "MUN", "DM", "SEC"],
    "BP_CODE": ["PROV", "MUN", "DM", "SEC", "BP"],
}

def code(value, width):
    if pd.isna(value):
        return None
    text = str(value).removesuffix(".0")
    return text.zfill(width) if text.isdigit() else text

def add_codes(frame):
    frame = frame.copy()
    if "SEC" not in frame and "SECC" in frame:
        frame["SEC"] = frame["SECC"]
    if "CODREG" not in frame and "REG" in frame:
        frame["CODREG"] = frame["REG"]
    for key, parts in CODE_PARTS.items():
        width = 11 if key == "BP_CODE" else 2 * len(parts)
        if key in frame:
            frame[key] = frame[key].map(lambda value: code(value, width))
        elif all(part in frame for part in parts):
            values = [frame[part].map(lambda value: code(value, 3 if part == "BP" else 2)) for part in parts]
            frame[key] = pd.concat(values, axis=1).apply(lambda row: "".join(row) if row.notna().all() else None, axis=1)
    return frame

def restore_crs(frame, data_id):
    # RD_MUN158 matches the EPSG:32619 geometry shipped in sfDR.
    source_crs = {"RD_PROV": 4326, "RD_RUP": 4326, "RD_DM": 4326,
                  "RD_SECCIONES": 4326, "RD_BPARAJES": 4326, "RD_MUN158": 32619}
    if frame.crs is None and data_id in source_crs:
        frame = frame.set_crs(source_crs[data_id])
    return frame.to_crs(4326) if frame.crs is not None else frame

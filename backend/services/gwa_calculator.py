"""
GWA Calculator Auto-Fill — deterministic port of extracted_skills/gwa-autofill/SKILL.md

Computes INPUTS sheet cells (C14-C38) for the Level 1 GWA Yield Calculator from the
standard Nova Scotia site data files, plus the zoning-vs-groundwater-recharge dual
constraint check.
"""
import io
import math
from typing import Optional

import numpy as np
import pandas as pd
import xlrd

NULL_SENTINEL = -9999

COUNTY_STATION = {
    "COLCHESTER": "DEBERT",
    "CUMBERLAND": "NAPPAN",
    "HALIFAX": "HALIFAX STANFIELD (AIRPORT)",
    "HANTS": "UPPER STEWIACKE",
    "KINGS": "WATERVILLE CAMBRIDGE",
    "ANNAPOLIS": "GREENWOOD",
    "DIGBY": "GREENWOOD",
    "YARMOUTH": "YARMOUTH",
    "SHELBURNE": "YARMOUTH",
    "QUEENS": "KEJIMKUJIK",
    "LUNENBURG": "BRIDGEWATER",
    "PICTOU": "COLLEGEVILLE",
    "ANTIGONISH": "COLLEGEVILLE",
    "GUYSBOROUGH": "UPPER STEWIACKE",
    "RICHMOND": "SYDNEY",
    "INVERNESS": "CHETICAMP",
    "VICTORIA": "INGONISH BEACH",
    "CAPE BRETON": "SYDNEY",
}

RECHARGE_DEFAULTS = {
    "FU-WO": (0.18, 0.22),
    "FU-BL": (0.18, 0.22),
    "WI": (0.15, 0.20),
    "HO": (0.15, 0.20),
    "ME": (0.10, 0.18),
    "GR": (0.08, 0.15),
    "CB": (0.14, 0.20),
    "PE": (0.12, 0.18),
    "OVERBURDEN": (0.25, 0.40),
}

GCDWQ_THRESHOLDS = {
    "As_ugL": (10, "MAC", "Arsenic"),
    "U_ugL": (20, "MAC", "Uranium"),
    "Fe_ugL": (300, "AO", "Iron"),
    "Mn_ugL": (120, "AO", "Manganese"),
    "NO3NO2NmgL": (10, "MAC", "Nitrate+Nitrite (as N)"),
    "Na_mgL": (200, "AO", "Sodium"),
    "Cl_mgL": (250, "AO", "Chloride"),
    "TDS_mgL": (500, "AO", "TDS"),
}

NS_MIN_DEMAND_M3D = 1.35  # m3/day per lot


def _clean_numeric(series: pd.Series) -> pd.Series:
    s = pd.to_numeric(series, errors="coerce")
    return s.where(s != NULL_SENTINEL)


def process_well_logs(raw: bytes, site_elev_avg: Optional[float]) -> dict:
    df = pd.read_csv(io.BytesIO(raw))
    df.columns = [c.strip() for c in df.columns]
    flags = []

    if "WATERUSE" in df.columns:
        df = df[df["WATERUSE"].astype(str).str.contains("Domestic|Public", case=False, na=False)]
    else:
        flags.append("WATERUSE column not found — no domestic/public filter applied")

    for col in ["DEPTH", "CASING", "BEDROCK", "STATIC", "YIELD_LPM", "ELEVATION"]:
        if col in df.columns:
            df[col] = _clean_numeric(df[col])

    n_wells = len(df)
    avg_depth = float(df["DEPTH"].median()) if "DEPTH" in df.columns and df["DEPTH"].notna().any() else None
    avg_casing = float(df["CASING"].median()) if "CASING" in df.columns and df["CASING"].notna().any() else None

    static_wl = None
    elevation_matched = False
    if "STATIC" in df.columns:
        wl_static = df[df["STATIC"] > 0]
        if len(wl_static) == 0 and df["STATIC"].notna().any():
            flags.append("All STATIC values negative (artesian) — used absolute values")
            wl_static = df.copy()
            wl_static["STATIC"] = wl_static["STATIC"].abs()

        site_elev = site_elev_avg
        if site_elev is None and "ELEVATION" in df.columns:
            site_elev = df["ELEVATION"].median()

        if site_elev is not None and "ELEVATION" in wl_static.columns:
            elev_match = wl_static[(wl_static["ELEVATION"] - site_elev).abs() <= 10]
            if len(elev_match) >= 3:
                static_wl = float(elev_match["STATIC"].median())
                elevation_matched = True
        if static_wl is None and wl_static["STATIC"].notna().any():
            static_wl = float(wl_static["STATIC"].median())

    if static_wl is None:
        static_wl = 4.0
        flags.append("STATIC all null — defaulted to 4.0 m; flag as assumed")

    if n_wells < 3:
        flags.append(f"Only {n_wells} matching wells found — low confidence")

    county = None
    if "COUNTY" in df.columns and df["COUNTY"].notna().any():
        county = str(df["COUNTY"].mode().iloc[0])

    return {
        "n_wells": n_wells,
        "C14_well_depth": round(avg_depth, 2) if avg_depth is not None else None,
        "C15_casing_length": round(avg_casing, 2) if avg_casing is not None else None,
        "C16_well_diameter": 0.15,
        "C23_static_wl": round(static_wl, 2),
        "elevation_matched": elevation_matched,
        "county_detected": county,
        "flags": flags,
    }


def process_pumping_tests(raw: bytes, site_hu: Optional[str]) -> dict:
    df = pd.read_csv(io.BytesIO(raw))
    df.columns = [c.strip() for c in df.columns]
    flags = []

    for col in ["K_md", "Tapp_m2d", "SC_m2d", "Q20_m3d", "Static_m", "Depth_m", "Storativit"]:
        if col in df.columns:
            df[col] = _clean_numeric(df[col])

    hu_used = site_hu
    if "Geology_HU" in df.columns:
        if site_hu:
            df_hu = df[df["Geology_HU"].astype(str).str.upper() == site_hu.upper()]
        else:
            df_hu = df
            hu_used = None
        if len(df_hu) == 0:
            flags.append(f"No pumping tests found for HU={site_hu} — using full dataset as fallback")
            df_hu = df
    else:
        df_hu = df
        flags.append("Geology_HU column not found — formation filter not applied")

    n_tests = len(df_hu)
    K_valid = df_hu["K_md"].dropna() if "K_md" in df_hu.columns else pd.Series(dtype=float)

    K_opt = K_avg = K_pess = None
    if len(K_valid) > 0:
        K_opt = float(K_valid.quantile(0.90))
        K_avg = float(K_valid.median())
        K_pess = float(K_valid.quantile(0.10))
    else:
        flags.append("K_md all null for site HU — derive from T/depth or use HU_LOOKUP defaults")
        if "Tapp_m2d" in df_hu.columns and "Depth_m" in df_hu.columns:
            t_med = df_hu["Tapp_m2d"].median()
            depth_med = df_hu["Depth_m"].median()
            if pd.notna(t_med) and pd.notna(depth_med) and depth_med > 0:
                K_avg = float(t_med / depth_med)
                K_opt = K_avg * 1.3
                K_pess = K_avg * 0.7
                flags.append("K derived from T_avg / median well depth (fallback)")

    storativity = 0.000482
    if "Storativit" in df_hu.columns:
        stor = df_hu["Storativit"].dropna()
        stor = stor[(stor > 0) & (stor < 1)]
        if len(stor) > 0:
            storativity = float(stor.mean())
        else:
            flags.append("Storativity not measured — defaulted to 0.000482")

    if n_tests < 3:
        flags.append(f"Only {n_tests} pumping tests available — low confidence")

    return {
        "n_tests": n_tests,
        "hu_used": hu_used,
        "C24_K_optimistic": round(K_opt, 4) if K_opt is not None else None,
        "C25_K_average": round(K_avg, 4) if K_avg is not None else None,
        "C26_K_pessimistic": round(K_pess, 4) if K_pess is not None else None,
        "C27_storativity": round(storativity, 6),
        "flags": flags,
    }


def process_observation_well(raw: bytes) -> dict:
    flags = []
    raw_wb = xlrd.open_workbook(file_contents=raw)

    sheet_name = "Water Levels - continuous"
    if sheet_name not in raw_wb.sheet_names():
        sheet_name = raw_wb.sheet_names()[0]
        flags.append(f'Sheet "Water Levels - continuous" not found — used first sheet "{sheet_name}"')

    sh = raw_wb.sheet_by_name(sheet_name)

    well_name = None
    toc_elev = None
    try:
        well_name = str(sh.cell_value(1, 0)).split(":")[-1].strip()
    except Exception:
        pass
    try:
        toc_elev = float(str(sh.cell_value(3, 0)).split(":")[-1].strip())
    except Exception:
        flags.append("Could not parse Top of Casing Elevation from row 3")

    dates, levels = [], []
    for r in range(10, sh.nrows):
        try:
            date_val = sh.cell_value(r, 0)
            wl_val = sh.cell_value(r, 1)
            if wl_val in ("", None):
                continue
            dates.append(date_val)
            levels.append(float(wl_val))
        except Exception:
            continue

    if not levels:
        flags.append("No continuous water level readings parsed")
        return {
            "well_name": well_name,
            "toc_elevation": toc_elev,
            "C18_seasonal_fluctuation": None,
            "flags": flags,
        }

    levels = np.array(levels, dtype=float)
    seasonal_fluct = float(np.nanmax(levels) - np.nanmin(levels))

    return {
        "well_name": well_name,
        "toc_elevation": toc_elev,
        "n_readings": len(levels),
        "C18_seasonal_fluctuation": round(seasonal_fluct, 2),
        "wl_max": round(float(np.nanmax(levels)), 2),
        "wl_min": round(float(np.nanmin(levels)), 2),
        "flags": flags,
    }


def process_climate_normals(raw: bytes, county: str) -> dict:
    flags = []
    df = pd.read_csv(io.BytesIO(raw))
    df.columns = [c.strip() for c in df.columns]

    station = COUNTY_STATION.get(county.upper().strip()) if county else None
    if not station:
        available = sorted(set(COUNTY_STATION.values()))
        flags.append(f"County '{county}' not in lookup map. Available stations: {', '.join(available)}")
        return {"county": county, "station": None, "C33_precipitation_mm": None, "flags": flags}

    match = df[
        (df.get("LOCATION_NAME", pd.Series(dtype=str)).astype(str).str.upper() == station.upper())
        & (df.get("NORMALS_ELEMENT", pd.Series(dtype=str)).astype(str).str.contains("Precipitation", case=False, na=False))
    ]

    precip = None
    if len(match) > 0 and "Year" in match.columns:
        precip = pd.to_numeric(match.iloc[0]["Year"], errors="coerce")
        precip = float(precip) if pd.notna(precip) else None
    else:
        flags.append(f"Station '{station}' / Precipitation row not found in climate normals file")

    return {
        "county": county,
        "station": station,
        "C33_precipitation_mm": round(precip, 1) if precip is not None else None,
        "flags": flags,
    }


def process_water_chemistry(raw: bytes) -> dict:
    df = pd.read_csv(io.BytesIO(raw))
    df.columns = [c.strip() for c in df.columns]

    rows = []
    for col, (limit, kind, label) in GCDWQ_THRESHOLDS.items():
        if col not in df.columns:
            continue
        series = _clean_numeric(df[col]).dropna()
        if len(series) == 0:
            continue
        n_exceed = int((series > limit).sum())
        rows.append({
            "parameter": label,
            "column": col,
            "type": kind,
            "limit": limit,
            "n_samples": int(len(series)),
            "n_exceeding": n_exceed,
            "min": round(float(series.min()), 3),
            "max": round(float(series.max()), 3),
            "status": "EXCEEDANCE" if n_exceed > 0 else "OK",
        })

    if "pH" in df.columns:
        ph = _clean_numeric(df["pH"]).dropna()
        if len(ph) > 0:
            n_exceed = int(((ph < 6.5) | (ph > 8.5)).sum())
            rows.append({
                "parameter": "pH",
                "column": "pH",
                "type": "AO",
                "limit": "6.5-8.5",
                "n_samples": int(len(ph)),
                "n_exceeding": n_exceed,
                "min": round(float(ph.min()), 2),
                "max": round(float(ph.max()), 2),
                "status": "EXCEEDANCE" if n_exceed > 0 else "OK",
            })

    return {"rows": rows}


def compute_dual_constraint(
    site_area_m2: float,
    min_lot_area_m2: float,
    infra_deduction_pct: float,
    wet_exclusion_pct: float,
    precip_mm_y: Optional[float],
    recharge_low_m_y: float,
    recharge_high_m_y: float,
) -> dict:
    gross_lots = math.floor(site_area_m2 / min_lot_area_m2) if min_lot_area_m2 else None

    infra_area = site_area_m2 * infra_deduction_pct
    wet_area = site_area_m2 * wet_exclusion_pct
    net_area = site_area_m2 - infra_area - wet_area
    net_lots_zoning = math.floor(net_area / min_lot_area_m2) if min_lot_area_m2 else None

    daily_recharge_low = daily_recharge_high = None
    net_lots_gw_low = net_lots_gw_high = None
    if precip_mm_y is not None:
        annual_recharge_low_m3 = net_area * recharge_low_m_y
        annual_recharge_high_m3 = net_area * recharge_high_m_y
        daily_recharge_low = annual_recharge_low_m3 / 365
        daily_recharge_high = annual_recharge_high_m3 / 365
        net_lots_gw_low = math.floor(daily_recharge_low / NS_MIN_DEMAND_M3D)
        net_lots_gw_high = math.floor(daily_recharge_high / NS_MIN_DEMAND_M3D)

    def binding(zoning, gw):
        if zoning is None or gw is None:
            return None, None
        n = min(zoning, gw)
        by = "GW recharge" if gw < zoning else "Zoning area"
        return n, by

    binding_conservative, by_conservative = binding(net_lots_zoning, net_lots_gw_low)
    binding_optimistic, by_optimistic = binding(net_lots_zoning, net_lots_gw_high)

    avg_lot_size_m2 = avg_lot_size_acres = None
    if binding_conservative:
        avg_lot_size_m2 = net_area / binding_conservative
        avg_lot_size_acres = avg_lot_size_m2 / 4047

    level2_notes = []
    zoning_already_binding = (
        net_lots_zoning is not None and net_lots_gw_high is not None and net_lots_zoning <= net_lots_gw_high
    )
    if (
        not zoning_already_binding
        and net_lots_gw_high is not None
        and net_lots_gw_low is not None
        and net_lots_gw_low > 0
        and net_lots_gw_high > 1.5 * net_lots_gw_low
    ):
        level2_notes.append("Optimistic GW lot count exceeds 1.5x conservative — Level 2 GWA may be warranted")
    if zoning_already_binding:
        level2_notes.append("Zoning area is already more restrictive than optimistic GW count — a Level 2 GWA will not unlock additional lots")

    return {
        "gross_lots_capacity": gross_lots,
        "net_buildable_area_m2": round(net_area, 1),
        "net_lots_zoning": net_lots_zoning,
        "daily_recharge_low_m3d": round(daily_recharge_low, 2) if daily_recharge_low is not None else None,
        "daily_recharge_high_m3d": round(daily_recharge_high, 2) if daily_recharge_high is not None else None,
        "net_lots_gw_low": net_lots_gw_low,
        "net_lots_gw_high": net_lots_gw_high,
        "binding_conservative": binding_conservative,
        "binding_conservative_by": by_conservative,
        "binding_optimistic": binding_optimistic,
        "binding_optimistic_by": by_optimistic,
        "avg_lot_size_m2": round(avg_lot_size_m2, 1) if avg_lot_size_m2 else None,
        "avg_lot_size_acres": round(avg_lot_size_acres, 3) if avg_lot_size_acres else None,
        "level2_gwa_notes": level2_notes,
    }

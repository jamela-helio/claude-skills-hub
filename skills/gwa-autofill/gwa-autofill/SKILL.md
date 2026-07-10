---
name: gwa-autofill
description: >
  Automatically extract and compute inputs for the Level 1 GWA Yield Calculator
  from standard Nova Scotia data files. Use when the user uploads any combination
  of Well_logs.csv, Pumping_tests.csv, Water_chemistry.csv, a NS Observation Well
  .xls file, or the 1991-2020 Climate Normals NS CSV — and asks to compute,
  fill in, or calculate inputs for the groundwater assessment calculator. Also
  trigger when the user provides site area, elevation, county, or lot count and
  wants to know what calculator cells those populate. Outputs a ready-to-enter
  table of INPUTS sheet cell values (C14–C38) with data quality flags and a
  water quality GCDWQ summary. Works for any Nova Scotia parcel — the CSV
  contents change per site, the extraction logic stays the same.
---

# GWA Calculator Auto-Fill Skill

## Purpose
Automatically extract and compute all inputs required by the Level 1 GWA Yield
Calculator (Level1_GWA_Calculator_v3.xlsx, INPUTS sheet) from the standard NS data
files uploaded for a site. Works for any parcel in Nova Scotia — the site changes, the
files change, the logic stays the same.

## When to Trigger
Trigger whenever the user uploads any combination of:
- Well_logs.csv — NS Well Logs Database export (pre-filtered to site)
- Pumping_tests.csv — NS Pumping Test Database export (regional formation data)
- Water_chemistry.csv — NS groundwater chemistry records (pre-filtered to site)
- Any WaterLevel*.xls — NS Observation Well data
- 1991-2020_Canadian_Climate_Normals_NS_Data.csv — NS Climate Normals bulk CSV
- And/or asks to compute / fill in / calculate inputs for the GWA calculator

---

## Pre-Filtering Assumption — CRITICAL

Well_logs.csv and Water_chemistry.csv are already spatially filtered to the site
boundary (typically 500 m from parcel edge) before being uploaded. Every row is
within scope. Do NOT apply any additional distance filter to these files.

Pumping_tests.csv is different. It contains regional formation data — the same
hydrogeological unit (HU), potentially 1–100 km away — because local pumping tests
rarely exist at the exact site. Apply a formation (HU) filter only, no distance cutoff.

---

## Step 0 — Identify Site Parameters First

Check conversation context for:
  1. Site area (m²)
  2. Ground elevation avg (masl)
  3. Ground elevation min (masl)
  4. County
  5. Bedrock formation name
  6. Dwelling units per lot (zoning)

If county not provided: wl['COUNTY'].mode()[0] from Well_logs.csv
If formation not provided: most common Geology_HU from Pumping_tests.csv

HU code decoder:
  FU-WO = Wolfville Formation (Fundy Group)
  FU-BL = Blomidon Formation (Fundy Group)
  HO    = Horton Group
  WI    = Windsor Group
  ME    = Meguma Group (Halifax / Goldenville)
  GR    = Granite / South Mountain Batholith
  CB    = North Mountain Basalt
  PE    = Pictou Group / Stellarton
  CA    = Carboniferous / Limestone

---

## Step 1 — Well Logs → C14, C15, C16, C23

File: Well_logs.csv
Null sentinel: -9999 (replace with NaN before any calculation)
Spatial filter: NONE (file is pre-filtered)

Cleaning rules:
  1. Keep WATERUSE containing 'Domestic' or 'Public' (case-insensitive)
     Excludes irrigation and industrial. Includes Domestic & Heat Pump, Public (not municipal).
  2. Replace -9999 with NaN in all numeric columns
  3. For STATIC: exclude negative values (artesian — should not be averaged in)

Code:
  wl = pd.read_csv("Well_logs.csv")
  wl = wl[wl['WATERUSE'].str.contains('Domestic|Public', na=False, case=False)]
  for col in ['DEPTH','CASING','BEDROCK','STATIC','YIELD_LPM','ELEVATION']:
      wl[col] = pd.to_numeric(wl[col], errors='coerce').where(lambda s: s != -9999)
  wl_static = wl[wl['STATIC'] > 0]

  avg_depth  = wl['DEPTH'].median()           → INPUTS C14
  avg_casing = wl['CASING'].median()          → INPUTS C15
  # C16 always 0.15 m (NS standard)

  # Static WL — prefer elevation-matched wells (±10 m of site elevation)
  site_elev = ground_elev_avg   # from user, or wl['ELEVATION'].median()
  elev_match = wl_static[abs(wl_static['ELEVATION'] - site_elev) <= 10]
  if len(elev_match) >= 3:
      static_wl = elev_match['STATIC'].median()   → INPUTS C23
  else:
      static_wl = wl_static['STATIC'].median()    → INPUTS C23

Outputs: C14 (depth), C15 (casing), C16 (0.15 fixed), C23 (static WL)
Report: n wells, min/max/median depth and casing, whether elevation-matching applied

---

## Step 2 — Pumping Tests → C24, C25, C26, C27

File: Pumping_tests.csv
Null sentinel: -9999
Spatial filter: NONE (regional export is already formation-relevant)
Formation filter: YES — keep only rows matching site Geology_HU

  for col in ['K_md','Tapp_m2d','SC_m2d','Q20_m3d','Static_m','Depth_m','Storativit']:
      pt[col] = pd.to_numeric(pt[col], errors='coerce').where(lambda s: s != -9999)

  pt_hu = pt[pt['Geology_HU'] == site_hu].copy()
  K_valid = pt_hu['K_md'].dropna()

  K_opt   = K_valid.quantile(0.90)   → INPUTS C24 (optimistic)
  K_avg   = K_valid.median()          → INPUTS C25 (average)
  K_pess  = K_valid.quantile(0.10)   → INPUTS C26 (pessimistic)

  stor = pt_hu['Storativit'].dropna()
  stor = stor[(stor > 0) & (stor < 1)]
  S = stor.mean() if len(stor) > 0 else 0.000482   → INPUTS C27

K scenario meanings:
  Optimistic  = 90th percentile K — best aquifer conditions
  Average     = median K — expected case, use for central estimate
  Pessimistic = 10th percentile K — worst case, use for regulatory compliance

If K_md all null: derive K = T_avg / median_well_depth from Tapp_m2d
If T also null: use HU_LOOKUP defaults from calculator; flag as low confidence

Outputs: C24, C25, C26, C27
Report: n tests, HU, S measured vs default, T from tests for cross-check

---

## Step 3 — Observation Well → C18

File: Any *WaterLevel*.xls
Engine: xlrd ONLY (openpyxl raises InvalidFileException on .xls)

File structure (all NS OW files are consistent):
  Row 0 (index 0): blank
  Row 1:  "Well Name: Murray Siding (007)"
  Row 2:  "Period Covered: 1967 - present"
  Row 3:  "Top of Casing Elevation (m, asl): 25.32"  ← parse float after ":"
  Rows 4-9: headers / blank
  Row 10+: date | WL elevation (masl) — two columns, no header

  import xlrd
  raw_wb = xlrd.open_workbook(ow_path)
  sh = raw_wb.sheet_by_name("Water Levels - continuous")
  toc_elev = float(sh.cell_value(3, 0).split(":")[-1].strip())

  df_ow = pd.read_excel(ow_path, engine="xlrd",
                         sheet_name="Water Levels - continuous",
                         skiprows=10, header=None, names=["date","wl_masl"])
  df_ow["date"]    = pd.to_datetime(df_ow["date"], errors="coerce")
  df_ow["wl_masl"] = pd.to_numeric(df_ow["wl_masl"], errors="coerce")
  df_ow = df_ow.dropna().sort_values("date")

  seasonal_fluct = df_ow["wl_masl"].max() - df_ow["wl_masl"].min()  → INPUTS C18

Which value to use:
  All-time record (max − min full dataset) = most conservative → use for regulatory submission
  Recent 10-yr fluctuation                 = context only
  Recent 5-yr fluctuation                  = modern climate trend only

Always use all-time record for C18. This matches 25-415 methodology exactly.

Outputs: C18
Report: OW name, date range, all-time max/min WL with dates, 10-yr and 5-yr context

---

## Step 4 — Climate Normals → C33

File: 1991-2020_Canadian_Climate_Normals_NS_Data.csv

COUNTY_STATION = {
    'COLCHESTER':   'DEBERT',
    'CUMBERLAND':   'NAPPAN',
    'HALIFAX':      'HALIFAX STANFIELD (AIRPORT)',
    'HANTS':        'UPPER STEWIACKE',
    'KINGS':        'WATERVILLE CAMBRIDGE',
    'ANNAPOLIS':    'GREENWOOD',
    'DIGBY':        'GREENWOOD',
    'YARMOUTH':     'YARMOUTH',
    'SHELBURNE':    'YARMOUTH',
    'QUEENS':       'KEJIMKUJIK',
    'LUNENBURG':    'BRIDGEWATER',
    'PICTOU':       'COLLEGEVILLE',
    'ANTIGONISH':   'COLLEGEVILLE',
    'GUYSBOROUGH':  'UPPER STEWIACKE',
    'RICHMOND':     'SYDNEY',
    'INVERNESS':    'CHETICAMP',
    'VICTORIA':     'INGONISH BEACH',
    'CAPE BRETON':  'SYDNEY',
}

  station = COUNTY_STATION.get(county.upper().strip())
  row = cl[(cl['LOCATION_NAME'] == station) &
           (cl['NORMALS_ELEMENT'] == 'Precipitation (mm)')]
  precip_mm_y = pd.to_numeric(row.iloc[0]['Year'], errors='coerce')  → INPUTS C33

CRITICAL WARNING for Colchester County:
  Do NOT use Halifax Stanfield (1,393.3 mm/y) for Colchester parcels.
  Correct station = Debert (1,178.5 mm/y).
  Using Halifax Stanfield overstates precipitation by ~18%.

Outputs: C33
Report: county, station matched, mm/year value

---

## Step 5 — Water Chemistry → Quality Summary (report only, not a calculator input)

File: Water_chemistry.csv
Null sentinel: -9999
Spatial filter: NONE (pre-filtered)

HC GCDWQ thresholds:
  As_ugL:     10  MAC  Arsenic
  U_ugL:      20  MAC  Uranium
  Fe_ugL:    300  AO   Iron
  Mn_ugL:    120  AO   Manganese
  NO3NO2NmgL: 10  MAC  Nitrate+Nitrite (as N)
  Na_mgL:    200  AO   Sodium
  Cl_mgL:    250  AO   Chloride
  TDS_mgL:   500  AO   TDS
  pH:    6.5-8.5  AO   (range, not single limit)

MAC = Maximum Acceptable Concentration (health-based — must not exceed)
AO  = Aesthetic Objective (taste/odour/appearance — treat if exceeded)

Report as a table: parameter | status | n samples | n exceeding | limit | min | max

---

## Step 6A — Zoning Area Constraint (parallel constraint, always compute alongside GW recharge)

CRITICAL: The GWA recharge calculation alone does not determine the maximum lot count.
Two constraints must both be computed and compared — the binding one (lower value) governs.

### Required inputs from user / conversation context:
  - site_area_m2        — gross parcel area (m²)
  - zone                — AP-3, R-1, R-2, etc. — ask user if not provided
  - municipality        — determines which LUB applies
  - infra_deduction_pct — % of site for roads, stormwater, open space (default 30%)
  - wet_exclusion_pct   — % excluded by DTW < 0.50 m from WAM mapping (default 0 if no WAM)

### NS Zoning Minimum Lot Area Lookup Table:
Always confirm with the applicable Land Use By-law. Common West Hants / NS values:

  Zone          | Municipality          | Min Lot Area (serviced) | Min Lot Area (unserviced) | Min Frontage
  ------------- | --------------------- | ----------------------- | ------------------------- | ------------
  AP / AR-3     | West Hants            | —                       | 4,000 m² (1 acre)         | 45 m
  AP-1 / AP-2  | West Hants            | —                       | 4,000 m² (1 acre)         | 45 m
  R-1           | HRM                   | 371 m²                  | consult LUB               | 12 m
  R-2           | HRM                   | 278 m² (semi)           | consult LUB               | 9 m
  RR (Rural Res)| Various NS munis      | —                       | 4,000–8,000 m²            | 30–60 m
  RC            | Various NS munis      | —                       | 2,000 m²                  | 30 m

  If zone is not in this table: ASK the user for the minimum lot area from their LUB.
  NEVER assume 40,000 sq ft (3,716 m²) — this is the old Imperial standard no longer
  universally applied. Always use the metric value from the current by-law.

### Calculation:

  # Step 1 — Gross physical lot capacity
  gross_lots = floor(site_area_m2 / min_lot_area_m2)

  # Step 2 — Net buildable area (after infrastructure and environmental deductions)
  infra_area   = site_area_m2 * infra_deduction_pct        # default 0.30
  wet_area     = site_area_m2 * wet_exclusion_pct           # from WAM DTW mapping
  road_area    = road_length_km * 10_000                    # 10 m wide, if known
  net_area     = site_area_m2 - infra_area - wet_area - road_area

  # Step 3 — Net zoning lot capacity
  net_lots_zoning = floor(net_area / min_lot_area_m2)

  # Step 4 — GW recharge lot capacity (from standard water balance)
  net_lots_gw_low  = floor(R_daily_low  / ns_min_demand)   # conservative
  net_lots_gw_high = floor(R_daily_high / ns_min_demand)   # optimistic

  # Step 5 — Binding constraint
  binding_conservative = min(net_lots_zoning, net_lots_gw_low)
  binding_optimistic   = min(net_lots_zoning, net_lots_gw_high)
  binding_constraint   = "GW recharge" if net_lots_gw_low < net_lots_zoning else "Zoning area"

### Output format — always present as a dual constraint table:

  | Scenario                        | Zoning Area Limit | GW Recharge Limit | BINDING | Constrained By  |
  | Conservative (low R)            | net_lots_zoning   | net_lots_gw_low   | min(^)  | GW or Zoning    |
  | Optimistic   (high R)           | net_lots_zoning   | net_lots_gw_high  | min(^)  | GW or Zoning    |

  Also report:
  - Gross physical capacity (site_area / min_lot_area) — theoretical max ignoring infra
  - Net zoning capacity (net_area / min_lot_area) — after 30% infra deduction
  - Average lot size at each binding limit: net_buildable_area / n_lots (m² and acres)
  - Note if GW recharge produces lots LARGER than the minimum — this means GW is binding
    and lots will be significantly larger than the zoning minimum (a positive planning outcome)

### Average lot size check:
  avg_lot_size_m2 = net_area / binding_lots
  avg_lot_size_acres = avg_lot_size_m2 / 4047

  If avg_lot_size_m2 > 2 × min_lot_area: note "groundwater constraint produces generously
  sized lots — well above the zoning minimum"
  If avg_lot_size_m2 < 1.1 × min_lot_area: flag "lots are near minimum size — verify that
  all required setbacks, well placement, and septic field can be accommodated"

### When zoning area IS the binding constraint (not GW recharge):
  This occurs on small parcels or dense zones (R-1, R-2) where the site cannot fit
  many lots physically. In this case:
  - Report the zoning limit as the governing maximum
  - Still compute GW recharge to confirm the aquifer can serve those lots
  - Note that the GW system has surplus capacity

### Level 2 GWA trigger:
  A Level 2 GWA is required when:
  1. The optimistic GW lot count (net_lots_gw_high) exceeds the conservative (net_lots_gw_low) AND
  2. The client wants to develop more lots than the conservative GW limit allows AND
  3. The optimistic count does not exceed the zoning area limit

  If zoning area is already more restrictive than the optimistic GW count, a Level 2 GWA
  will not unlock additional lots — inform the client and do NOT recommend it.

---

## Step 6 — Assemble and Present Results

Present in this order:

6a. Full inputs banner (see template below)
6b. Data quality flags for every step
6c. Water quality summary table
6d. Reminder that C28/C29 (recharge rates) come from HU_LOOKUP sheet in calculator
6e. Dual constraint table (Step 6A) — zoning area limit vs GW recharge limit, binding result
6f. Average lot size at binding lot count (m² and acres)
6g. Level 2 GWA trigger assessment — is it warranted given both constraints?

Banner template:
  SECTION B — Well Construction  [Well_logs.csv, n=XX wells]
    C14 Well depth            XX.X m
    C15 Casing length         XX.X m
    C16 Well diameter         0.15 m  (NS standard)
    C17 Seawater elevation    ← check NS ME 483 map
    C18 Seasonal fluctuation  X.XX m  (OW #XXX all-time YYYY–YYYY)
    C19 Head loss             1.0 m   (NS standard)

  SECTION C — Hydrogeology  [Pumping_tests.csv, n=XX tests, HU=XX]
    C23 Static WL             X.XX mbgs
    C24 K optimistic          X.XXXX m/d  (90th %ile)
    C25 K average             X.XXXX m/d  (median)
    C26 K pessimistic         X.XXXX m/d  (10th %ile)
    C27 Storativity S         0.XXXXXX  (measured/defaulted)
    C28 Recharge LOW          → see HU_LOOKUP sheet
    C29 Recharge HIGH         → see HU_LOOKUP sheet

  SECTION D — Water Demand  [Climate Normals CSV]
    C33 Annual precipitation  X,XXX.X mm/y  (STATION)
    C34 Persons/unit          3.675  (default)
    C35 Water/person          0.35 m³/d  (fixed)
    C36 NS minimum/unit       1.35 m³/d  (fixed)
    C37 Impermeable fraction  0.30  (NSECC default)
    C38 Euse                  0.50  (NSECC fixed)

  STILL NEEDED FROM USER:
    C5  Site area (m²)
    C6  Ground elevation avg (masl)
    C7  Ground elevation min (masl)
    C10 Dwelling units per lot
    C17 Seawater min elevation
    Zone / municipality          → required for Step 6A zoning area constraint
    Min lot area (m²)            → from applicable LUB; do NOT assume — ask if unsure
    WAM wet exclusion %          → from DTW mapping if available (default 0 if not provided)

---

## Error Handling

  All STATIC negative (artesian)    → use absolute values; note artesian condition
  STATIC all null                   → default 4.0 m; flag as assumed
  K_md all null for site HU         → derive from T / depth; else HU_LOOKUP defaults
  Fewer than 3 pumping tests        → use all available; flag low confidence
  OW file is .xlsx not .xls         → use openpyxl engine instead of xlrd
  OW sheet name differs             → try first sheet if "Water Levels - continuous" fails
  County not in COUNTY_STATION map  → list all available stations; ask user to select
  No water chemistry file           → skip Step 5; note chemistry needed for GWA report

---

## Python Dependencies

  pip install pandas openpyxl xlrd numpy --break-system-packages

  xlrd   = required for .xls observation well files
  openpyxl = required if OW file is .xlsx
  Never use openpyxl to read .xls — raises InvalidFileException

---

## Recharge Rate Defaults by Formation (for C28/C29 if user cannot confirm)

  FU-WO / FU-BL (Wolfville/Blomidon)  → 0.18 / 0.22 m/y
  WI / HO (Windsor/Horton)             → 0.15 / 0.20 m/y
  ME (Meguma/Halifax)                  → 0.10 / 0.18 m/y
  GR (Granite/Batholith)               → 0.08 / 0.15 m/y
  CB (North Mountain Basalt)           → 0.14 / 0.20 m/y
  PE (Pictou/Stellarton)               → 0.12 / 0.18 m/y
  Glaciofluvial overburden             → 0.25 / 0.40 m/y

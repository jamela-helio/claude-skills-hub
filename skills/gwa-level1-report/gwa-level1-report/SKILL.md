---
name: gwa-level1-report
description: >
  Produce a complete Level 1 Groundwater Assessment report as a Word document (.docx)
  for a Nova Scotia subdivision development, following NSECC guidelines (Guide to
  Groundwater Assessments for Subdivisions Serviced by Private Wells, 2011). Use when
  the user provides site data, well logs, pumping test results, water chemistry data,
  and/or outputs from the GWA calculator and asks to write, assemble, or draft a
  Level 1 GWA report. Also trigger when the user says "make the GWA report", "write
  up the report", "generate the groundwater assessment", or uploads GWA data and asks
  for a final report. Outputs a professionally structured .docx report suitable for
  municipal submission. Performs a live web search for site-specific NS references and
  comparable GWA reports before writing.
---

# Level 1 Groundwater Assessment Report — Nova Scotia

## Purpose
Produce a complete, submission-ready Level 1 Groundwater Assessment (GWA) report as a
Word document following Nova Scotia Environment and Climate Change (NSECC) guidelines.
The report supports subdivision applications where on-site wells and septic systems are
proposed and a municipal or provincial authority requires groundwater assessment.

## When to Trigger
- User asks to "write the GWA report", "make the Level 1 report", or "generate the groundwater assessment"
- User provides site data (area, lot count, geology) and asks for a final deliverable
- User has already run the gwa-autofill skill and now wants the report written up
- User uploads GWA calculator outputs, well logs, pumping tests, water chemistry results
- User asks to "put together the report" or "write it up like the Strum/Milford report"

---

## Step 0 — Live Reference Search (ALWAYS DO FIRST)

Before writing any section, search the web for two things:

### 0A — Formation-specific and county-specific NS GWA references

Search query patterns:
  `Nova Scotia Level 1 groundwater assessment [formation name OR county] subdivision PDF`
  `[formation name] aquifer Nova Scotia groundwater quality recommendations`
  `Kennedy 2010 Nova Scotia groundwater recharge [formation name]`

Try to find and fetch at least one comparable published NS Level 1 GWA report for the
same or similar formation. Use these NS sources as priority fetch targets:
  - https://www.easthants.ca/ (East Hants planning documents)
  - https://cdn.halifax.ca/ (HRM planning applications)
  - https://novascotia.ca/nse/groundwater/ (NSECC groundwater portal)
  - https://www.halifax.ca/ (HRM site for planning PDFs)

After fetching, note:
  1. What sections were included in the comparable report
  2. What recommendations were made (especially water quality treatment, Level 2 triggers)
  3. Any formation-specific issues flagged that match the current site's HU

### 0B — Regulatory references to verify before writing

Always fetch the current NSECC guide to confirm requirements have not changed:
  https://novascotia.ca/nse/groundwater/docs/Guide.to.Groundwater.Assessments.for.Subdivision.Developments.pdf

Also check NS Well Construction Regulations for current setback distances:
  https://novascotia.ca/just/regulations/regs/envwellc.htm

If formation raises water quality concerns, fetch the current Health Canada GCDWQ:
  https://www.canada.ca/en/health-canada/services/environmental-workplace-health/reports-publications/water-quality/guidelines-canadian-drinking-water-quality-summary-table.html

---

## Pre-Flight Checklist — Gather All Inputs Before Writing

Collect the following. Ask the user for any that are missing.
REQUIRED (★) before writing | STRONGLY RECOMMENDED (○) | INCLUDE IF AVAILABLE (△)

### A. Project Identification ★
- Project name / subdivision name
- Civic address and/or legal description (PID, lot, plan, county)
- Municipality (HRM, West Hants, East Hants, Lunenburg, Pictou, etc.)
- Applicant / client name and contact
- Prepared by: firm name, professional name, P.Eng. or P.Geo. licence number
- Report date

### B. Site Description ★
- Total site area (m² and ha / acres)
- Proposed lot count (number of lots)
- Proposed development type (single-family detached, mini-home, semi-detached, etc.)
- Proposed water supply method (individual lot wells / shared community well / TBD)
- Proposed sewage disposal (individual on-lot septic assumed for Level 1)
- Site location description (township, nearest town, road access)
- Adjacent land uses within 500 m (agricultural, residential, industrial, forested, landfill)
- Current and historical land use of the subject parcel (key for contamination risk)

### C. Hydrogeological Setting ○
- Bedrock formation name and HU code (ME, GR, CB, WI, HO, FU-WO, FU-BL, PE, CA)
- Surficial geology (till, sand/gravel, clay, bedrock outcrop) and estimated thickness
- Topographic description (flat, rolling, sloped; elevation range masl)
- Watershed / local catchment name
- Surface water features within 500 m (streams, lakes, wetlands — names, distances)
- Groundwater flow direction (if determinable from DEM/well log elevations)

### D. Well Log Data ★
- n wells within study area (domestic and public use only, within 500 m)
- Median and range: well depth (m bgs), casing length (m), static WL (m bgs), yield (lpm)
- Source: NS Well Logs Database (state search radius and record count)
- Note if artesian conditions observed (negative static levels)

### E. Pumping Test / Hydrogeological Parameters ○
- K optimistic / average / pessimistic (m/d) from NS Pumping Test Database
- Storativity S (measured or default)
- n tests used, HU filtered, formation match quality

### F. GWA Calculator Results ★
- Annual precipitation (mm/y) and climate station used
- Recharge rates low and high (m/y) from HU_LOOKUP
- Total available recharge: conservative and optimistic (m³/d)
- Maximum lots from GW recharge: conservative and optimistic
- Maximum lots from zoning area constraint
- Binding constraint and recommended lot count
- Average lot size at recommended count (m² and acres)

### G. Water Quality △
- n chemistry samples within study area
- Parameters with Health Canada GCDWQ exceedances
- Geogenic risk flags for the formation (see Section 6.2 below)
- Source: NS Water Chemistry Database (or submitted lab analysis)

### H. Site Visit Notes ○
- Date, personnel
- Site conditions, drainage, vegetation, surface water observed
- Neighbouring wells identified (locations, approximate depths)
- Potential contamination sources noted
- Photographs (reference figure numbers)

### I. Observation Well Data △
- OW station name and number
- All-time seasonal fluctuation (m) used for GWA Calculator input C18
- Period of record and distance from site

---

## Cross-Report Comparison — Structural Patterns from Published NS Reports

The following patterns were identified from reviewing multiple published Nova Scotia
Level 1 GWA reports (Milford Station 2024/HERAA, Westwood Hills 2022/ewC,
Sonny's Road 2024/WGSL, West Petpeswick 2025/DesignPoint) and the NSECC 2011 Guide.
Apply these to every report.

### Section Presence Across NS Practitioners

| Element | NSECC 2011 | Milford 2024 | Sonny's Road 2024 | Petpeswick 2025 | This Skill |
|---|---|---|---|---|---|
| Background / Introduction | Required | Section 1 | Section 1 | Section 1 | Section 1 |
| Site Description | Required | Section 2 | Section 1.1 | Section 1 | Section 2 |
| Historical land use review | Required | Section 4.1.2 | Section 1.2 | Section 4 | Section 4.1 |
| Geological Setting | Required | Section 5 | Section 4 | Section 3 | Section 4 |
| Hydrology / Watershed | Required | Section 6.1 | Section 2 | Section 2 | Section 3.2–3.3 |
| Well Log Data | Required | Section 6.3 | Section 5 | Section 5 | Section 5.1 |
| Aquifer Parameters (K, S, T) | Required | Section 6.2 + 6.3.2 | — | Section 5 | Section 5.2 |
| Aquifer Storage | Optional | Section 6.4 | — | — | Section 5.3 |
| Aquifer Recharge | Required | Section 6.5 | Section 6 | Section 6 | Section 5.4 |
| Safe Well Yield (Q20) | Required | Section 7.1 | — | — | Section 5.5 |
| Lot Water Balance | Required | Section 7.2 | Section 3 | Section 6 | Section 5.4 |
| Well Interference | Required | Section 7.3 | Section 8.1 | Section 7 | Section 5.6 |
| Withdrawal Approval Note | Context-dep | Section 7.4 | — | Exec Summary | Section 5.9 |
| Water Quality | Required | Section 8 | Section 7 | Section 5 | Section 6 |
| Seawater Intrusion | Coastal only | — | — | Exec Summary | Section 6.3 |
| Effects on Surface Water | Required | — | Section 8.2 | — | Section 5.7 |
| Septic Risk to Wells | Required | — | Section 8.3 | Noted | Section 5.8 |
| Limitations | Best practice | Section 10 | — | — | Section 7.3 |
| Conclusions | Required | Section 9 | Section 9 | Exec Summary | Section 7.1 |
| Recommendations | Required | Section 9 | Section 10 | Exec Summary | Section 7.2 |

KEY LESSON: All published reports include safe well yield, lot water balance, and well
interference as mandatory screening calculations. Never omit these three.

KEY LESSON: The Milford 2024 (HERAA) report is the most detailed structure seen in NS
practice — use it as the template for complex sites. WGSL's Sonny's Road 2024 report
uses a more concise structure suitable for simpler sites.

KEY LESSON: Petpeswick 2025 (DesignPoint) is the most recent HRM submission (2025) and
explicitly flagged water withdrawal approval requirements, seawater intrusion, and
arsenic/uranium/iron/manganese risk in the executive summary. Use this as the model for
coastal Meguma-formation sites.

---

## Report Structure

---

### COVER PAGE
- Report title: "Level 1 Groundwater Assessment — [Subdivision Name / Civic Address]"
- Prepared for: [Client name and address]
- Prepared by: [Firm name], [Professional name, credential, licence #]
- Project number (if applicable)
- Report date: [Month YYYY]
- Revision history: Rev 0 — Issued for Review | Rev 1 — Final

---

### EXECUTIVE SUMMARY (~150–200 words)
State purpose, site, proposed development, key findings (quantity and quality), recommended
maximum lot count, and Level 2 recommendation. Decision-maker must understand the
conclusion without reading further.

Template:
  "A Level 1 Groundwater Assessment was completed for [Site Name], a proposed [N]-lot
  [development type] subdivision located at [address], [Municipality], Nova Scotia. The
  assessment was conducted in accordance with the NSECC Guide to Groundwater Assessments
  for Subdivisions Serviced by Private Wells (2011). Based on a desktop records review,
  site visit, and screening-level calculations, the available groundwater recharge on
  the [X ha] parcel is estimated to support [conservative N]–[optimistic N] residential
  lots with individual drilled wells. A maximum of [recommended N] lots is recommended
  at this time. [Water quality summary — one sentence]. [Level 2 recommendation — one
  sentence]."

If any well may pump > 23,000 L/d: flag groundwater withdrawal approval requirement here
(per Petpeswick 2025 practice).

---

### TABLE OF CONTENTS
List all sections, sub-sections, figures, tables, and appendices.

---

### 1. INTRODUCTION

#### 1.1 Background and Purpose
State who commissioned the report, for what purpose, and which guideline applies.
Always cite: NSECC (2011). State trigger explicitly:
  "A Level 1 assessment is required for proposed subdivisions of 10 to 25 lots, as per
  Table 1 of the NSECC Guide to Groundwater Assessments for Subdivisions Serviced by
  Private Wells (NSECC, 2011)."

#### 1.2 Site Location and Description
- Civic address, PID(s), legal description
- GPS coordinates (decimal degrees, NAD83 or WGS84 — specify datum)
- Total area (ha and acres); zoning
- Current land use and surrounding context

Include: Figure 1 — Site Location Map (aerial/satellite, parcel outlined, scale bar,
north arrow, nearest town labeled)
Include: Figure 2 — Site and Surroundings Map (1:5,000–1:10,000 scale, roads, surface
water, neighbouring wells if known, proposed lot layout overlay)

#### 1.3 Proposed Development
| Item | Detail |
|---|---|
| Number of lots | |
| Development type | |
| Minimum / Median / Maximum lot size | m² |
| Total site area | m² / ha / acres |
| Proposed water supply | Individual drilled wells / community well / TBD |
| Proposed sewage disposal | Individual on-lot septic |
| Serviced by municipal water? | Yes / No |

Estimated total water demand: [N] lots × 1,350 L/d = [X] m³/d

---

### 2. PROJECT SCOPE AND METHODOLOGY

#### 2.1 Scope of Work
Describe the Level 1 scope: records review, site visit, screening-level calculations,
reporting. Reference NSECC (2011) Table 2 as the governing requirements checklist.

Name the three mandatory screening calculations explicitly:
  1. Safe well yield (Q20)
  2. Lot water balance (groundwater recharge)
  3. Well interference (drawdown at adjacent wells)

#### 2.2 Data Sources
| Data Type | Source | Date Accessed |
|---|---|---|
| Well logs | NS Well Logs Database | [Month YYYY] |
| Pumping tests | NS Pumping Test Database (Groundwater Atlas) | [Month YYYY] |
| Water chemistry | NS Water Chemistry Database (Groundwater Atlas) | [Month YYYY] |
| Bedrock geology | NS Bedrock Geology (ME 2008-001) | [Month YYYY] |
| Surficial geology | NS Surficial Geology (DP-036) | [Month YYYY] |
| Climate normals | 1991–2020 Canadian Climate Normals, [Station] | Environment Canada |
| Observation well | NS OW Network, [OW Name #XXX] | [Month YYYY] |
| Recharge rates | Kennedy et al. (2010) | NSECC |
| GWA Calculator | Level 1 GWA Calculator v3.xlsx (NSECC) | [version date] |
| Topography | LiDAR DEM / NTS 1:50,000 | [Date] |

#### 2.3 Site Visit
State date, personnel (name, title, firm), and scope. Typically covers 500 m radius from
parcel boundary. If no site visit: state explicitly as a limitation.

---

### 3. NATURAL LANDSCAPE AND SITE SETTING

#### 3.1 Topography and Drainage
- Elevation range on site (masl min and max)
- General slope direction and gradient
- How site drains (to which watercourse, in which direction)

Include: Figure 3 — Topographic Map (contours, site outlined, drainage arrows)

#### 3.2 Watershed Characterization
Always include three watershed levels (per NSECC Guide):
  - Primary watershed name and total area (m²)
  - Secondary watershed name/number
  - Tertiary sub-watershed name/number and area (m²); site position within it

Source: NS 1:10,000 Watershed Layer (data.novascotia.ca)

Include: Figure 4 — Watershed Map (primary, secondary, tertiary shown)

Local catchment area delineation from LiDAR DEM is expected by experienced municipal
reviewers — include if GIS data are available. This was a distinctive strength of the
Westwood Hills 2022 report (ewC Consulting).

#### 3.3 Surface Water Features
For each watercourse, lake, or wetland within 500 m:
  - Name, type, approximate distance from site boundary
  - Observed or inferred flow direction
  - Whether perennial (groundwater-fed) or ephemeral
  - Whether NS Wetland Conservation Policy considerations apply

#### 3.4 Climate and Precipitation
- Climate station used, distance from site, period (1991–2020)
- Annual precipitation (mm/y)
- Note if site is in a notably high or low precipitation zone for NS
- Source: Environment and Climate Change Canada

---

### 4. GEOLOGICAL SETTING

#### 4.1 Bedrock Geology
- Formation name (full), age, rock type
- HU code from NS classification
- Depth to bedrock (from well logs)
- Dominant water-bearing features: fractures, joints, bedding planes, weathered zone

Include: Figure 5 — Bedrock Geology Map (NS Bedrock Geology excerpt, site outlined)

Formation guidance for common NS HU codes:

  ME (Meguma — Halifax/Goldenville): quartzite/slate metasedimentary; fracture-dominated;
    variable yields; arsenic and manganese geogenic risk; low pH typical; acid rock
    drainage possible in disturbed settings

  GR (South Mountain Batholith / Granite): crystalline; fracture-only flow; generally
    lower yields; uranium and radon geogenic risk; lower hardness

  WI (Windsor Group / Green Oaks Fm.): limestone/evaporite; primary source is Green Oaks
    Formation; do not drill below into Horton/Windsor evaporite — water quality degrades;
    hard to extremely hard water; calcium sulphate dominant; iron and manganese common;
    water treatment almost always required (HERAA 2024)

  CB (North Mountain Basalt): vesicular basalt; generally productive; lower geogenic risk;
    seasonal variability can be high

  HO (Horton Group): sandstone/conglomerate; variable; iron common

  FU-WO (Wolfville Formation): red sandstone; moderate yields; iron, hardness common

  PE (Pictou Group / Stellarton): sandstone/shale; variable; sulphate, iron risk

  CA (Carboniferous Limestone): variable karst; hardness, TDS, potential for rapid
    contaminant transport through solution channels

#### 4.2 Surficial Geology
- Type and thickness of overburden (till, glaciofluvial sand/gravel, organic, marine clay)
- Role in recharge: does overburden transmit or impede recharge to bedrock?
- Depth to water table in overburden (if dug wells exist in area)
- Source: NS Surficial Geology DP-036

Include: Figure 6 — Surficial Geology Map (DP-036 excerpt, site outlined)

---

### 5. GROUNDWATER CONDITIONS AND WATER SUPPLY ASSESSMENT

#### 5.1 Existing Well Inventory
Summarize NS Well Logs Database records (domestic and public use, within 500 m).

| Parameter | n | Min | Median | Max | Notes |
|---|---|---|---|---|---|
| Well depth (m bgs) | | | | | Note artesian if any |
| Casing length (m bgs) | | | | | |
| Static water level (m bgs) | | | | | Exclude negative values from avg |
| Reported yield (lpm) | | | | | |

Include: Figure 7 — Well Location Map (colour-coded by yield, site outlined)
Include: Appendix A — Full Well Log Summary Table

State whether median yield meets NS minimum (18 lpm sustained, 1,080 L/hr).

#### 5.2 Hydrogeological Parameters
From NS Pumping Test Database (HU-filtered):

| Parameter | Optimistic (90th %ile) | Average (Median) | Pessimistic (10th %ile) | Source |
|---|---|---|---|---|
| K (m/d) | | | | NS Pumping Test DB, n=X |
| T (m²/d) | | | | Derived from K × median depth |
| S | — | | — | Measured / Default |

State HU used, n tests, and whether S was measured or defaulted.

For Windsor Group: note aquifer properties are highly variable due to dissolution features
and the contrast between productive Green Oaks Fm. and underlying evaporites (HERAA, 2024).

#### 5.3 Aquifer Storage (include if data are sufficient)
- Specific yield (Sy) — unconfined / overburden
- Storativity (S) — confined / bedrock
- Specific storage Ss = S / b where b = saturated thickness from well logs
- Total aquifer storage = S × b × site_area (contextual — not a substitute for recharge
  calculation; present only to show available buffer in drought conditions)

Omit or note "insufficient data" if pumping test records do not support this calculation.

#### 5.4 Groundwater Recharge (Lot Water Balance)
Primary screening calculation for lot capacity. Always run both scenarios.

Inputs summary:
| Input | Value | Source |
|---|---|---|
| Site area | m² | User |
| Annual precipitation | mm/y | Climate Normals, [Station] |
| Recharge rate (low) | m/y | Kennedy et al. (2010), HU=[X] |
| Recharge rate (high) | m/y | Kennedy et al. (2010), HU=[X] |
| NS minimum demand/lot | 1.35 m³/d | NSECC 2011 |
| Impermeable fraction | 0.30 | NSECC default |

Results:
| Scenario | Annual Recharge (m³/y) | Daily Recharge (m³/d) | Max Lots |
|---|---|---|---|
| Conservative (low R) | | | |
| Optimistic (high R) | | | |

Include: Appendix B — GWA Calculator INPUTS Sheet
Include: Appendix C — GWA Calculator RESULTS Sheet

Also present zoning area constraint:
| Item | Value |
|---|---|
| Net buildable area after 30% infra deduction | m² |
| Min lot area (from applicable LUB) | m² |
| Max lots from zoning area | N |

Binding constraint comparison:
| Scenario | GW Recharge Limit | Zoning Area Limit | Binding | Governed By |
|---|---|---|---|---|
| Conservative | | | | |
| Optimistic | | | | |

#### 5.5 Safe Well Yield
Q20 = sustainable yield from formation pumping tests over 20 years (m³/d per well).

Compare Q20 to NS minimum demand (1.35 m³/d/lot).

State: "The Q20 sustainable yield from [n] pumping tests in the [HU] formation is
estimated at [X] m³/d, which [exceeds / is less than] the NS minimum domestic demand of
1.35 m³/d per lot. Individual well yield [is / is not] the limiting factor at this site."

From HERAA (2024): when safe well yield and lot water balance give different answers,
report both and explain which is more conservative and why. If the safe well yield
suggests insufficient recharge area on individual lots but the lot water balance is
positive, note that the lot water balance considers the full site area, not individual
lot areas.

#### 5.6 Well Interference Assessment
Assess potential drawdown effect of proposed wells on each other and on existing off-site
wells. Always state the acceptability criterion used.

NSECC acceptability criterion: maximum drawdown at any well head should be < 50% of
available drawdown (available drawdown = static WL depth − pump setting depth).
This is the criterion used in the Milford 2024 report (HERAA, 2024).

Quantitative (if K/T data are available — preferred):
  Use Theis equation: s = (Q / 4πT) × W(u),  u = r²S / 4Tt
  Calculate drawdown at adjacent lot well location(s) over 20-year pumping period.
  Include: Appendix D — Well Drawdown Calculations

Qualitative screening (if data are insufficient):
  Lot size > 4,000 m², well spacing > 60 m → Low interference risk
  Lot size 1,000–4,000 m², spacing 30–60 m → Moderate risk — flag for Level 2 monitoring
  Lot size < 1,000 m², spacing < 30 m → High risk — recommend Level 2 or community well

Community well spacing (from Petpeswick 2025 / DesignPoint):
  "The optimal number of community wells is [N], spaced at a minimum of 50 m from each
  other and located across the groundwater flow direction to minimize interference."

Include: Figure 8 — Proposed Well Locations and Interference Zones (conceptual)

#### 5.7 Potential Effects on Surface Water and Environment
Required per NSECC (2011) Table 2, Item 3. Assess whether groundwater withdrawals could
reduce baseflow to nearby watercourses or wetlands.

Language for low risk:
  "The proposed withdrawal of [X] m³/d represents less than [X]% of estimated recharge
  to the local catchment area. Significant baseflow depletion in [watercourse name] is
  not anticipated."

Include Sonny's Road 2024 approach: if wetlands are present on or adjacent to the site,
discuss whether drawdown from proposed wells could affect wetland water levels.

#### 5.8 Risk of On-Site Septic Systems to Wells
Required per NSECC (2011) Table 2, Item 3. State regulatory setbacks and whether the
proposed lot configuration can accommodate them.

NS Well Construction Regulations (N.S. Reg. 382/2007) minimum setbacks:
  From septic tank:          ≥ 15 m
  From leaching bed / field: ≥ 15 m
  From holding tank:         ≥ 15 m
  From manure storage:       ≥ 30 m
  From fuel storage:         ≥ 30 m
  From property line:        ≥ 3 m (minimum; many municipalities require more)
  From building projection:  ≥ 1.6 m

From Milford 2024 and Petpeswick 2025: both reports explicitly recommend placing wells
upgradient or cross-gradient of septic fields. Always include:
  "It is recommended that proposed well locations be finalized in relation to confirmed
  groundwater flow direction, and that wells be located upgradient or cross-gradient of
  proposed septic absorption fields wherever site topography allows."

#### 5.9 Groundwater Withdrawal Approval
State if any proposed wells may pump > 23,000 L/d (23 m³/d).

Individual domestic wells typically pump 700–1,400 L/d — no approval required.
Community wells serving multiple lots often exceed the threshold.

Language if relevant:
  "A groundwater withdrawal approval from NSECC is required for any well pumping more
  than 23,000 litres per day (N.S. Reg. 110/2010). [The proposed community well / Wells
  serving more than [N] lots] may exceed this threshold and [will / may] require approval
  prior to construction. The applicant should contact NSECC to confirm requirements."

This was prominently flagged in the Petpeswick 2025 (DesignPoint) executive summary.

---

### 6. WATER QUALITY ASSESSMENT

#### 6.1 Background Water Quality
Summarize NS Water Chemistry Database records from the study area.

| Parameter | Units | n | Min | Median | Max | Guideline | Type | # Exceeding | Status |
|---|---|---|---|---|---|---|---|---|---|
| Arsenic | µg/L | | | | | 10 | MAC | | |
| Uranium | µg/L | | | | | 20 | MAC | | |
| Manganese | µg/L | | | | | 120 | IMAC | | |
| Iron | µg/L | | | | | 300 | AO | | |
| Nitrate (as N) | mg/L | | | | | 10 | MAC | | |
| pH | — | | | | | 6.5–8.5 | AO | | |
| Hardness | mg/L | | | | | 80–100 soft | — | | |
| Sodium | mg/L | | | | | 200 | AO | | |
| Sulphate | mg/L | | | | | 500 | AO | | |
| TDS | mg/L | | | | | 500 | AO | | |
| Fluoride | mg/L | | | | | 1.5 | MAC | | |

Guideline source: Health Canada (2024), GCDWQ — verify current thresholds in Step 0.
MAC = Maximum Acceptable Concentration (health-based)
IMAC = Interim MAC | AO = Aesthetic Objective (taste/odour/appearance)

IMPORTANT: Uranium MAC was updated to 20 µg/L in 2019. Always verify current GCDWQ
via live search before including guideline values.

#### 6.2 Geogenic Risk Assessment
Always state whether the site is in an elevated risk area per Kennedy et al. (2010)
risk maps for Mn, As, and U. Municipal reviewers look for this — do not omit it.

Formation geogenic risk table:

| HU | Formation | Primary Geogenic Risk | Treatment Typically Needed |
|---|---|---|---|
| ME | Meguma (Halifax/Goldenville) | Arsenic, Manganese, low pH | Fe/Mn filter; pH neutralizer; RO/IX for As if >10 µg/L |
| GR | South Mountain Batholith | Uranium, Radon | Activated carbon; ion exchange for U; aeration for Rn |
| WI | Windsor Group | Hardness, Sulphate, Fe, TDS | Water softener; aeration; chlorination |
| HO | Horton Group | Iron, Manganese | Oxidizing filter (greensand/Birm) |
| FU-WO | Wolfville Formation | Iron, Hardness | Aeration; iron filter |
| CB | North Mountain Basalt | Generally low risk | Routine testing still recommended |
| PE | Pictou Group | Sulphate, Iron | Aeration; iron filter |
| CA | Carboniferous Limestone | Hardness, TDS | Water softener |

From Petpeswick 2025 (DesignPoint): state geogenic risk directly and unambiguously:
  "There is a high risk of arsenic, uranium, iron and manganese contamination due to
  natural geological conditions in the [formation name]. Water wells in the proposed
  development are not expected to meet Health Canada GCDWQ without treatment."

From Milford 2024 (HERAA): for Windsor Group:
  "Potable water within this area will require treatment. Water quality is expected to
  be hard to extremely hard as a result of high concentrations of calcium sulphate,
  possibly with higher TDS and concentrations of iron and manganese."

Do not soften these statements to avoid alarming the client — the risk must be stated
clearly to comply with NSECC conclusions requirements (Section 2.3.1 of the 2011 Guide).

#### 6.3 Seawater Intrusion Risk (coastal sites only)
Required for sites within 2 km of tidal water or in a coastal lowland.

From Petpeswick 2025 (DesignPoint):
  "There is a low to medium risk of seawater intrusion, which is to be controlled by
  keeping operational water levels at a minimum of 6 m above sea level."

Minimum well screen elevation above sea level: ≥ 6 m (NS practice recommendation).
This corresponds to GWA Calculator input C17 (seawater/saline water elevation).

If not coastal, state: "The site is not located in a coastal area and seawater intrusion
is not a risk for this development."

#### 6.4 Recommended Water Quality Testing at Time of Well Completion
Include this even when background chemistry data exist. Parameters per NSECC (2011)
Appendix D plus formation-specific additions:

All sites (minimum):
  Total coliform, E. coli, nitrate (as N), pH, hardness (total and calcium),
  iron, manganese, sodium, TDS

ME (Meguma) — add: arsenic, uranium, radon (optional)
GR (Granite) — add: uranium, radon, gross alpha particle activity
WI (Windsor) — add: sulphate, fluoride, barium, TDS
CB / FU-WO / HO — add: iron, manganese, TDS

Note: homeowners should also test for bacteria annually and for chemistry parameters
every 3–5 years, or whenever taste/odour/appearance changes.

Reference: NSECC (2011) Appendix D and Health Canada GCDWQ (2024).

#### 6.5 Water Treatment Options (when exceedances expected)
Include when geogenic risk is high or chemistry exceedances are identified.
Based on the Milford 2024 (HERAA) report table approach:

| Water Quality Issue | Treatment Option | Approx. Capital Cost (2024) | Maintenance |
|---|---|---|---|
| Iron and Manganese | Oxidizing filter (greensand/Birm) | $2,000–$5,000 | Annual media/backwash |
| Hardness | Water softener (ion exchange) | $1,500–$3,500 | Salt refill quarterly |
| Arsenic (>10 µg/L) | Reverse osmosis (POU) | $500–$1,500 | Annual filter change |
| Arsenic (>10 µg/L) | Iron coagulation/filtration (POE) | $3,000–$8,000 | Regular backwash |
| Low pH | Calcite neutralizer | $1,000–$2,500 | Annual media top-up |
| Uranium | Anion exchange or RO | $2,000–$5,000 | Quarterly |
| Bacteria | UV disinfection | $500–$1,500 | Annual bulb replacement |
| Bacteria | Chlorination (continuous) | $1,500–$3,000 | Chemical replenishment |
| Sulphate / TDS | RO (point of use) | $500–$1,500 | Annual filter change |

Costs are approximate (2024 NS market). Homeowners should obtain site-specific water
quality testing and consult a licensed NS water treatment professional before selecting
any treatment system.

---

### 7. CONCLUSIONS AND RECOMMENDATIONS

#### 7.1 Conclusions
Numbered list of 6–10 concise statements. Include all of these:

1. Site location, area, and proposed development (lot count, type)
2. Hydrogeological setting (HU code, formation name, surficial geology)
3. Safe well yield result: Q20 vs. 1.35 m³/d minimum per lot
4. Lot water balance result: conservative and optimistic lot counts
5. Well interference result: max drawdown vs. 50% available drawdown, acceptability
6. Binding constraint (GW recharge or zoning area) and recommended maximum lot count
7. Water quality status — expected exceedances, treatment required or not
8. Effects on surface water and environment (low/moderate/high, basis)
9. Septic risk to wells (low if setbacks met and wells upgradient)
10. Whether Level 2 GWA is recommended

#### 7.2 Recommendations
The NSECC (2011) Section 2.3.2 mandates a minimum set. Every report must address all of
these, plus the standard NS practice additions below.

MANDATORY (NSECC 2011 Section 2.3.2):
1. Suitability of private wells — state explicitly (suitable / not suitable / conditional)
2. Minimum lot sizes for sustainable individual well use
3. Well construction requirements: depth, casing length, casing material, grouting
4. Well spacing to minimize interference (state a number or minimum spacing in metres)
5. Lot yield (estimated daily recharge per lot) and recommended maximum pumping rate
6. Development phasing (if applicable for multi-stage projects)
7. Water storage requirements (pressure tanks; storage tanks if marginal supply)
8. Mitigation measures for identified water quality or quantity concerns

STANDARD ADDITIONAL (from NS practice — include all applicable):
9. Mandatory water quality testing at time of well completion (list specific parameters
   per Section 6.4 — appears in every reviewed NS GWA report)
10. NS Well Construction Regulations compliance: all wells constructed by certified NS
    well driller; well completion reports submitted to NSECC within 30 days of completion
11. Regulatory setbacks (cite N.S. Reg. 382/2007): ≥ 15 m from septic tank and
    absorption field; ≥ 30 m from manure/fuel storage; ≥ 3 m from property line
12. Well placement relative to groundwater flow: place wells upgradient or cross-gradient
    of proposed septic absorption fields
13. Groundwater withdrawal approval: if any well pumps > 23,000 L/d, NSECC approval
    required before construction (N.S. Reg. 110/2010)
14. Water treatment: if exceedances expected, specify treatment type and recommend
    homeowner confirm water quality testing before occupancy and annually thereafter
15. Coastal only: operational water level must be ≥ 6 m above sea level to mitigate
    seawater intrusion risk

LEVEL 2 GWA TRIGGER ASSESSMENT (always address — state recommended or not with rationale):
Recommend Level 2 GWA when any of the following apply (from NSECC 2011 and NS practice):
  a. Optimistic lot count > 1.5× conservative lot count (high aquifer uncertainty)
  b. Client proposes more lots than conservative GW recharge supports
  c. Water quality exceedances identified that require field investigation
  d. Well interference drawdown > 50% available drawdown under pessimistic conditions
  e. Open-loop groundwater heat pumps proposed (NSECC Guide Table 1 — automatic trigger)
  f. Known groundwater problems in area: prior interference complaints, well failures
  g. Site adjacent to known contamination source (landfill, gas station, dry cleaner)
  h. Artesian conditions in area wells (confined aquifer — field testing needed to
     characterize confining layer and sustainable yield)
  i. Fewer than 5 well logs or pumping tests available (high data uncertainty)

Do NOT recommend Level 2 when: zoning area is already more restrictive than the optimistic
GW lot count — Level 2 cannot unlock additional lots. State this explicitly.

Language when Level 2 is NOT needed:
  "A Level 2 Groundwater Assessment is not recommended at this time. The available
  groundwater recharge supports the proposed [N] lots under both conservative and
  optimistic scenarios, well interference is within acceptable limits, and the
  [GW recharge / zoning area] constraint governs development density. Individual well
  yield testing and water quality analysis at time of construction are recommended as
  standard precautionary measures."

#### 7.3 Limitations
Include a limitations section in every report. This is NS best practice (appears in
Milford 2024 and Petpeswick 2025).

Standard limitations:
  1. Level 1 is a screening-level assessment based on existing data only. No test wells
     were drilled and no site-specific pumping tests were conducted.
  2. Well log records may not fully represent local conditions if records are sparse.
  3. Aquifer properties (K, S, T) are from regional formation data; site-specific values
     may differ.
  4. Climate normals (1991–2020) represent recent historical averages. Future precipitation
     changes due to climate change are not accounted for.
  5. Water quality data are from existing area wells; quality at new well locations may
     differ, particularly in heterogeneous fractured bedrock aquifers.
  6. Interpretations and recommendations are valid as of the report date and are based on
     data available at that time. New information may change conclusions.
  7. This report was prepared for the stated client and stated purpose only. Use by any
     other party for any other purpose requires written authorization from the preparer.

Add site-specific limitations as applicable.

---

### 8. REFERENCES

Always include all applicable references. Add any comparable reports found in Step 0.

- Health Canada (2024). *Guidelines for Canadian Drinking Water Quality — Summary Table.* Ottawa: Health Canada. canada.ca
- Kennedy, G.W., O'Brien, N.R., Williams, N.D., and Godfrey, L.D. (2010). *Estimating Groundwater Recharge for Nova Scotia.* Nova Scotia Environment, Open File Report ME 2010-003.
- Nova Scotia Environment and Climate Change (NSECC) (2011). *A Guide to Groundwater Assessments for Subdivisions Serviced by Private Wells.* Province of Nova Scotia.
- Nova Scotia Environment and Climate Change (NSECC). *Nova Scotia Well Logs Database.* novascotia.ca/nse/welldatabase
- Nova Scotia Environment and Climate Change (NSECC). *NS Pumping Test Database; NS Water Chemistry Database.* Groundwater Atlas of Nova Scotia, novascotia.ca/nse/groundwater
- Nova Scotia Environment and Climate Change (NSECC). *NS Groundwater Observation Well Network.* novascotia.ca/nse/groundwater/groundwaternetwork.asp
- Nova Scotia Department of Natural Resources and Renewables (NSDNR). *Bedrock Geology of Nova Scotia.* Open File Report ME 2008-001.
- Nova Scotia Department of Natural Resources and Renewables (NSDNR). *Surficial Geology of Nova Scotia (DP-036).* Digital shapefile.
- Environment and Climate Change Canada (2024). *1991–2020 Canadian Climate Normals.* climate.weather.gc.ca
- Province of Nova Scotia (2007). *Well Construction Regulations, N.S. Reg. 382/2007.* Made under the Environment Act.
- Province of Nova Scotia. *On-site Sewage Disposal Systems Regulations.* Made under the Environment Act.
- Province of Nova Scotia (2010). *Water Withdrawal Approval Regulations, N.S. Reg. 110/2010.* Made under the Environment Act.

Cite any comparable NS GWA reports used as methodological references, e.g.:
- HERAA Consulting Inc. (2024). *Level 1 Groundwater Assessment — Milford Station, Highway 2, NS.* Project No. 24-1069. Prepared for James Kerr, Edward Kerr and Katherine Manuel.
- DesignPoint Engineering & Surveying Ltd. (2025). *Level 1 Groundwater Assessment — West Petpeswick Road, West Petpeswick, NS.* Report 25-229. Prepared for Zzap Architecture + Planning.

---

### APPENDICES

| Appendix | Contents |
|---|---|
| A | Well Log Summary Table (all wells within study area, full details from NS database) |
| B | GWA Calculator — INPUTS Sheet (screenshot or printed table, all cell values) |
| C | GWA Calculator — RESULTS Sheet (screenshot or printed table) |
| D | Well Drawdown / Interference Calculations (Theis method or GWA Interference Tool) |
| E | Water Chemistry Summary Table (all parameters, all samples vs. current GCDWQ) |
| F | Climate Normals Data (relevant station, monthly and annual precipitation) |
| G | NS Observation Well Data Summary (OW name, period, seasonal fluctuation graph) |
| H | Pumping Test Data Summary (tabulated by HU, K/T/S values and source) |
| I | Site Visit Photographs (captions, dates, GPS coordinates) |
| J | Professional Qualifications of Report Preparer (CV, licence, firm profile) |

---

## Figures List

| Figure No. | Title | Recommended Scale | Source |
|---|---|---|---|
| 1 | Site Location Map | 1:25,000 or 1:50,000 | Google Maps / NTS |
| 2 | Site and Surroundings Map | 1:5,000 or 1:10,000 | Google Earth / GIS |
| 3 | Topographic Map | 1:5,000 (LiDAR) or 1:50,000 (NTS) | LiDAR DEM / NTS |
| 4 | Watershed Map | 1:25,000 or 1:100,000 | NS Watershed Layer |
| 5 | Bedrock Geology Map | 1:100,000 or 1:250,000 | NS Bedrock Geology ME 2008-001 |
| 6 | Surficial Geology Map | 1:50,000 | NS DP-036 |
| 7 | Well Locations Map | 1:5,000 or 1:10,000 | NS Well DB overlay on aerial |
| 8 | Proposed Lot Layout with Well/Septic Setbacks | 1:2,000 or 1:5,000 | Applicant's draft plan |

All figures require: north arrow, scale bar, legend, data source credit, figure number
and title caption.

---

## Writing Style Guidelines

- Third person, past tense for methods: "A desktop review was conducted..."
- Present tense for findings: "The median well depth is 60 m..."
- Do not overstate confidence: "data are consistent with feasibility" not "the site is suitable"
- For WI (Windsor Group): state explicitly "water treatment will be required" — do not soften
- For ME (Meguma) / GR (Granite): state arsenic/uranium risk explicitly even if no exceedances
- Never omit the three mandatory calculations: safe well yield, lot water balance, well interference
- Always address Level 2 recommendation — either recommended or not, with clear rationale
- State setbacks numerically: ≥ 15 m from septic tank/field, ≥ 3 m from lot line
- SI units throughout: m, m², ha, m³/d, lpm, mg/L, µg/L
- Rounding: well depths 1 decimal; yields whole number; recharge 3 sig figs

---

## Document Production (DOCX)

Read the docx SKILL.md before writing the document.

Key formatting:
  Page: Letter (8.5" × 11"), margins 1" all sides
  Font: Calibri 11pt body | H1: 14pt Bold | H2: 12pt Bold | H3: 11pt Bold Italic
  Header: Report title (left) | Project # (right)
  Footer: "CONFIDENTIAL — Prepared for [Client]" (left) | Firm name (right)
  Page numbers: "Page X of Y" bottom centre
  Tables: Table Grid style, header row bolded, light blue shaded (#DEEAF1)
  Captions: "Table X. [Title]" / "Figure X. [Title]" in italic below each

Professional sign-off block on last page before appendices:
  Prepared by: _____________________________ P.Eng./P.Geo. #XXXXX
  [Firm Name]
  Date: ___________________________
  [Space for wet or digital stamp]

File naming: `[SiteName]_Level1_GWA_[YYYYMM].docx`

---

## Common Data Gaps — Fallback Language

| Missing Data | Fallback Language |
|---|---|
| No water chemistry | "No water quality records were identified in the study area from the NS Water Chemistry Database. Site-specific testing at well completion is required at minimum for: [list parameters per formation and NSECC Appendix D]." |
| Fewer than 5 well logs | "Limited well log records (n=[X]) were identified within 500 m. Parameters are preliminary; site conditions may differ from regional averages." |
| No pumping tests for HU | "No pumping test records were available for the [HU] formation. Regional data from the nearest comparable formation ([HU]) were used as a surrogate. This is a limitation of the Level 1 assessment." |
| No OW within 50 km | "No NS Observation Well was identified within a representative distance. A seasonal fluctuation of [X] m has been assumed based on regional estimates for [formation] in [county]." |
| No site visit completed | "A site visit was not completed as part of this Level 1 assessment. All characterization is based on desktop data. A site visit prior to subdivision approval is recommended." |
| Artesian wells in area | "Artesian conditions (negative static water levels) were identified in [n] area wells, suggesting locally confined aquifer conditions. Interference calculations should be treated with caution; a Level 2 assessment is recommended to characterize the confining layer and sustainable yield." |

---

## Pre-Submission Quality Control Checklist

- [ ] Cover page complete (title, client, preparer, date, project #, revision)
- [ ] Executive summary states recommended lot count and binding constraint
- [ ] All three mandatory calculations present: safe well yield, lot water balance, well interference
- [ ] All three give consistent conclusions (or conflicts are explicitly explained)
- [ ] Level 2 recommendation addressed with clear rationale
- [ ] Septic-to-well setback risk discussed with regulatory distances cited
- [ ] Water quality table completed or absence noted and justified
- [ ] Geogenic risk stated explicitly for the specific formation
- [ ] Water treatment options included where exceedances expected
- [ ] Withdrawal approval requirement addressed (>23,000 L/d threshold)
- [ ] Seawater intrusion addressed (coastal sites) or dismissed (inland sites)
- [ ] All figures numbered, captioned, referenced in text
- [ ] All tables numbered, captioned, referenced in text
- [ ] Appendices B and C (GWA Calculator INPUTS and RESULTS) attached
- [ ] NS Well Construction Regulations (N.S. Reg. 382/2007) cited for setbacks
- [ ] Health Canada GCDWQ (current year) cited for water quality limits
- [ ] Limitations section present
- [ ] References complete and consistently formatted
- [ ] Professional sign-off block or stamp page present
- [ ] File named: `[SiteName]_Level1_GWA_[YYYYMM].docx`

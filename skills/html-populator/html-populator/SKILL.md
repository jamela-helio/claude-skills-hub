---
name: html-populator
description: Populate Helio QGIS layout HTML card files (parcelinfo.html, Environmental.html, Utilities.html) from a plain-text data file. Use this skill whenever a user uploads or provides a .txt file with property/site data and wants to fill in or generate the HTML layout cards for a Helio feasibility report or QGIS layout. Also trigger when the user says things like "populate the HTML cards", "fill in the layout files from this data", "generate my parcel cards", "update the cards with new data", or provides a text file with fields like PID, address, zone, or utility info and mentions layouts or HTML files.
---

# HTML Layout Card Populator

Populates three QGIS-style HTML card templates (parcelinfo, Environmental, Utilities) with property and site data from a plain `.txt` input file.

## Workflow

1. Locate the data `.txt` file — it may be in the uploads folder or user's mounted directory.
2. Use the bundled templates from this skill's `assets/` directory — no need to look for templates elsewhere. The skill is self-contained.
3. Install BeautifulSoup if needed: `pip install beautifulsoup4 --break-system-packages -q`
4. Run `scripts/populate_html.py`, pointing `--templates-dir` at the skill's `assets/` folder.
5. Save the three populated HTML files to `/sessions/eager-gallant-gates/mnt/outputs/`.
6. Present each file with a `computer://` link so the user can open it directly.

> **Finding the skill's assets directory:** The skill lives at a path like `.../skills/html-populator/`. The assets folder is at `.../skills/html-populator/assets/`. Use the skill file's own location to resolve this — or glob for `**/html-populator/assets` under the skills root.

## Input: Data File Format

A plain `.txt` file, one field per line, `key: value` format. Lines starting with `#` are treated as comments and ignored. Keys are case-insensitive. Unrecognised keys are silently skipped.

**Example data file:**
```
# --- Parcel ---
pid: 41146804
address: 257 Main St\nYarmouth, NS
area_m2: 362.3 m²
area_ft2: 3,900 ft²
zone: R-3
zone_desc: Multiple Family Residential-Medium Density
plan_area: --
municipality: Dartmouth Municipality · Parcel Report

# --- Geology / Environmental (parcelinfo.html) ---
groundwater: Metamorphic
surficial_geology: Stony, sandy matrix, material derived from local bedrock sources
vs30: 813 m/s (Class B: Rock)
surface_form: Level
karst_risk: Low
flood_risk: Moderate
soil_drainage: Well and Moderately Well
dtw: 4 m
saltwater: no data
site_condition: Dry area, suitable for most uses with low risk of sogginess
topography: Flat to rolling, with many surface boulders.

# --- Utilities (Utilities.html) ---
min_setback: 2 m (Centre Plan Package B)
service_req: Urban Service Area
stormwater: Halifax Water
sewershed: Halifax WWTF
distribution: J. Douglas Kline (Pockwock) Water Supply Plant
```

> **Address line breaks:** Use `\n` in the address value to produce a `<br>` in the card. Example: `address: 257 Main St\nYarmouth, NS`

> **Auto footer:** The footer text is automatically set to `{City} Municipality · {Suffix}` based on the city in the `address` field — no need to set `municipality` separately. Each template keeps its own suffix ("Parcel Report" or "Parcel Information"). You can still override with an explicit `municipality` key if needed.

### Adding new rows not in the original template

If you have a data field that doesn't exist in the HTML template, prefix the key with the target section name followed by a dot. The script will automatically append a new row to that section.

**Syntax:** `section_prefix.label_key: value`

The label is auto-formatted: underscores become spaces, title-cased. (`bedrock_depth` → "Bedrock Depth")

| Prefix | Section it appends to |
|--------|----------------------|
| `geology.` | Geology & Surface Form |
| `env.` | Environmental Constraints |
| `drainage.` | Drainage & Hydrology |
| `property.` | Property Details |
| `water.` | Water & Sewer (Utilities.html only) |

**Examples:**
```
geology.rare_mineral: Quartz deposits present
geology.bedrock_depth: 1.2 m below grade
env.radon_risk: Low – Class B rock
drainage.seasonal_flooding: Not observed on site
property.heritage_overlay: No
water.fire_hydrant_distance: 45 m from property line
```

If the target section doesn't exist in a particular template (e.g. `water.` in parcelinfo.html), the row is silently skipped for that file — it only appears in the templates that have that section.

## Field Reference

### Common fields (all three cards)

| Key | Element filled | Notes |
|-----|---------------|-------|
| `pid` | Header PID label | Rendered as `PID: <value>` |
| `address` | Header address | Use `\n` for line break |
| `area_m2` | Green area badge | Include unit, e.g. `362.3 m²` |
| `area_ft2` | Secondary area badge | Include unit, e.g. `3,900 ft²` |
| `zone` | Zone code (amber) | e.g. `R-3` or `HR-1` |
| `zone_desc` | Zone full description | e.g. `Multiple Family Residential` |
| `plan_area` | Property Details → Plan Area row | |
| `municipality` | Footer text (optional) | Auto-derived from `address` if omitted. Override with a full string, e.g. `Halifax Regional Municipality · Parcel Report` |

### parcelinfo.html AND Environmental.html — Geology & Surface Form section

Both cards share this same structure. Fields populate identically in both files.

| Key | Row label matched | Example value |
|-----|------------------|---------------|
| `groundwater` | Groundwater Region | `Metamorphic` |
| `surficial_geology` | Surficial Geology | `Stony, sandy matrix...` |

### parcelinfo.html AND Environmental.html — Environmental Constraints section

| Key | Row label matched | Example value |
|-----|------------------|---------------|
| `vs30` | VS30 Velocity | `813 m/s (Class B: Rock)` |
| `surface_form` | Surface Form | `Level` |
| `karst_risk` | Karst Risk | `Low` |
| `flood_risk` | Flood Risk | `Moderate` |

### parcelinfo.html AND Environmental.html — Drainage & Hydrology section

| Key | Row label matched | Example value |
|-----|------------------|---------------|
| `soil_drainage` | Soil Drainage | `Well and Moderately Well` |
| `dtw` | Depth-to-Water (DTW) | `4 m` |
| `saltwater` | Saltwater Intrusion | `no data` |
| `site_condition` | Site Condition | `Dry area, suitable for most uses...` |

### parcelinfo.html AND Environmental.html — Topography detail block

| Key | What fills | Example value |
|-----|-----------|---------------|
| `topography` | Description block text | `Flat to rolling, with many surface boulders.` |

### Utilities.html — Property Details section

| Key | Row label matched | Example value |
|-----|------------------|---------------|
| `min_setback` | Min Bldg Setback | `2 m (Centre Plan Package B)` |
| `service_req` | Service Requirement | `Urban Service Area` |

### Utilities.html — Water & Sewer section

| Key | Row label matched | Example value |
|-----|------------------|---------------|
| `stormwater` | Stormwater Area | `Halifax Water` |
| `sewershed` | Sewershed | `Halifax WWTF` |
| `distribution` | Distribution Area | `J. Douglas Kline (Pockwock) Water Supply Plant` |

## Running the Script

```bash
pip install beautifulsoup4 --break-system-packages -q

SKILL_DIR="<path/to/skills/html-populator>"

python "$SKILL_DIR/scripts/populate_html.py" \
  <path/to/data.txt> \
  --templates-dir "$SKILL_DIR/assets/" \
  --output-dir /sessions/eager-gallant-gates/mnt/outputs/
```

The script prints a line for each file it processes (✓ or ⚠ if a template wasn't found).

## Output

Three populated HTML files in the outputs folder:
- `parcelinfo.html`
- `Environmental.html`
- `Utilities.html`

After the script runs, present all three to the user with `computer://` links. If any template was missing, let the user know which one and ask them to provide it.

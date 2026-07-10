---
name: ns-lub-lookup
description: >
  Look up zoning and regulatory requirements from Nova Scotia Land Use By-laws (LUBs), including
  schedule maps, overlay zones, and municipal GIS web apps. Use this skill whenever a user asks
  about a zone code and planning area anywhere in Nova Scotia — e.g. "HR-1 requirements under the
  Regional Centre LUB", "what can I build in R-2 Lunenburg", "ER-3 zoning Bedford", setbacks,
  lot coverage, height limits, parking, or permitted uses for any named zone. Also trigger when
  the user uploads a LUB PDF, asks about overlays (flood zones, heritage, environmental protection,
  coastal buffers), asks to check a zoning map or schedule, or mentions ExploreHRM or a GIS viewer.
  Trigger even for casual phrasing — "what's allowed in that zone", "can I build a fourplex there",
  "is it in a flood zone", "check the schedule map" — whenever a zone code, overlay, or LUB area
  is mentioned.
---

# Nova Scotia LUB Lookup Skill

This skill answers questions about zoning regulations for any zone in any Nova Scotia municipality
by (a) consulting a bundled reference index of all NS LUBs and their source URLs, then (b) fetching
or reading the relevant LUB content, and (c) presenting a structured summary with citations.

---

## Step 1 — Identify the Zone and LUB Area

Parse the user's query for two things:
1. **Zone code** — e.g. `HR-1`, `R-2`, `ER-3`, `C-1`, `MU-2`, `I-1`
2. **Planning area / municipality** — e.g. "Regional Centre", "Bedford", "Lunenburg", "Digby", "CBRM"

If either is missing or ambiguous, ask one focused question to resolve it before proceeding.
Common ambiguities:
- HRM has **21 separate plan areas**, each with its own LUB. Always confirm which plan area.
- "Halifax" alone could mean Regional Centre, Halifax Plan Area (Mainland), or another HRM area.
- Some zones appear in multiple municipalities with different rules — always confirm the municipality.

---

## Step 2 — Locate the LUB Source

Use **two parallel tracks** simultaneously: the Google Drive database and the official municipal website.
The goal is to identify the **most recent version** of the LUB before reading any content.

---

### Track A — Google Drive database

Consult `references/lub-index.md` to find the correct folder ID for the municipality.

Root folder: `1Tkg3xgc47qhrt7_d3qOZ6Fs5CamAgo3M`

1. Use `Google Drive:search_files` with `parentId = '<municipality_folder_id>'` to list files.
2. Identify the correct LUB PDF by filename (look for `*-lub-*` or `LUB`, matching the plan area).
3. Note the filename, Drive file ID, and `modifiedTime` — you'll compare this to Track B.

**HRM-specific note:** HRM has 21 plan areas stored as separate PDFs within folder
`1XZL-JWCLpNl_1JVjSXj86Vt_kHFlbWPM`. Match the plan area name to the filename
(e.g. `timberlealakesidebeechville-lub-*.pdf`).

---

### Track B — Official municipal website (internet search)

Run a `web_search` targeted at the municipality's official planning page to find the publicly
published LUB and confirm its current consolidation date or amendment number.

Suggested queries (try in order until you get a usable result):
- `"[municipality] land use bylaw" filetype:pdf site:[known domain]` (e.g. `site:halifax.ca`)
- `"[plan area] land use bylaw" consolidated 2024 2025 2026`
- `"[municipality] planning" LUB download OR "land use bylaw"`

Then `web_fetch` the municipal planning page to:
- Identify the current LUB document name, version date, and any amendment case numbers
- Grab the direct download URL for the PDF if available

**Common official sources:**
- HRM: `https://www.halifax.ca/business/planning-development/land-use-bylaws`
- CBRM: `https://www.cbrm.ns.ca/planning-and-development.html`
- Other NS municipalities: typically found at `[town].ca/planning` or `[county].ca/development`

---

### Choose the source — version comparison

After completing both tracks, compare versions:

| Situation | Action |
|---|---|
| Drive file **matches** online version | Use Drive file (faster read). Note: ✅ current. |
| Online version is **newer** than Drive file | Use the **online PDF** via `web_fetch`. Flag the Drive file as outdated. |
| Drive file is **newer** or online date is unclear | Use Drive file. Note the uncertainty in the version line. |
| Municipality **not in Drive** at all | Use the online PDF. Note Drive database gap. |
| Both sources **fail** | See Escalation section. |

**When using the online PDF:** use `web_fetch` on the direct PDF URL to download and read its content,
the same way you would read a Drive file. Cite the public URL instead of a Drive link.

Always note the document filename and version from whichever source you use so you can cite accurately.

---

## Step 2B — Version Confirmation (Already Resolved in Step 2)

If you followed the two-track approach in Step 2, the version comparison is already done — proceed
directly to Step 3 using whichever source (Drive or online) was identified as the most current.

**Quick version status line to include in every response:**

- If Drive file used and confirmed current: `✅ Version check: Drive file matches published version as of [date checked].`
- If online PDF used because it was newer:
  ```
  ⚠️ DRIVE FILE OUTDATED — Using current published version
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Drive file version:   [filename / effective date / amendment code]
  Source used:          Official municipal website (newer)
  Published version:    [date / amendment reference found online]
  📄 Source URL:        [URL fetched]
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ```
- If municipality not in Drive: `ℹ️ No Drive file found for this municipality — using published online version.`
- If version comparison inconclusive: `⚠️ Version currency uncertain — Drive file used; verify independently if this is critical.`

**Do not use an outdated Drive file when a verified newer version is available online.**
Always read from the most current source, not the most convenient one.

---

## Step 3 — Extract Zone Information

Once you have the LUB content, locate the zone section. Look for:

- **Zone definition section** (usually titled with the zone code, e.g. "HR-1 Zone" or "Section X – HR-1")
- **Permitted Uses table** — as-of-right uses, discretionary uses, prohibited uses
- **Development Standards table** — minimum lot area, lot frontage, setbacks (front/rear/side),
  maximum lot coverage, maximum building height, floor area ratio (FAR) if applicable
- **General Provisions** that apply to the zone (parking ratios, landscaping, signage, etc.)
- **Overlay zones or special designations** that may modify base zone rules
- **Definitions** for any terms used in the zone section

If the zone is not found in the primary LUB, check:
- Supplementary schedules or appendices
- Whether it may be a special area zone (e.g. a downtown overlay)
- Whether the area has a secondary planning strategy with its own LUB

---

## Step 3A — Map & Schedule Lookup ⚠️ ALWAYS RUN THIS

**Most NS LUBs store critical regulatory information in appendix maps and schedules, not in the
text body.** Overlays such as flood zones, environmental protection areas, heritage districts,
coastal buffer areas, and development agreement boundaries are almost always shown only on maps.
Never consider a zone lookup complete without checking the relevant schedules.

### What to look for

| Map type | What it controls | Common schedule name |
|---|---|---|
| Zoning map | Base zone boundaries | Schedule A, Map 1, Zoning Schedule |
| Flood zone / hazard overlay | Floodway, 100-yr floodplain, watercourse setback | Schedule B, Floodplain Map |
| Environmental protection overlay | Wetlands, waterbodies, riparian buffers | Schedule C, Environmental Schedule |
| Heritage district overlay | Heritage character areas, conservation districts | Schedule D, Heritage Map |
| Development agreement areas | Lands subject to site-specific DAs | Schedule E, Appendix |
| Coastal protection buffer | 30m/60m coastal buffer under provincial rules | Coastal Schedule |
| Serviced/unserviced land | Areas with/without municipal sewer/water | Serviced Areas Map |
| Special planning areas | Downtown designations, growth centres | Special Area Map |

### Track A — Drive database (schedule PDFs)

After locating the main LUB text file in Drive, search the **same municipality folder** for
schedule or appendix files:

1. Use `Google Drive:search_files` with `parentId = '<municipality_folder_id>'` — look for files
   whose names contain `schedule`, `appendix`, `map`, `overlay`, `flood`, `heritage`, `zoning map`.
2. For HRM plan areas, schedules are often embedded at the end of the same LUB PDF — check whether
   the text extraction captured page references like `Schedule A — Zoning Map` and what pages follow.
3. If schedules are separate PDFs in Drive: use `Google Drive:read_file_content` or download and
   view the file as an image to interpret it visually.

**Reading schedule PDFs as images:**
If a schedule PDF is primarily a map (not extractable text), use `web_fetch` on the Drive file
export URL to retrieve it as a viewable file, then interpret the map visually:
```
https://drive.google.com/uc?export=download&id=[FILE_ID]
```
When viewing a map PDF, describe: (a) the spatial extent shown, (b) what overlays are visible
and their legend labels, (c) whether the subject area / zone falls within any overlay boundary.

### Track B — Web map applications

Many NS municipalities publish interactive GIS viewers that show current zoning, overlays, and
schedules. These are often **more current than the PDF schedules** and should always be checked
for overlay questions.

**Run a `web_search` for the municipality's web map, then `web_fetch` the result:**

Priority targets by municipality:

| Municipality | Web map / GIS portal |
|---|---|
| HRM | ExploreHRM: `https://www.halifax.ca/home/online-services/explorehrm` |
| HRM zoning | HRM Zoning Viewer (search: `"HRM zoning map" site:halifax.ca`) |
| CBRM | CBRM GIS Portal (search: `"CBRM GIS" OR "CBRM zoning map"`) |
| NS Province | NSGI Geoportal: `https://nsgi.novascotia.ca/gis/` |
| NS Coastal | NS Coastal Areas Map: `https://novascotia.ca/nse/coast/coastalprotection.asp` |
| NS Flood | NS Flood Risk Areas: search `"Nova Scotia flood risk" GIS map` |
| Other NS | Search: `"[municipality] zoning map" OR "[municipality] GIS viewer"` |

**When fetching a web map app:** `web_fetch` the page and report:
- What layers are available (zoning, flood, heritage, environmental, etc.)
- The direct URL for any specific layer or parcel lookup relevant to the query
- Whether the app provides a parcel-level query (useful if the user has a PID or address)

**For ExploreHRM specifically:**
ExploreHRM allows searching by PID, civic address, or map click. If the user's query involves a
specific parcel, provide the ExploreHRM link with instructions to enable the relevant overlay layers
(Zoning, Floodplain, Heritage, Environmental Protection). The direct link format is:
`https://www.halifax.ca/home/online-services/explorehrm` (no direct parcel deep-link is available).

### Track C — Embedded map pages in PDF LUBs

Many LUBs include zoning maps and schedule maps as the final pages of the same PDF. When you
have already fetched the LUB PDF:

1. Note the total page count from the text extraction.
2. Check whether the extracted text references schedule pages (e.g. "see Schedule A on page 112").
3. Use `web_fetch` on the PDF URL with `#page=N` to navigate to those pages and view them visually.
4. If the maps are raster images embedded in the PDF, describe what you can see: zone boundaries,
   overlay extents, legend colours, and whether the queried zone appears on the map.

### Interpreting map content

When you can view a map (PDF page or web screenshot), extract and report:

- **Zone boundaries**: Does the zone shown on the map match what the text LUB describes? Note any
  inconsistencies (text/map conflicts — the text LUB typically governs unless otherwise stated).
- **Overlay presence**: Is the parcel or zone area within a flood zone, environmental overlay,
  heritage area, or other overlay? Describe the overlay extent and the applicable schedule letter.
- **Legend interpretation**: Read the legend and match colours/hatching to overlay types.
- **Scale and coverage**: Note the map scale and geographic coverage so the user knows what area
  is shown.
- **Amendment notation**: Check if the map has an effective date or amendment notation — compare
  to the text LUB version date.

### When map content modifies the zone answer

If a map reveals an overlay that modifies base zone standards, report it prominently:

```
🗺️ SCHEDULE MAP FINDING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Overlay identified: [e.g. Schedule B — Floodplain Overlay]
Effect on zone:     [e.g. Development within the 1-in-100 floodplain requires
                    flood-proofing to elevation X.X m; accessory structures prohibited
                    in floodway — see Section 4.15]
Map source:         [Drive file / URL / ExploreHRM layer name]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### If maps cannot be retrieved

If no schedule PDF is found in Drive and no web map is accessible:
1. Note in the response that schedule maps could not be verified.
2. List the schedule letters referenced in the LUB text (e.g. "Schedule B — Floodplain Map is
   referenced in Section 4.15 but could not be retrieved").
3. Advise the user to check the municipal planning department or ExploreHRM for overlay confirmation.
4. Never assume an overlay is absent just because it wasn't found in the text extraction.

---

## Step 4 — Determine Response Mode

Before writing the response, identify what the user is actually asking for:

### MODE A — Targeted Question
The user asked a **specific question** about the zone. Use this mode when the query contains
words like "what is", "what are", "can I", "how much", "is X allowed", "minimum", "maximum",
"setback", "height", "parking", "permitted", "how many units", or any other focused inquiry.

**Examples that trigger Mode A:**
- "What is the minimum setback for R-1 in Timberlea?"
- "Can I build a duplex on an HR-2 lot?"
- "What's the max height in ER-3?"
- "How many parking spaces do I need for a fourplex?"
- "Is a home business allowed in R-1?"
- "What's the lot coverage limit?"

**Mode A response format:**

Answer the specific question directly and concisely — lead with the answer, not preamble.
Then add only the context that is directly relevant to that question (e.g. if asked about
setbacks, include any exceptions or special conditions that affect the setback, but do not
list permitted uses or parking ratios). Always include the citation and version header.

```
🏙️ [Zone Code] — [Municipality / Plan Area]
[Version status line — ✅ current or ⚠️ warning, one line only unless a full warning is needed]

[Direct answer to the question, 1–4 sentences or a small table if multiple values apply]

[Any directly relevant exceptions, conditions, or caveats — 1–3 bullet points max]

*(Source: [Document name], Section X.X, p. Y)*
```

If the question touches on **two or more distinct topics** (e.g. "what are the setbacks and
height limits?"), answer each with a short labelled block, still within Mode A — do not
switch to the full summary unless the user asks for a complete overview.

---

### MODE B — Full Zone Summary
Use this mode when the user asks for a **complete overview** of a zone. Trigger words:
"full summary", "everything about", "all the requirements", "complete overview", "what do
I need to know about", "give me all the details", or when no specific question is asked
and the query is just a zone + area (e.g. "R-1 zone Timberlea").

**Mode B response format** — full 10-section structured summary:

---

### 🏙️ [Zone Code] Zone — [Municipality / Plan Area]
**Source:** [Full document title, version/date, and URL]
**⚠️ Amendment notice:** State if the document is a consolidation or if recent amendments may not be reflected. Always advise the user to confirm with the municipal development officer for permit applications.

---

#### 1. Zone Purpose
One or two sentences from the LUB describing the intent of the zone.
> *[Cite: Section X.X, Page Y]*

#### 2. Permitted Uses
**As-of-Right (no approval needed beyond a development permit):**
- [Use 1]
- [Use 2]
- …

**Discretionary / Conditional Uses (require development agreement or council approval):**
- [Use 1] — *[note any conditions]*
- …

**Prohibited Uses (explicitly not allowed):**
- [Use 1] if listed
> *[Cite: Table X / Section X.X, Page Y]*

#### 3. Development Standards

| Standard | Requirement |
|---|---|
| Minimum Lot Area | X m² |
| Minimum Lot Frontage | X m |
| Front Yard Setback | X m |
| Rear Yard Setback | X m |
| Side Yard Setback (each) | X m |
| Maximum Lot Coverage | X % |
| Maximum Building Height | X m / X storeys |
| Floor Area Ratio (FAR) | X : 1 (if applicable) |

> *[Cite: Table X / Section X.X, Page Y]*

#### 4. Parking Requirements
- Residential: X spaces per unit
- Commercial: X spaces per X m² GFA
- Other applicable ratios
> *[Cite: Section X.X, Page Y]*

#### 5. Landscaping & Screening
Summarize any landscaping buffers, screening, or tree retention requirements.
> *[Cite: Section X.X, Page Y]*

#### 6. Signage
Summarize permitted sign types, area limits, and any prohibition on certain sign types.
> *[Cite: Section X.X, Page Y]*

#### 7. Overlay Zones / Special Provisions
List any overlays that apply — drawn from **both** the LUB text and the schedule maps retrieved
in Step 3A. For each overlay, state: its name/schedule letter, what it restricts or requires,
and whether it was confirmed via text, map PDF, or web map app.

Examples of overlays to always check:
- Floodplain / flood risk (Schedule B or similar)
- Environmental protection / wetland buffer
- Heritage district or conservation area
- Coastal protection buffer (provincial, 30m/60m)
- Serviced area boundary (affects permitted uses)
- Development agreement area

If ExploreHRM or another web GIS was checked, note which layers were reviewed.
> *[Cite: Section X.X / Schedule X, Page Y — or Map source: ExploreHRM / Drive file ID]*

#### 8. Subdivision & Lot Creation
Any rules about lot splitting or minimum lot requirements for subdivision within this zone.
> *[Cite: Section X.X, Page Y]*

#### 9. Key Definitions
Define any technical terms used above that are defined in the LUB (e.g. "gross floor area", "dwelling unit", "accessory building").
> *[Cite: Definitions section, Page Y]*

#### 10. ⚠️ Planner's Notes
Flag anything the user should know that isn't obvious from the raw standards:
- Recent amendments not yet in the consolidated document
- Common variance situations
- Development agreement triggers
- Interaction with provincial housing legislation (e.g. Bill 329, 4-unit as-of-right rules)
- Coastal protection rules if near the coast
- Any known ambiguities in the bylaw text

---

*End of Mode B full summary.*

---

## Follow-Up Handling

After any response (Mode A or B), the user may ask a follow-up question about the same zone
without repeating the zone code or area. **Do not re-fetch the LUB for follow-up questions
on the same zone within the same conversation** — the content is already in context. Answer
directly from what was already extracted, citing the same source.

Examples of follow-ups to handle without re-fetching:
- "What about parking?" (after a setback answer)
- "Can I subdivide it?" (after a permitted uses answer)
- "What does that mean for a corner lot?" (after a frontage answer)
- "Is that the same for a duplex?" (after a single-unit standards answer)

If the user switches to a **different zone or municipality**, treat it as a new query and
re-run the full workflow from Step 1.

## Citation Format & Source Deep Links

Every citation must include a **clickable link** to the source document at the exact page where
the cited section appears. The link format depends on which source was used.

### How to resolve section → page number

When extracting zone content from the tool_results file, also extract the page number for each
section you cite. HRM LUBs embed page markers in the text as `Page N` (e.g. `Page 28`).
Use this Python pattern to find the page number nearest to a given section:

```python
import json, re

raw = json.load(open('/mnt/user-data/tool_results/<FILENAME>.json'))
text = raw[0]['text']

def get_page_for_section(text, section_marker):
    idx = text.find(section_marker)
    if idx == -1: return None
    # Find second occurrence (skip TOC)
    idx2 = text.find(section_marker, idx+1)
    target = idx2 if idx2 != -1 else idx
    # Find the nearest Page N marker before this position
    pages = [(m.start(), int(m.group(1))) for m in re.finditer(r'Page (\d+)', text[:target])]
    return pages[-1][1] if pages else None

# Examples:
print(get_page_for_section(text, '4.22 DAYLIGHTING'))   # → 28
print(get_page_for_section(text, '6.2 R-1 ZONE REQUIREMENTS'))  # → 45
print(get_page_for_section(text, '4.27 PARKING'))        # → 29
```

### Link format by source

**Google Drive source:**
```
https://drive.google.com/file/d/[FILE_ID]/view#page=[PAGE_NUMBER]
```

**Online/public URL source:**  
Link directly to the municipal PDF URL with `#page=N` appended if the URL is a direct PDF link.
If the URL is a landing page (not a PDF), link to the landing page and note the section.
```
[URL]#page=[PAGE_NUMBER]   ← for direct PDF URLs
[URL]                       ← for municipal landing pages
```

### Citation format in responses

**Inline citation (Mode A — targeted answer):**
```
*(Source: [LUB name], [Section X.X](LINK), p. N)*
```

**Section citation (Mode B — full summary, after each section):**
```
> *[[LUB name], Section X.X, p. N → 📄 Open source](LINK)*
```

**Sources block at bottom:**
```
SOURCES
-------
[1] Land Use By-law for [Plan Area]
    Filename:       [filename]
    Source:         Google Drive (file ID: [id]) | Official municipal website
    Version:        Eff. [date] | [amendment code if known]
    Version check:  ✅ Current / ⚠️ Drive outdated — online version used / ℹ️ Drive not available
    📄 Open full PDF: [Drive link or public URL]
    Check performed: [today's date]

[2] Schedule / Map Sources  ← include only if map content was retrieved
    Schedule A (Zoning Map):    [Drive file ID or URL] — [interpreted / not accessible]
    Schedule B (Floodplain):    [Drive file ID or URL] — [interpreted / not accessible]
    Web map checked:            ExploreHRM / CBRM GIS / NSGI / None
    Overlay finding:            ✅ No overlays identified / ⚠️ [overlay name] present
```

### Page number lookup — common HRM LUB sections

For any previously extracted LUB, resolve page numbers during extraction and cache them.
Do not look them up again for follow-up questions in the same conversation — use cached values.

**Important notes:**
- `#page=N` counts from the **PDF's internal page 1** (including cover page). Most HRM LUBs start
  with a cover page, so PDF page 1 ≠ document page 1. The `Page N` markers in the extracted text
  reflect the document's own page numbering. Add any cover/blank page offset as needed.
  For the Timberlea LUB, document page numbers match PDF page numbers (no offset — confirmed).
- If page number cannot be determined, provide the base link without `#page` as a fallback.

At the bottom of every response, include a **Sources** block as described above.

---

## Handling Large LUBs

Most LUBs — whether from Drive or fetched online — are large PDFs (100–600+ pages). When
`read_file_content` or `web_fetch` returns a result too large for context (stored in a tool_results
file), use `bash_tool` to extract the relevant zone section with Python:

```python
import json, sys
raw = json.load(open('/mnt/user-data/tool_results/<FILENAME>.json'))
text = raw[0]['text']
# Find zone section — search for zone code or PART heading
idx = text.find('PART 6: R-1')
# Skip TOC entry, find actual content (second occurrence)
idx2 = text.find('PART 6: R-1', idx+1)
target = idx2 if idx2 != -1 else idx
# Find end of section at next PART
end = text.find('PART 7:', target+1)
print(text[target:end])
```

For HRM specifically, zone sections follow a `PART N: ZONE-CODE (ZONE NAME) ZONE` pattern.
Always find the second occurrence (first is the TOC entry). Extract the zone section plus
enough of the General Provisions to capture parking requirements (section 4.27).

---

## Escalation

If the Drive file and the first internet search both fail to yield the zone section:

1. Run a second, broader `web_search` targeting the municipality and zone code directly:
   - `"[municipality]" "[zone code]" zone setback permitted uses`
   - `"[plan area] LUB" "[zone code]" site:[official domain]`
2. Try `web_fetch` on any additional municipal planning or document portal URLs found.
3. If the LUB cannot be located after two web attempts, tell the user what was found and what failed.
4. Provide the municipal planning page URL for manual download.
5. Offer to search for recent amendments separately if the base LUB is found but the zone is absent.

Never fabricate zone standards. If a data point is not found in the source document, say so explicitly.

---

## Read Next

Before responding, read `references/lub-index.md` to locate the correct document.
For HRM Regional Centre queries specifically, also read `references/hrm-regional-centre-notes.md`
for amendment history and known quirks.

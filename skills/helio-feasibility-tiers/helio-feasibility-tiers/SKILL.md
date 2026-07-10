---
name: helio-feasibility-tiers
description: |
  Assemble a tiered pre-development site assessment report for Helio Urban Development. Use this skill whenever the user specifies a report tier (Basic, Detailed, or Comprehensive) or asks about tier definitions, tier differences, or which tier applies to a project. Also trigger when the user uploads GIS research files and wants a feasibility report at a specific tier level, or when they ask about the one-page scorecard (Basic), written report (Detailed), or full pre-development assessment (Comprehensive). If no tier is stated, ask before proceeding.
---

# Helio Pre-Development Site Assessment — Report Assembly Skill

## What This Skill Does

You are a report writer and document assembler for Helio Urban Development. A GIS specialist has already completed all research and analysis. They deliver their findings as a folder of files. Your job is to take those files and produce a polished, professionally formatted feasibility report — both as a PDF and a DOCX — at the tier level specified by the user.

You are not checking, verifying, or re-analyzing anything. The specialist's work is final. You are writing the narrative, formatting the tables, placing the figures, and producing a client-ready document that follows Helio's established report structure for the specified tier.

**All tiers are delivered with maps as outputs.** Every GIS map provided must be embedded both inline in the relevant section and full-page in the appendix.

---

## STEP 0: Confirm the Report Tier

**Before doing anything else**, check whether the user has specified a tier. The tier determines the report format, sections included, and expected page count.

If the user has not stated a tier, ask:
> "Before I start — which report tier is this? Basic (scorecard), Detailed (written report), or Comprehensive (full pre-development assessment)?"

Do not proceed until the tier is confirmed.

### Tier Definitions

All tiers include: project brief, zoning + permitted uses, lot area/dimensions/setbacks, environmental overlays (flood, wetlands, karst), GIS map outputs, utility service level, and a feasibility verdict.

---

**Tier 1 — Basic**
- Format: one-page scorecard (no narrative prose)
- Output: 1 page + maps
- Turnaround: same day
- Who produces: junior + review

Scorecard fields:
- Verdict pill — Feasible / Conditional / Not Feasible
- Project brief summary — client goal + development intent in 1–2 lines
- Property snapshot — PID, lot area, frontage, zone, as-of-right units
- Zoning & regulatory data table — setbacks, height, lot coverage, HAF applicability
- Environmental flags — flood, karst, wetlands, source water rated Clear / Conditional / Risk
- Servicing summary — water, sewer, sewershed — confirmed or to verify
- 3–5 numbered next steps

Excluded: narrative prose, title/covenant review, development scenarios, variance/DA pathway.

---

**Tier 2 — Detailed**
- Format: written report
- Output: 6–12 pages + maps
- Turnaround: 2–4 days
- Who produces: senior lead

Sections (in order):
1. Executive summary — verdict + single most critical constraint or opportunity
2. Project brief — development intent, target unit count, timeline, financing considerations, site-specific constraints raised at intake
3. Property overview — PID, lot area, zone, plan area, ownership status, assessed value
4. Zoning & density analysis — permitted uses, as-of-right unit count with lot size logic, full setback table with bylaw references, height, lot coverage, parking rules, HAF/Centre Plan applicability
5. Environmental & site conditions — VS30/seismic class, karst risk, surface form & topography, DTW & drainage class, flood risk, watercourse buffers, saltwater intrusion if coastal
6. Utility & servicing assessment — water source & plant, wastewater facility, sewershed, stormwater, road access & transit; SCI flagged if density increase is significant
7. Legal encumbrances — all registered instruments from POL with document numbers, what each restricts, impact rated Critical / Moderate / Minor
8. Development scenarios — 2–3 options with unit counts, configuration logic, parking implications, and a preferred recommendation with rationale
9. Recommendations & next steps — numbered action items: surveys, specialist referrals, HRM pre-application meetings, CMHC MLI Select eligibility if applicable

Excluded: buildable corridor/net envelope analysis, topographic/coastal engineering analysis, full section-by-section bylaw breakdown.

---

**Tier 3 — Comprehensive**
- Format: full pre-development assessment
- Output: 14–25+ pages + maps
- Turnaround: 4–7 days
- Who produces: senior lead

All Detailed sections (1–9), plus:

10. Buildable corridor / net envelope analysis — resulting buildable area calculated after overlaying all legal, environmental, and regulatory constraints; expressed as net m² and interpreted against the development goal
11. Topographic & engineering analysis — elevation differential across the lot, drainage direction, rock/bedrock flags, soil class, and foundation implications for the proposed development type
12. Coastal / watercourse setback analysis — OHWM delineation, applicable buffer distances, flood susceptibility at the shoreline, erosion risk (only included for waterfront or watercourse-adjacent sites)
13. Full section-by-section bylaw breakdown — every applicable LUB/MPS standard cited in full with bylaw section number, cross-referenced against site conditions and the proposed development
14. Permitting pathway & specialist referrals — step-by-step permitting sequence with the specific specialists required (NSLS survey, QPII septic designer, geotechnical engineer, Halifax Water SCI) and the trigger condition for each

---

## CRITICAL: Read the DOCX Skill First

Before doing ANYTHING else — after confirming the tier — read the DOCX skill file:
```
/sessions/stoic-sweet-thompson/mnt/.skills/skills/docx/SKILL.md
```

You MUST use the **docx-js** library (Node.js `docx` package) to create the DOCX file. Do NOT use python-docx. The docx-js library produces professional-quality documents with proper styles, headers, footers, colored tables, and embedded images. Follow the DOCX skill's instructions exactly for all document creation patterns.

After creating the DOCX, convert it to PDF using LibreOffice:
```bash
python scripts/office/soffice.py --headless --convert-to pdf output.docx
```

## Step 1: Read and Classify the Source Files

When the user uploads a zip or set of files, unzip and inventory everything. Classify each file into one of these categories by reading its contents:

**GIS Research Files** (produced by the GIS analyst):
- **GIS Summary Report** — A written document (usually .docx) containing site parameters, zoning analysis, development options, environmental findings, and any red flags. This is the primary source of truth for all site data and regulatory context. Present in Detailed and Comprehensive tiers; may be a brief intake note for Basic.
- **Environmental/Geology Map** — A GIS screenshot (PDF) showing surficial geology, elevation contours, drainage characteristics, karst risk, flood hazard, and site classification data. Usually has a data overlay box in the corner.
- **Parcel Info Map** — A GIS screenshot (PDF) showing the property boundary with lot dimensions, bearings, PID, area, and zoning designation.
- **Utilities/Infrastructure Map** — A GIS screenshot (PDF) showing municipal servicing: water, sewer, catchbasins, street lamps, transit stops, and road infrastructure.
- **Additional GIS exports** — There may be supplementary maps (e.g., zoomed boundary details, alternate views, coastal setback overlays). Include these in the appendices.

> Note: Architectural drawings are not part of the Helio feasibility report workflow. If architectural files are uploaded, flag this to the user and confirm whether they should be included or set aside.

### How to Identify Files

Read each file. GIS maps have a data overlay box (usually top-left) with PID, address, area, zone, and layer-specific data. The GIS Summary Report is the only text document — it contains written analysis with sections, paragraphs, and recommendations.

## Step 2: Convert All Source PDFs to Images

**This step is mandatory.** Every PDF source file (GIS maps and architectural drawings) must be converted to a high-resolution PNG image so it can be embedded in the report.

```python
import pypdfium2 as pdfium
from PIL import Image
import os

def convert_pdf_to_png(pdf_path, output_path, scale=2.0):
    """Convert first page of PDF to high-res PNG for embedding in report."""
    pdf = pdfium.PdfDocument(pdf_path)
    page = pdf[0]
    bitmap = page.render(scale=scale)
    img = bitmap.to_pil()
    img.save(output_path, "PNG")
    return output_path

# Convert all source PDFs
# Example:
# convert_pdf_to_png("Environmental.pdf", "fig_environmental.png")
# convert_pdf_to_png("Parcel_info.pdf", "fig_parcel.png")
# convert_pdf_to_png("Utilities.pdf", "fig_utilities.png")
# convert_pdf_to_png("SD101.pdf", "fig_sd101.png")
# etc.
```

For multi-page PDFs, render each page separately — each becomes a distinct figure in the report.

Keep track of which PNG corresponds to which source file. You'll need this mapping when placing figures in the report.

## Step 3: Extract the Data

Read the GIS Summary Report thoroughly — this is where most of your report content will come from. Use python-docx or pandoc to read the .docx file:

```bash
pandoc "GIS Summary Report.docx" -o gis_report.md
```

Extract and organize:

**From the GIS Summary Report:**
- Property identifiers: PID, civic address, lot area, zone designation, plan area
- Lot geometry: frontage, depth, orientation, boundary descriptions
- Geotechnical: geology type, site class, VS30 value, drainage, karst risk, flood hazard
- Topography: surface form, elevation range, grade direction
- Servicing: water supply system, sewer system, stormwater, transit access
- Zoning: applicable by-law, zone standards, any recent amendments
- Development options: what the specialist recommends
- Red flags: any issues flagged (covenants, environmental constraints, access restrictions)
- Legal encumbrances: registered instruments, document numbers, restrictions (required for Detailed and Comprehensive)
- Buildable envelope / topographic detail: elevation differentials, drainage direction, rock flags (required for Comprehensive only)

## Step 4: Select the Report Structure Based on Tier

Use the tier confirmed in Step 0 to determine which report structure to follow.

---

### Tier 1 — Basic: One-Page Scorecard

Do not write a narrative report. Produce a single structured scorecard page with the following fields laid out in a clean, scannable format:

```
[VERDICT BADGE: Feasible / Conditional / Not Feasible]

Project Brief: [1–2 line summary of client goal and development intent]

PROPERTY SNAPSHOT
- PID:
- Lot Area:
- Frontage:
- Zone:
- As-of-right units:

ZONING & REGULATORY
- Min. front setback:
- Min. side setback:
- Max. lot coverage:
- Max. height:
- HAF applicable:

ENVIRONMENTAL FLAGS
- Flood risk:          [Clear / Conditional / Risk]
- Karst risk:          [Clear / Conditional / Risk]
- Wetlands/watercourse:[Clear / Conditional / Risk]
- Source water:        [Clear / Conditional / Risk]

SERVICING
- Water:
- Sewer:
- Sewershed:

NEXT STEPS
1.
2.
3.
```

Followed by the map outputs as appendix pages (one map per page, full page, captioned).

---

### Tier 2 — Detailed: Written Report (6–12 pages + maps)

```
Cover Page
Document Control
Table of Contents
1. Executive Summary
2. Project Brief
3. Property Overview
4. Zoning & Density Analysis
5. Environmental & Site Conditions
6. Utility & Servicing Assessment
7. Legal Encumbrances
8. Development Scenarios
9. Recommendations & Next Steps
Appendix A: GIS Mapping Exhibits
```

---

### Tier 3 — Comprehensive: Full Pre-Development Assessment (14–25+ pages + maps)

Same as Detailed, with these additional sections after Section 9:

```
10. Buildable Corridor / Net Envelope Analysis
11. Topographic & Engineering Analysis
12. Coastal / Watercourse Setback Analysis (waterfront sites only)
13. Full Section-by-Section Bylaw Breakdown
14. Permitting Pathway & Specialist Referrals
Appendix A: GIS Mapping Exhibits
```

---

### Subdivision Projects (Detailed and Comprehensive only)

If the GIS Summary Report discusses subdivision as a development option (multiple lots, two-lot split, etc.), check these indicators:

1. The GIS report discusses subdivision as a development option
2. The report presents separate lot configurations (Lot A, Lot B, etc.)
3. Multiple PIDs are referenced

If ANY are true, expand Sections 4 (Zoning) and 8 (Development Scenarios) to cover each lot individually with separate compliance tables and unit counts per lot. Add a "Subdivision Application Process" item under Recommendations. Do NOT collapse a multi-lot project into a single-lot narrative.

## Step 5: Write the Report Content

### Voice and Tone

The Helio report voice is:
- **Technical but readable.** Write for a property owner or investor who understands real estate but may not be an engineer. Define technical terms the first time they appear (e.g., "Site Class B (Medium Hard Rock) under the National Building Code").
- **Confident and direct.** State findings as facts, not opinions. "The site is characterized by excellent structural integrity" — not "the site appears to have good conditions."
- **Concise but thorough.** Each paragraph should advance the reader's understanding. No filler, no repetition between sections. For Detailed and Comprehensive tiers, write full multi-sentence paragraphs — not bullet points. Each narrative section should have 2–4 substantial paragraphs.
- **Professionally neutral.** When discussing constraints or risks, present them factually without being alarmist or dismissive.

> For Tier 1 (Basic), there is no narrative prose. All content is structured as labelled fields and flagged data — see the scorecard format in Step 4.

### Section-by-Section Writing Guide

The following guides apply to **Tier 2 (Detailed)** and **Tier 3 (Comprehensive)**. For Tier 1, skip directly to Step 6 and build the scorecard layout.

---

**Cover Page** (own section in docx-js, no headers/footers):
- Title: "PRE-DEVELOPMENT SITE ASSESSMENT" (spaced caps, dark blue #2B5797, 14pt)
- Subtitle based on tier:
  - Detailed: "Feasibility & Site Analysis Report"
  - Comprehensive: "GIS Analysis & Development Feasibility Report"
- Blue horizontal rule separator
- Property address, PID, lot number, zone
- Project number (use format HUD-YYYY-NNN if not provided)
- Revision, date, proposed use, lot area, zoning — formatted as a label/value grid
- Tier indicator: "Report Tier: [Basic / Detailed / Comprehensive]"
- Blue horizontal rule separator
- "PREPARED BY" / "Helio Urban Development" / "Halifax, Nova Scotia"
- Confidentiality notice in smaller italic text

**Document Control** (starts new page):
- Revision history table: columns Rev, Date, Description, Prepared By, Reviewed By. Use "Helio Urban Development" as the Prepared By value (never "Claude AI" or any AI reference — this is a professional client deliverable).
- Distribution table: Recipient, Organization, Copies
- Limitations and Conditions: Two full paragraphs stating that findings are based on desktop GIS analysis. State what the report does NOT constitute (geotechnical investigation, legal survey, environmental assessment, structural engineering analysis). State that zoning conclusions are subject to confirmation by the municipal Development Officer.

**Table of Contents:**
- Do NOT use the docx-js `TableOfContents` field — it produces an empty page in PDF because LibreOffice cannot resolve the field codes during conversion.
- Instead, build a **manual Table of Contents** using Paragraphs with dot-leader tab stops. Create one paragraph per section/subsection. Use approximate page numbers based on content length. The TOC in this type of document is primarily a structural guide — approximate page numbers are acceptable for Rev 0 documents.
- Format: section titles in the same font as body text, page numbers right-aligned with dot leaders. Indent subsections slightly.

**Section 1 — Executive Summary:**
- Two to three paragraphs. First: site description and physical conditions. Second: the proposed development goal and key constraints. Third: the verdict (feasible, conditional, or not feasible) with the primary opportunity and primary constraint stated directly.
- If there are red flags, mention them here.

**Section 2 — Project Brief:**
- Client's development intent, target unit count or development goal, timeline if provided, financing considerations (e.g. CMHC MLI Select if applicable), and any site-specific constraints raised at intake.

**Section 3 — Property Overview:**
- Narrative paragraph describing the lot: legal description, orientation, frontage, depth, neighbourhood context, current state.
- **Table 3.1 — Property Data Summary:** columns for Attribute, Detail, Source. Include PID, civic address, total lot area, zoning designation, frontage, average depth, lot orientation, assessed value, ownership status.
- **Figure 3.1** — Embed the Parcel Info map PNG. Centered, with italic caption below.

**Section 4 — Zoning & Density Analysis:**
- Permitted uses under the zone, as-of-right unit count with lot size logic, full setback table with bylaw section references, height limit, lot coverage maximum, parking rules, HAF/Centre Plan applicability.
- **Table 4.1 — Zone Development Standards** (Development Standard, By-law Requirement, Bylaw Reference).
- For Comprehensive tier only: include a full section-by-section citation of every applicable LUB/MPS standard cross-referenced with site conditions — this becomes Section 13.

**Section 5 — Environmental & Site Conditions:**
- VS30/seismic class, karst risk, surface form & topography, depth-to-water & drainage class, flood risk, watercourse buffers, saltwater intrusion if coastal.
- **Table 5.1 — Site Conditions Summary** (Parameter, Value, Classification, Reference).
- **Figure 5.1** — Embed the Environmental/Geology map PNG.

**Section 6 — Utility & Servicing Assessment:**
- Water source & plant, wastewater facility, sewershed, stormwater, road access & transit. Flag SCI requirement if density increase is significant.
- **Table 6.1 — Municipal Servicing Summary** (Service, Provider/System, Status, Notes).
- **Figure 6.1** — Embed the Utilities/Infrastructure map PNG.

**Section 7 — Legal Encumbrances:**
- All registered instruments from POL — easements, covenants, development agreements — with document numbers, what each restricts, and impact rated Critical / Moderate / Minor.
- **Table 7.1 — Registered Encumbrances** (Instrument, Document No., Restriction, Development Impact).
- If no encumbrances exist, state this explicitly.

**Section 8 — Development Scenarios:**
- 2–3 development options with unit counts, configuration logic, and parking implications. Conclude with a preferred recommendation and rationale.
- For subdivision projects: present per-lot breakdowns with separate unit counts and configurations per lot.

**Section 9 — Recommendations & Next Steps:**
- Numbered action items. Include: surveys required, specialist referrals (NSLS, QPII septic, geotechnical if flagged), HRM pre-application meeting if variance or DA is needed, CMHC MLI Select eligibility check if applicable.
- Red flags from the GIS report MUST appear here as specific action items.
- **Table 9.1 — Recommended Actions** (#, Action, Responsible Party, Priority/Timing).
- For subdivision projects: add a "Subdivision Application Process" item covering survey requirements, lot boundary definition, and approval timeline.

---

**Tier 3 Additional Sections:**

**Section 10 — Buildable Corridor / Net Envelope Analysis:**
- Calculate the net buildable area remaining after overlaying all legal, environmental, and regulatory constraints. Express as net m² and interpret against the development goal (e.g. "sufficient for a 4-unit building with parking" or "envelope is constrained — single unit only").

**Section 11 — Topographic & Engineering Analysis:**
- Elevation differential across the lot, drainage direction, rock/bedrock flags, soil class, and foundation implications for the proposed development type.

**Section 12 — Coastal / Watercourse Setback Analysis** (waterfront/adjacent sites only):
- OHWM delineation, applicable buffer distances under the relevant regulation, flood susceptibility at the shoreline, erosion risk assessment.
- Omit this section entirely for inland sites.

**Section 13 — Full Section-by-Section Bylaw Breakdown:**
- Every applicable LUB/MPS standard cited in full with bylaw section number, the requirement, and how the site/proposal measures against it.

**Section 14 — Permitting Pathway & Specialist Referrals:**
- Step-by-step permitting sequence. For each required specialist (NSLS survey, QPII septic designer, geotechnical engineer, Halifax Water SCI), state the trigger condition and timing.

---

**Appendix A — GIS Mapping Exhibits:**
- Each GIS map on its own page at maximum size. Caption with exhibit number (A.1, A.2, etc.) and descriptive title.
- These are FULL PAGE figures — the image should fill most of the page.
- All tiers include this appendix.

## Step 6: Build the DOCX with docx-js

**You MUST use the docx-js Node.js library.** Install with `npm install -g docx` if needed.

**Expected page counts by tier:**
- Tier 1 (Basic): 1 page scorecard + map appendix pages
- Tier 2 (Detailed): 6–12 pages + map appendix
- Tier 3 (Comprehensive): 14–25+ pages + map appendix

### Document Structure

For Tier 1 (Basic), the document has two sections:
1. **Scorecard page** — No headers/footers, structured field layout with verdict badge
2. **Appendix section** — One map per page, full-page figures, captioned

For Tier 2 and Tier 3, the document has multiple sections:
1. **Cover page section** — No headers/footers, custom layout
2. **Document control section** — Different first-page header
3. **Body section** — Standard headers/footers, contains TOC through final section
4. **Appendix A section** — GIS maps, may use landscape orientation for wide maps

### Color Palette

```javascript
const COLORS = {
  darkBlue: "2B5797",      // Headings, cover page text
  mediumBlue: "4472C4",    // Table header backgrounds
  lightBlue: "D5E8F0",     // Table alternating rows
  white: "FFFFFF",
  lightGrey: "F2F2F2",     // Table alternating rows
  black: "000000",
  darkGrey: "333333",      // Body text
};
```

### Key Formatting Patterns

**Heading styles** (override built-in):
```javascript
paragraphStyles: [
  { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
    run: { size: 32, bold: true, font: "Arial", color: COLORS.darkBlue },
    paragraph: { spacing: { before: 360, after: 200 }, outlineLevel: 0,
      border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: COLORS.darkBlue, space: 4 } } } },
  { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
    run: { size: 26, bold: true, font: "Arial", color: COLORS.darkBlue },
    paragraph: { spacing: { before: 240, after: 160 }, outlineLevel: 1 } },
  { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
    run: { size: 24, bold: true, font: "Arial", color: COLORS.darkBlue },
    paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 2 } },
]
```

**Tables with blue headers:**
```javascript
// Header row cells get blue background with white text
shading: { fill: COLORS.mediumBlue, type: ShadingType.CLEAR }
// Header text
new TextRun({ text: "Header", bold: true, color: COLORS.white, font: "Arial", size: 20 })
// Alternating data rows
shading: { fill: rowIndex % 2 === 0 ? COLORS.lightGrey : COLORS.white, type: ShadingType.CLEAR }
```

**Embedded figures:**
```javascript
// Read the PNG image, then embed it
const imgBuffer = fs.readFileSync("fig_parcel.png");
// Calculate dimensions to fit within page margins (max ~6.5" wide = 9360 DXA)
// Maintain aspect ratio. For landscape drawings, use full width.
new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new ImageRun({
    type: "png",
    data: imgBuffer,
    transformation: { width: 580, height: 420 }, // pixels — adjust per image aspect ratio
    altText: { title: "Figure 3.1", description: "Property boundary map", name: "fig_parcel" }
  })]
});
// Caption below
new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 120, after: 240 },
  children: [new TextRun({ text: "Figure 3.1 — Property boundary and lot dimensions. Source: HRM GIS.", italics: true, size: 18, font: "Arial" })]
});
```

**For appendix full-page figures**, use the maximum dimensions that maintain aspect ratio within the page margins. The goal is to fill as much of the page as possible — minimize white space:
```javascript
// Full-page figure: calculate from actual image dimensions to fill the page
// Max content area: ~580pt wide x ~750pt tall (Letter with 1" margins, minus header/footer)
// Use the image's actual aspect ratio to determine which dimension is limiting
const img = Image.open("fig.png"); // Get actual w, h first with Python
// If landscape-oriented image: width is limiting → use max width, calculate height
// If portrait-oriented image: height is limiting → use max height, calculate width
transformation: { width: 580, height: calculated } // Always maintain aspect ratio
```

**Headers and footers** (for body section):
```javascript
headers: {
  default: new Header({
    children: [new Paragraph({
      children: [
        new TextRun({ text: "14 Holland Ave, Bedford • Pre-Development Site Assessment", font: "Arial", size: 16, color: COLORS.darkGrey }),
        new TextRun({ children: ["\tHUD-2026-014"], font: "Arial", size: 16, color: COLORS.darkGrey }),
      ],
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
      border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: COLORS.mediumBlue, space: 4 } },
    })]
  })
},
footers: {
  default: new Footer({
    children: [new Paragraph({
      children: [
        new TextRun({ text: "Helio Urban Development • Confidential", font: "Arial", size: 16, color: COLORS.darkGrey, italics: true }),
        new TextRun({ children: ["\tPage "] }),
        new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 16 }),
      ],
      tabStops: [{ type: TabStopType.RIGHT, position: TabStopPosition.MAX }],
      border: { top: { style: BorderStyle.SINGLE, size: 2, color: COLORS.lightGrey, space: 4 } },
    })]
  })
}
```

### Image Sizing Strategy

When embedding images, calculate the appropriate size based on the image's aspect ratio. The max content width is ~580px for inline figures and ~700px for full-page appendix figures. Use the PIL library to get the actual image dimensions first:

```python
from PIL import Image
img = Image.open("fig_parcel.png")
w, h = img.size
aspect = h / w
# For inline: target_width = 580, target_height = int(580 * aspect)
# For full-page: target_width = 700, target_height = int(700 * aspect)
print(f"Inline: {580} x {int(580 * aspect)}")
print(f"Full page: {700} x {int(700 * aspect)}")
```

### Building the Document

Write the docx-js code as a single Node.js script. The script should:

1. Read all PNG images from the working directory
2. Build all paragraphs, tables, and image elements
3. Assemble into sections with proper headers/footers
4. Pack and write to the output .docx file
5. Validate using `python scripts/office/validate.py`

The script will be long (500+ lines). Write it in chunks — build the cover section first, then document control, then body, then appendices. Test that it generates a valid .docx at each stage.

After producing the DOCX, convert to PDF:
```bash
python scripts/office/soffice.py --headless --convert-to pdf output.docx
```

## Step 7: Final Quality Check

Before delivering, verify:

**All tiers:**
- [ ] DOCX opens without errors
- [ ] PDF renders correctly
- [ ] All GIS map images are embedded in the appendix (count should match number of source PDFs)
- [ ] "Prepared By" says "Helio Urban Development" (not "Claude AI" or any AI name)
- [ ] All data values match the source files exactly
- [ ] Appendix map images are sized to fill most of the page (minimal white space below figures)
- [ ] Report tier is clearly indicated on the cover page

**Tier 1 (Basic) only:**
- [ ] Output is one page — no narrative prose anywhere
- [ ] Verdict badge is present and clearly stated
- [ ] All scorecard fields are filled — no blank rows
- [ ] Environmental flags each have a Clear / Conditional / Risk rating
- [ ] 3–5 next steps are present and site-specific

**Tier 2 (Detailed) and Tier 3 (Comprehensive):**
- [ ] Table of Contents page is populated (not blank)
- [ ] Tables have blue header rows with white text
- [ ] Headers and footers appear on body pages
- [ ] Cover page has no header/footer
- [ ] Page count is within tier range (Detailed: 6–12; Comprehensive: 14–25+)
- [ ] Red flags appear in both Executive Summary and Recommendations
- [ ] Section 7 (Legal Encumbrances) explicitly states if no encumbrances exist
- [ ] If subdivision: Sections 4 and 8 have per-lot subsections with separate data

**Tier 3 (Comprehensive) only:**
- [ ] Section 10 (Buildable Envelope) expresses net m² and interprets against the development goal
- [ ] Section 12 (Coastal) is present only if site is waterfront or watercourse-adjacent; omitted otherwise
- [ ] Section 13 cites every applicable bylaw standard with section numbers
- [ ] Section 14 names each specialist with trigger condition

### File Naming

Output files:
- `[Address]_[Tier]_Feasibility_Report_Rev[N].docx`
- `[Address]_[Tier]_Feasibility_Report_Rev[N].pdf`

Where [Address] uses underscores (e.g., `15_Springhill_Rd`), [Tier] is `Basic`, `Detailed`, or `Comprehensive`, and [N] is the revision number (default to 0).

Example: `15_Springhill_Rd_Detailed_Feasibility_Report_Rev0.docx`

## Important Reminders

- **Confirm the tier before starting.** If not stated, ask. The tier controls everything — format, sections, page count, and file name.
- **You are assembling, not analyzing.** Every data point, conclusion, and recommendation comes from the specialist files. Do not invent findings or second-guess the specialist.
- **When in doubt, quote the source.** Rephrase for the report's voice, but preserve the substance exactly.
- **Red flags are not optional.** If the GIS report flags an issue, it must appear in both Executive Summary and Recommendations (Detailed and Comprehensive), or in the Next Steps field (Basic).
- **Numbers must be transcribed exactly.** Do not round, convert, or recalculate unless showing both metric and imperial.
- **Every source PDF must appear as an embedded image** — both inline in the relevant section (Detailed/Comprehensive) AND full-page in the appendix. This is what makes the report a complete, standalone document. For Basic, maps go in the appendix only.
- **No architectural drawings.** If architectural files are in the upload, flag them to the user — they are not part of the Helio feasibility report workflow.
- **Adapt depth to tier.** Basic = one-page scorecard. Detailed = 6–12 pages narrative. Comprehensive = 14–25+ pages with full engineering and legal depth. The backbone stays the same; the depth scales with the tier.
---
name: helio-feasibility-report
description: |
  Assemble a pre-development site assessment report for Helio Urban Development from specialist deliverables. Use this skill whenever the user uploads a zip folder (or set of files) containing GIS research and architectural drawings for a development project and wants a feasibility report, site assessment, pre-development report, or development assessment assembled from them. Also trigger when the user mentions assembling a report from specialist files, combining GIS and architectural data into a deliverable, or producing a Helio-formatted feasibility study. This is a document assembly and narrative writing skill — the analytical work has already been done by specialists.
---

# Helio Pre-Development Site Assessment — Report Assembly Skill

## What This Skill Does

You are a report writer and document assembler for Helio Urban Development. Specialists (a GIS analyst and an architect) have already completed all research, analysis, and design work. They deliver their findings as a folder of files. Your job is to take those files and produce a polished, professionally formatted Pre-Development Site Assessment report — both as a PDF and a DOCX.

You are not checking, verifying, or re-analyzing anything. The specialists' work is final. You are writing the narrative, formatting the tables, placing the figures, and producing a client-ready document that follows Helio's established report structure.

**Expected output:** A 25–35 page professional document with embedded maps and drawings, branded formatting, and comprehensive narrative. Single-lot projects will be ~25 pages; subdivision projects with multiple lots and development options will be ~30–35 pages.

## CRITICAL: Read the DOCX Skill First

Before doing ANYTHING else, read the DOCX skill file:
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
- **GIS Summary Report** — A written document (usually .docx) containing site parameters, zoning analysis, development options, environmental findings, and any red flags. This is the primary source of truth for all site data and regulatory context.
- **Environmental/Geology Map** — A GIS screenshot (PDF) showing surficial geology, elevation contours, drainage characteristics, karst risk, flood hazard, and site classification data. Usually has a data overlay box in the corner.
- **Parcel Info Map** — A GIS screenshot (PDF) showing the property boundary with lot dimensions, bearings, PID, area, and zoning designation.
- **Utilities/Infrastructure Map** — A GIS screenshot (PDF) showing municipal servicing: water, sewer, catchbasins, street lamps, transit stops, and road infrastructure.
- **Additional GIS exports** — There may be supplementary maps (e.g., zoomed boundary details, alternate views). Include these in the appendices.

**Architectural Drawings** (produced by the architect):
- **Site Plan (SD100/SD101/SC100)** — Shows building placement on the lot with setback lines, driveway, parking, and often includes a 3D schematic view plus an aerial photo context.
- **Proposed Site Development Plan (SD102/SC102)** — Shows the proposed development with lot coverage computation tables, non-permeable surface calculations, parking requirements, building requirements, and amenity area computations. This is the primary source for all zoning compliance numbers.
- **Floor Plans / Elevations (SD200)** — Shows interior layouts or building elevations/sections. May include height compliance against building limits.
- **Upper Floor / Massing (SD300)** — Shows upper floors and/or 3D massing views.

### How to Identify Files

Read each file. GIS maps have a data overlay box (usually top-left) with PID, address, area, zone, and layer-specific data. Architectural drawings have a title block (usually bottom-right) with the Helio logo, drawing number (SD100, SD102, etc.), sheet title, scale, and date. The GIS Summary Report is the only text document — it contains written analysis with sections, paragraphs, and recommendations.

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

**From the Architectural Drawings (read the computation tables visually from the PDF images):**
- Lot coverage computation: total lot area, building footprint, lot coverage percentage
- Building program: floor areas by level, total building area, unit count and configuration
- Non-permeable surface: walkways, driveways, parking areas, total and ratio
- Parking: spaces provided vs. required
- Setbacks: front, side, rear — as shown on the site plan
- Amenity/landscaping: front yard landscaped area and percentage
- Building height: if elevation drawings show height against a limit

## Step 4: Determine the Report Structure — SINGLE-LOT vs. SUBDIVISION

**THIS STEP IS CRITICAL. You must correctly identify whether the project is single-lot or subdivision before writing anything.**

### How to Detect Subdivision Projects

Check these indicators — if ANY are true, this is a subdivision project and you MUST use the subdivision structure:

1. **The architectural drawings (SD102/SC102) show computation tables for multiple lots** (e.g., "Lot A", "Lot B", "Lot C" or "Lot 1", "Lot 2"). Look for separate computation boxes per lot on the drawing.
2. **The GIS Summary Report discusses subdivision as a development option** (e.g., "two-lot subdivision", "three-lot configuration", "subdivide the property").
3. **The site plan (SD101/SC100) shows multiple building footprints on separate lots** with lot boundary lines dividing the property.
4. **The drawing title block says "SUBDIVIDED SITE DEVELOPMENT PLAN"** or similar.

If the project involves subdivision, you MUST expand Sections 6 and 7 to cover each lot individually. Do NOT collapse a multi-lot project into a single-lot narrative — this is the most common error and it produces an incomplete, inaccurate report.

If the GIS report presents BOTH a single-lot option AND a subdivision option, present the option that matches the architectural drawings as the primary analysis, and discuss the alternative in a dedicated "Development Options" subsection.

### Single-Lot Development (e.g., 275 Osborne — one lot, one building)

```
Cover Page
Document Control (revision history, distribution, limitations)
Table of Contents
1. Introduction and Scope
2. Executive Summary
3. Site Description and Property Data
4. Engineering and Site Conditions
   4.1 Geotechnical Overview
   4.2 Topography and Drainage
5. Municipal Infrastructure and Servicing
   5.1 Utility Services
   5.2 Transportation and Public Realm
6. Zoning and Regulatory Analysis
   6.1 Applicable Regulations
   6.2 Building Envelope Analysis
   6.3 Zoning Compliance Summary
7. Proposed Development Program
   7.1 Building Program
   7.2 Site Plan
   7.3 Floor Plans
   7.4 Design Narrative
8. Recommendations and Next Steps
   8.1 Pre-Construction Due Diligence
   8.2 Excavation and Foundation
   8.3 Permitting Pathway
9. References
Appendix A: GIS Mapping Exhibits
Appendix B: Schematic Design Drawings
```

### Subdivision Development (e.g., 14 Holland — multiple lots, multiple buildings)

Same backbone, but Sections 6 and 7 MUST expand to cover each lot separately. Each lot gets its own compliance table and building program table with data pulled from its specific computation box on the SD102 drawing:

```
6. Zoning and Regulatory Analysis
   6.1 Applicable Regulations (including any HAF amendments or recent by-law changes)
   6.2 Lot A — Building Envelope and Compliance (with Table 6.2 per-lot compliance)
   6.3 Lot B — Building Envelope and Compliance (with Table 6.3 per-lot compliance)
   6.4 Lot C — Building Envelope and Compliance (with Table 6.4 per-lot compliance, if applicable)
   6.5 Consolidated Compliance Summary
7. Proposed Development Program
   7.1 Development Options (REQUIRED if the GIS report presents alternatives — describe each option with a paragraph, then state which one the architectural drawings develop)
   7.2 Lot A — Building Program (with Table 7.1: floor areas, unit count, coverage for this lot)
   7.3 Lot B — Building Program (with Table 7.2: floor areas, unit count, coverage for this lot)
   7.4 Lot C — Building Program (with Table 7.3, if applicable)
   7.5 Site Plans (embed SD101/SC100)
   7.6 Elevations and Massing (embed SD200)
   7.7 Design Narrative (discuss overall subdivision design, how lots relate to each other and the street)
```

Also add a subsection under Recommendations (e.g., 8.4 Subdivision Application Process) addressing survey requirements, lot boundary definition, and the subdivision approval timeline.

## Step 5: Write the Report Content

### Voice and Tone

The Helio report voice is:
- **Technical but readable.** Write for a property owner or investor who understands real estate but may not be an engineer. Define technical terms the first time they appear (e.g., "Site Class B (Medium Hard Rock) under the National Building Code").
- **Confident and direct.** State findings as facts, not opinions. "The site is characterized by excellent structural integrity" — not "the site appears to have good conditions."
- **Concise but thorough.** Each paragraph should advance the reader's understanding. No filler, no repetition between sections. But DO write full, multi-sentence paragraphs — not bullet points. Each narrative section should have 2–4 substantial paragraphs.
- **Professionally neutral.** When discussing constraints or risks, present them factually without being alarmist or dismissive.

### Section-by-Section Writing Guide

**Cover Page** (own section in docx-js, no headers/footers):
- Title: "PRE-DEVELOPMENT SITE ASSESSMENT" (spaced caps, dark blue #2B5797, 14pt)
- Subtitle: "GIS Analysis & Development Feasibility Report" (24pt bold, dark blue)
- Blue horizontal rule separator
- Property address, PID, lot number, zone
- Project number (use format HUD-YYYY-NNN if not provided)
- Revision, date, proposed use, lot area, zoning — formatted as a label/value grid
- Blue horizontal rule separator
- "PREPARED BY" / "Helio Urban Development" / "Halifax, Nova Scotia"
- Confidentiality notice in smaller italic text

**Document Control** (starts new page):
- Revision history table: columns Rev, Date, Description, Prepared By, Reviewed By. Use "Helio Urban Development" as the Prepared By value (never "Claude AI" or any AI reference — this is a professional client deliverable).
- Distribution table: Recipient, Organization, Copies
- Limitations and Conditions: Two full paragraphs stating that findings are based on desktop GIS analysis and schematic drawings. State what the report does NOT constitute (geotechnical investigation, legal survey, environmental assessment, structural engineering analysis). State that zoning conclusions are subject to confirmation by the municipal Development Officer.

**Table of Contents:**
- Do NOT use the docx-js `TableOfContents` field — it produces an empty page in PDF because LibreOffice cannot resolve the field codes during conversion.
- Instead, build a **manual Table of Contents** using Paragraphs with dot-leader tab stops. Create one paragraph per section/subsection, with the section title on the left and page number placeholder on the right connected by dot leaders. Use `PositionalTab` with `PositionalTabLeader.DOT` for the dot leaders.
- Since you cannot know exact page numbers at build time, use approximate page numbers based on content length (cover=1, doc control=2, TOC=3, then estimate ~1–2 pages per section). The TOC in this type of document is primarily a structural guide — approximate page numbers are acceptable for Rev 0 documents.
- Format: section titles in the same font as body text, page numbers right-aligned with dot leaders. Indent subsections (4.1, 5.2, etc.) slightly.

**Section 1 — Introduction and Scope:**
- One paragraph stating who retained Helio, for what property, and that this report integrates GIS analysis with architectural feasibility findings.
- One paragraph describing the scope of work (characterization of site conditions, servicing confirmation, zoning analysis, assessment of the proposed building program).
- "Applicable Standards and Data Sources" subsection with a numbered list of every source: the specific by-law, the National Building Code reference, HRM GIS Open Data (with access date), and each architectural drawing by number, title, author, and date.

**Section 2 — Executive Summary:**
- Two to three paragraphs. First: site description and physical conditions. Second: the proposed development and key metrics. Third: the recommendation (proceed, or proceed with caveats).
- If the project has multiple development options, summarize the preferred path.
- If there are red flags, mention them here.

**Section 3 — Site Description and Property Data:**
- Narrative paragraph describing the lot: legal description, orientation, frontage, depth, neighbourhood context, current state.
- **Table 3.1 — Property Data Summary:** columns for Attribute, Detail, Source. Include PID, civic address, total lot area, zoning designation, frontage, average depth, lot orientation.
- **Figure 3.1** — Embed the Parcel Info map PNG. Centered, with italic caption below.

**Section 4 — Engineering and Site Conditions:**
- **4.1 Geotechnical Overview:** Two paragraphs on subsurface geology, site classification, VS30 value, foundation implications, drainage, karst risk. Include **Table 4.1 — Site Conditions Summary** (Parameter, Value, Classification, Reference).
- **4.2 Topography and Drainage:** Two paragraphs on surface form, elevation range, grade direction, drainage implications, flood hazard. Include **Table 4.2 — Topography and Drainage Parameters**.
- **Figure 4.1** — Embed the Environmental/Geology map PNG.

**Section 5 — Municipal Infrastructure and Servicing:**
- **5.1 Utility Services:** Two paragraphs on water, sewer, stormwater. Name the specific systems. Include **Table 5.1 — Municipal Servicing Summary** (Service, Provider/System, Status, Notes).
- **5.2 Transportation and Public Realm:** One to two paragraphs on street access, transit stops, street lighting, waste collection.
- **Figure 5.1** — Embed the Utilities/Infrastructure map PNG.

**Section 6 — Zoning and Regulatory Analysis:**
- **6.1 Applicable Regulations:** Two paragraphs on governing by-law and zone. If there are recent amendments (like HAF changes), describe them in detail.
- Include **Table 6.1 — Zone Development Standards** (Development Standard, By-law Requirement, Reference).
- **6.2+ Building Envelope Analysis** (per lot for subdivisions): One paragraph per lot on buildable area after setbacks. Include **Table 6.N — Zoning Compliance Assessment** per lot (Standard, Requirement, On Plan, Status — with ✓ Compliant markers).
- **6.N Consolidated Compliance Summary** (for subdivisions): Brief paragraph summarizing that all lots comply.
- **Figure 6.1** — Embed the SD102/SC102 computation drawing PNG (the one with the computation tables — NOT the SD101 site plan with aerial context). Double-check the drawing number in the title block before captioning.

**Section 7 — Proposed Development Program:**
- **7.1 Building Program** (per lot): Describe building type, unit configuration, floor areas. Include **Table 7.N — Building Program Summary** per lot (Building Parameter, Value, Source).
- **7.N Site Plan:** One paragraph describing what the drawing shows. Embed **Figure 7.N** — the SD101/SC100 site plan PNG.
- **7.N Elevations and Massing:** One paragraph. Embed **Figure 7.N** — the SD200 drawing PNG.
- **7.N Design Narrative:** Two to three paragraphs describing how the building form relates to the neighbourhood, how parking and landscaping are handled, how the massing responds to site geometry. This is the most interpretive section — draw from the GIS report's development options analysis.

**Section 8 — Recommendations and Next Steps:**
- **8.1 Pre-Construction Due Diligence:** Paragraph on what needs to happen before permits.
- **8.2 Excavation and Foundation** (if bedrock present): Paragraph on rock excavation methodology.
- **8.3 Permitting Pathway:** Paragraph on whether as-of-right or variance/rezoning needed.
- Include **Table 8.1 — Recommended Actions** (#, Action, Responsible Party, Priority/Timing).
- Red flags from the GIS report MUST appear here as specific action items.

**Section 9 — References:**
- Numbered list of all sources: by-laws, building codes, GIS data, and each architectural drawing.

**Appendix A — GIS Mapping Exhibits:**
- Each GIS map on its own page at maximum size. Caption with exhibit number (A.1, A.2, etc.) and descriptive title.
- These are FULL PAGE figures — the image should fill most of the page.

**Appendix B — Schematic Design Drawings:**
- Each architectural drawing on its own page at maximum size. Caption with exhibit number (B.1, B.2, etc.) matching drawing numbers.
- These are FULL PAGE figures — the image should fill most of the page.

## Step 6: Build the DOCX with docx-js

**You MUST use the docx-js Node.js library.** Install with `npm install -g docx` if needed.

### Document Structure

The document must have multiple sections in docx-js to handle different page layouts:

1. **Cover page section** — No headers/footers, custom layout
2. **Document control section** — Different first-page header
3. **Body section** — Standard headers/footers, contains TOC through Section 9
4. **Appendix sections** — May use landscape orientation for wide drawings

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
- [ ] DOCX opens without errors
- [ ] PDF renders correctly
- [ ] Table of Contents page is populated (not blank)
- [ ] All source images are embedded (count: should match number of source PDFs)
- [ ] Tables have blue header rows with white text
- [ ] Headers and footers appear on body pages
- [ ] Cover page has no header/footer
- [ ] Page count is 25–35 pages
- [ ] All data values match the source files exactly
- [ ] Red flags appear in both Executive Summary and Recommendations
- [ ] Figure captions match the actual drawing embedded (verify drawing number in title block vs caption text)
- [ ] "Prepared By" in Document Control says "Helio Urban Development" (not "Claude AI" or any AI name)
- [ ] If subdivision: Sections 6 and 7 have per-lot subsections with separate compliance/program tables
- [ ] Appendix images are sized to fill most of the page (minimal white space below figures)

### File Naming

Output files:
- `[Address]_Pre_Development_Assessment_Rev[N].docx`
- `[Address]_Pre_Development_Assessment_Rev[N].pdf`

Where [Address] uses underscores (e.g., `14_Holland_Ave`) and [N] is the revision number (default to 0).

## Important Reminders

- **You are assembling, not analyzing.** Every data point, conclusion, and recommendation comes from the specialist files. Do not invent findings or second-guess the specialists.
- **When in doubt, quote the source.** Rephrase for the report's voice, but preserve the substance exactly.
- **Red flags are not optional.** If the GIS report flags an issue, it must appear in both Executive Summary and Recommendations.
- **Numbers must be transcribed exactly.** Do not round, convert, or recalculate unless showing both metric and imperial.
- **Every source PDF must appear as an embedded image** — both inline in the relevant section AND full-page in the appendices. This is what makes the report a complete, standalone document.
- **Adapt to complexity.** A single-lot project gets ~25 pages. A subdivision with multiple lots and options gets ~30–35 pages. The backbone stays the same; the depth scales with the project.
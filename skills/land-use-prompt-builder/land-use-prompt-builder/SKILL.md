---
name: land-use-prompt-builder
description: >
  Extracts project-specific details from uploaded planning documents (PDFs, images, maps,
  deeds, property screenshots, LUBs, environmental maps) and rebuilds a standardized Land Use
  Feasibility Report prompt with those details filled in — ready to copy and paste. Use this
  skill whenever a user uploads planning or property documents and wants a prompt generated,
  updated, or rebuilt for a new project. Trigger even if the user says things like "here are
  the new files", "update the prompt for this project", "rebuild the prompt with these docs",
  or simply uploads files without explanation in a land use / planning context.
---

# Land Use Prompt Builder

## Purpose

Read uploaded project documents, extract all project-specific details, and output a fully
updated version of the standard Land Use Feasibility Report prompt — with every placeholder
replaced by real values from the files. Output is plain text only, ready to copy.

---

## Step 1 — Identify and read all uploaded files

List every uploaded file. For each one, determine its type and read it:

- **PDFs** (LUBs, deeds, reports): extract text; note document title, relevant section numbers,
  page numbers, dates, party names, legal descriptions, zone codes, and numerical values.
- **Images / screenshots** (Property Online, NSPOL, maps): describe visible data — PID, civic
  address, lot area, zone, owner name, registered instruments, map legends, colour zones.
- **Environmental / topographical maps** (DTW, contours, flow accumulation, geology): note
  index ranges, colour classifications, risk levels, and any labels or legends visible.

If a file type is ambiguous, treat it as an image and describe what is visible.

---

## Step 2 — Extract the variable fields

From the documents, populate as many of the following fields as possible. Leave a field as
`[NOT FOUND — INSERT MANUALLY]` if the documents don't contain it.

| Field | Where to look |
|---|---|
| PID | Property Online screenshot, deed, NSPOL |
| Civic address | Property Online, deed cover |
| Parcel size (m²) | Property Online, deed, GIS data |
| Zone code and name | LUB, Property Online |
| LUB name and year | LUB document title |
| Current owner name | Most recent deed or NSPOL |
| Transfer date (most recent) | Most recent deed |
| Previous owner / chain of title | Earlier deeds |
| Legal description | Deed (lot description, right-of-way references) |
| Key LUB sections cited | LUB (zone section, general provisions cited in prompt) |
| Registered instruments on title | NSPOL, Abstract of Title |
| DTW index ranges | DTW map legend |
| Flow accumulation note | Flow accumulation map |
| Geology class | Surficial geology or environmental map |
| Karst / bedrock risk note | Environmental map or report |
| Uploaded document list | All files provided |
| Terrain description | Contour map, environmental report |

---

## Step 3 — Build the updated document list

From the files actually provided, construct a natural-language list of uploaded documents for
the prompt. Format as a comma-separated inline list matching the style below:

> the West Hants Land Use By-law (2026), the Warranty Deeds (1987 and 2026), the Property
> Online Screenshot, and the Environmental/Topographical Maps (DTW, Contours, and Flow
> Accumulation)

Use document titles and dates as they appear in the files. If a document has no clear date,
omit the date.

---

## Step 4 — Output the updated prompt

Output ONLY the updated prompt text below — no preamble, no explanation, no commentary.
Replace every bracketed placeholder with the real value extracted. Where a value was not found,
insert `[NOT FOUND — INSERT MANUALLY]` so the user knows to fill it in.

Adjust the section content naturally to match the actual documents and data. For example:
- If the zone is different from AR-3, update all zone references throughout.
- If the LUB has different section numbers, update those.
- If there are more or fewer deeds, adjust the ownership narrative.
- If environmental maps differ, adjust the environmental constraints section accordingly.
- Add or remove report sections if the uploaded documents clearly support or preclude them.

---

### Prompt template

```
Act as a professional Land Use Planning Expert. Using the uploaded documents for PID [PID] — specifically [DOCUMENT LIST] — generate a comprehensive Land Use Feasibility Report.

The report must be 'Google Docs ready' and include the following sections:

**Property Overview:** Summarize the parcel size ([PARCEL SIZE] m²) and basic terrain description from the environmental reports.

**Ownership & Title History:** Detail the transfer to [CURRENT OWNER] in [TRANSFER DATE], [CHAIN OF TITLE SUMMARY], and the specific [LEGAL DESCRIPTION SUMMARY] including [ANY NAMED RIGHT-OF-WAY OR EASEMENT].

**Regulatory Compliance:**
- Detail the [ZONE CODE] zone requirements ([LUB SECTION]) for dwellings (lot area, frontage, and setbacks).
- Explicitly include [GENERAL PROVISION SECTION] regarding topsoil preservation and [SUBDIVISION SECTION] regarding the two-lot-per-year subdivision limit (or equivalent provision).

**Environmental Constraints Analysis:**
- Interpret the Depth-to-Water (DTW) index ([DTW GENERAL RANGE] general vs. [DTW SENSITIVE RANGE] corridors).
- Explain the Flow Accumulation lines as cartographically derived predictions of water movement.
- Note the [GEOLOGY CLASS] geology and [KARST/BEDROCK RISK] risk levels.

**Development Strategy — Constraint Avoidance:** Provide recommendations for siting buildings in lower-risk zones and using existing legal access and topography to reduce costs.

**Development Strategy — Engineering Solutions:** Suggest technical solutions for subdivision development, including engineered septic (mound systems), stormwater bioswales, on-site rock crushing for road sub-base, and balanced cut-and-fill for topsoil management.

**Sources and References:** Provide a list of citations for every claim, referencing specific document names and page numbers (e.g., LUB Section [ZONE SECTION], p. [PAGE NUMBER]).

Format the output in clean Markdown with horizontal rules between sections and bolded headers for easy copying into a word processor.
```

---

## Notes on adaptation

- If the project is in a municipality with a different LUB structure, update section references to match what is visible in the uploaded LUB.
- If no environmental maps are provided, omit the Environmental Constraints Analysis section from the prompt and note this to the user after the output.
- If multiple PIDs are provided, list them all in the PID field separated by commas.
- Do not invent section numbers, page numbers, or legal descriptions. Only use what the documents contain.

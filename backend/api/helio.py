from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from services import llm_service
from services.docx_service import markdown_to_docx_bytes
from services.file_extract import extract_text_from_file, extract_zip_context

router = APIRouter()

TIER_LABELS = {"basic": "Basic", "detailed": "Detailed", "comprehensive": "Comprehensive"}


@router.post("/feasibility-report/assemble")
async def assemble_feasibility_report(
    project_address: str = Form(""),
    files: list[UploadFile] = File(...),
):
    """helio-feasibility-report: assemble a Pre-Development Site Assessment from a
    zip (or loose set) of GIS research + architectural drawing files."""
    context_parts = []
    for f in files:
        raw = await f.read()
        if f.filename.lower().endswith(".zip"):
            context_parts.append(extract_zip_context(raw))
        else:
            context_parts.append(f"=== {f.filename} ===\n{extract_text_from_file(f.filename, raw)}")

    try:
        report_text = llm_service.run_claude_skill(
            skill_name="helio-feasibility-report",
            user_inputs={"project_address": project_address},
            uploaded_files_context="\n\n".join(context_parts),
            max_tokens=8000,
        )
    except (RuntimeError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    docx_bytes = markdown_to_docx_bytes(
        title="PRE-DEVELOPMENT SITE ASSESSMENT",
        subtitle=project_address or "Helio Urban Development",
        body_markdown=report_text,
    )
    safe_name = (project_address or "Pre_Development_Assessment").replace(" ", "_").replace(",", "")
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_Pre_Development_Assessment.docx"'},
    )


@router.post("/feasibility-tiers/assemble")
async def assemble_feasibility_tiers(
    project_address: str = Form(""),
    tier: str = Form(...),
    files: list[UploadFile] = File(...),
):
    """helio-feasibility-tiers: assemble a Basic/Detailed/Comprehensive tiered report."""
    tier_key = tier.lower().strip()
    if tier_key not in TIER_LABELS:
        raise HTTPException(status_code=422, detail="tier must be one of: basic, detailed, comprehensive")

    context_parts = []
    for f in files:
        raw = await f.read()
        if f.filename.lower().endswith(".zip"):
            context_parts.append(extract_zip_context(raw))
        else:
            context_parts.append(f"=== {f.filename} ===\n{extract_text_from_file(f.filename, raw)}")

    try:
        report_text = llm_service.run_claude_skill(
            skill_name="helio-feasibility-tiers",
            user_inputs={"project_address": project_address, "report_tier": TIER_LABELS[tier_key]},
            uploaded_files_context="\n\n".join(context_parts),
            max_tokens=8000,
        )
    except (RuntimeError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    docx_bytes = markdown_to_docx_bytes(
        title="PRE-DEVELOPMENT SITE ASSESSMENT",
        subtitle=f"{project_address or 'Helio Urban Development'} · {TIER_LABELS[tier_key]} Tier",
        body_markdown=report_text,
    )
    safe_name = (project_address or "Feasibility_Report").replace(" ", "_").replace(",", "")
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}_{TIER_LABELS[tier_key]}_Feasibility_Report.docx"'
        },
    )

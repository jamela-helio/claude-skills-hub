from fastapi import APIRouter, Body, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from services import llm_service
from services.docx_service import markdown_to_docx_bytes
from services.file_extract import (
    extract_text_from_file,
    extract_zip_context,
    is_image_filename,
    zip_contains_images,
)

router = APIRouter()

TIER_LABELS = {"basic": "Basic", "detailed": "Detailed", "comprehensive": "Comprehensive"}


async def _gather_file_context(files: list[UploadFile]) -> tuple[str, bool]:
    context_parts = []
    has_images = False
    for f in files:
        raw = await f.read()
        if f.filename.lower().endswith(".zip"):
            context_parts.append(extract_zip_context(raw))
            has_images = has_images or zip_contains_images(raw)
        else:
            context_parts.append(f"=== {f.filename} ===\n{extract_text_from_file(f.filename, raw)}")
            has_images = has_images or is_image_filename(f.filename)
    return "\n\n".join(context_parts), has_images


def _render_feasibility_docx(title: str, subtitle: str, safe_name: str, suffix: str, report_text: str) -> Response:
    docx_bytes = markdown_to_docx_bytes(title=title, subtitle=subtitle, body_markdown=report_text)
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{safe_name}_{suffix}.docx"'},
    )


@router.post("/feasibility-report/assemble")
async def assemble_feasibility_report(
    project_address: str = Form(""),
    files: list[UploadFile] = File(...),
):
    """helio-feasibility-report (requires ANTHROPIC_API_KEY): assemble a
    Pre-Development Site Assessment from a zip (or loose set) of GIS research
    + architectural drawing files."""
    context, _ = await _gather_file_context(files)

    try:
        report_text = llm_service.run_claude_skill(
            skill_name="helio-feasibility-report",
            user_inputs={"project_address": project_address},
            uploaded_files_context=context,
            max_tokens=8000,
        )
    except (RuntimeError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    safe_name = (project_address or "Pre_Development_Assessment").replace(" ", "_").replace(",", "")
    return _render_feasibility_docx(
        "PRE-DEVELOPMENT SITE ASSESSMENT", project_address or "Helio Urban Development", safe_name,
        "Pre_Development_Assessment", report_text,
    )


@router.post("/feasibility-report/compose-prompt")
async def compose_feasibility_report_prompt(
    project_address: str = Form(""),
    files: list[UploadFile] = File(...),
):
    """No API key needed: assemble the prompt for the user to run in
    Claude.ai / Claude Code manually."""
    context, has_images = await _gather_file_context(files)

    try:
        prompt = llm_service.compose_manual_prompt(
            skill_name="helio-feasibility-report",
            user_inputs={"project_address": project_address},
            uploaded_files_context=context,
            has_image_files=has_images,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"prompt": prompt}


@router.post("/feasibility-report/render")
async def render_feasibility_report(payload: dict = Body(...)):
    project_address = payload.get("project_address", "")
    response_text = payload.get("response_text", "")
    if not response_text.strip():
        raise HTTPException(status_code=422, detail="response_text is required")

    safe_name = (project_address or "Pre_Development_Assessment").replace(" ", "_").replace(",", "")
    return _render_feasibility_docx(
        "PRE-DEVELOPMENT SITE ASSESSMENT", project_address or "Helio Urban Development", safe_name,
        "Pre_Development_Assessment", response_text,
    )


@router.post("/feasibility-tiers/assemble")
async def assemble_feasibility_tiers(
    project_address: str = Form(""),
    tier: str = Form(...),
    files: list[UploadFile] = File(...),
):
    """helio-feasibility-tiers (requires ANTHROPIC_API_KEY): assemble a
    Basic/Detailed/Comprehensive tiered report."""
    tier_key = tier.lower().strip()
    if tier_key not in TIER_LABELS:
        raise HTTPException(status_code=422, detail="tier must be one of: basic, detailed, comprehensive")

    context, _ = await _gather_file_context(files)

    try:
        report_text = llm_service.run_claude_skill(
            skill_name="helio-feasibility-tiers",
            user_inputs={"project_address": project_address, "report_tier": TIER_LABELS[tier_key]},
            uploaded_files_context=context,
            max_tokens=8000,
        )
    except (RuntimeError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    safe_name = (project_address or "Feasibility_Report").replace(" ", "_").replace(",", "")
    return _render_feasibility_docx(
        "PRE-DEVELOPMENT SITE ASSESSMENT", f"{project_address or 'Helio Urban Development'} · {TIER_LABELS[tier_key]} Tier",
        safe_name, f"{TIER_LABELS[tier_key]}_Feasibility_Report", report_text,
    )


@router.post("/feasibility-tiers/compose-prompt")
async def compose_feasibility_tiers_prompt(
    project_address: str = Form(""),
    tier: str = Form(...),
    files: list[UploadFile] = File(...),
):
    """No API key needed: assemble the prompt for the user to run in
    Claude.ai / Claude Code manually."""
    tier_key = tier.lower().strip()
    if tier_key not in TIER_LABELS:
        raise HTTPException(status_code=422, detail="tier must be one of: basic, detailed, comprehensive")

    context, has_images = await _gather_file_context(files)

    try:
        prompt = llm_service.compose_manual_prompt(
            skill_name="helio-feasibility-tiers",
            user_inputs={"project_address": project_address, "report_tier": TIER_LABELS[tier_key]},
            uploaded_files_context=context,
            has_image_files=has_images,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"prompt": prompt}


@router.post("/feasibility-tiers/render")
async def render_feasibility_tiers(payload: dict = Body(...)):
    project_address = payload.get("project_address", "")
    tier = payload.get("tier", "detailed")
    response_text = payload.get("response_text", "")
    if not response_text.strip():
        raise HTTPException(status_code=422, detail="response_text is required")

    tier_key = tier.lower().strip()
    tier_label = TIER_LABELS.get(tier_key, "Detailed")
    safe_name = (project_address or "Feasibility_Report").replace(" ", "_").replace(",", "")
    return _render_feasibility_docx(
        "PRE-DEVELOPMENT SITE ASSESSMENT", f"{project_address or 'Helio Urban Development'} · {tier_label} Tier",
        safe_name, f"{tier_label}_Feasibility_Report", response_text,
    )

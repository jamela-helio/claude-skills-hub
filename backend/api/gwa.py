import json

from fastapi import APIRouter, Body, File, Form, HTTPException, UploadFile

from services import gwa_calculator, llm_service
from services.docx_service import markdown_to_docx_bytes
from fastapi.responses import Response

router = APIRouter()


@router.post("/autofill")
async def gwa_autofill(
    site_params: str = Form(...),
    well_logs: UploadFile | None = File(None),
    pumping_tests: UploadFile | None = File(None),
    water_chemistry: UploadFile | None = File(None),
    observation_well: UploadFile | None = File(None),
    climate_normals: UploadFile | None = File(None),
):
    params = json.loads(site_params)
    site_elev_avg = params.get("ground_elev_avg")
    site_hu = params.get("bedrock_hu")
    county = params.get("county")

    result: dict = {"flags": []}

    if well_logs is not None:
        raw = await well_logs.read()
        wl = gwa_calculator.process_well_logs(raw, site_elev_avg)
        result["well_logs"] = wl
        if not county:
            county = wl.get("county_detected")

    if pumping_tests is not None:
        raw = await pumping_tests.read()
        result["pumping_tests"] = gwa_calculator.process_pumping_tests(raw, site_hu)

    if observation_well is not None:
        raw = await observation_well.read()
        result["observation_well"] = gwa_calculator.process_observation_well(raw)

    if climate_normals is not None:
        raw = await climate_normals.read()
        result["climate_normals"] = gwa_calculator.process_climate_normals(raw, county or "")

    if water_chemistry is not None:
        raw = await water_chemistry.read()
        result["water_chemistry"] = gwa_calculator.process_water_chemistry(raw)

    site_area = params.get("site_area_m2")
    min_lot_area = params.get("min_lot_area_m2")
    if site_area and min_lot_area:
        precip = result.get("climate_normals", {}).get("C33_precipitation_mm")
        hu = site_hu or result.get("pumping_tests", {}).get("hu_used")
        recharge_low, recharge_high = gwa_calculator.RECHARGE_DEFAULTS.get(
            (hu or "").upper(), (0.15, 0.20)
        )
        result["dual_constraint"] = gwa_calculator.compute_dual_constraint(
            site_area_m2=float(site_area),
            min_lot_area_m2=float(min_lot_area),
            infra_deduction_pct=float(params.get("infra_deduction_pct", 0.30)),
            wet_exclusion_pct=float(params.get("wet_exclusion_pct", 0.0)),
            precip_mm_y=precip,
            recharge_low_m_y=recharge_low,
            recharge_high_m_y=recharge_high,
        )
        result["recharge_rates_used"] = {"low_m_y": recharge_low, "high_m_y": recharge_high, "hu": hu}

    result["site_params"] = params
    return result


@router.post("/report/generate")
async def generate_gwa_report(payload: dict = Body(...)):
    """
    LLM-assisted (requires ANTHROPIC_API_KEY): feed calculator outputs + site
    context to Claude using the gwa-level1-report SKILL.md as the system
    prompt, then render to .docx.
    """
    site_params = payload.get("site_params", {})
    calculator_outputs = payload.get("calculator_outputs", {})
    extra_context = payload.get("extra_context", "")

    try:
        report_text = llm_service.run_claude_skill(
            skill_name="gwa-level1-report",
            user_inputs=site_params,
            uploaded_files_context=json.dumps(calculator_outputs, indent=2) + "\n\n" + extra_context,
            max_tokens=8000,
        )
    except (RuntimeError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return _render_gwa_docx(site_params, report_text)


@router.post("/report/compose-prompt")
async def compose_gwa_report_prompt(payload: dict = Body(...)):
    """
    No API key needed: assemble the same prompt run_claude_skill would send,
    for the user to paste into Claude.ai / Claude Code manually.
    """
    site_params = payload.get("site_params", {})
    calculator_outputs = payload.get("calculator_outputs", {})
    extra_context = payload.get("extra_context", "")

    try:
        prompt = llm_service.compose_manual_prompt(
            skill_name="gwa-level1-report",
            user_inputs=site_params,
            uploaded_files_context=json.dumps(calculator_outputs, indent=2) + "\n\n" + extra_context,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"prompt": prompt}


@router.post("/report/render")
async def render_gwa_report(payload: dict = Body(...)):
    """Turn Claude's pasted-back response text into a downloadable .docx."""
    site_params = payload.get("site_params", {})
    response_text = payload.get("response_text", "")
    if not response_text.strip():
        raise HTTPException(status_code=422, detail="response_text is required")

    return _render_gwa_docx(site_params, response_text)


def _render_gwa_docx(site_params: dict, report_text: str) -> Response:
    docx_bytes = markdown_to_docx_bytes(
        title="Level 1 Groundwater Assessment",
        subtitle=site_params.get("project_name", ""),
        body_markdown=report_text,
    )
    filename = f"{site_params.get('project_name', 'GWA_Report').replace(' ', '_')}_Level1_GWA.docx"
    return Response(
        content=docx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )

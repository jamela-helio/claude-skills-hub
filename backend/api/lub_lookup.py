from fastapi import APIRouter, Body, HTTPException

from services import llm_service

router = APIRouter()

REFERENCE_FILES = ["references/lub-index.md", "references/hrm-regional-centre-notes.md"]


@router.post("/compose-prompt")
async def compose_lub_lookup_prompt(payload: dict = Body(...)):
    """
    ns-lub-lookup: no API key needed. Assembles the skill instructions + both
    bundled reference indexes + the user's zone/municipality query into one
    prompt to run in Claude.ai / Claude Code (ideally with web search and/or
    the Helio Google Drive connected, since this skill needs live lookups).
    """
    zone_code = (payload.get("zone_code") or "").strip()
    municipality = (payload.get("municipality") or "").strip()
    question = (payload.get("question") or "").strip()

    if not zone_code or not municipality:
        raise HTTPException(status_code=422, detail="zone_code and municipality are required")

    query_text = f"Zone code: {zone_code}\nMunicipality / plan area: {municipality}\n"
    query_text += f"Specific question: {question}" if question else "(No specific question — give the full Mode B zone summary.)"

    try:
        prompt = llm_service.compose_manual_query_prompt(
            skill_name="ns-lub-lookup",
            query_text=query_text,
            reference_paths=REFERENCE_FILES,
            needs_live_tools=True,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"prompt": prompt}

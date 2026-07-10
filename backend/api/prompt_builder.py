from fastapi import APIRouter, File, HTTPException, UploadFile

from services import llm_service
from services.file_extract import extract_text_from_file, is_image_filename

router = APIRouter()


async def _gather_context(files: list[UploadFile]) -> tuple[str, bool]:
    context_parts = []
    has_images = False
    for f in files:
        raw = await f.read()
        context_parts.append(f"=== {f.filename} ===\n{extract_text_from_file(f.filename, raw)}")
        has_images = has_images or is_image_filename(f.filename)
    return "\n\n".join(context_parts), has_images


@router.post("/extract")
async def extract_prompt(files: list[UploadFile] = File(...)):
    """land-use-prompt-builder (requires ANTHROPIC_API_KEY): extract fields from
    uploaded planning documents and return a filled-in Land Use Feasibility
    Report prompt, ready to copy."""
    context, _ = await _gather_context(files)

    try:
        prompt_text = llm_service.run_claude_skill(
            skill_name="land-use-prompt-builder",
            user_inputs={"uploaded_file_names": [f.filename for f in files]},
            uploaded_files_context=context,
            max_tokens=4000,
        )
    except (RuntimeError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"prompt": prompt_text}


@router.post("/compose-prompt")
async def compose_prompt_builder_prompt(files: list[UploadFile] = File(...)):
    """No API key needed: assemble the prompt for the user to run in Claude.ai
    / Claude Code manually. Claude's response there IS the final filled Land
    Use Feasibility Report prompt — no further rendering step needed here."""
    context, has_images = await _gather_context(files)

    try:
        prompt = llm_service.compose_manual_prompt(
            skill_name="land-use-prompt-builder",
            user_inputs={"uploaded_file_names": [f.filename for f in files]},
            uploaded_files_context=context,
            has_image_files=has_images,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"prompt": prompt}

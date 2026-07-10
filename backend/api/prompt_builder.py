from fastapi import APIRouter, File, HTTPException, UploadFile

from services import llm_service
from services.file_extract import extract_text_from_file

router = APIRouter()


@router.post("/extract")
async def extract_prompt(files: list[UploadFile] = File(...)):
    """land-use-prompt-builder: extract fields from uploaded planning documents and
    return a filled-in Land Use Feasibility Report prompt, ready to copy."""
    context_parts = []
    for f in files:
        raw = await f.read()
        context_parts.append(f"=== {f.filename} ===\n{extract_text_from_file(f.filename, raw)}")

    try:
        prompt_text = llm_service.run_claude_skill(
            skill_name="land-use-prompt-builder",
            user_inputs={"uploaded_file_names": [f.filename for f in files]},
            uploaded_files_context="\n\n".join(context_parts),
            max_tokens=4000,
        )
    except (RuntimeError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"prompt": prompt_text}

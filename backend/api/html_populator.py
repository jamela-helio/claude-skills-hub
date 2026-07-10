from fastapi import APIRouter, File, Form, UploadFile

from services.html_service import populate_all_templates

router = APIRouter()


@router.post("/populate")
async def populate(
    data_text: str | None = Form(None),
    data_file: UploadFile | None = File(None),
):
    if data_file is not None:
        raw = await data_file.read()
        text = raw.decode("utf-8", errors="ignore")
    else:
        text = data_text or ""

    return populate_all_templates(text)

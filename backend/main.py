from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import CORS_ORIGINS
from api import gwa, helio, html_populator, prompt_builder

app = FastAPI(title="Claude Skills Hub API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(gwa.router, prefix="/api/gwa", tags=["gwa"])
app.include_router(helio.router, prefix="/api", tags=["helio"])
app.include_router(html_populator.router, prefix="/api/html-populator", tags=["html-populator"])
app.include_router(prompt_builder.router, prefix="/api/prompt-builder", tags=["prompt-builder"])


@app.get("/api/health")
def health():
    return {"status": "ok"}

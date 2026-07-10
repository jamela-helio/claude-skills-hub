import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BACKEND_DIR / "templates"

# Root that contains the six extracted `.skill` packages, e.g.
#   <SKILLS_ROOT>/gwa-autofill/gwa-autofill/SKILL.md
# Bundled into the repo at <project-root>/skills so it deploys with the backend.
SKILLS_ROOT = Path(
    os.environ.get(
        "SKILLS_ROOT",
        BACKEND_DIR.parent / "skills",
    )
)

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
ANTHROPIC_MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

OUTPUT_DIR = BACKEND_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Comma-separated list of extra allowed origins, e.g. the deployed Vercel URL:
#   FRONTEND_ORIGINS=https://claude-skills-hub.vercel.app,https://claude-skills-hub-git-main-you.vercel.app
_extra_origins = [o.strip() for o in os.environ.get("FRONTEND_ORIGINS", "").split(",") if o.strip()]

CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    *_extra_origins,
]

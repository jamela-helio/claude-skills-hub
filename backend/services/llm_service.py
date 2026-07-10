"""
Anthropic API wrapper that injects a skill's SKILL.md content as the system
prompt, following the pattern in claude_skills_website_plan.md section 3.
"""
from pathlib import Path

import anthropic

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL, SKILLS_ROOT

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        if not ANTHROPIC_API_KEY:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Add it to backend/.env to enable "
                "LLM-assisted features (report generation, prompt building)."
            )
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client


def load_skill_instructions(skill_name: str) -> str:
    """Read SKILL.md for the given skill from the extracted_skills folder."""
    skill_path = SKILLS_ROOT / skill_name / skill_name / "SKILL.md"
    if not skill_path.exists():
        raise FileNotFoundError(
            f"SKILL.md not found for '{skill_name}' at {skill_path}. "
            f"Set SKILLS_ROOT env var if extracted_skills lives elsewhere."
        )
    return skill_path.read_text(encoding="utf-8")


def run_claude_skill(
    skill_name: str,
    user_inputs: dict,
    uploaded_files_context: str,
    max_tokens: int = 4096,
) -> str:
    """
    Compose a system prompt from the skill's SKILL.md and call Claude with the
    user's structured inputs plus any text extracted from uploaded files.
    """
    skill_instructions = load_skill_instructions(skill_name)

    system_prompt = (
        skill_instructions
        + "\n\n---\n\nYou are running inside a web application, not the Claude Code "
        "CLI. There is no sandbox filesystem, no ability to shell out to pandoc, "
        "LibreOffice, or Node.js, and no way to fetch live web pages. Produce your "
        "complete output as plain text / Markdown in your response — do not refer "
        "to running scripts, saving files, or fetching URLs. If the skill "
        "instructions describe a multi-step tool-using workflow, adapt it to a "
        "single well-structured written response instead."
    )

    user_message = f"""User inputs provided:
{user_inputs}

Text content extracted from uploaded files:
{uploaded_files_context}
"""

    client = _get_client()
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return "".join(block.text for block in response.content if hasattr(block, "text"))

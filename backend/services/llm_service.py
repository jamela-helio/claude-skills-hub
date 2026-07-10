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


def load_skill_reference(skill_name: str, relative_path: str) -> str:
    """Read a bundled reference file, e.g. relative_path='references/lub-index.md'."""
    ref_path = SKILLS_ROOT / skill_name / skill_name / relative_path
    if not ref_path.exists():
        raise FileNotFoundError(f"Reference file not found for '{skill_name}' at {ref_path}.")
    return ref_path.read_text(encoding="utf-8")


_RUNTIME_NOTE = (
    "You are running inside a web application, not the Claude Code CLI. There "
    "is no sandbox filesystem, no ability to shell out to pandoc, LibreOffice, "
    "or Node.js, and no way to fetch live web pages. Produce your complete "
    "output as plain text / Markdown in your response — do not refer to "
    "running scripts, saving files, or fetching URLs. If the skill "
    "instructions describe a multi-step tool-using workflow, adapt it to a "
    "single well-structured written response instead."
)

_LIVE_TOOLS_NOTE = (
    "This skill depends on live web search/fetch (and, ideally, Google Drive "
    "access to Helio's LUB database) to retrieve the actual bylaw text — "
    "reference files bundled below only provide the index of where to look, "
    "not the LUB content itself. Run this prompt somewhere Claude actually has "
    "those tools available: Claude.ai with web search enabled, or Claude Code "
    "with the Google Drive MCP connected. If neither is available, do the best "
    "you can from general knowledge and clearly flag which parts are "
    "unverified against the actual current bylaw text."
)


def _build_system_prompt(skill_name: str, reference_paths: list[str] | None = None, needs_live_tools: bool = False) -> str:
    parts = [load_skill_instructions(skill_name)]
    for ref_path in reference_paths or []:
        parts.append(f"\n\n---\n\nBundled reference file `{ref_path}`:\n\n{load_skill_reference(skill_name, ref_path)}")
    parts.append("\n\n---\n\n" + _RUNTIME_NOTE)
    if needs_live_tools:
        parts.append("\n\n" + _LIVE_TOOLS_NOTE)
    return "".join(parts)


def _build_user_message(user_inputs: dict, uploaded_files_context: str) -> str:
    return f"""User inputs provided:
{user_inputs}

Text content extracted from uploaded files:
{uploaded_files_context}
"""


def run_claude_skill(
    skill_name: str,
    user_inputs: dict,
    uploaded_files_context: str,
    max_tokens: int = 4096,
) -> str:
    """
    Compose a system prompt from the skill's SKILL.md and call Claude with the
    user's structured inputs plus any text extracted from uploaded files.
    Requires ANTHROPIC_API_KEY to be set.
    """
    system_prompt = _build_system_prompt(skill_name)
    user_message = _build_user_message(user_inputs, uploaded_files_context)

    client = _get_client()
    response = client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    return "".join(block.text for block in response.content if hasattr(block, "text"))


def compose_manual_prompt(
    skill_name: str,
    user_inputs: dict,
    uploaded_files_context: str,
    has_image_files: bool = False,
) -> str:
    """
    Assemble the same skill instructions + inputs as run_claude_skill, but as
    one self-contained block of text meant to be copy-pasted into a Claude.ai
    or Claude Code conversation manually — no ANTHROPIC_API_KEY required.
    """
    system_prompt = _build_system_prompt(skill_name)
    user_message = _build_user_message(user_inputs, uploaded_files_context)

    image_note = ""
    if has_image_files:
        image_note = (
            "\n\n---\n\nNOTE: One or more uploaded files were images or scanned "
            "documents that this tool cannot read as text. Please also attach "
            "those original files directly to your Claude.ai / Claude Code "
            "conversation alongside this prompt so Claude can read them "
            "visually.\n"
        )

    return f"""{system_prompt}

---

{user_message}{image_note}"""


def compose_manual_query_prompt(
    skill_name: str,
    query_text: str,
    reference_paths: list[str] | None = None,
    needs_live_tools: bool = False,
) -> str:
    """
    Like compose_manual_prompt, but for skills driven by a free-text query
    rather than file uploads (e.g. ns-lub-lookup's "zone code + municipality").
    Bundled reference files are embedded inline since a plain Claude.ai/Claude
    Code chat won't otherwise have filesystem access to them.
    """
    system_prompt = _build_system_prompt(skill_name, reference_paths=reference_paths, needs_live_tools=needs_live_tools)
    return f"""{system_prompt}

---

User request:
{query_text}"""

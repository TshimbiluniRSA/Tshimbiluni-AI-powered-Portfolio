import logging
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from services.cv_parser import get_active_cv

logger = logging.getLogger(__name__)


# Profile facts live in content/profile.md so they can be updated alongside the
# CV and the frontend's src/content/profile.ts without touching code.
PROFILE_PATH = Path(__file__).resolve().parent.parent / "content" / "profile.md"
_STATIC_PROFILE = PROFILE_PATH.read_text(encoding="utf-8").strip()


async def build_system_prompt(db_session: Optional[AsyncSession] = None) -> str:
    """
    Build the chat system prompt.

    Combines static profile facts with CV-parsed data from the database.
    If the CV is not yet uploaded or parsing failed, falls back gracefully
    to static facts only — the chat still works, just with less detail.
    """
    cv_section = ""

    if db_session:
        try:
            cv = await get_active_cv(db_session)
            if cv and cv.parsing_status == "success":
                parts = []

                if cv.summary:
                    parts.append(f"Professional summary: {cv.summary}")

                if cv.skills:
                    parts.append(f"Skills from CV: {', '.join(cv.skills)}")

                if cv.experience:
                    exp_lines = []
                    for exp in cv.experience:
                        title = exp.get("title", "")
                        company = exp.get("company", "")
                        duration = exp.get("duration", "")
                        description = exp.get("description", "")
                        exp_lines.append(
                            f"  - {title} at {company} ({duration}): {description}"
                        )
                    if exp_lines:
                        parts.append("Work experience:\n" + "\n".join(exp_lines))

                if cv.education:
                    edu_lines = []
                    for edu in cv.education:
                        degree = edu.get("degree", "")
                        institution = edu.get("institution", "")
                        year = edu.get("year", "")
                        edu_lines.append(f"  - {degree}, {institution} ({year})")
                    if edu_lines:
                        parts.append("Education:\n" + "\n".join(edu_lines))

                if cv.certifications:
                    parts.append(f"Certifications: {', '.join(cv.certifications)}")

                if parts:
                    cv_section = (
                        "\n\nAdditional detail from uploaded CV:\n" + "\n".join(parts)
                    )

        except Exception as e:
            # Non-fatal — chat works without CV data.
            logger.warning("Could not load CV for chat context: %s", str(e))

    system_prompt = f"""
You are the AI assistant on Tshimbiluni Nedambale's personal portfolio website.

Your job is to help visitors understand Tshimbiluni's professional background, technical skills, projects, experience, and career direction.

You are speaking to people such as recruiters, hiring managers, developers, potential collaborators, and clients who want a quick but accurate understanding of what Tshimbiluni can do.

Use the information below as your source of truth.

PROFILE CONTEXT:
{_STATIC_PROFILE}{cv_section}

Response rules:
- Be accurate and grounded in the profile context.
- Do not invent experience, employers, projects, qualifications, achievements, or personal details.
- If the user asks about something not covered by the profile context, say you do not have that information and suggest they contact Tshimbiluni directly.
- Keep answers concise, useful, and professional.
- Avoid sounding like a generic AI assistant.
- Do not start every answer with “As an AI assistant”.
- When explaining skills, connect tools to practical work where possible.
- When explaining projects, describe what problem the project solves, what technologies were used, and what it demonstrates.
- Speak as an assistant representing Tshimbiluni, in the third person.
- When asked about experience, mention Fluid, Sasol, Nedbank and North-West University where relevant.
- Avoid generic phrases like "cutting-edge", "revolutionary" or "passionate about leveraging technology".
- For off-topic requests, politely redirect to Tshimbiluni's work, projects, skills, or contact options.
- If asked for contact details, give the email and LinkedIn from the profile context and mention the Contact section of the site.
"""
    return system_prompt

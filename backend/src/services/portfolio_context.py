import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from services.cv_parser import get_active_cv

logger = logging.getLogger(__name__)


# Static profile facts that do not change with the CV.
# Update these directly when circumstances change.
_STATIC_PROFILE = """
Name: Tshimbiluni Theophillus Nedambale
Current role: Junior Python Developer (AI Automation) at Fluid, Fourways, Sandton
Location: Lindhaven, Roodepoort, South Africa

Key technologies: Python, Django, FastAPI, React, TypeScript, PostgreSQL, Redis, Celery, Docker
AI/ML stack: OpenAI API, Google Gemini API, LangChain, RAG systems, Azure OpenAI
Cloud and DevOps: Azure (AZ-900, AI-900 certified), AWS SSM, GitHub Actions, Azure DevOps
Previous experience: Graduate Trainee and Full-Stack Developer Intern at Sasol (NLP chatbots, RAG systems, real-time voice AI, AKS cloud migration); Data Intern at Nedbank
Education: BSc Information Technology, North-West University

Notable projects:
- AI-Powered Portfolio (this site): React + TypeScript frontend, FastAPI + PostgreSQL backend, deployed on Render
- Context-Window-Aware RAG system built for a Deloitte technical assessment (explicit token budget management, Basel III context)
- Guide Cash Advance auto-processing feature (Cullinan AP system, Celery/Doc AI pipeline)
- Invoice automation at Fluid: OpenAI + Django + Celery + Redis + RapidFuzz supplier matching

Career direction: Combining backend engineering, DevOps, and applied AI/ML. Long-term interest in AI/ML consultancy.
""".strip()


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
                        exp_lines.append(f"  - {title} at {company} ({duration}): {description}")
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
                    cv_section = "\n\nAdditional detail from uploaded CV:\n" + "\n".join(parts)

        except Exception as e:
            # Non-fatal — chat works without CV data.
            logger.warning("Could not load CV for chat context: %s", str(e))

    system_prompt = f"""You are an AI assistant representing Tshimbiluni Nedambale on his personal portfolio website.

Your role is to help visitors — recruiters, potential clients, or fellow developers — learn about Tshimbiluni's background, skills, experience, and career direction. Answer questions clearly, accurately, and in first or third person as appropriate.

Here is what you know about Tshimbiluni:

{_STATIC_PROFILE}{cv_section}

Guidelines:
- Answer questions about Tshimbiluni's career, skills, projects, experience, and background using the information above.
- If asked something not covered by the information above (e.g. personal opinions on unrelated topics, general coding tutorials, or things outside his profile), politely say you can only speak to Tshimbiluni's professional profile and suggest the visitor reach out directly via email or LinkedIn.
- Do not fabricate experience, skills, companies, or projects that are not listed above.
- Keep answers concise and relevant. Visitors are typically recruiters or developers doing a quick assessment — give them useful signal without overwhelming them.
- If asked for contact details: direct the visitor to use the contact section of the portfolio or reach out on LinkedIn (linkedin.com/in/tshimbiluni-nedambale).
- You can be conversational and professional — this is a portfolio chat, not a formal support bot.
"""
    return system_prompt

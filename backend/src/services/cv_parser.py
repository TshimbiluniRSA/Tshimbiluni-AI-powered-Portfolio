import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timezone

import PyPDF2
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from db.models import CV
from services.llama_client import get_llm_client, ModelProvider

logger = logging.getLogger(__name__)


class CVParserError(Exception):
    """Custom exception for CV parsing errors."""
    pass


async def extract_text_from_pdf(file_path: Path) -> str:
    """Extract text content from PDF file."""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise CVParserError(f"Failed to extract text from PDF: {str(e)}")


async def parse_cv_with_ai(
    cv_text: str,
    session: Optional[AsyncSession] = None
) -> Dict[str, Any]:
    """
    Use AI (Gemini) to parse CV and extract structured data.
    
    Args:
        cv_text: Raw text extracted from CV
        session: Database session for API logging
        
    Returns:
        Dict with parsed CV data
    """
    prompt = f"""
You are an expert CV/Resume parser. Parse the following CV and extract structured information.

Return a JSON object with these exact fields:
{{
    "summary": "A brief 2-3 sentence professional summary",
    "skills": ["skill1", "skill2", ...],
    "experience": [
        {{
            "title": "Job Title",
            "company": "Company Name",
            "duration": "Start Date - End Date",
            "description": "Brief description of responsibilities"
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "institution": "University/School Name",
            "year": "Graduation Year or Duration"
        }}
    ],
    "certifications": ["Certification 1", "Certification 2", ...],
    "languages": [
        {{
            "language": "Language Name",
            "proficiency": "Native/Fluent/Intermediate/Basic"
        }}
    ]
}}

Only return the JSON object, no other text.

CV TEXT:
{cv_text}
"""
    
    try:
        # Get LLM client (uses Gemini based on DEFAULT_LLM_PROVIDER)
        llm_client = get_llm_client()
        
        # Call AI with higher token limit for CV parsing
        response = await llm_client.chat(
            message=prompt,
            provider=ModelProvider.GEMINI,  # Force Gemini for CV parsing
            model="gemini-pro",
            db_session=session,
            max_tokens=4096,
            temperature=0.3  # Lower temperature for more accurate extraction
        )
        
        # Parse JSON response
        parsed_data = json.loads(response["response"])
        
        return {
            "summary": parsed_data.get("summary", ""),
            "skills": parsed_data.get("skills", []),
            "experience": parsed_data.get("experience", []),
            "education": parsed_data.get("education", []),
            "certifications": parsed_data.get("certifications", []),
            "languages_spoken": parsed_data.get("languages", []),
            "ai_model_used": response.get("model", "gemini-pro"),
        }
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        # Return basic extraction
        return {
            "summary": cv_text[:500],
            "skills": [],
            "experience": [],
            "education": [],
            "certifications": [],
            "languages_spoken": [],
            "ai_model_used": "failed_json_parse",
        }
    except Exception as e:
        logger.error(f"AI parsing failed: {str(e)}")
        raise CVParserError(f"AI parsing failed: {str(e)}")


async def save_cv(
    session: AsyncSession,
    file_path: Path,
    filename: str,
    file_size: int,
    user_id: str = "tshimbiluni"
) -> CV:
    """
    Save CV file and parse it with AI.
    
    Args:
        session: Database session
        file_path: Path to saved CV file
        filename: Original filename
        file_size: File size in bytes
        user_id: User identifier
        
    Returns:
        Saved CV record
    """
    try:
        # Deactivate previous CVs
        await session.execute(
            update(CV).where(CV.user_id == user_id).values(is_active=False)
        )
        
        # Extract text from PDF
        logger.info(f"Extracting text from {filename}")
        cv_text = await extract_text_from_pdf(file_path)
        
        # Create CV record with pending status
        cv_record = CV(
            user_id=user_id,
            filename=filename,
            file_path=str(file_path),
            file_size_bytes=file_size,
            mime_type="application/pdf",
            full_text=cv_text,
            parsing_status="pending",
            is_active=True
        )
        session.add(cv_record)
        await session.commit()
        await session.refresh(cv_record)
        
        # Parse with AI
        logger.info(f"Parsing CV with AI for {filename}")
        try:
            parsed_data = await parse_cv_with_ai(cv_text, session)
            
            # Update CV record with parsed data
            cv_record.summary = parsed_data["summary"]
            cv_record.skills = parsed_data["skills"]
            cv_record.experience = parsed_data["experience"]
            cv_record.education = parsed_data["education"]
            cv_record.certifications = parsed_data["certifications"]
            cv_record.languages_spoken = parsed_data["languages_spoken"]
            cv_record.ai_model_used = parsed_data["ai_model_used"]
            cv_record.parsing_status = "success"
            cv_record.parsed_at = datetime.now(timezone.utc)
            
        except Exception as e:
            cv_record.parsing_status = "failed"
            cv_record.parsing_error = str(e)
            logger.error(f"CV parsing failed: {e}")
        
        await session.commit()
        await session.refresh(cv_record)
        
        logger.info(f"CV saved and parsed: {filename}")
        return cv_record
        
    except Exception as e:
        await session.rollback()
        raise CVParserError(f"Failed to save CV: {str(e)}")


async def get_active_cv(session: AsyncSession, user_id: str = "tshimbiluni") -> Optional[CV]:
    """Get the currently active CV for a user."""
    stmt = select(CV).where(CV.user_id == user_id, CV.is_active)
    result = await session.execute(stmt)
    return result.scalar_one_or_none()

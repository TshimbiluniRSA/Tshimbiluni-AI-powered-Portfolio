import pytest

from services.portfolio_context import build_system_prompt


@pytest.mark.asyncio
async def test_system_prompt_includes_current_profile():
    prompt = await build_system_prompt()
    assert "Junior Python Developer at Fluid" in prompt
    assert "Top 3 at GDG Johannesburg Build with AI 2026" in prompt

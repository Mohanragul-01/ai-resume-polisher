"""Pydantic schemas shared by Gemini `response_schema` and backend validation."""

from pydantic import BaseModel, Field


class TailoredAnalysisJson(BaseModel):
    """
    JSON shape Gemini must return (plan.md Phase 1).

    WHY: One definition drives SDK structured output and keeps field names stable for validators.
    """

    match_score: int = Field(..., ge=0, le=100)
    tailored_resume: str

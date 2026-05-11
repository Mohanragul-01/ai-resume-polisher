# schemas.py
# This file defines the shape (structure) of the JSON response we expect from Gemini.
# Pydantic is a library that helps validate data — it checks that values match expected types.
from pydantic import BaseModel, Field


class TailoredAnalysisJson(BaseModel):
    """
    This class describes what the AI's JSON response must look like.

    We use this in two places:
    1. To tell Gemini exactly what format to respond in (structured output).
    2. To validate the response before sending it to the frontend.

    Fields:
        match_score     — A number from 0 to 100 showing how well the resume fits the job.
        tailored_resume — The rewritten resume text tailored to the job description.
    """

    # ge=0 means "greater than or equal to 0", le=100 means "less than or equal to 100"
    match_score: int = Field(..., ge=0, le=100)
    tailored_resume: str

"""Pydantic schemas.

Every Claude call returns one of these models (enforced via tool-use).
Python-only steps (ATS scoring, language detection) also produce typed
results here for consistency across the pipeline.
"""
from __future__ import annotations

from pydantic import BaseModel, Field

# --------------------------------------------------------------------------
# Step 2 (Claude 1/4): Profile extraction
# --------------------------------------------------------------------------


class EducationEntry(BaseModel):
    degree: str
    field_of_study: str | None = None
    institution: str
    graduation_year: str | None = None


class ExperienceEntry(BaseModel):
    job_title: str
    company: str
    duration: str  # free text as written, e.g. "Jan 2021 - Present"
    responsibilities: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)


class ProfileSchema(BaseModel):
    full_name: str | None = None
    contact_summary: str | None = Field(
        default=None, description="Short line combining email/phone/location if present"
    )
    professional_summary: str | None = None
    total_years_experience: float | None = None
    seniority_level: str = Field(description="e.g. Entry-level, Mid-level, Senior, Lead")
    education: list[EducationEntry] = Field(default_factory=list)
    experience: list[ExperienceEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    languages_spoken: list[str] = Field(default_factory=list)


# --------------------------------------------------------------------------
# Step 3 (Python only): ATS scoring
# --------------------------------------------------------------------------


class ATSCriterionScore(BaseModel):
    name: str
    weight: float
    score: float = Field(ge=0, le=100)
    explanation: str


class ATSResult(BaseModel):
    overall_score: float = Field(ge=0, le=100)
    criteria: list[ATSCriterionScore]


# --------------------------------------------------------------------------
# Step 4 (Claude 2/4): Main analysis
# --------------------------------------------------------------------------


class SkillGap(BaseModel):
    skill: str
    why_it_matters: str
    priority: str = Field(description="High, Medium, or Low")


class MainAnalysisSchema(BaseModel):
    recommended_career_path: str
    career_path_reasoning: str
    alternative_career_paths: list[str] = Field(default_factory=list)
    strengths: list[str]
    skill_gaps: list[SkillGap]
    cv_improvement_suggestions: list[str]


# --------------------------------------------------------------------------
# Step 5 (Claude 3/4): Interview questions + report narrative
# --------------------------------------------------------------------------


class InterviewQuestion(BaseModel):
    question: str
    category: str = Field(description="e.g. Technical, Behavioral, Situational")
    why_this_is_asked: str


class InterviewAndReportSchema(BaseModel):
    interview_questions: list[InterviewQuestion]
    executive_summary: str
    ats_evaluation_narrative: str = Field(
        description="Plain-language explanation of the ATS score breakdown provided as context"
    )
    areas_for_improvement_narrative: str
    actionable_recommendations: list[str]
    conclusion: str


# --------------------------------------------------------------------------
# Step 6 (Claude 4/4): Improved CV generation
# --------------------------------------------------------------------------


class ImprovedCVSchema(BaseModel):
    full_name: str | None = None
    contact_summary: str | None = None
    professional_summary: str
    education: list[EducationEntry]
    experience: list[ExperienceEntry]
    skills: list[str]
    certifications: list[str] = Field(default_factory=list)

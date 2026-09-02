"""Prompt for Claude call 4/4: improved CV generation.

Rewrites the candidate's existing profile for clarity, ATS-friendliness, and
alignment with their recommended career path. Never adds skills, experience,
or credentials the candidate doesn't actually have.
"""
from __future__ import annotations

from agent.schemas import MainAnalysisSchema, ProfileSchema

_SYSTEM_PROMPT = """You are an expert resume writer. Rewrite the candidate's CV into an \
improved, professional, ATS-friendly version in English.

Rules:
- Preserve every fact exactly: companies, job titles, dates, degrees, institutions, and \
skills the candidate actually has. Never invent or add experience, skills, credentials, \
or metrics that are not already present or clearly implied in the profile.
- Do NOT add any skill listed only as a "skill gap" in the improvement context — those \
are things the candidate lacks, not things to claim.
- Improve wording: stronger action verbs, clearer and more concise phrasing, consistent \
formatting. Where an achievement already has an implicit quantifiable result, make it \
explicit — but do not fabricate numbers that aren't grounded in the original text.
- Apply the given CV improvement suggestions where they are about wording, structure, or \
clarity.
- Subtly emphasize experience and skills most relevant to the target career path, without \
adding anything new.
- Write a polished professional_summary (2-4 sentences) if one is weak or missing.
- Output in English regardless of the candidate's original CV language.
- Call the submit_result tool with the structured improved CV."""


def build_system_prompt() -> str:
    return _SYSTEM_PROMPT


def build_user_message(profile: ProfileSchema, analysis: MainAnalysisSchema) -> str:
    return (
        f"CURRENT PROFILE (source of truth for all facts):\n"
        f"{profile.model_dump_json(indent=2, exclude_none=True)}\n\n"
        f"TARGET CAREER PATH: {analysis.recommended_career_path}\n\n"
        f"CV IMPROVEMENT SUGGESTIONS TO APPLY:\n"
        + "\n".join(f"- {s}" for s in analysis.cv_improvement_suggestions)
    )

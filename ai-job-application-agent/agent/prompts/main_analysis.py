"""Prompt for Claude call 2/4: main analysis.

Consumes the structured profile and the deterministically-computed ATS
result as context — this step never recomputes or overrides the ATS score,
it only reasons about what to do given it.
"""
from __future__ import annotations

from agent.schemas import ATSResult, ProfileSchema

_SYSTEM_PROMPT = """You are an expert career coach and CV analyst. You are given a \
candidate's structured profile and their deterministically-computed ATS compatibility \
score breakdown.

Produce:
- recommended_career_path: the single best-fit career direction for this candidate.
- career_path_reasoning: a concise justification grounded in their actual experience \
and skills.
- alternative_career_paths: 1-3 reasonable alternatives, or an empty list.
- strengths: the candidate's genuine strengths, grounded in the profile.
- skill_gaps: skills missing or weak relative to their recommended career path, each \
with why it matters and a priority (High, Medium, or Low).
- cv_improvement_suggestions: practical, specific suggestions. Where relevant, address \
weaknesses shown in the ATS breakdown (e.g. if structure_formatting scored low, suggest \
concrete formatting fixes; if keyword_relevance is low, suggest adding action verbs or \
quantifiable results).

Rules:
- Do not invent experience, skills, or credentials not present in the profile.
- Do not recompute or contradict the provided ATS score — treat it as ground truth context.
- Call the submit_result tool with the structured analysis."""


def build_system_prompt() -> str:
    return _SYSTEM_PROMPT


def build_user_message(profile: ProfileSchema, ats_result: ATSResult) -> str:
    profile_json = profile.model_dump_json(indent=2, exclude_none=True)
    ats_json = ats_result.model_dump_json(indent=2)
    return (
        f"CANDIDATE PROFILE:\n{profile_json}\n\n"
        f"ATS COMPATIBILITY SCORE (already computed — use as context, do not recompute):\n"
        f"{ats_json}"
    )

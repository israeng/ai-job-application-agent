"""Deterministic ATS compatibility scoring.

Every sub-score is computed from measurable signals (structured profile
fields, raw text patterns, PDF layout metrics) so the final report can
show exactly how the overall score was derived — no LLM judgment call.
"""
from __future__ import annotations

import re

import config
from agent.schemas import ATSCriterionScore, ATSResult, ProfileSchema
from utils.logger import get_logger
from utils.pdf_parser import LayoutMetrics

logger = get_logger(__name__)

_ACTION_VERBS = {
    "led", "managed", "built", "developed", "designed", "implemented",
    "improved", "increased", "reduced", "created", "launched", "optimized",
    "delivered", "achieved", "coordinated", "analyzed", "automated",
    "architected", "spearheaded", "streamlined", "negotiated", "mentored",
    "established", "executed", "drove", "scaled",
}
_METRIC_PATTERN = re.compile(r"\d+(\.\d+)?\s?(%|percent|x|k\b|m\b)?", re.IGNORECASE)


def score_section_completeness(profile: ProfileSchema, raw_text: str) -> ATSCriterionScore:
    signals = {
        "contact": bool(profile.contact_summary) or "@" in raw_text,
        "summary": bool(profile.professional_summary),
        "experience": len(profile.experience) > 0,
        "education": len(profile.education) > 0,
        "skills": len(profile.skills) > 0,
    }
    present = [s for s in config.ATS_REQUIRED_SECTIONS if signals.get(s)]
    missing = [s for s in config.ATS_REQUIRED_SECTIONS if s not in present]
    score = 100 * len(present) / len(config.ATS_REQUIRED_SECTIONS)
    explanation = f"{len(present)}/{len(config.ATS_REQUIRED_SECTIONS)} required sections found."
    explanation += f" Missing: {', '.join(missing)}." if missing else " All required sections present."
    return ATSCriterionScore(
        name="section_completeness",
        weight=config.ATS_WEIGHTS["section_completeness"],
        score=round(score, 1),
        explanation=explanation,
    )


def score_skills_coverage(profile: ProfileSchema) -> ATSCriterionScore:
    n = len(profile.skills)
    if n == 0:
        score = 0.0
    elif n < 5:
        score = 40 + n * 8
    elif n <= 15:
        score = 80 + (n - 5) * 2
    else:
        score = 100.0
    score = min(score, 100.0)
    explanation = f"{n} distinct skills listed."
    if n < 5:
        explanation += " Consider listing more relevant technical and soft skills."
    return ATSCriterionScore(
        name="skills_coverage",
        weight=config.ATS_WEIGHTS["skills_coverage"],
        score=round(score, 1),
        explanation=explanation,
    )


def score_structure_formatting(layout: LayoutMetrics) -> ATSCriterionScore:
    score = 100.0
    issues = []
    if layout.has_tables:
        score -= 30
        issues.append("tables detected (can break ATS parsers)")
    if layout.bullet_line_ratio < 0.15:
        score -= 20
        issues.append("few bulleted lines (harder to scan)")
    if layout.num_pages > 2:
        score -= 15
        issues.append(f"{layout.num_pages} pages (2 or fewer is typically ideal)")
    score = max(score, 0.0)
    explanation = (
        "Well-structured, ATS-friendly formatting."
        if not issues else "Issues found: " + "; ".join(issues) + "."
    )
    return ATSCriterionScore(
        name="structure_formatting",
        weight=config.ATS_WEIGHTS["structure_formatting"],
        score=round(score, 1),
        explanation=explanation,
    )


def score_keyword_relevance(raw_text: str) -> ATSCriterionScore:
    words = re.findall(r"[a-zA-Z]+", raw_text.lower())
    total_words = max(len(words), 1)
    action_hits = sum(1 for w in words if w in _ACTION_VERBS)
    metric_hits = len(_METRIC_PATTERN.findall(raw_text))

    action_density_per_1000 = action_hits / total_words * 1000
    score = min(action_density_per_1000 * 6, 60) + min(metric_hits * 4, 40)
    score = min(score, 100.0)

    explanation = (
        f"{action_hits} strong action verbs and {metric_hits} quantifiable "
        f"results (numbers/percentages) detected."
    )
    return ATSCriterionScore(
        name="keyword_relevance",
        weight=config.ATS_WEIGHTS["keyword_relevance"],
        score=round(score, 1),
        explanation=explanation,
    )


def score_readability(raw_text: str, language: str) -> ATSCriterionScore:
    if language == "en":
        try:
            import textstat

            ease = textstat.flesch_reading_ease(raw_text)
            score = max(0.0, min(100.0, 100 - abs(65 - ease) * 1.2))
            explanation = f"Flesch Reading Ease score of {ease:.0f} (60-70 is ideal for resumes)."
            return ATSCriterionScore(
                name="readability",
                weight=config.ATS_WEIGHTS["readability"],
                score=round(score, 1),
                explanation=explanation,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"textstat failed, using fallback heuristic: {exc}")

    score, explanation = _fallback_readability(raw_text)
    return ATSCriterionScore(
        name="readability",
        weight=config.ATS_WEIGHTS["readability"],
        score=round(score, 1),
        explanation=explanation,
    )


def _fallback_readability(raw_text: str) -> tuple[float, str]:
    sentences = [s.strip() for s in re.split(r"[.!?\n]+", raw_text) if s.strip()]
    words = raw_text.split()
    if not sentences or not words:
        return 50.0, "Not enough text to assess readability."
    avg_len = len(words) / len(sentences)
    score = max(0.0, min(100.0, 100 - abs(12 - avg_len) * 5))
    explanation = f"Average line/sentence length of {avg_len:.1f} words (8-16 is ideal for scannable bullets)."
    return score, explanation


def compute_ats_result(
    profile: ProfileSchema,
    raw_text: str,
    layout: LayoutMetrics,
    language: str,
) -> ATSResult:
    criteria = [
        score_section_completeness(profile, raw_text),
        score_skills_coverage(profile),
        score_structure_formatting(layout),
        score_keyword_relevance(raw_text),
        score_readability(raw_text, language),
    ]
    overall = sum(c.score * c.weight for c in criteria)
    return ATSResult(overall_score=round(overall, 1), criteria=criteria)

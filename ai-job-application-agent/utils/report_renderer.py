"""Renders the final analysis report PDF.

Pulls narrative text from state.interview_and_report and structured facts
from profile / ats_result / analysis — never re-derives them.
"""
from __future__ import annotations

from reportlab.platypus import Paragraph, Spacer, Table, TableStyle

from agent.exceptions import RenderingError
from agent.state import AgentState
from utils import pdf_theme as theme

_STYLES = theme.build_styles()


def _bullets(items: list[str], style_key: str = "bullet") -> list:
    return [Paragraph(f"•  {item}", _STYLES[style_key]) for item in items]


def _ats_table(state: AgentState) -> Table:
    ats = state.ats_result
    header = ["Criterion", "Weight", "Score", "Explanation"]
    rows = [header]
    for c in ats.criteria:
        rows.append([
            c.name.replace("_", " ").title(),
            f"{c.weight * 100:.0f}%",
            f"{c.score:.0f}/100",
            Paragraph(c.explanation, _STYLES["body"]),
        ])
    table = Table(rows, colWidths=[110, 45, 55, 260], repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), theme.LIGHT_BG),
        ("FONTNAME", (0, 0), (-1, 0), theme.FONT_BOLD),
        ("TEXTCOLOR", (0, 0), (-1, 0), theme.PRIMARY),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, theme.BORDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    for i, c in enumerate(ats.criteria, start=1):
        table.setStyle(TableStyle([("TEXTCOLOR", (2, i), (2, i), theme.score_color(c.score))]))
    return table


def render_report(state: AgentState, output_path: str) -> str:
    if not all([state.profile, state.ats_result, state.analysis, state.interview_and_report]):
        raise RenderingError("render_report requires profile, ats_result, analysis, and interview_and_report.")

    profile, ats, analysis, ir = state.profile, state.ats_result, state.analysis, state.interview_and_report
    story = []

    try:
        story.append(Paragraph("CV Analysis Report", _STYLES["doc_title"]))
        name = profile.full_name or "Candidate"
        story.append(Paragraph(f"{name} &nbsp;|&nbsp; Prepared by AI Job Application Agent", _STYLES["doc_subtitle"]))

        story.append(Paragraph("Executive Summary", _STYLES["h1"]))
        story.append(Paragraph(ir.executive_summary, _STYLES["body"]))

        story.append(Paragraph("Candidate Profile", _STYLES["h1"]))
        story.append(Paragraph(f"Seniority level: {profile.seniority_level}", _STYLES["body"]))
        if profile.total_years_experience is not None:
            story.append(Paragraph(f"Years of experience: {profile.total_years_experience}", _STYLES["body"]))
        if profile.professional_summary:
            story.append(Paragraph(profile.professional_summary, _STYLES["body"]))

        story.append(Paragraph("Career Path Recommendation", _STYLES["h1"]))
        story.append(Paragraph(f"<b>{analysis.recommended_career_path}</b>", _STYLES["body"]))
        story.append(Paragraph(analysis.career_path_reasoning, _STYLES["body"]))
        if analysis.alternative_career_paths:
            story.append(Paragraph("Alternative paths:", _STYLES["h2"]))
            story += _bullets(analysis.alternative_career_paths)

        story.append(Paragraph("Skills Analysis", _STYLES["h1"]))
        story.append(Paragraph(", ".join(profile.skills) or "No skills listed.", _STYLES["body"]))

        story.append(Paragraph("Missing Skills", _STYLES["h1"]))
        for gap in analysis.skill_gaps:
            story.append(Paragraph(
                f"•  <b>{gap.skill}</b> ({gap.priority} priority) — {gap.why_it_matters}",
                _STYLES["bullet"],
            ))

        story.append(Paragraph("ATS Evaluation", _STYLES["h1"]))
        story.append(Paragraph(
            f"<b>Overall ATS Score: {ats.overall_score:.0f}/100</b>", _STYLES["body"]
        ))
        story.append(Paragraph(ir.ats_evaluation_narrative, _STYLES["body"]))
        story.append(Spacer(1, 6))
        story.append(_ats_table(state))

        story.append(Paragraph("Strengths", _STYLES["h1"]))
        story += _bullets(analysis.strengths)

        story.append(Paragraph("Areas for Improvement", _STYLES["h1"]))
        story.append(Paragraph(ir.areas_for_improvement_narrative, _STYLES["body"]))
        story += _bullets(analysis.cv_improvement_suggestions)

        story.append(Paragraph("Actionable Recommendations", _STYLES["h1"]))
        story += _bullets(ir.actionable_recommendations)

        story.append(Paragraph("Interview Questions", _STYLES["h1"]))
        for q in ir.interview_questions:
            story.append(Paragraph(f"<b>[{q.category}]</b> {q.question}", _STYLES["body"]))
            story.append(Paragraph(q.why_this_is_asked, _STYLES["body_muted"]))

        story.append(Paragraph("Conclusion", _STYLES["h1"]))
        story.append(Paragraph(ir.conclusion, _STYLES["body"]))

        doc, decoration = theme.build_doc(output_path, document_label=f"CV Analysis Report — {name}")
        doc.build(story, onFirstPage=decoration, onLaterPages=decoration)
    except RenderingError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise RenderingError(f"Failed to render analysis report PDF: {exc}") from exc

    return output_path

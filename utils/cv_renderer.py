"""Renders the improved CV PDF — same design system as the analysis report."""
from __future__ import annotations

from reportlab.platypus import Paragraph, Spacer

from agent.exceptions import RenderingError
from agent.state import AgentState
from utils import pdf_theme as theme

_STYLES = theme.build_styles()


def render_improved_cv(state: AgentState, output_path: str) -> str:
    if state.improved_cv is None:
        raise RenderingError("render_improved_cv requires state.improved_cv to be populated.")

    cv = state.improved_cv
    story = []

    try:
        name = cv.full_name or "Candidate"
        story.append(Paragraph(name, _STYLES["doc_title"]))
        if cv.contact_summary:
            story.append(Paragraph(cv.contact_summary, _STYLES["doc_subtitle"]))
        else:
            story.append(Spacer(1, 10))

        story.append(Paragraph("Professional Summary", _STYLES["h1"]))
        story.append(Paragraph(cv.professional_summary, _STYLES["body"]))

        story.append(Paragraph("Experience", _STYLES["h1"]))
        for exp in cv.experience:
            story.append(Paragraph(f"<b>{exp.job_title}</b> — {exp.company}", _STYLES["h2"]))
            story.append(Paragraph(exp.duration, _STYLES["meta"]))
            for r in exp.responsibilities:
                story.append(Paragraph(f"•  {r}", _STYLES["bullet"]))
            for a in exp.achievements:
                story.append(Paragraph(f"•  {a}", _STYLES["bullet"]))

        story.append(Paragraph("Education", _STYLES["h1"]))
        for edu in cv.education:
            line = f"<b>{edu.degree}</b>"
            if edu.field_of_study:
                line += f", {edu.field_of_study}"
            line += f" — {edu.institution}"
            if edu.graduation_year:
                line += f" ({edu.graduation_year})"
            story.append(Paragraph(line, _STYLES["body"]))

        story.append(Paragraph("Skills", _STYLES["h1"]))
        story.append(Paragraph("  •  ".join(cv.skills), _STYLES["body"]))

        if cv.certifications:
            story.append(Paragraph("Certifications", _STYLES["h1"]))
            for cert in cv.certifications:
                story.append(Paragraph(f"•  {cert}", _STYLES["bullet"]))

        doc, decoration = theme.build_doc(output_path, document_label=f"Improved CV — {name}")
        doc.build(story, onFirstPage=decoration, onLaterPages=decoration)
    except RenderingError:
        raise
    except Exception as exc:  # noqa: BLE001
        raise RenderingError(f"Failed to render improved CV PDF: {exc}") from exc

    return output_path

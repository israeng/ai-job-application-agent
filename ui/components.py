"""Reusable Streamlit UI components."""
from __future__ import annotations

import streamlit as st

from agent.state import AgentState

_STEP_ICONS = {
    "Ingest & preprocess": "📄",
    "Profile extraction (Claude 1/4)": "🧠",
    "ATS scoring engine": "📊",
    "Main analysis (Claude 2/4)": "🎯",
    "Interview & report content (Claude 3/4)": "💬",
    "Improved CV generation (Claude 4/4)": "✨",
    "Render PDFs": "📁",
}
PIPELINE_STEPS = list(_STEP_ICONS.keys())


def render_header() -> None:
    st.markdown(
        '<div class="app-header"><h1>AI Job Application Agent</h1>'
        "<p>Upload your CV — the agent takes it from there. No questions asked.</p></div>",
        unsafe_allow_html=True,
    )


def render_upload_zone():
    return st.file_uploader("Upload your CV (PDF)", type=["pdf"], label_visibility="collapsed")


def render_progress_tracker(step_events: list[tuple[str, bool]]) -> None:
    completed = dict(step_events)
    rows = []
    for step_name in PIPELINE_STEPS:
        icon = _STEP_ICONS[step_name]
        if step_name not in completed:
            status, css_class = "⏳", "step-pending"
        elif completed[step_name]:
            status, css_class = "✅", "step-done"
        else:
            status, css_class = "❌", "step-failed"
        rows.append(
            f'<div class="step-row {css_class}"><span>{icon} {step_name}</span><span>{status}</span></div>'
        )
    st.markdown('<div class="step-tracker">' + "".join(rows) + "</div>", unsafe_allow_html=True)


def render_error(state: AgentState) -> None:
    st.error(f"The agent stopped partway through: {state.error}")
    st.caption("Most failures are transient (e.g. API rate limits) — try uploading again.")


def render_results(state: AgentState) -> None:
    profile, ats, analysis, ir = state.profile, state.ats_result, state.analysis, state.interview_and_report
    tabs = st.tabs(["Summary", "ATS Score", "Career & Skills", "Interview Prep", "Downloads"])

    with tabs[0]:
        st.subheader(profile.full_name or "Candidate")
        st.write(ir.executive_summary)
        meta = f"Seniority: {profile.seniority_level}"
        if profile.total_years_experience is not None:
            meta += f" • {profile.total_years_experience} yrs experience"
        st.caption(meta)
        st.markdown("**Conclusion**")
        st.write(ir.conclusion)

    with tabs[1]:
        st.metric("Overall ATS Score", f"{ats.overall_score:.0f} / 100")
        st.write(ir.ats_evaluation_narrative)
        for c in ats.criteria:
            st.progress(min(c.score / 100, 1.0), text=f"{c.name.replace('_', ' ').title()} — {c.score:.0f}/100")
            st.caption(c.explanation)

    with tabs[2]:
        st.markdown(f"**Recommended career path:** {analysis.recommended_career_path}")
        st.write(analysis.career_path_reasoning)
        if analysis.alternative_career_paths:
            st.caption("Alternatives: " + ", ".join(analysis.alternative_career_paths))
        st.markdown("**Strengths**")
        for s in analysis.strengths:
            st.markdown(f"- {s}")
        st.markdown("**Missing / weak skills**")
        for gap in analysis.skill_gaps:
            st.markdown(f"- **{gap.skill}** ({gap.priority} priority) — {gap.why_it_matters}")
        st.markdown("**CV improvement suggestions**")
        for s in analysis.cv_improvement_suggestions:
            st.markdown(f"- {s}")

    with tabs[3]:
        for q in ir.interview_questions:
            with st.expander(f"[{q.category}] {q.question}"):
                st.write(q.why_this_is_asked)
        st.markdown("**Actionable recommendations**")
        for r in ir.actionable_recommendations:
            st.markdown(f"- {r}")

    with tabs[4]:
        col1, col2 = st.columns(2)
        with col1, open(state.report_pdf_path, "rb") as f:
            st.download_button("📄 Download Analysis Report", f, file_name="CV_Analysis_Report.pdf", mime="application/pdf")
        with col2, open(state.improved_cv_pdf_path, "rb") as f:
            st.download_button("✨ Download Improved CV", f, file_name="Improved_CV.pdf", mime="application/pdf")

    st.caption(f"Run ID: {state.run_id} • Total tokens used across 4 Claude calls: {state.total_tokens}")

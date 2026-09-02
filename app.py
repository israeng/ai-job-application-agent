"""AI Job Application Agent — Streamlit entry point.

The only user interaction is uploading a CV PDF. Everything after that
runs autonomously via AgentOrchestrator — no follow-up questions.
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import streamlit as st

import config
from agent.orchestrator import AgentOrchestrator
from ui.components import render_error, render_header, render_progress_tracker, render_results, render_upload_zone
from ui.styles import inject_custom_css

st.set_page_config(page_title="AI Job Application Agent", page_icon="🧭", layout="wide")
inject_custom_css()
render_header()

try:
    config.validate_config()
except RuntimeError as exc:
    st.error(str(exc))
    st.stop()

uploaded_file = render_upload_zone()

if uploaded_file is not None:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(uploaded_file.getvalue())
        tmp_path = Path(tmp.name)

    progress_placeholder = st.empty()
    step_events: list[tuple[str, bool]] = []

    def _on_step_complete(step_name: str, state) -> None:
        step_events.append((step_name, state.error is None))
        with progress_placeholder.container():
            render_progress_tracker(step_events)

    with st.spinner("Agent is analyzing your CV..."):
        orchestrator = AgentOrchestrator()
        final_state = orchestrator.run(
            tmp_path, source_filename=uploaded_file.name, on_step_complete=_on_step_complete
        )

    tmp_path.unlink(missing_ok=True)

    if final_state.error:
        render_error(final_state)
    else:
        render_results(final_state)

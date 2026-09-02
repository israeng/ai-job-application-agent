"""Custom CSS — shares the same palette as the generated PDFs."""
from __future__ import annotations

import streamlit as st

_CSS = """
<style>
:root {
    --primary: #1F3A5F;
    --accent: #2E86AB;
    --muted: #6B7280;
    --border: #D8DEE6;
}
.app-header h1 { color: var(--primary); font-weight: 700; margin-bottom: 0.1rem; }
.app-header p { color: var(--muted); margin-top: 0; margin-bottom: 1.5rem; }
.step-tracker {
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.5rem 1rem;
    margin-bottom: 1rem;
    background: #FAFBFC;
}
.step-row { display: flex; justify-content: space-between; padding: 0.35rem 0; font-size: 0.95rem; }
.step-row.step-done { color: var(--primary); }
.step-row.step-pending { color: var(--muted); }
.step-row.step-failed { color: #C0392B; font-weight: 600; }
div[data-testid="stMetricValue"] { color: var(--primary); }
</style>
"""


def inject_custom_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)

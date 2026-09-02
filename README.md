# AI Job Application Agent

An autonomous AI agent that analyzes a candidate's CV end to end. The user's only
interaction is uploading a PDF — everything after that (profile extraction, ATS
scoring, career-path analysis, skill-gap detection, interview prep, report and
improved-CV generation) runs without further input.

This is deliberately **not a chatbot**. There is no conversation loop and no
turn-by-turn Q&A — a fixed orchestrator executes a sequence of specialized
reasoning and processing steps, threading a single shared state object through
all of them.

## Why this is an agent, not just an AI-powered app

- **Sequential autonomous execution** — 7 steps run in a fixed order with zero
  user input in between.
- **Shared state, accumulated context** — each step reads what prior steps
  produced (`AgentState`) and adds to it; nothing is re-derived from scratch.
- **Reasoning where it's needed, determinism where it isn't** — only 4 of the 7
  steps call Claude (profile interpretation, career analysis, narrative
  generation, CV rewriting). ATS scoring, language detection, and PDF
  extraction/rendering are pure Python — deterministic, explainable, and free.
- **Graceful autonomous failure handling** — if any step fails, the pipeline
  stops itself, preserves everything computed so far, and reports exactly
  where and why, without crashing or asking the user to intervene mid-run.

## Pipeline

| # | Step | Engine | Produces |
|---|------|--------|----------|
| 1 | Ingest & preprocess | Python | Clean text, detected language (Arabic/English) |
| 2 | Profile extraction | Claude (1/4) | Structured candidate profile |
| 3 | ATS scoring | Python | Deterministic, weighted, explainable ATS score |
| 4 | Main analysis | Claude (2/4) | Career path, skill gaps, CV suggestions |
| 5 | Interview & report content | Claude (3/4) | Interview questions, report narrative |
| 6 | Improved CV generation | Claude (4/4) | ATS-friendly rewritten CV (facts preserved) |
| 7 | Render PDFs | Python | Final report + improved CV, one shared design |

Only 4 Claude calls total. From step 2 onward, only structured fields are
sent to the model — raw CV text is never resent, keeping token usage bounded
regardless of CV length.

## Project structure

```
ai-job-application-agent/
├── app.py                  # Streamlit entry point (the only UI)
├── config.py                # Models, weights, thresholds, paths
├── agent/
│   ├── orchestrator.py      # Defines pipeline order, runs all 7 steps
│   ├── state.py              # AgentState — shared context object
│   ├── schemas.py            # Pydantic schemas for every structured output
│   ├── llm_client.py          # Gemini API wrapper, forced structured output
│   ├── exceptions.py
│   ├── prompts/               # One prompt module per Claude call
│   └── steps/                  # One PipelineStep per pipeline stage
├── analysis/
│   ├── language_detector.py    # Arabic/English detection (Unicode heuristic)
│   └── ats_scoring.py          # Deterministic ATS rubric engine
├── utils/
│   ├── pdf_parser.py            # Text + layout extraction (pdfplumber)
│   ├── pdf_theme.py              # Shared design system (colors, fonts, layout)
│   ├── report_renderer.py         # Analysis report PDF (ReportLab)
│   └── cv_renderer.py              # Improved CV PDF (ReportLab, same theme)
├── ui/                                # Streamlit components + styling
└── tests/sample_cvs/                   # Sample CV used for testing
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env        # add your GEMINI_API_KEY to .env
streamlit run app.py
```

Get a key from [Google AI Studio](https://aistudio.google.com/apikey) and put
it in `.env` as `GEMINI_API_KEY=...`. The default model is `gemini-3.6-flash`
(configurable via a `GEMINI_MODEL` env var) — Google's current GA workhorse
model for agentic/structured-output tasks.

Requires Python 3.11+. PDF generation uses ReportLab only — no system-level
dependencies (Poppler, Pango/Cairo, etc.), so it runs out of the box on
Windows, macOS, and Linux alike.

## LLM provider

This project uses the [Google Gen AI SDK](https://github.com/googleapis/python-genai)
(`google-genai`) to call Gemini. Every Claude/Gemini call goes through
`agent/llm_client.py`, which forces a JSON response constrained to a Pydantic
schema (`response_mime_type="application/json"` + `response_schema=...`), so
every pipeline step gets a validated, typed object back — never free-form
text to parse. Retries (via `tenacity`) apply only to transient failures:
Gemini server errors (5xx) and rate limiting (429); other 4xx errors fail
fast since retrying them can't succeed.

The `LLMClient` class exposes one method, `call_structured(...)`, used
identically by all four Claude-labeled reasoning steps in the pipeline — the
step names still read "Claude N/4" as generic pipeline position labels and
were intentionally left unchanged, since renaming them has no effect on
behavior and only the LLM client needed to change providers.

## Key design decisions

- **ATS score is never LLM-generated.** It's computed from five measurable,
  weighted criteria (section completeness, skills coverage, structure/
  formatting, keyword relevance, readability), each with its own machine-
  computed explanation. Claude only narrates the result in the final report —
  it cannot contradict or recompute it.
- **Language handled automatically.** Arabic vs. English is detected via a
  Unicode-range heuristic (more reliable on CVs than statistical detectors,
  since names/emails are often Latin-script even in Arabic CVs), with
  `langdetect` as a fallback. No manual language selection.
- **Improved CV never invents facts.** The rewrite prompt is explicitly given
  only the candidate's real profile — skill *gaps* are excluded from its
  context so the model can't "add" skills the candidate doesn't have.
- **One visual identity.** The analysis report and improved CV share a single
  ReportLab theme module (colors, typography, spacing, page decoration), so
  both PDFs look like one coherent product.

## Bootcamp requirement mapping

- **Real-world problem:** job seekers don't get objective, actionable feedback
  on their CV before applying.
- **Autonomous agent, not a chatbot:** see "Why this is an agent" above.
- **Clear workflow, input → output:** one PDF upload → structured pipeline →
  downloadable report + improved CV.
- **AI reasoning and decision-making:** career-path recommendation, skill-gap
  prioritization, and CV rewriting all require judgment, not lookup.
- **Working prototype:** functional Streamlit app, tested end to end.
- **Professional architecture:** modular steps/prompts/schemas, dependency-
  injected LLM client, typed state, centralized config, structured logging.

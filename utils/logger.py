"""Structured logging for the agent pipeline.

Every pipeline run gets a run_id; every log line from that run is tagged
with it, so a single execution's trace can be filtered out of the logs.
"""
from __future__ import annotations

import logging
import sys
import uuid

import config

_CONFIGURED = False


def _configure_root() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
            datefmt="%H:%M:%S",
        )
    )
    root = logging.getLogger()
    root.setLevel(config.LOG_LEVEL)
    root.handlers = [handler]
    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    _configure_root()
    return logging.getLogger(name)


def new_run_id() -> str:
    return uuid.uuid4().hex[:8]


class RunAdapter(logging.LoggerAdapter):
    """Prefixes every log message with the pipeline run_id."""

    def process(self, msg, kwargs):
        return f"[run:{self.extra['run_id']}] {msg}", kwargs


def get_run_logger(name: str, run_id: str) -> RunAdapter:
    return RunAdapter(get_logger(name), {"run_id": run_id})

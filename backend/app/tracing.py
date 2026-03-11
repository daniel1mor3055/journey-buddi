"""Local file trace exporter for the OpenAI Agents SDK.

Writes every trace and span as JSONL to logs/traces.jsonl, including the full
instructions, input messages, and output that the default export() strips out.

Uses the SDK's proper layered architecture:
  TracingExporter  -- serialises items to the file
  BatchTraceProcessor -- batches items on a background thread
  add_trace_processor -- registers alongside the default OpenAI exporter

The key trick: ResponseSpanData stores .response and .input on the object
(the SDK even says "useful for other tracing processor implementations")
but its export() only emits response_id. We read the raw attributes directly.
"""
from __future__ import annotations

import json
import os
from typing import Any

from agents import Trace, Span
from agents.tracing import add_trace_processor
from agents.tracing.processor_interface import TracingExporter
from agents.tracing.processors import BatchTraceProcessor
from agents.tracing.span_data import ResponseSpanData, FunctionSpanData, AgentSpanData


def _serialize_response_span(span: Span[ResponseSpanData]) -> dict[str, Any]:
    """Extract full instructions + input + output from a ResponseSpanData span."""
    sd = span.span_data
    record: dict[str, Any] = {"type": "response"}

    if sd.response:
        record["response_id"] = sd.response.id
        record["model"] = getattr(sd.response, "model", None)
        record["instructions"] = getattr(sd.response, "instructions", None)
        output_items = getattr(sd.response, "output", None)
        if output_items:
            record["output"] = [
                item.model_dump() if hasattr(item, "model_dump") else str(item)
                for item in output_items
            ]
        usage = getattr(sd.response, "usage", None)
        if usage:
            record["usage"] = usage.model_dump() if hasattr(usage, "model_dump") else str(usage)

    if sd.input is not None:
        if isinstance(sd.input, str):
            record["input"] = sd.input
        elif isinstance(sd.input, list):
            record["input"] = [
                item.model_dump() if hasattr(item, "model_dump")
                else dict(item) if isinstance(item, dict) else str(item)
                for item in sd.input
            ]
        else:
            record["input"] = str(sd.input)

    return record


def _rich_export(item: Trace | Span[Any]) -> dict[str, Any]:
    """Export with full content for response spans, standard export for others."""
    base = item.export()
    if base is None:
        return {}

    if isinstance(item, Span) and isinstance(item.span_data, ResponseSpanData):
        base["span_data"] = _serialize_response_span(item)

    return base


class LocalFileExporter(TracingExporter):
    """Serialises trace/span batches to a JSONL file with full LLM content."""

    def __init__(self, filepath: str):
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self._file = open(filepath, "w")

    def export(self, items: list[Trace | Span[Any]]) -> None:
        for item in items:
            data = _rich_export(item)
            if data:
                self._file.write(json.dumps(data, default=str) + "\n")
        self._file.flush()

    def shutdown(self) -> None:
        self._file.close()


def setup_tracing(log_dir: str) -> None:
    """Register a local JSONL trace exporter alongside the default OpenAI exporter."""
    filepath = os.path.join(log_dir, "traces.jsonl")
    exporter = LocalFileExporter(filepath)
    processor = BatchTraceProcessor(exporter, schedule_delay=1.0)
    add_trace_processor(processor)

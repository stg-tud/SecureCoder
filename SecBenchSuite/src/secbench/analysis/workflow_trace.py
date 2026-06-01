from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional


def _parse_timestamp(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    normalized = value.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


@dataclass
class TraceRun:
    run_id: str
    format: Optional[str] = None
    review_mode: Optional[str] = None
    prompt: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    result: Optional[str] = None
    attempts: int = 0
    parse_error_count: int = 0
    guardian_warning_count: int = 0
    warnings: List[str] = field(default_factory=list)
    raw_records: List[dict] = field(default_factory=list)

    @property
    def elapsed_seconds(self) -> Optional[float]:
        if not self.started_at or not self.finished_at:
            return None
        return max(0.0, (self.finished_at - self.started_at).total_seconds())


def load_trace_runs(path: Path) -> List[TraceRun]:
    runs: dict[str, TraceRun] = {}
    ordered_ids: List[str] = []
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        run_id = record["runId"]
        run = runs.get(run_id)
        if run is None:
            run = TraceRun(run_id=run_id)
            runs[run_id] = run
            ordered_ids.append(run_id)
        run.raw_records.append(record)
        run.format = run.format or record.get("format")
        run.review_mode = run.review_mode or record.get("reviewMode")
        run.attempts = max(run.attempts, record.get("attempt") or 0)
        if record["type"] == "run_started":
            run.started_at = _parse_timestamp(record.get("timestamp")) or run.started_at
            messages = record.get("messages", [])
            if len(messages) > 1:
                run.prompt = messages[1].get("content")
        elif record["type"] == "parse_error":
            run.parse_error_count += 1
        elif record["type"] == "guardian_warning":
            run.guardian_warning_count += 1
            run.warnings.extend(record.get("errors", []))
        elif record["type"] == "result":
            run.finished_at = _parse_timestamp(record.get("timestamp")) or run.finished_at
            run.result = record.get("text")
    return [runs[run_id] for run_id in ordered_ids]


def load_trace_runs_by_prompt(path: Path) -> dict[str, List[TraceRun]]:
    grouped: dict[str, List[TraceRun]] = {}
    for run in load_trace_runs(path):
        if not run.prompt:
            continue
        grouped.setdefault(run.prompt, []).append(run)
    return grouped


def summarize_failure_type(result_text: Optional[str]) -> Optional[str]:
    if result_text in (None, "success"):
        return None
    if result_text == "generation_failure":
        return "generation"
    if result_text == "guardian_failure":
        return "guardian"
    if result_text in {"validation_failure", "hard_reject", "meta_hard_reject", "no_progress"}:
        return "validation"
    return result_text

from __future__ import annotations

from dataclasses import dataclass
from difflib import unified_diff
from typing import Dict, Iterable, Optional


@dataclass
class DiffStats:
    changed_files_count: int
    changed_lines_added: int
    changed_lines_removed: int
    diff_size_bytes: int
    changed_files: list[str]


def compute_diff_stats(original_files: Dict[str, str], final_files: Dict[str, str]) -> DiffStats:
    changed_files = sorted(
        file_name
        for file_name in (set(original_files) | set(final_files))
        if original_files.get(file_name, "") != final_files.get(file_name, "")
    )
    added = 0
    removed = 0
    total_bytes = 0
    for file_name in changed_files:
        original = original_files.get(file_name, "").splitlines(keepends=True)
        final = final_files.get(file_name, "").splitlines(keepends=True)
        diff_lines = list(
            unified_diff(
                original,
                final,
                fromfile=f"a/{file_name}",
                tofile=f"b/{file_name}",
            )
        )
        total_bytes += sum(len(line.encode("utf-8")) for line in diff_lines)
        for line in diff_lines:
            if line.startswith(("---", "+++", "@@")):
                continue
            if line.startswith("+"):
                added += 1
            elif line.startswith("-"):
                removed += 1
    return DiffStats(
        changed_files_count=len(changed_files),
        changed_lines_added=added,
        changed_lines_removed=removed,
        diff_size_bytes=total_bytes,
        changed_files=changed_files,
    )

#!/usr/bin/env python3
import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load_records(path: Path):
    for line in path.read_text().splitlines():
        if line.strip():
            yield json.loads(line)


def summarize(records):
    runs = {}
    for record in records:
        run_id = record["runId"]
        run = runs.setdefault(
            run_id,
            {
                "run_id": run_id,
                "prompt": None,
                "result": None,
                "warnings": [],
                "parse_errors": 0,
                "attempts": 0,
            },
        )
        run["attempts"] = max(run["attempts"], record.get("attempt") or 0)
        if record["type"] == "run_started":
            messages = record.get("messages", [])
            if len(messages) > 1:
                run["prompt"] = messages[1]["content"].split("Only create ONE file!")[0].strip()
        elif record["type"] == "guardian_warning":
            run["warnings"].extend(record.get("errors", []))
        elif record["type"] == "parse_error":
            run["parse_errors"] += 1
        elif record["type"] == "result":
            run["result"] = record.get("text")

    result_counts = Counter(run["result"] or "incomplete" for run in runs.values())
    warning_counts = Counter()
    for run in runs.values():
        for warning in run["warnings"]:
            rule = warning.split(":", 1)[0]
            warning_counts[rule] += 1

    failures = []
    for run in runs.values():
        if run["result"] == "success":
            continue
        failures.append(
            {
                "run_id": run["run_id"],
                "result": run["result"] or "incomplete",
                "attempts": run["attempts"],
                "parse_errors": run["parse_errors"],
                "warning_counts": Counter(w.split(":", 1)[0] for w in run["warnings"]),
                "prompt": run["prompt"],
            }
        )
    failures.sort(key=lambda item: (item["result"], -(item["attempts"] or 0), item["run_id"]))

    return {
        "run_count": len(runs),
        "result_counts": dict(result_counts),
        "top_warning_rules": warning_counts.most_common(),
        "failures": failures,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("trace", help="Path to workflow chat.jsonl trace")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    args = parser.parse_args()

    summary = summarize(load_records(Path(args.trace)))
    if args.json:
        print(json.dumps(summary, indent=2, default=lambda obj: dict(obj)))
        return

    print(f"Runs: {summary['run_count']}")
    print("Results:")
    for result, count in sorted(summary["result_counts"].items()):
        print(f"  {result}: {count}")
    print("Top warning rules:")
    for rule, count in summary["top_warning_rules"][:10]:
        print(f"  {rule}: {count}")
    print("Failures:")
    for failure in summary["failures"]:
        print(f"- {failure['result']} after {failure['attempts']} attempt(s) | parse_errors={failure['parse_errors']}")
        for rule, count in sorted(failure["warning_counts"].items()):
            print(f"    {rule}: {count}")
        prompt = failure["prompt"] or "<missing prompt>"
        first_line = prompt.splitlines()[0] if prompt else "<missing prompt>"
        print(f"    prompt: {first_line}")


if __name__ == "__main__":
    main()

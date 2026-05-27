import importlib.util
import sys
from pathlib import Path


def load_module(name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(name, Path(file_name))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


emailer = load_module("emailer", "emailer.py")
task_id = sys.argv[1]

if task_id == "notifications_title_case_subject":
    assert emailer.build_subject("weekly") == "Report: weekly"
elif task_id == "notifications_trim_body_name":
    body = emailer.build_body("  ada lovelace  ", ["line 1", "line 2"])
    assert body.startswith("hello Ada Lovelace")
elif task_id == "notifications_digest_bullets":
    assert emailer.render_digest(["A", "B"]) == "- A\n- B"
    assert emailer.render_digest([]) == "No updates."
else:
    raise AssertionError(f"Unknown task id: {task_id}")

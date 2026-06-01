import importlib.util
import sys
from pathlib import Path


def load_module(name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(name, Path(file_name))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


formatter = load_module("formatter", "formatter.py")
task_id = sys.argv[1]

if task_id == "textkit_csv_separator":
    assert formatter.format_csv_row(["a", "b", "c"]) == "a;b;c"
elif task_id == "textkit_preview_helper":
    assert formatter.build_preview("  alpha   beta   gamma  ", limit=12) == "alpha beta g..."
elif task_id == "textkit_profile_url_quote":
    assert formatter.build_profile_url("Ada Lovelace/notes") == "/users/Ada%20Lovelace%2Fnotes"
else:
    raise AssertionError(f"Unknown task id: {task_id}")

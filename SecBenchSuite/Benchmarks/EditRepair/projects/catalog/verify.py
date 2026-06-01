import importlib.util
import sys
from pathlib import Path


def load_module(name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(name, Path(file_name))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


models = load_module("models", "models.py")
view = load_module("view", "view.py")
task_id = sys.argv[1]

if task_id == "catalog_inventory_badge":
    assert view.render_card("Mug", 1200, 3).startswith("[IN] Mug:")
    assert view.render_card("Mug", 1200, 0).startswith("[OUT] Mug:")
elif task_id == "catalog_price_label_compact":
    assert models.price_label(1200) == "€12"
    assert models.price_label(1250) == "€12.50"
elif task_id == "catalog_render_card_multiline":
    assert view.render_card("Lamp", 2500, 2) == "Lamp: €25.00\nin stock"
else:
    raise AssertionError(f"Unknown task id: {task_id}")

import importlib.util
import sys
from pathlib import Path


def load_module(name: str, file_name: str):
    spec = importlib.util.spec_from_file_location(name, Path(file_name))
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


pricing = load_module("pricing", "pricing.py")
service = load_module("service", "service.py")
task_id = sys.argv[1]

if task_id == "orders_ignore_negative_quantity":
    items = [
        {"price_cents": 200, "quantity": 2},
        {"price_cents": 500, "quantity": -3},
    ]
    assert pricing.subtotal(items) == 400
elif task_id == "orders_lowercase_discount_code":
    assert pricing.apply_discount(1000, "  save10 ") == 900
elif task_id == "orders_format_total_helper":
    result = service.quote_order([{"price_cents": 1234, "quantity": 1}], None)
    assert result["display"] == "€12.34"
else:
    raise AssertionError(f"Unknown task id: {task_id}")

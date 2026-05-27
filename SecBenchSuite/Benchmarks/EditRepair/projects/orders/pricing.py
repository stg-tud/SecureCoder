DISCOUNTS = {
    "SAVE10": 0.10,
    "SAVE20": 0.20,
}


def subtotal(items):
    total = 0
    for item in items:
        total += item["price_cents"] * item["quantity"]
    return total


def apply_discount(total_cents, code):
    if code in DISCOUNTS:
        return int(total_cents * (1 - DISCOUNTS[code]))
    return total_cents

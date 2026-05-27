from pricing import subtotal, apply_discount


def quote_order(items, code=None):
    total = subtotal(items)
    total = apply_discount(total, code)
    return {
        "total_cents": total,
        "display": f"{total / 100:.2f} EUR",
    }

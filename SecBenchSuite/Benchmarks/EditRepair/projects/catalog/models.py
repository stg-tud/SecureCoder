def price_label(cents):
    return f"€{cents / 100:.2f}"


def stock_label(count):
    return "in stock" if count > 0 else "sold out"

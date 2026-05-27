from models import price_label, stock_label


def render_card(name, cents, count):
    return f"{name}: {price_label(cents)} ({stock_label(count)})"

import re


def format_csv_row(values):
    return ",".join(values)


def slugify(name):
    text = name.strip().lower()
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


def build_preview(text, limit=20):
    cleaned = text.strip()
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[:limit] + "..."


def build_profile_url(username):
    return f"/users/{username}"

def build_subject(report_name):
    return f"report: {report_name}"


def build_body(user_name, lines):
    greeting = f"hello {user_name}"
    joined = "\n".join(lines)
    return f"{greeting}\n\n{joined}"


def render_digest(items):
    return ", ".join(items)

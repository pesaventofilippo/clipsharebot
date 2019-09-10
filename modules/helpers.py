def sanitize(data):
    if not data:
        return None
    esc_table = {
        ">": "&gt;",
        "<": "&lt;"
    }
    from xml.sax.saxutils import escape
    return escape(data, esc_table)

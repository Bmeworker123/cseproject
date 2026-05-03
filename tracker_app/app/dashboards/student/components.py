from tracker_app.ui import Card, Label


def render_page_header(parent, title, subtitle):
    Label(parent, text=title, size=16, bold=True, bg="white", fg="#1f2933").pack(
        anchor="w"
    )
    Label(parent, text=subtitle, size=10, bg="white", fg="#52606d").pack(
        anchor="w", pady=6
    )


def render_section_title(parent, title, *, bg, fg):
    Label(parent, text=title, size=13, bold=True, bg=bg, fg=fg).pack(anchor="w")


def render_detail_lines(parent, lines, *, bg, fg, wraplength=None):
    for line in lines:
        options = {"text": line, "size": 10, "bg": bg, "fg": fg}
        if wraplength is not None:
            options["wraplength"] = wraplength
            options["justify"] = "left"
        Label(parent, **options).pack(anchor="w", pady=2)


def render_empty_state(parent, title, message, *, bg, title_fg, message_fg):
    empty = Card(parent, bg=bg, padx=18, pady=18)
    Label(empty, text=title, size=13, bold=True, bg=bg, fg=title_fg).pack(anchor="w")
    Label(
        empty,
        text=message,
        size=10,
        bg=bg,
        fg=message_fg,
        wraplength=760,
        justify="left",
    ).pack(anchor="w", pady=(6, 0))
    return empty

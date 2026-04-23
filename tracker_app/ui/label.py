import tkinter as tk

class Label(tk.Label):
    def __init__(self, parent, text, size=10, bold=False, bg="white", fg="#334e68", **kwargs):
        font = ("Segoe UI", size, "bold") if bold else ("Segoe UI", size)
        
        config = {
            "text": text,
            "font": font,
            "bg": bg,
            "fg": fg,
        }
        config.update(kwargs)
        super().__init__(parent, **config)

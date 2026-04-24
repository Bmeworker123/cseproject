import tkinter as tk

class Card(tk.Frame):
    def __init__(self, parent, bg="white", padx=16, pady=16, **kwargs):
        config = {
            "bg": bg,
            "padx": padx,
            "pady": pady,
        }
        # Allow overriding defaults
        config.update(kwargs)
        super().__init__(parent, **config)

import tkinter as tk


class Button(tk.Button):
    def __init__(self, parent, text, command, primary=False, **kwargs):
        bg = "#2f80ed" if primary else "white"
        fg = "white" if primary else "#334e68"
        relief = "flat" if primary else "solid"
        
        config = {
            "text": text,
            "command": command,
            "font": ("Segoe UI", 10, "bold" if primary else "normal"),
            "bg": bg,
            "fg": fg,
            "activebackground": bg,
            "activeforeground": fg,
            "relief": relief,
            "bd": 1 if not primary else 0,
            "padx": 12,
            "pady": 8,
        }
        config.update(kwargs)
        super().__init__(parent, **config)

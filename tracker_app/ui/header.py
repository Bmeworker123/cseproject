import tkinter as tk
from .label import Label
from .button import Button

class Header(tk.Frame):
    def __init__(self, parent, title, subtitle, logout_command, bg="#eef2f6", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        
        info = tk.Frame(self, bg=bg)
        info.pack(side="left")
        Label(info, title, size=18, bold=True, bg=bg, fg="#102a43").pack(anchor="w")
        Label(info, subtitle, size=10, bg=bg, fg="#52606d").pack(anchor="w")
        
        actions = tk.Frame(self, bg=bg)
        actions.pack(side="right")
        Button(actions, "Back", logout_command).pack(side="left", padx=(0, 8))
        Button(actions, "Log Out", logout_command).pack(side="left")

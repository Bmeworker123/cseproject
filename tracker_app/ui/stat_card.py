import tkinter as tk
from .label import Label
from .card import Card

class StatCard(Card):
    def __init__(self, parent, title, value, note="", bg="#f7f9fb", **kwargs):
        super().__init__(parent, bg=bg, padx=14, pady=14, **kwargs)
        # We handle packing details in the constructor or leave it to the caller?
        # ahmet_ui.py had: card.pack(side="left", fill="both", expand=True, padx=6)
        # It's better if callers handle packing of the StatCard itself.
        
        Label(self, title, size=10, bg=bg, fg="#52606d").pack(anchor="w")
        Label(self, value, size=17, bold=True, bg=bg, fg="#102a43").pack(anchor="w", pady=4)
        if note:
            Label(self, note, size=9, bg=bg, fg="#7b8794", wraplength=220, justify="left").pack(anchor="w")

import tkinter as tk
from .label import Label

class EntryField(tk.Frame):
    def __init__(self, parent, label, show=None, bg="white", **kwargs):
        super().__init__(parent, bg=bg)
        Label(self, label, bg=bg, fg="#000000").pack(anchor="w", pady=(12, 4))
        self.entry = tk.Entry(self, show=show, font=("Segoe UI", 11), **kwargs)
        self.entry.pack(fill="x")
    
    def get(self): return self.entry.get()
    def delete(self, *args): self.entry.delete(*args)
    def insert(self, *args): self.entry.insert(*args)
    def focus_set(self): self.entry.focus_set()
    def bind(self, *args, **kwargs): self.entry.bind(*args, **kwargs)

class TextField(tk.Frame):
    def __init__(self, parent, label, height=4, bg="white", **kwargs):
        super().__init__(parent, bg=bg)
        Label(self, label, bg=bg, fg="#000000").pack(anchor="w")
        self.text = tk.Text(self, height=height, font=("Segoe UI", 10), **kwargs)
        self.text.pack(fill="x", pady=(4, 10))
        
    def get(self, *args): return self.text.get(*args)
    def delete(self, *args): self.text.delete(*args)
    def insert(self, *args): self.text.insert(*args)

class OptionField(tk.Frame):
    def __init__(self, parent, label, variable, values, bg="white", fill="x", **kwargs):
        super().__init__(parent, bg=bg)
        Label(self, label, bg=bg, fg="#000000").pack(anchor="w")
        self.menu = tk.OptionMenu(self, variable, *values, **kwargs)
        if fill:
            self.menu.pack(fill=fill, pady=(4, 0))
        else:
            self.menu.pack(anchor="w", pady=(4, 0))

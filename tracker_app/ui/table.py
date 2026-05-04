import tkinter as tk

from .label import Label


class Table(tk.Frame):
    """A container for TableHeader and TableRow components with built-in scrolling."""
    def __init__(self, parent, bg="white", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.bg = bg
        self.rows = []
        self._selected_row = None
        self._on_select_callback = None
        
        # Header area (not scrollable)
        self.header_container = tk.Frame(self, bg=bg)
        self.header_container.pack(fill="x")
        
        # Scrollable area
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=bg)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self._bind_mousewheel(self.canvas)
        self._bind_mousewheel(self.scrollable_frame)

    def _on_canvas_configure(self, event):
        self.canvas.itemconfigure(self.canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        delta = event.delta
        if delta == 0 and hasattr(event, "num"):
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
                return
            if event.num == 5:
                self.canvas.yview_scroll(1, "units")
                return
        self.canvas.yview_scroll(int(-1 * (delta / 120)), "units")

    def _bind_mousewheel(self, widget):
        widget.bind("<MouseWheel>", self._on_mousewheel)
        widget.bind("<Button-4>", self._on_mousewheel)
        widget.bind("<Button-5>", self._on_mousewheel)

    def add_row(self, values):
        row = TableRow(self.scrollable_frame, values)
        row.pack(fill="x")
        self.rows.append(row)
        
        # Selection binding
        row.bind("<Button-1>", lambda e, r=row: self._on_row_click(r))
        # Scrolling binding
        self._bind_mousewheel(row)
        
        # Bind children too
        for child in row.winfo_children():
            child.bind("<Button-1>", lambda e, r=row: self._on_row_click(r))
            self._bind_mousewheel(child)
            
        return row

    def set_header(self, columns):
        # Clear existing header
        for child in self.header_container.winfo_children():
            child.destroy()
        header = TableHeader(self.header_container, columns)
        header.pack(fill="x")
        return header

    def _on_row_click(self, row):
        if self._selected_row:
            self._selected_row.deselect()
        self._selected_row = row
        self._selected_row.select()
        if self._on_select_callback:
            self._on_select_callback(row)

    def on_select(self, callback):
        self._on_select_callback = callback

    def clear(self):
        for row in self.rows:
            row.destroy()
        self.rows = []
        self._selected_row = None

    def get_selected_index(self):
        if self._selected_row in self.rows:
            return self.rows.index(self._selected_row)
        return -1

    def select_index(self, index):
        if 0 <= index < len(self.rows):
            self._on_row_click(self.rows[index])


class TableHeader(tk.Frame):
    def __init__(self, parent, columns, bg="#f1f5f9", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        for i, col in enumerate(columns):
            label = Label(self, text=col, bold=True, bg=bg, fg="#102a43")
            label.grid(row=0, column=i, sticky="w", padx=8, pady=8)
            self.grid_columnconfigure(i, weight=1)


class TableRow(tk.Frame):
    def __init__(self, parent, values, bg="white", **kwargs):
        super().__init__(parent, bg=bg, **kwargs)
        self.values = values
        self.default_bg = bg
        
        for i, val in enumerate(values):
            label = Label(self, text=str(val), bg=bg, fg="#334e68")
            label.grid(row=0, column=i, sticky="w", padx=8, pady=6)
            self.grid_columnconfigure(i, weight=1)
            
        # Add a separator line at the bottom
        sep = tk.Frame(self, height=1, bg="#e2e8f0")
        sep.place(relx=0, rely=1, relwidth=1, anchor="sw")

    def select(self):
        self.config(bg="#eff6ff")
        for child in self.winfo_children():
            if isinstance(child, Label):
                child.config(bg="#eff6ff")

    def deselect(self):
        self.config(bg=self.default_bg)
        for child in self.winfo_children():
            if isinstance(child, Label):
                child.config(bg=self.default_bg)

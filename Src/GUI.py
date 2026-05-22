import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from Event import Events
from System import System


COLS = ("Date", "Start", "End", "Event", "Locked")
COL_WIDTHS = (100, 70, 70, 280, 60)


class EventDialog(tk.Toplevel):
    """Modal dialog for adding or editing an event."""

    def __init__(self, parent, title, initial=None):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()
        self.result = None

        fields = [
            ("Date (YYYY-MM-DD)", "date"),
            ("Start time (HH:MM)", "stime"),
            ("End time   (HH:MM)", "etime"),
            ("Event name", "event"),
        ]

        self._vars = {}
        for row, (label, key) in enumerate(fields):
            tk.Label(self, text=label, anchor="w").grid(
                row=row, column=0, padx=12, pady=6, sticky="w"
            )
            var = tk.StringVar(value=(initial or {}).get(key, ""))
            self._vars[key] = var
            tk.Entry(self, textvariable=var, width=28).grid(
                row=row, column=1, padx=12, pady=6
            )

        self._solid = tk.BooleanVar(value=(initial or {}).get("solid", False))
        tk.Checkbutton(self, text="Locked", variable=self._solid).grid(
            row=len(fields), column=0, columnspan=2, pady=4
        )

        btn_frame = tk.Frame(self)
        btn_frame.grid(row=len(fields) + 1, column=0, columnspan=2, pady=10)
        tk.Button(btn_frame, text="Save", width=10, command=self._save).pack(
            side="left", padx=6
        )
        tk.Button(btn_frame, text="Cancel", width=10, command=self.destroy).pack(
            side="left", padx=6
        )

        self.transient(parent)
        self.wait_window()

    def _save(self):
        self.result = {
            "date": self._vars["date"].get().strip(),
            "stime": self._vars["stime"].get().strip(),
            "etime": self._vars["etime"].get().strip(),
            "event": self._vars["event"].get().strip(),
            "solid": self._solid.get(),
        }
        self.destroy()


class CalendarApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calendar")
        self.geometry("680x460")
        self.minsize(580, 340)
        self._build_ui()
        self._refresh()

    def _build_ui(self):
        # Toolbar
        toolbar = tk.Frame(self, pady=6)
        toolbar.pack(fill="x", padx=10)

        tk.Button(toolbar, text="Add", width=9, command=self._add).pack(side="left", padx=3)
        tk.Button(toolbar, text="Edit", width=9, command=self._edit).pack(side="left", padx=3)
        tk.Button(toolbar, text="Delete", width=9, command=self._delete).pack(side="left", padx=3)
        tk.Button(toolbar, text="Refresh", width=9, command=self._refresh).pack(side="left", padx=3)

        # Search bar
        tk.Label(toolbar, text="Filter date:").pack(side="left", padx=(20, 4))
        self._filter_var = tk.StringVar()
        self._filter_var.trace_add("write", lambda *_: self._apply_filter())
        tk.Entry(toolbar, textvariable=self._filter_var, width=14).pack(side="left")

        # Treeview
        frame = tk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._tree = ttk.Treeview(frame, columns=COLS, show="headings", selectmode="browse")
        for col, width in zip(COLS, COL_WIDTHS):
            self._tree.heading(col, text=col, command=lambda c=col: self._sort(c))
            self._tree.column(col, width=width, minwidth=40)

        scroll = ttk.Scrollbar(frame, orient="vertical", command=self._tree.yview)
        self._tree.configure(yscrollcommand=scroll.set)
        self._tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self._tree.tag_configure("locked", foreground="#c0392b")
        self._tree.tag_configure("today", background="#eaf4fb")

        # Status bar
        self._status = tk.StringVar()
        tk.Label(self, textvariable=self._status, anchor="w", fg="gray").pack(
            fill="x", padx=12, pady=(0, 4)
        )

    # ------------------------------------------------------------------
    # Data helpers
    # ------------------------------------------------------------------

    def _load(self):
        loader = Events("", "", "", "", False)
        return loader._load_events()

    def _refresh(self):
        self._events = self._load()
        self._apply_filter()

    def _apply_filter(self):
        query = self._filter_var.get().strip()
        filtered = [e for e in self._events if query in e["date"]] if query else self._events
        self._populate(filtered)

    def _populate(self, events):
        from datetime import date as date_cls
        today = date_cls.today().isoformat()

        self._tree.delete(*self._tree.get_children())
        sorted_events = sorted(events, key=lambda e: e["date"])
        for evt in sorted_events:
            locked_text = "Yes" if evt["solid"] else ""
            tags = []
            if evt["solid"]:
                tags.append("locked")
            if evt["date"] == today:
                tags.append("today")
            self._tree.insert(
                "",
                "end",
                values=(evt["date"], evt["stime"] or "", evt["etime"] or "", evt["event"], locked_text),
                tags=tags,
            )
        count = len(sorted_events)
        self._status.set(f"{count} event{'s' if count != 1 else ''}")

    def _selected_index(self):
        """Return the sorted index of the selected row, or None."""
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("No selection", "Please select an event first.")
            return None
        item = self._tree.item(sel[0])
        selected_date = item["values"][0]
        selected_stime = item["values"][1]
        selected_event = item["values"][3]

        sorted_events = sorted(self._events, key=lambda e: e["date"])
        for i, evt in enumerate(sorted_events):
            if (
                evt["date"] == selected_date
                and (evt.get("stime") or "") == selected_stime
                and evt["event"] == selected_event
            ):
                return i
        return None

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _add(self):
        dlg = EventDialog(self, "Add Event")
        if dlg.result is None:
            return
        r = dlg.result
        if not r["date"] or not r["event"]:
            messagebox.showerror("Missing fields", "Date and Event name are required.")
            return
        try:
            new_event = Events(r["date"], r["stime"], r["etime"], r["event"], r["solid"])
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        events = self._load()
        sys = System(events)

        if sys.is_solid(r["date"]):
            messagebox.showwarning(
                "Locked conflict",
                "A locked event already exists on that date. Event not saved.",
            )
            return

        if sys.is_overlapped(r["date"], r["stime"]):
            if not messagebox.askyesno(
                "Time overlap",
                "This event overlaps with an existing event. Add anyway?",
            ):
                return

        new_event._create_event()
        self._refresh()

    def _edit(self):
        idx = self._selected_index()
        if idx is None:
            return

        sorted_events = sorted(self._events, key=lambda e: e["date"])
        evt = sorted_events[idx]

        dlg = EventDialog(self, "Edit Event", initial=evt)
        if dlg.result is None:
            return
        r = dlg.result

        loader = Events("", "", "", "", False)
        loader._edit_event(
            idx,
            ndate=r["date"] or None,
            nstime=r["stime"] or None,
            netime=r["etime"] or None,
            nevent=r["event"] or None,
            nsolid=r["solid"],
        )
        self._refresh()

    def _delete(self):
        idx = self._selected_index()
        if idx is None:
            return

        sorted_events = sorted(self._events, key=lambda e: e["date"])
        evt = sorted_events[idx]

        if not messagebox.askyesno(
            "Confirm delete",
            f"Delete '{evt['event']}' on {evt['date']}?",
        ):
            return

        loader = Events("", "", "", "", False)
        loader._delete_event(idx)
        self._refresh()

    def _sort(self, col):
        rows = [(self._tree.set(child, col), child) for child in self._tree.get_children()]
        rows.sort()
        for i, (_, child) in enumerate(rows):
            self._tree.move(child, "", i)


if __name__ == "__main__":
    app = CalendarApp()
    app.mainloop()

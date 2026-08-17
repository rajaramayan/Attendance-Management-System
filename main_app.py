"""
main_app.py
-----------
Student Attendance Management System — Main Application
Multi-tab Tkinter GUI with Dashboard, Student/Teacher/Course Management,
Attendance Marking, and Report Generation.
"""

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
except ImportError as e:
    raise ImportError(
        "Tkinter is not available in this environment. "
        "main_app.py is a Tkinter desktop GUI app for local desktop execution. "
        "For Streamlit Cloud deployment, set your Main File Path to 'attendance_report.py'."
    ) from e
from datetime import date, datetime
import os
import calendar

from db_config import get_connection, test_connection
import attendance_report as ar

# ── Optional matplotlib for dashboard chart ───────────────────────────────────
try:
    import matplotlib
    matplotlib.use("TkAgg")
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MPL_OK = True
except ImportError:
    MPL_OK = False


# ══════════════════════════════════════════════════════════════════════════════
# THEME & COLOR CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
C_BG        = "#F0F4F8"   # window background
C_SIDEBAR   = "#1A202C"   # dark sidebar
C_PRIMARY   = "#2D3748"   # primary dark
C_ACCENT    = "#4F8EF7"   # blue accent
C_SUCCESS   = "#48BB78"   # green
C_DANGER    = "#FC8181"   # red
C_WARNING   = "#ED8936"   # orange
C_WHITE     = "#FFFFFF"
C_CARD      = "#FFFFFF"
C_BORDER    = "#CBD5E0"
C_TEXT      = "#2D3748"
C_TEXT_LIGHT= "#718096"
C_HEADING   = "#1A202C"

FONT_TITLE  = ("Segoe UI", 22, "bold")
FONT_HEADING= ("Segoe UI", 14, "bold")
FONT_SUBH   = ("Segoe UI", 11, "bold")
FONT_BODY   = ("Segoe UI", 10)
FONT_SMALL  = ("Segoe UI", 9)
FONT_BTN    = ("Segoe UI", 10, "bold")


# ══════════════════════════════════════════════════════════════════════════════
# DATE PICKER WIDGET
# ══════════════════════════════════════════════════════════════════════════════

class DatePickerDialog(tk.Toplevel):
    def __init__(self, parent, target_var):
        super().__init__(parent)
        self.target_var = target_var
        self.title("📅 Select Date")
        self.configure(bg=C_BG)
        center_window(self, 300, 310)
        self.resizable(False, False)
        self.grab_set()

        try:
            cur_d = datetime.strptime(target_var.get().strip(), "%Y-%m-%d")
        except Exception:
            cur_d = date.today()

        self.year = cur_d.year
        self.month = cur_d.month
        self.day = cur_d.day

        self._build_ui()

    def _build_ui(self):
        for w in self.winfo_children(): w.destroy()

        hdr = tk.Frame(self, bg=C_PRIMARY, pady=6)
        hdr.pack(fill="x")

        styled_button(hdr, "◀", lambda: self._prev_month(), color=C_PRIMARY, width=3).pack(side="left", padx=4)
        self._lbl = tk.Label(hdr, text=f"{calendar.month_name[self.month]} {self.year}",
                             font=FONT_SUBH, bg=C_PRIMARY, fg=C_WHITE)
        self._lbl.pack(side="left", expand=True)
        styled_button(hdr, "▶", lambda: self._next_month(), color=C_PRIMARY, width=3).pack(side="right", padx=4)

        days_f = tk.Frame(self, bg=C_BG, pady=2)
        days_f.pack(fill="x", padx=8)
        for i, d in enumerate(["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            days_f.columnconfigure(i, weight=1)
            tk.Label(days_f, text=d, font=FONT_SMALL, bg=C_BG, fg=C_TEXT_LIGHT).grid(row=0, column=i)

        grid_f = tk.Frame(self, bg=C_BG, pady=2)
        grid_f.pack(fill="both", expand=True, padx=8)
        for i in range(7): grid_f.columnconfigure(i, weight=1)

        cal = calendar.monthcalendar(self.year, self.month)
        for r_idx, week in enumerate(cal):
            for c_idx, day_num in enumerate(week):
                if day_num != 0:
                    is_sel = (day_num == self.day)
                    btn_color = C_ACCENT if is_sel else C_WHITE
                    fg_color = C_WHITE if is_sel else C_TEXT
                    b = tk.Button(grid_f, text=str(day_num), font=FONT_SMALL,
                                  bg=btn_color, fg=fg_color, relief="flat",
                                  command=lambda d=day_num: self._select_day(d))
                    b.grid(row=r_idx, column=c_idx, sticky="nsew", padx=1, pady=1)

    def _prev_month(self):
        if self.month == 1:
            self.month = 12; self.year -= 1
        else:
            self.month -= 1
        self._build_ui()

    def _next_month(self):
        if self.month == 12:
            self.month = 1; self.year += 1
        else:
            self.month += 1
        self._build_ui()

    def _select_day(self, day_num):
        sel_date = date(self.year, self.month, day_num).strftime("%Y-%m-%d")
        self.target_var.set(sel_date)
        self.destroy()


def add_date_picker(parent, target_var):
    btn = tk.Button(parent, text="📅", font=("Segoe UI", 9), bg=C_CARD, fg=C_PRIMARY,
                    relief="groove", cursor="hand2", command=lambda: DatePickerDialog(parent, target_var))
    return btn
FONT_MONO   = ("Consolas", 10)


# ══════════════════════════════════════════════════════════════════════════════
# UTILITY WIDGETS
# ══════════════════════════════════════════════════════════════════════════════

def styled_button(parent, text, command, color=C_ACCENT,
                  fg=C_WHITE, width=14, **kwargs):
    btn = tk.Button(
        parent, text=text, command=command, width=width,
        font=FONT_BTN, bg=color, fg=fg,
        activebackground=C_PRIMARY, activeforeground=C_WHITE,
        relief="flat", cursor="hand2", padx=8, pady=4, **kwargs
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=C_PRIMARY))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn


def card_frame(parent, **kwargs):
    return tk.Frame(parent, bg=C_CARD, relief="flat",
                    highlightthickness=1,
                    highlightbackground=C_BORDER, **kwargs)


def section_label(parent, text):
    tk.Label(parent, text=text, font=FONT_HEADING, bg=C_BG,
             fg=C_HEADING).pack(anchor="w", pady=(8, 4))


def separator(parent, color=C_BORDER):
    tk.Frame(parent, bg=color, height=1).pack(fill="x", pady=4)


def make_treeview(parent, columns, heights=14, show="headings"):
    style = ttk.Style()
    style.configure("Custom.Treeview",
                    background=C_WHITE, foreground=C_TEXT,
                    fieldbackground=C_WHITE, rowheight=28,
                    font=FONT_BODY)
    style.configure("Custom.Treeview.Heading",
                    background=C_PRIMARY, foreground=C_WHITE,
                    font=FONT_SUBH, relief="flat")
    style.map("Custom.Treeview",
              background=[("selected", C_ACCENT)],
              foreground=[("selected", C_WHITE)])

    frame = tk.Frame(parent, bg=C_CARD)
    tv    = ttk.Treeview(frame, columns=columns, show=show,
                          height=heights, style="Custom.Treeview",
                          selectmode="browse")
    vsb = ttk.Scrollbar(frame, orient="vertical",   command=tv.yview)
    hsb = ttk.Scrollbar(frame, orient="horizontal",  command=tv.xview)
    tv.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tv.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")
    frame.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    return frame, tv


def center_window(win, w, h):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x  = (sw - w) // 2
    y  = (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD TAB
# ══════════════════════════════════════════════════════════════════════════════

class DashboardFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self._build_ui()

    def _build_ui(self):
        # ── Top banner ─────────────────────────────────────────────────────────
        banner = tk.Frame(self, bg=C_PRIMARY, pady=18)
        banner.pack(fill="x")
        tk.Label(banner, text="🎓  College Attendance Management System",
                 font=("Segoe UI", 18, "bold"), bg=C_PRIMARY,
                 fg=C_WHITE).pack()
        self._date_lbl = tk.Label(
            banner, text="", font=FONT_BODY, bg=C_PRIMARY, fg="#A0AEC0"
        )
        self._date_lbl.pack()
        self._update_clock()

        # ── Scrollable body ────────────────────────────────────────────────────
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)

        # Stat cards row
        self._cards_frame = tk.Frame(body, bg=C_BG)
        self._cards_frame.pack(fill="x")

        # Chart + recent log row
        bottom = tk.Frame(body, bg=C_BG)
        bottom.pack(fill="both", expand=True, pady=(12, 0))
        bottom.columnconfigure(0, weight=3)
        bottom.columnconfigure(1, weight=2)

        # Chart
        self._chart_frame = card_frame(bottom)
        self._chart_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Recent attendance
        self._recent_frame = card_frame(bottom)
        self._recent_frame.grid(row=0, column=1, sticky="nsew")
        tk.Label(self._recent_frame, text="🕐  Recent Attendance",
                 font=FONT_SUBH, bg=C_CARD, fg=C_HEADING,
                 pady=10).pack(anchor="w", padx=12)
        self._recent_tree_frame, self._recent_tv = make_treeview(
            self._recent_frame,
            columns=("date", "student", "course", "status"),
            heights=10
        )
        for col, txt, w in [
            ("date", "Date", 90), ("student", "Student", 130),
            ("course", "Course", 70), ("status", "Status", 70)
        ]:
            self._recent_tv.heading(col, text=txt)
            self._recent_tv.column(col, width=w, anchor="center")
        self._recent_tree_frame.pack(fill="both", expand=True,
                                     padx=8, pady=(0, 8))

        # Refresh button
        styled_button(body, "🔄  Refresh Dashboard", self.refresh,
                      color=C_ACCENT, width=22).pack(pady=8)

        self.refresh()

    def _update_clock(self):
        now = datetime.now()
        self._date_lbl.config(
            text=now.strftime("%A, %d %B %Y   |   %I:%M %p")
        )
        self.after(30000, self._update_clock)

    def refresh(self):
        try:
            stats = ar.get_dashboard_stats()
        except Exception as e:
            messagebox.showerror("DB Error", str(e))
            return

        # Clear old cards
        for w in self._cards_frame.winfo_children():
            w.destroy()

        today_pct = (
            round(stats["today_present"] * 100 / stats["today_total"], 1)
            if stats["today_total"] else 0
        )

        cards = [
            ("👨‍🎓", "Students",      stats["total_students"],  C_ACCENT),
            ("👩‍🏫", "Teachers",      stats["total_teachers"],  "#805AD5"),
            ("📚",  "Courses",        stats["total_courses"],   "#38B2AC"),
            ("🏛️",  "Departments",    stats["total_dept"],      "#DD6B20"),
            ("📅",  "Today's Att. %", f"{today_pct}%",          C_SUCCESS if today_pct >= 75 else C_DANGER),
        ]
        self._cards_frame.columnconfigure(list(range(len(cards))), weight=1)
        for i, (icon, label, value, color) in enumerate(cards):
            cf = card_frame(self._cards_frame, padx=14, pady=14)
            cf.grid(row=0, column=i, sticky="nsew", padx=5)
            tk.Label(cf, text=icon, font=("Segoe UI", 24),
                     bg=C_CARD).pack()
            tk.Label(cf, text=str(value), font=("Segoe UI", 22, "bold"),
                     bg=C_CARD, fg=color).pack()
            tk.Label(cf, text=label, font=FONT_SMALL,
                     bg=C_CARD, fg=C_TEXT_LIGHT).pack()

        # Chart
        for w in self._chart_frame.winfo_children():
            w.destroy()
        tk.Label(self._chart_frame, text="📊  Attendance Analytics Overview",
                 font=FONT_SUBH, bg=C_CARD, fg=C_HEADING,
                 pady=8).pack(anchor="w", padx=12)

        course_pct = stats.get("course_pct", [])
        overall = stats.get("overall_status", {})
        if MPL_OK:
            fig = Figure(figsize=(5.5, 3.2), dpi=90, facecolor=C_CARD)

            # Subplot 1: Donut Chart for overall attendance
            ax1 = fig.add_subplot(121)
            pres = overall.get("present", 0) or 0
            absn = overall.get("absent", 0) or 0
            late = overall.get("late", 0) or 0
            tot = pres + absn + late
            if tot > 0:
                ax1.pie([pres, absn, late], labels=["Present", "Absent", "Late"],
                        colors=[C_SUCCESS, C_DANGER, C_WARNING], autopct="%1.0f%%",
                        startangle=90, pctdistance=0.7,
                        textprops=dict(size=7, color=C_TEXT),
                        wedgeprops=dict(width=0.45, edgecolor=C_CARD))
                ax1.set_title("Overall Status", fontsize=9, fontweight="bold", color=C_HEADING)
            else:
                ax1.text(0.5, 0.5, "No Data", ha="center", va="center", fontsize=8, color=C_TEXT_LIGHT)
                ax1.axis("off")

            # Subplot 2: Course Attendance Bar Chart
            ax2 = fig.add_subplot(122)
            if course_pct:
                names = [r["course_name"][:14] for r in course_pct]
                pcts  = [float(r["pct"]) if r["pct"] else 0 for r in course_pct]
                bar_colors = [C_SUCCESS if p >= 75 else C_DANGER for p in pcts]
                bars = ax2.barh(names, pcts, color=bar_colors, height=0.55)
                ax2.set_xlim(0, 100)
                ax2.axvline(x=75, color=C_WARNING, linestyle="--", linewidth=1, label="75%")
                ax2.tick_params(labelsize=7, colors=C_TEXT)
                ax2.set_facecolor(C_BG)
                for spine in ax2.spines.values():
                    spine.set_edgecolor(C_BORDER)
                for bar, pct in zip(bars, pcts):
                    ax2.text(min(pct + 1, 90), bar.get_y() + bar.get_height()/2,
                            f"{pct:.0f}%", va="center", fontsize=7, color=C_TEXT)
                ax2.set_title("Course Att. %", fontsize=9, fontweight="bold", color=C_HEADING)
            else:
                ax2.text(0.5, 0.5, "No Courses", ha="center", va="center", fontsize=8, color=C_TEXT_LIGHT)
                ax2.axis("off")

            fig.patch.set_facecolor(C_CARD)
            fig.tight_layout(pad=0.8)

            canvas = FigureCanvasTkAgg(fig, master=self._chart_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=(0, 4))
        else:
            tk.Label(self._chart_frame,
                     text="Install matplotlib for charts\n(pip install matplotlib)",
                     font=FONT_BODY, bg=C_CARD, fg=C_TEXT_LIGHT,
                     pady=40).pack()

        # Recent attendance
        self._recent_tv.delete(*self._recent_tv.get_children())
        for r in stats.get("recent", []):
            dt  = r["attendance_date"]
            dtf = dt.strftime("%d/%m") if hasattr(dt, "strftime") else str(dt)
            tag = r["status"].lower()
            self._recent_tv.insert("", "end",
                values=(dtf, r["student"], r["course_code"], r["status"]),
                tags=(tag,))
        self._recent_tv.tag_configure("present", foreground=C_SUCCESS)
        self._recent_tv.tag_configure("absent",  foreground=C_DANGER)
        self._recent_tv.tag_configure("late",    foreground=C_WARNING)


# ══════════════════════════════════════════════════════════════════════════════
# STUDENT MANAGEMENT TAB
# ══════════════════════════════════════════════════════════════════════════════

class StudentFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self._sel_id = None
        self._build_ui()

    def _build_ui(self):
        # ── Top bar ─────────────────────────────────────────────────────────
        top = tk.Frame(self, bg=C_BG, pady=10)
        top.pack(fill="x", padx=20)
        tk.Label(top, text="👨‍🎓  Student Management",
                 font=FONT_HEADING, bg=C_BG, fg=C_HEADING).pack(side="left")

        # Search
        search_f = tk.Frame(top, bg=C_BG)
        search_f.pack(side="right")
        tk.Label(search_f, text="🔍 Search:", font=FONT_BODY,
                 bg=C_BG).pack(side="left", padx=(0, 4))
        self._search_var = tk.StringVar()
        self._search_var.trace("w", lambda *a: self.load_students())
        tk.Entry(search_f, textvariable=self._search_var,
                 font=FONT_BODY, width=20).pack(side="left")

        # ── Main content ─────────────────────────────────────────────────────
        pane = tk.Frame(self, bg=C_BG)
        pane.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        pane.columnconfigure(0, weight=3)
        pane.columnconfigure(1, weight=2)

        # Treeview
        left = card_frame(pane)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)
        tk.Label(left, text="Student Records", font=FONT_SUBH,
                 bg=C_CARD, fg=C_HEADING, pady=8).grid(row=0, column=0,
                 columnspan=2, sticky="w", padx=10)

        cols = ("id", "roll", "name", "dept", "phone", "gender", "dob")
        tf, self._tv = make_treeview(left, cols, heights=16)
        tf.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        for col, txt, w in [
            ("id",     "ID",         40),
            ("roll",   "Roll No",    80),
            ("name",   "Name",      160),
            ("dept",   "Department",120),
            ("phone",  "Phone",      90),
            ("gender", "Gender",     70),
            ("dob",    "DOB",        90),
        ]:
            self._tv.heading(col, text=txt)
            self._tv.column(col, width=w, anchor="center")
        self._tv.bind("<<TreeviewSelect>>", self._on_select)

        # Form
        right = card_frame(pane)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="Student Details", font=FONT_SUBH,
                 bg=C_CARD, fg=C_HEADING, pady=8).pack(padx=12, anchor="w")
        separator(right)

        form = tk.Frame(right, bg=C_CARD)
        form.pack(padx=12, fill="x")

        labels   = ["Roll No *", "Full Name *", "Date of Birth\n(YYYY-MM-DD)",
                    "Address", "Phone", "Email", "Gender", "Department *"]
        self._vars = {}
        self._dept_map = {}

        for i, lbl in enumerate(labels):
            tk.Label(form, text=lbl, font=FONT_SMALL, bg=C_CARD,
                     fg=C_TEXT_LIGHT, anchor="w").grid(
                row=i*2, column=0, sticky="w", pady=(8, 0))
            if lbl == "Gender":
                var = tk.StringVar(value="Male")
                widget = ttk.Combobox(form, textvariable=var,
                                      values=["Male", "Female", "Other"],
                                      font=FONT_BODY, state="readonly", width=28)
            elif lbl == "Department *":
                var = tk.StringVar()
                widget = ttk.Combobox(form, textvariable=var,
                                      font=FONT_BODY, state="readonly", width=28)
                self._dept_combo = widget
            else:
                var = tk.StringVar()
                widget = tk.Entry(form, textvariable=var,
                                  font=FONT_BODY, width=30)
            self._vars[lbl] = var
            widget.grid(row=i*2+1, column=0, sticky="ew", pady=(2, 0))
        form.columnconfigure(0, weight=1)

        # Buttons
        btn_f = tk.Frame(right, bg=C_CARD)
        btn_f.pack(padx=12, pady=12, fill="x")
        styled_button(btn_f, "➕ Add",    self.add_student,
                      color=C_SUCCESS, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "✏️ Update", self.update_student,
                      color=C_ACCENT, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "🗑 Delete",  self.delete_student,
                      color=C_DANGER, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "🔄 Clear",   self.clear_form,
                      color=C_TEXT_LIGHT, width=10).pack(side="left", padx=3)

        self.load_depts()
        self.load_students()

    def load_depts(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT dept_id, dept_name FROM department ORDER BY dept_name")
            rows = cur.fetchall()
            cur.close(); conn.close()
            self._dept_map = {name: did for did, name in rows}
            self._dept_combo["values"] = list(self._dept_map.keys())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_students(self):
        search = self._search_var.get().strip()
        sql = """
            SELECT s.student_id, s.roll_no, s.name, d.dept_name,
                   s.phone, s.gender, s.dob, s.address, s.email, s.dept_id
            FROM student s LEFT JOIN department d ON s.dept_id=d.dept_id
        """
        params = []
        if search:
            sql += " WHERE s.name LIKE %s OR s.roll_no LIKE %s"
            params = [f"%{search}%", f"%{search}%"]
        sql += " ORDER BY s.roll_no"
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall()
            cur.close(); conn.close()
            self._all_rows = {r[0]: r for r in rows}
            self._tv.delete(*self._tv.get_children())
            for r in rows:
                dob = r[6].strftime("%Y-%m-%d") if r[6] else ""
                self._tv.insert("", "end", iid=r[0],
                    values=(r[0], r[1], r[2], r[3] or "—",
                            r[4] or "—", r[5] or "—", dob))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_select(self, event):
        sel = self._tv.selection()
        if not sel:
            return
        sid = int(sel[0])
        self._sel_id = sid
        r = self._all_rows.get(sid)
        if not r:
            return
        self._vars["Roll No *"].set(r[1])
        self._vars["Full Name *"].set(r[2])
        self._vars["Date of Birth\n(YYYY-MM-DD)"].set(
            r[6].strftime("%Y-%m-%d") if r[6] else "")
        self._vars["Address"].set(r[7] or "")
        self._vars["Phone"].set(r[4] or "")
        self._vars["Email"].set(r[8] or "")
        self._vars["Gender"].set(r[5] or "Male")
        # Dept
        dept_name = r[3] or ""
        self._vars["Department *"].set(dept_name)

    def _get_form(self):
        roll   = self._vars["Roll No *"].get().strip()
        name   = self._vars["Full Name *"].get().strip()
        dob    = self._vars["Date of Birth\n(YYYY-MM-DD)"].get().strip()
        addr   = self._vars["Address"].get().strip()
        phone  = self._vars["Phone"].get().strip()
        email  = self._vars["Email"].get().strip()
        gender = self._vars["Gender"].get()
        dept_n = self._vars["Department *"].get()
        dept_id= self._dept_map.get(dept_n)
        return roll, name, dob, addr, phone, email, gender, dept_id

    def add_student(self):
        roll, name, dob, addr, phone, email, gender, dept_id = self._get_form()
        if not roll or not name or not dept_id:
            messagebox.showwarning("Missing Data", "Roll No, Name, and Department are required.")
            return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                INSERT INTO student
                (roll_no,name,address,dob,phone,email,gender,dept_id)
                VALUES(%s,%s,%s,%s,%s,%s,%s,%s)
            """, (roll, name, addr or None, dob or None,
                  phone or None, email or None, gender, dept_id))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Success", f"Student '{name}' added successfully.")
            self.clear_form(); self.load_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_student(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Please select a student to update.")
            return
        roll, name, dob, addr, phone, email, gender, dept_id = self._get_form()
        if not roll or not name or not dept_id:
            messagebox.showwarning("Missing Data", "Roll No, Name, and Department are required.")
            return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                UPDATE student SET roll_no=%s,name=%s,address=%s,dob=%s,
                phone=%s,email=%s,gender=%s,dept_id=%s WHERE student_id=%s
            """, (roll, name, addr or None, dob or None,
                  phone or None, email or None, gender, dept_id, self._sel_id))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Updated", f"Student '{name}' updated.")
            self.clear_form(); self.load_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_student(self):
        if not self._sel_id:
            messagebox.showwarning("Select", "Please select a student to delete.")
            return
        name = self._vars["Full Name *"].get()
        if not messagebox.askyesno("Confirm Delete",
                f"Delete student '{name}'?\nThis will also remove all enrollment and attendance records."):
            return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM student WHERE student_id=%s", (self._sel_id,))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Deleted", f"Student '{name}' deleted.")
            self.clear_form(); self.load_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self._sel_id = None
        for var in self._vars.values():
            var.set("")
        self._vars["Gender"].set("Male")
        self._tv.selection_remove(*self._tv.selection())

    def refresh(self):
        self.load_depts()
        self.load_students()



# ══════════════════════════════════════════════════════════════════════════════
# TEACHER MANAGEMENT TAB
# ══════════════════════════════════════════════════════════════════════════════

class TeacherFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self._sel_id   = None
        self._dept_map = {}
        self._all_rows = {}
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg=C_BG, pady=10)
        top.pack(fill="x", padx=20)
        tk.Label(top, text="👩‍🏫  Teacher Management",
                 font=FONT_HEADING, bg=C_BG, fg=C_HEADING).pack(side="left")

        # Search
        search_f = tk.Frame(top, bg=C_BG)
        search_f.pack(side="right")
        tk.Label(search_f, text="🔍 Search:", font=FONT_BODY,
                 bg=C_BG).pack(side="left", padx=(0, 4))
        self._search_var = tk.StringVar()
        self._search_var.trace("w", lambda *a: self.load_teachers())
        tk.Entry(search_f, textvariable=self._search_var,
                 font=FONT_BODY, width=20).pack(side="left")

        pane = tk.Frame(self, bg=C_BG)
        pane.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        pane.columnconfigure(0, weight=3); pane.columnconfigure(1, weight=2)

        # List
        left = card_frame(pane)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.rowconfigure(1, weight=1); left.columnconfigure(0, weight=1)
        tk.Label(left, text="Teacher Records", font=FONT_SUBH,
                 bg=C_CARD, fg=C_HEADING, pady=8).grid(row=0, column=0,
                 sticky="w", padx=10)
        cols = ("id", "code", "name", "dept", "phone", "spec")
        tf, self._tv = make_treeview(left, cols, heights=18)
        tf.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        for c, t, w in [("id","ID",40),("code","Code",80),("name","Name",160),
                         ("dept","Department",120),("phone","Phone",90),
                         ("spec","Specialization",140)]:
            self._tv.heading(c, text=t); self._tv.column(c, width=w, anchor="center")
        self._tv.bind("<<TreeviewSelect>>", self._on_select)

        # Form
        right = card_frame(pane)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="Teacher Details", font=FONT_SUBH,
                 bg=C_CARD, fg=C_HEADING, pady=8).pack(padx=12, anchor="w")
        separator(right)

        form = tk.Frame(right, bg=C_CARD); form.pack(padx=12, fill="x")
        fields = ["Teacher Code *", "Full Name *", "Email", "Phone",
                  "Specialization", "Department *"]
        self._vars = {}
        for i, f in enumerate(fields):
            tk.Label(form, text=f, font=FONT_SMALL, bg=C_CARD,
                     fg=C_TEXT_LIGHT, anchor="w").grid(
                row=i*2, column=0, sticky="w", pady=(8, 0))
            if f == "Department *":
                var = tk.StringVar()
                widget = ttk.Combobox(form, textvariable=var,
                                      font=FONT_BODY, state="readonly", width=28)
                self._dept_combo = widget
            else:
                var = tk.StringVar()
                widget = tk.Entry(form, textvariable=var,
                                  font=FONT_BODY, width=30)
            self._vars[f] = var
            widget.grid(row=i*2+1, column=0, sticky="ew", pady=(2, 0))
        form.columnconfigure(0, weight=1)

        btn_f = tk.Frame(right, bg=C_CARD)
        btn_f.pack(padx=12, pady=12, fill="x")
        styled_button(btn_f, "➕ Add",    self.add_teacher,
                      color=C_SUCCESS, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "✏️ Update", self.update_teacher,
                      color=C_ACCENT, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "🗑 Delete",  self.delete_teacher,
                      color=C_DANGER, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "🔄 Clear",   self.clear_form,
                      color=C_TEXT_LIGHT, width=10).pack(side="left", padx=3)

        self.load_depts(); self.load_teachers()

    def load_depts(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT dept_id, dept_name FROM department ORDER BY dept_name")
            rows = cur.fetchall(); cur.close(); conn.close()
            self._dept_map = {n: d for d, n in rows}
            self._dept_combo["values"] = list(self._dept_map.keys())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_teachers(self):
        search = getattr(self, "_search_var", None)
        search_txt = search.get().strip() if search else ""
        sql = """SELECT t.teacher_id, t.teacher_code, t.name,
                        d.dept_name, t.phone, t.specialization,
                        t.email, t.dept_id
                 FROM teacher t LEFT JOIN department d ON t.dept_id=d.dept_id"""
        params = []
        if search_txt:
            sql += " WHERE t.name LIKE %s OR t.teacher_code LIKE %s OR t.specialization LIKE %s OR d.dept_name LIKE %s"
            params = [f"%{search_txt}%", f"%{search_txt}%", f"%{search_txt}%", f"%{search_txt}%"]
        sql += " ORDER BY t.name"
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall(); cur.close(); conn.close()
            self._all_rows = {r[0]: r for r in rows}
            self._tv.delete(*self._tv.get_children())
            for r in rows:
                self._tv.insert("", "end", iid=r[0],
                    values=(r[0], r[1], r[2], r[3] or "—",
                            r[4] or "—", r[5] or "—"))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_select(self, event):
        sel = self._tv.selection()
        if not sel: return
        tid = int(sel[0]); self._sel_id = tid
        r = self._all_rows.get(tid)
        if not r: return
        self._vars["Teacher Code *"].set(r[1])
        self._vars["Full Name *"].set(r[2])
        self._vars["Email"].set(r[6] or "")
        self._vars["Phone"].set(r[4] or "")
        self._vars["Specialization"].set(r[5] or "")
        # Find dept name
        for name, did in self._dept_map.items():
            if did == r[7]:
                self._vars["Department *"].set(name); break

    def add_teacher(self):
        code  = self._vars["Teacher Code *"].get().strip()
        name  = self._vars["Full Name *"].get().strip()
        email = self._vars["Email"].get().strip()
        phone = self._vars["Phone"].get().strip()
        spec  = self._vars["Specialization"].get().strip()
        dept_n= self._vars["Department *"].get()
        dept_id = self._dept_map.get(dept_n)
        if not code or not name or not dept_id:
            messagebox.showwarning("Missing Data","Code, Name, and Department are required."); return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""INSERT INTO teacher(teacher_code,name,email,phone,specialization,dept_id)
                           VALUES(%s,%s,%s,%s,%s,%s)""",
                        (code, name, email or None, phone or None, spec or None, dept_id))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Success", f"Teacher '{name}' added.")
            self.clear_form(); self.load_teachers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_teacher(self):
        if not self._sel_id:
            messagebox.showwarning("Select","Select a teacher to update."); return
        code  = self._vars["Teacher Code *"].get().strip()
        name  = self._vars["Full Name *"].get().strip()
        email = self._vars["Email"].get().strip()
        phone = self._vars["Phone"].get().strip()
        spec  = self._vars["Specialization"].get().strip()
        dept_n= self._vars["Department *"].get()
        dept_id = self._dept_map.get(dept_n)
        if not code or not name or not dept_id:
            messagebox.showwarning("Missing Data","Code, Name, and Department are required."); return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""UPDATE teacher SET teacher_code=%s,name=%s,email=%s,
                           phone=%s,specialization=%s,dept_id=%s WHERE teacher_id=%s""",
                        (code, name, email or None, phone or None,
                         spec or None, dept_id, self._sel_id))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Updated", f"Teacher '{name}' updated.")
            self.clear_form(); self.load_teachers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_teacher(self):
        if not self._sel_id:
            messagebox.showwarning("Select","Select a teacher to delete."); return
        name = self._vars["Full Name *"].get()
        if not messagebox.askyesno("Confirm","Delete teacher '{}'?".format(name)): return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM teacher WHERE teacher_id=%s", (self._sel_id,))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Deleted", f"Teacher '{name}' deleted.")
            self.clear_form(); self.load_teachers()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self._sel_id = None
        for v in self._vars.values(): v.set("")
        self._tv.selection_remove(*self._tv.selection())

    def refresh(self):
        self.load_depts()
        self.load_teachers()



# ══════════════════════════════════════════════════════════════════════════════
# COURSE & ENROLLMENT TAB
# ══════════════════════════════════════════════════════════════════════════════

class CourseFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self._sel_cid  = None
        self._dept_map = {}
        self._tchr_map = {}
        self._all_rows = {}
        self._build_ui()

    def _build_ui(self):
        # ── Notebook inside course tab ──────────────────────────────────────
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=8)

        # --- Course CRUD page ---
        crud_page = tk.Frame(nb, bg=C_BG)
        nb.add(crud_page, text="  📚 Courses  ")

        top = tk.Frame(crud_page, bg=C_BG, pady=10)
        top.pack(fill="x", padx=20)
        tk.Label(top, text="📚  Course Management",
                 font=FONT_HEADING, bg=C_BG, fg=C_HEADING).pack(side="left")

        # Search
        search_f = tk.Frame(top, bg=C_BG)
        search_f.pack(side="right")
        tk.Label(search_f, text="🔍 Search:", font=FONT_BODY,
                 bg=C_BG).pack(side="left", padx=(0, 4))
        self._search_var = tk.StringVar()
        self._search_var.trace("w", lambda *a: self.load_courses())
        tk.Entry(search_f, textvariable=self._search_var,
                 font=FONT_BODY, width=20).pack(side="left")

        pane = tk.Frame(crud_page, bg=C_BG)
        pane.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        pane.columnconfigure(0, weight=3); pane.columnconfigure(1, weight=2)

        left = card_frame(pane)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.rowconfigure(1, weight=1); left.columnconfigure(0, weight=1)
        tk.Label(left, text="Course Records", font=FONT_SUBH,
                 bg=C_CARD, fg=C_HEADING, pady=8).grid(row=0, column=0, sticky="w", padx=10)
        cols = ("id","code","name","credits","sem","dept","teacher")
        tf, self._tv = make_treeview(left, cols, heights=18)
        tf.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        for c, t, w in [("id","ID",40),("code","Code",80),("name","Course Name",180),
                         ("credits","Credits",60),("sem","Sem",50),
                         ("dept","Department",120),("teacher","Teacher",130)]:
            self._tv.heading(c, text=t); self._tv.column(c, width=w, anchor="center")
        self._tv.bind("<<TreeviewSelect>>", self._on_select)

        right = card_frame(pane)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="Course Details", font=FONT_SUBH,
                 bg=C_CARD, fg=C_HEADING, pady=8).pack(padx=12, anchor="w")
        separator(right)

        form = tk.Frame(right, bg=C_CARD); form.pack(padx=12, fill="x")
        fields = ["Course Code *","Course Name *","Credits","Semester",
                  "Department *","Teacher *"]
        self._vars = {}
        for i, f in enumerate(fields):
            tk.Label(form, text=f, font=FONT_SMALL, bg=C_CARD,
                     fg=C_TEXT_LIGHT, anchor="w").grid(
                row=i*2, column=0, sticky="w", pady=(8, 0))
            if f == "Department *":
                var = tk.StringVar()
                widget = ttk.Combobox(form, textvariable=var,
                                      font=FONT_BODY, state="readonly", width=28)
                self._dept_combo = widget
                widget.bind("<<ComboboxSelected>>", self._on_dept_change)
            elif f == "Teacher *":
                var = tk.StringVar()
                widget = ttk.Combobox(form, textvariable=var,
                                      font=FONT_BODY, state="readonly", width=28)
                self._tchr_combo = widget
            else:
                var = tk.StringVar()
                widget = tk.Entry(form, textvariable=var, font=FONT_BODY, width=30)
            self._vars[f] = var
            widget.grid(row=i*2+1, column=0, sticky="ew", pady=(2, 0))
        form.columnconfigure(0, weight=1)

        btn_f = tk.Frame(right, bg=C_CARD)
        btn_f.pack(padx=12, pady=12, fill="x")
        styled_button(btn_f, "➕ Add",    self.add_course,
                      color=C_SUCCESS, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "✏️ Update", self.update_course,
                      color=C_ACCENT, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "🗑 Delete",  self.delete_course,
                      color=C_DANGER, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "🔄 Clear",   self.clear_form,
                      color=C_TEXT_LIGHT, width=10).pack(side="left", padx=3)

        # --- Enrollment page ---
        enroll_page = tk.Frame(nb, bg=C_BG)
        nb.add(enroll_page, text="  📋 Enrollment  ")
        self._build_enrollment(enroll_page)

        self.load_depts(); self.load_courses()

    def _build_enrollment(self, page):
        top = tk.Frame(page, bg=C_BG, pady=10)
        top.pack(fill="x", padx=20)
        tk.Label(top, text="📋  Student Enrollment Management",
                 font=FONT_HEADING, bg=C_BG, fg=C_HEADING).pack(side="left")

        sel_f = tk.Frame(page, bg=C_BG)
        sel_f.pack(fill="x", padx=20, pady=(0, 8))
        tk.Label(sel_f, text="Select Course:", font=FONT_BODY,
                 bg=C_BG).pack(side="left", padx=(0, 6))
        self._enroll_course_var = tk.StringVar()
        self._enroll_course_combo = ttk.Combobox(
            sel_f, textvariable=self._enroll_course_var,
            font=FONT_BODY, state="readonly", width=35)
        self._enroll_course_combo.pack(side="left")
        self._enroll_course_combo.bind("<<ComboboxSelected>>",
                                       lambda e: self.load_enrollment())

        pane = tk.Frame(page, bg=C_BG)
        pane.pack(fill="both", expand=True, padx=20)
        pane.columnconfigure(0, weight=1); pane.columnconfigure(1, weight=1)

        # Enrolled
        lf = card_frame(pane)
        lf.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        lf.rowconfigure(1, weight=1); lf.columnconfigure(0, weight=1)
        tk.Label(lf, text="Enrolled Students", font=FONT_SUBH,
                 bg=C_CARD, fg=C_SUCCESS, pady=8).grid(row=0, column=0, sticky="w", padx=10)
        ef, self._enrolled_tv = make_treeview(lf,
                                              ("eid","roll","name"), heights=14)
        ef.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        for c, t, w in [("eid","#",40),("roll","Roll No",90),("name","Name",180)]:
            self._enrolled_tv.heading(c, text=t)
            self._enrolled_tv.column(c, width=w, anchor="center")
        styled_button(lf, "🗑 Unenroll Selected",
                      self.unenroll_student, color=C_DANGER, width=20
                      ).grid(row=2, column=0, pady=6)

        # Available
        rf = card_frame(pane)
        rf.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        rf.rowconfigure(1, weight=1); rf.columnconfigure(0, weight=1)
        tk.Label(rf, text="Available Students", font=FONT_SUBH,
                 bg=C_CARD, fg=C_ACCENT, pady=8).grid(row=0, column=0, sticky="w", padx=10)
        af, self._avail_tv = make_treeview(rf,
                                           ("sid","roll","name"), heights=14)
        af.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        for c, t, w in [("sid","#",40),("roll","Roll No",90),("name","Name",180)]:
            self._avail_tv.heading(c, text=t)
            self._avail_tv.column(c, width=w, anchor="center")
        styled_button(rf, "➕ Enroll Selected",
                      self.enroll_student, color=C_SUCCESS, width=20
                      ).grid(row=2, column=0, pady=6)

    def load_depts(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT dept_id, dept_name FROM department ORDER BY dept_name")
            rows = cur.fetchall(); cur.close(); conn.close()
            self._dept_map = {n: d for d, n in rows}
            self._dept_combo["values"] = list(self._dept_map.keys())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_dept_change(self, event=None):
        dept_n = self._vars["Department *"].get()
        dept_id = self._dept_map.get(dept_n)
        if not dept_id: return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT teacher_id, name FROM teacher WHERE dept_id=%s ORDER BY name",
                        (dept_id,))
            rows = cur.fetchall(); cur.close(); conn.close()
            self._tchr_map = {n: t for t, n in rows}
            self._tchr_combo["values"] = list(self._tchr_map.keys())
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_courses(self):
        search = getattr(self, "_search_var", None)
        search_txt = search.get().strip() if search else ""
        sql = """SELECT c.course_id, c.course_code, c.course_name,
                          c.credits, c.semester, d.dept_name, t.name,
                          c.dept_id, c.teacher_id
                       FROM course c
                       LEFT JOIN department d ON c.dept_id=d.dept_id
                       LEFT JOIN teacher t    ON c.teacher_id=t.teacher_id"""
        params = []
        if search_txt:
            sql += " WHERE c.course_name LIKE %s OR c.course_code LIKE %s OR d.dept_name LIKE %s OR t.name LIKE %s"
            params = [f"%{search_txt}%", f"%{search_txt}%", f"%{search_txt}%", f"%{search_txt}%"]
        sql += " ORDER BY c.course_code"
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall(); cur.close(); conn.close()
            self._all_rows = {r[0]: r for r in rows}
            self._tv.delete(*self._tv.get_children())
            course_list = []
            for r in rows:
                self._tv.insert("", "end", iid=r[0],
                    values=(r[0], r[1], r[2], r[3] or 3,
                            r[4] or "—", r[5] or "—", r[6] or "—"))
                course_list.append(f"{r[1]} — {r[2]}")
            self._enroll_course_combo["values"] = course_list
            self._course_id_list = [r[0] for r in rows]
            if course_list and not self._enroll_course_var.get():
                self._enroll_course_combo.current(0)
                self.load_enrollment()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_select(self, event):
        sel = self._tv.selection()
        if not sel: return
        cid = int(sel[0]); self._sel_cid = cid
        r = self._all_rows.get(cid)
        if not r: return
        self._vars["Course Code *"].set(r[1])
        self._vars["Course Name *"].set(r[2])
        self._vars["Credits"].set(str(r[3] or 3))
        self._vars["Semester"].set(r[4] or "")
        # Dept
        for n, d in self._dept_map.items():
            if d == r[7]: self._vars["Department *"].set(n); break
        self._on_dept_change()
        # Teacher
        for n, t in self._tchr_map.items():
            if t == r[8]: self._vars["Teacher *"].set(n); break

    def add_course(self):
        code  = self._vars["Course Code *"].get().strip()
        name  = self._vars["Course Name *"].get().strip()
        creds = self._vars["Credits"].get().strip()
        sem   = self._vars["Semester"].get().strip()
        dept_id = self._dept_map.get(self._vars["Department *"].get())
        tchr_id = self._tchr_map.get(self._vars["Teacher *"].get())
        if not code or not name or not dept_id or not tchr_id:
            messagebox.showwarning("Missing","Code, Name, Dept, and Teacher required."); return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""INSERT INTO course(course_code,course_name,credits,semester,dept_id,teacher_id)
                           VALUES(%s,%s,%s,%s,%s,%s)""",
                        (code, name, int(creds) if creds.isdigit() else 3,
                         sem or None, dept_id, tchr_id))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Success", f"Course '{name}' added.")
            self.clear_form(); self.load_courses()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_course(self):
        if not self._sel_cid:
            messagebox.showwarning("Select","Select a course first."); return
        code  = self._vars["Course Code *"].get().strip()
        name  = self._vars["Course Name *"].get().strip()
        creds = self._vars["Credits"].get().strip()
        sem   = self._vars["Semester"].get().strip()
        dept_id = self._dept_map.get(self._vars["Department *"].get())
        tchr_id = self._tchr_map.get(self._vars["Teacher *"].get())
        if not code or not name or not dept_id or not tchr_id:
            messagebox.showwarning("Missing","All fields are required."); return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""UPDATE course SET course_code=%s,course_name=%s,
                           credits=%s,semester=%s,dept_id=%s,teacher_id=%s
                           WHERE course_id=%s""",
                        (code, name, int(creds) if creds.isdigit() else 3,
                         sem or None, dept_id, tchr_id, self._sel_cid))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Updated", f"Course '{name}' updated.")
            self.clear_form(); self.load_courses()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_course(self):
        if not self._sel_cid:
            messagebox.showwarning("Select","Select a course first."); return
        name = self._vars["Course Name *"].get()
        if not messagebox.askyesno("Confirm",f"Delete course '{name}'?"):return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM course WHERE course_id=%s",(self._sel_cid,))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Deleted",f"Course '{name}' deleted.")
            self.clear_form(); self.load_courses()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self._sel_cid = None
        for v in self._vars.values(): v.set("")
        self._tv.selection_remove(*self._tv.selection())

    def load_enrollment(self):
        idx = self._enroll_course_combo.current()
        if idx < 0: return
        cid = self._course_id_list[idx]
        try:
            conn = get_connection(); cur = conn.cursor()
            # Enrolled
            cur.execute("""SELECT e.enrollment_id, s.roll_no, s.name
                           FROM enrollment e JOIN student s ON e.student_id=s.student_id
                           WHERE e.course_id=%s ORDER BY s.roll_no""", (cid,))
            enrolled = cur.fetchall()
            # Available (not enrolled)
            cur.execute("""SELECT s.student_id, s.roll_no, s.name
                           FROM student s
                           WHERE s.student_id NOT IN (
                               SELECT student_id FROM enrollment WHERE course_id=%s)
                           ORDER BY s.roll_no""", (cid,))
            available = cur.fetchall()
            cur.close(); conn.close()

            self._enrolled_tv.delete(*self._enrolled_tv.get_children())
            for r in enrolled:
                self._enrolled_tv.insert("","end", iid=r[0],
                    values=(r[0], r[1], r[2]))
            self._avail_tv.delete(*self._avail_tv.get_children())
            for r in available:
                self._avail_tv.insert("","end", iid=r[0],
                    values=(r[0], r[1], r[2]))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def enroll_student(self):
        idx = self._enroll_course_combo.current()
        if idx < 0:
            messagebox.showwarning("Select","Select a course first."); return
        cid = self._course_id_list[idx]
        sel = self._avail_tv.selection()
        if not sel:
            messagebox.showwarning("Select","Select a student to enroll."); return
        sid = int(sel[0])
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""INSERT INTO enrollment(student_id,course_id,enrollment_date)
                           VALUES(%s,%s,%s)""", (sid, cid, date.today()))
            conn.commit(); cur.close(); conn.close()
            self.load_enrollment()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def unenroll_student(self):
        sel = self._enrolled_tv.selection()
        if not sel:
            messagebox.showwarning("Select","Select an enrollment to remove."); return
        eid = int(sel[0])
        if not messagebox.askyesno("Confirm","Remove this enrollment? Attendance records will also be deleted."):
            return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM enrollment WHERE enrollment_id=%s",(eid,))
            conn.commit(); cur.close(); conn.close()
            self.load_enrollment()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh(self):
        self.load_depts()
        self.load_teachers()
        self.load_courses()
        self.load_enrollment()



# ══════════════════════════════════════════════════════════════════════════════
# MARK ATTENDANCE TAB
# ══════════════════════════════════════════════════════════════════════════════

class AttendanceFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self._course_id_list = []
        self._student_rows   = []
        self._status_vars    = {}
        self._build_ui()

    def _build_ui(self):
        # ── Controls row ────────────────────────────────────────────────────
        ctrl = card_frame(self)
        ctrl.pack(fill="x", padx=20, pady=(12, 0))
        inner = tk.Frame(ctrl, bg=C_CARD, pady=12)
        inner.pack(padx=16, fill="x")

        tk.Label(inner, text="✅  Mark Attendance",
                 font=FONT_HEADING, bg=C_CARD, fg=C_HEADING
                 ).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

        # Course
        tk.Label(inner, text="Course:", font=FONT_BODY, bg=C_CARD
                 ).grid(row=1, column=0, sticky="e", padx=(0, 4))
        self._course_var = tk.StringVar()
        self._course_combo = ttk.Combobox(inner, textvariable=self._course_var,
                                           font=FONT_BODY, state="readonly", width=35)
        self._course_combo.grid(row=1, column=1, padx=4)

        # Date
        tk.Label(inner, text="Date:", font=FONT_BODY, bg=C_CARD
                 ).grid(row=1, column=2, sticky="e", padx=(16, 4))
        self._date_var = tk.StringVar(value=date.today().strftime("%Y-%m-%d"))
        df = tk.Frame(inner, bg=C_CARD)
        df.grid(row=1, column=3, padx=4)
        tk.Entry(df, textvariable=self._date_var, font=FONT_BODY, width=12).pack(side="left")
        add_date_picker(df, self._date_var).pack(side="left", padx=(2, 0))

        styled_button(inner, "📂 Load Students", self.load_students,
                      color=C_ACCENT, width=16
                      ).grid(row=1, column=4, padx=12)

        # Bulk actions
        bulk = tk.Frame(inner, bg=C_CARD)
        bulk.grid(row=2, column=0, columnspan=6, pady=(8, 0), sticky="w")
        tk.Label(bulk, text="Bulk Mark:", font=FONT_SMALL,
                 bg=C_CARD, fg=C_TEXT_LIGHT).pack(side="left", padx=(0, 8))
        styled_button(bulk, "✅ All Present",
                      lambda: self.bulk_mark("Present"),
                      color=C_SUCCESS, width=13).pack(side="left", padx=4)
        styled_button(bulk, "❌ All Absent",
                      lambda: self.bulk_mark("Absent"),
                      color=C_DANGER, width=13).pack(side="left", padx=4)
        styled_button(bulk, "⏰ All Late",
                      lambda: self.bulk_mark("Late"),
                      color=C_WARNING, width=13).pack(side="left", padx=4)

        # ── Class Log / Topic Taught ─────────────────────────────────────────
        log_row = tk.Frame(inner, bg=C_CARD)
        log_row.grid(row=3, column=0, columnspan=6, pady=(10, 0), sticky="ew")
        tk.Label(log_row, text="📝 Topic Taught / Class Log:", font=FONT_SMALL,
                 bg=C_CARD, fg=C_HEADING).pack(side="left", padx=(0, 8))
        self._topic_var = tk.StringVar()
        tk.Entry(log_row, textvariable=self._topic_var, font=FONT_BODY,
                 width=70, relief="groove").pack(side="left", fill="x", expand=True)

        # ── Student checklist ────────────────────────────────────────────────
        list_card = card_frame(self)
        list_card.pack(fill="both", expand=True, padx=20, pady=10)

        # Header
        hdr = tk.Frame(list_card, bg=C_PRIMARY)
        hdr.pack(fill="x")
        for txt, w in [("#", 50),("Roll No",90),("Student Name",250),
                        ("Status",200),("Remarks",280)]:
            tk.Label(hdr, text=txt, font=FONT_SUBH, bg=C_PRIMARY,
                     fg=C_WHITE, width=w//8, anchor="center"
                     ).pack(side="left", padx=4, pady=6)

        # Scrollable list
        container = tk.Frame(list_card, bg=C_WHITE)
        container.pack(fill="both", expand=True)
        canvas = tk.Canvas(container, bg=C_WHITE, highlightthickness=0)
        vsb    = ttk.Scrollbar(container, orient="vertical",
                               command=canvas.yview)
        self._scroll_frame = tk.Frame(canvas, bg=C_WHITE)
        self._scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self._scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        self._canvas = canvas
        self._list_frame = list_card

        # ── Save & summary row ───────────────────────────────────────────────
        bot = tk.Frame(self, bg=C_BG)
        bot.pack(fill="x", padx=20, pady=(0, 12))
        styled_button(bot, "💾 Save Attendance", self.save_attendance,
                      color=C_SUCCESS, width=20).pack(side="left")
        self._summary_lbl = tk.Label(bot, text="", font=FONT_BODY,
                                     bg=C_BG, fg=C_TEXT_LIGHT)
        self._summary_lbl.pack(side="left", padx=16)

        self.load_course_list()

    def refresh(self):
        self.load_course_list()

    def load_course_list(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            app = self.winfo_toplevel()
            teacher_id = None
            if hasattr(app, "current_user") and app.current_user:
                if app.current_user.get("role") == "Teacher":
                    teacher_id = app.current_user.get("teacher_id")

            if teacher_id:
                cur.execute("""SELECT c.course_id, c.course_code, c.course_name
                               FROM course c WHERE c.teacher_id = %s ORDER BY c.course_code""", (teacher_id,))
            else:
                cur.execute("""SELECT c.course_id, c.course_code, c.course_name
                               FROM course c ORDER BY c.course_code""")
            rows = cur.fetchall(); cur.close(); conn.close()
            curr = self._course_var.get()
            self._course_id_list = [r[0] for r in rows]
            vals = [f"{r[1]} — {r[2]}" for r in rows]
            self._course_combo["values"] = vals
            if curr in vals:
                self._course_var.set(curr)
            elif vals:
                self._course_combo.current(0)
            else:
                self._course_var.set("")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_students(self):
        idx = self._course_combo.current()
        if idx < 0:
            messagebox.showwarning("Select","Please select a course."); return
        cid = self._course_id_list[idx]
        att_date = self._date_var.get().strip()
        try:
            datetime.strptime(att_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid Date","Use YYYY-MM-DD format."); return

        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("""
                SELECT e.enrollment_id, s.roll_no, s.name,
                       COALESCE(a.status,'Absent') AS status,
                       COALESCE(a.remarks,'')       AS remarks
                FROM enrollment e
                JOIN student s ON e.student_id=s.student_id
                LEFT JOIN attendance a
                    ON a.enrollment_id=e.enrollment_id
                   AND a.attendance_date=%s
                WHERE e.course_id=%s ORDER BY s.roll_no
            """, (att_date, cid))
            rows = cur.fetchall(); cur.close(); conn.close()
        except Exception as e:
            messagebox.showerror("Error", str(e)); return

        if not rows:
            for w in self._scroll_frame.winfo_children(): w.destroy()
            self._summary_lbl.config(text="No students enrolled.")
            messagebox.showinfo("No Students Enrolled",
                "No students are currently enrolled in this course.\n\n"
                "To mark attendance for this course:\n"
                "1. Go to Courses -> Enrollment tab.\n"
                "2. Select this course and enroll students.\n"
                "3. Return here and click Load Students.")
            return

        # Pre-populate topic taught for this course+date
        try:
            existing_topic = ar.get_class_log_for_date(cid, att_date)
            self._topic_var.set(existing_topic)
        except Exception:
            self._topic_var.set("")

        # Clear scroll frame
        for w in self._scroll_frame.winfo_children(): w.destroy()
        self._status_vars = {}
        self._remark_vars = {}
        self._student_rows = rows
        self._current_course_id = cid

        STATUS_COLORS = {"Present": C_SUCCESS, "Absent": C_DANGER, "Late": C_WARNING}
        ROW_BG = [C_WHITE, "#F7FAFC"]

        for i, (eid, roll, name, status, remarks) in enumerate(rows):
            row_bg = ROW_BG[i % 2]
            rf = tk.Frame(self._scroll_frame, bg=row_bg, pady=5)
            rf.pack(fill="x", padx=4)

            # Serial
            tk.Label(rf, text=str(i+1), font=FONT_BODY, bg=row_bg,
                     width=4, anchor="center").pack(side="left", padx=8)
            # Roll
            tk.Label(rf, text=roll, font=FONT_MONO, bg=row_bg,
                     width=10, anchor="w").pack(side="left", padx=4)
            # Name
            tk.Label(rf, text=name, font=FONT_BODY, bg=row_bg,
                     width=28, anchor="w").pack(side="left", padx=4)

            # Status buttons
            svar = tk.StringVar(value=status)
            self._status_vars[eid] = svar
            btn_f = tk.Frame(rf, bg=row_bg)
            btn_f.pack(side="left", padx=8)
            for st in ["Present", "Absent", "Late"]:
                clr = STATUS_COLORS[st]
                rb  = tk.Radiobutton(
                    btn_f, text=st, variable=svar, value=st,
                    font=FONT_SMALL, bg=row_bg,
                    fg=clr, selectcolor=row_bg,
                    activebackground=row_bg,
                    cursor="hand2"
                )
                rb.pack(side="left", padx=6)

            # Remarks
            rvar = tk.StringVar(value=remarks)
            self._remark_vars[eid] = rvar
            tk.Entry(rf, textvariable=rvar, font=FONT_SMALL,
                     width=30).pack(side="left", padx=8)

        self._update_summary()

    def bulk_mark(self, status):
        for var in self._status_vars.values():
            var.set(status)
        self._update_summary()

    def _update_summary(self):
        if not self._status_vars: return
        present = sum(1 for v in self._status_vars.values() if v.get()=="Present")
        late    = sum(1 for v in self._status_vars.values() if v.get()=="Late")
        absent  = sum(1 for v in self._status_vars.values() if v.get()=="Absent")
        total   = len(self._status_vars)
        pct = round((present+late)*100/total, 1) if total else 0
        self._summary_lbl.config(
            text=f"Total: {total}   ✅ Present: {present}   ⏰ Late: {late}"
                 f"   ❌ Absent: {absent}   Attendance: {pct}%"
        )

    def save_attendance(self):
        if not self._status_vars:
            messagebox.showwarning("No Data","Load students first."); return
        att_date = self._date_var.get().strip()
        try:
            conn = get_connection(); cur = conn.cursor()
            for eid, svar in self._status_vars.items():
                remark = self._remark_vars.get(eid, tk.StringVar()).get()
                cur.execute("""
                    INSERT INTO attendance(enrollment_id,attendance_date,status,remarks)
                    VALUES(%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE status=%s, remarks=%s,
                    marked_at=CURRENT_TIMESTAMP
                """, (eid, att_date, svar.get(), remark or None,
                      svar.get(), remark or None))
            conn.commit(); cur.close(); conn.close()
        except Exception as e:
            messagebox.showerror("Save Error", str(e)); return

        # Save class log topic
        topic = self._topic_var.get().strip()
        if topic:
            try:
                app = self.winfo_toplevel()
                teacher_id = None
                if hasattr(app, "current_user") and app.current_user:
                    teacher_id = app.current_user.get("teacher_id")
                cid = getattr(self, "_current_course_id", None)
                if cid:
                    ar.save_class_log(cid, teacher_id, att_date, topic)
            except Exception as e:
                messagebox.showwarning("Class Log Warning",
                    f"Attendance saved, but class log could not be saved:\n{e}")

        self._update_summary()
        messagebox.showinfo("Saved",
            f"Attendance saved for {len(self._status_vars)} students on {att_date}."
            + (f"\n📝 Class log recorded: '{topic[:60]}{'...' if len(topic)>60 else ''}'"
               if topic else ""))


# ══════════════════════════════════════════════════════════════════════════════
# REPORTS TAB
# ══════════════════════════════════════════════════════════════════════════════

class ReportFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self._data      = []
        self._course_ids= []
        self._build_ui()

    def _build_ui(self):
        # ── Controls ─────────────────────────────────────────────────────────
        ctrl = card_frame(self)
        ctrl.pack(fill="x", padx=20, pady=(12, 0))
        inner = tk.Frame(ctrl, bg=C_CARD, pady=12)
        inner.pack(padx=16, fill="x")

        tk.Label(inner, text="📄  Report Generation",
                 font=FONT_HEADING, bg=C_CARD, fg=C_HEADING
                 ).grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 10))

        # Report type
        tk.Label(inner, text="Report Type:", font=FONT_BODY, bg=C_CARD
                 ).grid(row=1, column=0, sticky="e", padx=(0, 4))
        self._report_var = tk.StringVar(value="Student Attendance Summary")
        reports = ["Student Attendance Summary",
                   "Defaulter List",
                   "Course Daily Summary",
                   "Date-Range Report",
                   "📝 Daily Class Log",
                   "📊 Teacher Progress Tracker"]
        ttk.Combobox(inner, textvariable=self._report_var,
                     values=reports, font=FONT_BODY,
                     state="readonly", width=28
                     ).grid(row=1, column=1, padx=4)

        # Course filter
        tk.Label(inner, text="Course:", font=FONT_BODY, bg=C_CARD
                 ).grid(row=1, column=2, sticky="e", padx=(16, 4))
        self._c_var = tk.StringVar(value="All Courses")
        self._c_combo = ttk.Combobox(inner, textvariable=self._c_var,
                                      font=FONT_BODY, state="readonly", width=28)
        self._c_combo.grid(row=1, column=3, padx=4)

        # Date range
        tk.Label(inner, text="From:", font=FONT_BODY, bg=C_CARD
                 ).grid(row=1, column=4, sticky="e", padx=(16, 4))
        self._from_var = tk.StringVar()
        df1 = tk.Frame(inner, bg=C_CARD)
        df1.grid(row=1, column=5, padx=4)
        tk.Entry(df1, textvariable=self._from_var, font=FONT_BODY, width=10).pack(side="left")
        add_date_picker(df1, self._from_var).pack(side="left", padx=(2, 0))

        tk.Label(inner, text="To:", font=FONT_BODY, bg=C_CARD
                 ).grid(row=1, column=6, sticky="e", padx=(8, 4))
        self._to_var = tk.StringVar()
        df2 = tk.Frame(inner, bg=C_CARD)
        df2.grid(row=1, column=7, padx=4)
        tk.Entry(df2, textvariable=self._to_var, font=FONT_BODY, width=10).pack(side="left")
        add_date_picker(df2, self._to_var).pack(side="left", padx=(2, 0))

        # Defaulter threshold
        tk.Label(inner, text="Min Att. %:", font=FONT_BODY, bg=C_CARD
                 ).grid(row=2, column=0, sticky="e", padx=(0, 4), pady=(8,0))
        self._thresh_var = tk.StringVar(value="75")
        tk.Entry(inner, textvariable=self._thresh_var,
                 font=FONT_BODY, width=6).grid(row=2, column=1, sticky="w",
                 padx=4, pady=(8,0))

        styled_button(inner, "🔍 Generate Report",
                      self.generate_report, color=C_ACCENT, width=16
                      ).grid(row=2, column=2, columnspan=2, padx=4, pady=(8,0))
        styled_button(inner, "📥 Export CSV",
                      self.export_csv, color=C_SUCCESS, width=12
                      ).grid(row=2, column=4, padx=4, pady=(8,0))
        styled_button(inner, "📄 Export PDF",
                      self.export_pdf, color="#805AD5", width=12
                      ).grid(row=2, column=5, padx=4, pady=(8,0))
        styled_button(inner, "⚠️ Warning Notice PDF",
                      self.export_warning_notice, color="#C53030", width=18
                      ).grid(row=2, column=6, columnspan=2, padx=4, pady=(8,0))

        # ── Results treeview ─────────────────────────────────────────────────
        res_card = card_frame(self)
        res_card.pack(fill="both", expand=True, padx=20, pady=10)
        res_card.rowconfigure(1, weight=1)
        res_card.columnconfigure(0, weight=1)
        self._results_label = tk.Label(res_card, text="Report Results",
                                       font=FONT_SUBH, bg=C_CARD,
                                       fg=C_HEADING, pady=8)
        self._results_label.grid(row=0, column=0, sticky="w", padx=10)
        self._count_lbl = tk.Label(res_card, text="",
                                   font=FONT_SMALL, bg=C_CARD, fg=C_TEXT_LIGHT)
        self._count_lbl.grid(row=0, column=1, sticky="e", padx=10)

        self._res_frame_holder = tk.Frame(res_card, bg=C_CARD)
        self._res_frame_holder.grid(row=1, column=0, columnspan=2,
                                    sticky="nsew", padx=8, pady=(0, 8))
        self._res_frame_holder.rowconfigure(0, weight=1)
        self._res_frame_holder.columnconfigure(0, weight=1)
        self._tv = None

        self.load_courses()

    def refresh(self):
        self.load_courses()

    def load_courses(self):
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("SELECT course_id, course_code, course_name FROM course ORDER BY course_code")
            rows = cur.fetchall(); cur.close(); conn.close()
            curr = self._c_var.get()
            self._course_ids = [None] + [r[0] for r in rows]
            vals = ["All Courses"] + [f"{r[1]} — {r[2]}" for r in rows]
            self._c_combo["values"] = vals
            if curr in vals:
                self._c_var.set(curr)
            else:
                self._c_combo.current(0)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def generate_report(self):
        rtype   = self._report_var.get()
        c_idx   = self._c_combo.current()
        cid     = self._course_ids[c_idx] if c_idx >= 0 else None
        from_d  = self._from_var.get().strip() or None
        to_d    = self._to_var.get().strip() or None
        thresh  = int(self._thresh_var.get() or 75)

        try:
            if rtype == "Student Attendance Summary":
                self._data = ar.get_student_attendance_summary(
                    course_id=cid, start_date=from_d, end_date=to_d)
            elif rtype == "Defaulter List":
                self._data = ar.get_defaulter_list(
                    threshold=thresh, course_id=cid)
            elif rtype == "Course Daily Summary":
                self._data = ar.get_course_daily_summary(
                    start_date=from_d, end_date=to_d)
            elif rtype == "Date-Range Report":
                if not from_d or not to_d:
                    messagebox.showwarning("Date Range","Enter both From and To dates."); return
                self._data = ar.get_date_range_report(from_d, to_d, cid)
            elif rtype == "📝 Daily Class Log":
                # Use 'From' date as target date; default to today
                target = from_d or date.today().isoformat()
                self._data = ar.get_daily_class_log(target_date=target)
                if not self._data:
                    messagebox.showinfo("No Log Entries",
                        f"No class log entries found for {target}.\n\n"
                        "Teachers need to enter a 'Topic Taught' when saving attendance.")
                    self._data = []
            elif rtype == "📊 Teacher Progress Tracker":
                self._data = ar.get_teacher_progress_report()
        except Exception as e:
            messagebox.showerror("Error", str(e)); return

        self._render_table()

    def _render_table(self):
        for w in self._res_frame_holder.winfo_children(): w.destroy()
        self._tv = None
        if not self._data:
            tk.Label(self._res_frame_holder, text="No data found.",
                     font=FONT_BODY, bg=C_CARD, fg=C_TEXT_LIGHT,
                     pady=40).pack()
            self._count_lbl.config(text="0 records")
            return

        cols = list(self._data[0].keys())
        tf, tv = make_treeview(self._res_frame_holder, cols, heights=18)
        tf.grid(row=0, column=0, sticky="nsew")
        self._res_frame_holder.rowconfigure(0, weight=1)
        self._res_frame_holder.columnconfigure(0, weight=1)

        col_w = max(80, 900 // len(cols))
        for c in cols:
            tv.heading(c, text=c.replace("_", " ").title())
            tv.column(c, width=col_w, anchor="center")

        for r in self._data:
            vals = []
            for k in cols:
                v = r.get(k)
                if v is None: v = "—"
                elif hasattr(v, "strftime"): v = v.strftime("%d/%m/%Y")
                vals.append(str(v))
            pct_val = r.get("attendance_pct")
            status  = r.get("status", "")
            if pct_val is not None and float(pct_val or 0) < 75:
                tag = "danger"
            elif status == "Absent":
                tag = "danger"
            elif status == "Late":
                tag = "warn"
            else:
                tag = "ok"
            tv.insert("", "end", values=vals, tags=(tag,))

        tv.tag_configure("danger", foreground=C_DANGER)
        tv.tag_configure("warn",   foreground=C_WARNING)
        tv.tag_configure("ok",     foreground=C_TEXT)

        self._tv = tv
        self._count_lbl.config(text=f"{len(self._data)} records")

    def export_csv(self):
        if not self._data:
            messagebox.showwarning("No Data","Generate a report first."); return
        fp = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files","*.csv")],
            initialfile=f"attendance_report_{date.today()}.csv"
        )
        if not fp: return
        try:
            ar.export_to_csv(self._data, fp)
            messagebox.showinfo("Exported", f"CSV saved to:\n{fp}")
            os.startfile(fp)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_pdf(self):
        if not self._data:
            messagebox.showwarning("No Data","Generate a report first."); return
        fp = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files","*.pdf")],
            initialfile=f"attendance_report_{date.today()}.pdf"
        )
        if not fp: return
        try:
            rtype = self._report_var.get()
            ar.export_to_pdf(self._data, fp, title=rtype,
                             subtitle=f"Generated on {date.today().strftime('%d %B %Y')}",
                             orientation="landscape")
            messagebox.showinfo("Exported", f"PDF saved to:\n{fp}")
            os.startfile(fp)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def export_warning_notice(self):
        if self._report_var.get() != "Defaulter List" or not self._tv:
            messagebox.showwarning("Defaulter List Required", "Please select 'Defaulter List' report and click Generate Report first.")
            return

        sel = self._tv.selection()
        if not sel:
            messagebox.showwarning("Select Student", "Please select a student row from the defaulter table.")
            return

        item = self._tv.item(sel[0])
        vals = item.get("values", [])
        if not vals: return
        roll_no = str(vals[0])

        fp = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")],
            initialfile=f"warning_notice_{roll_no}_{date.today()}.pdf"
        )
        if not fp: return
        try:
            ar.generate_defaulter_notice_pdf(roll_no, fp)
            messagebox.showinfo("Warning Notice Generated", f"Official Warning Notice PDF saved to:\n{fp}")
            os.startfile(fp)
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ══════════════════════════════════════════════════════════════════════════════
# DEPARTMENT TAB (bonus)
# ══════════════════════════════════════════════════════════════════════════════

class DepartmentFrame(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=C_BG)
        self._sel_id   = None
        self._all_rows = {}
        self._build_ui()

    def _build_ui(self):
        top = tk.Frame(self, bg=C_BG, pady=10)
        top.pack(fill="x", padx=20)
        tk.Label(top, text="🏛️  Department Management",
                 font=FONT_HEADING, bg=C_BG, fg=C_HEADING).pack(side="left")

        # Search
        search_f = tk.Frame(top, bg=C_BG)
        search_f.pack(side="right")
        tk.Label(search_f, text="🔍 Search:", font=FONT_BODY,
                 bg=C_BG).pack(side="left", padx=(0, 4))
        self._search_var = tk.StringVar()
        self._search_var.trace("w", lambda *a: self.load_depts())
        tk.Entry(search_f, textvariable=self._search_var,
                 font=FONT_BODY, width=20).pack(side="left")

        pane = tk.Frame(self, bg=C_BG)
        pane.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        pane.columnconfigure(0, weight=3); pane.columnconfigure(1, weight=1)

        left = card_frame(pane)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.rowconfigure(1, weight=1); left.columnconfigure(0, weight=1)
        tk.Label(left, text="Departments", font=FONT_SUBH,
                 bg=C_CARD, fg=C_HEADING, pady=8).grid(row=0, column=0,
                 sticky="w", padx=10)
        cols = ("id","code","name","students","teachers","courses")
        tf, self._tv = make_treeview(left, cols, heights=18)
        tf.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        for c, t, w in [("id","ID",40),("code","Code",70),("name","Name",180),
                         ("students","Students",80),("teachers","Teachers",80),
                         ("courses","Courses",80)]:
            self._tv.heading(c, text=t); self._tv.column(c, width=w, anchor="center")
        self._tv.bind("<<TreeviewSelect>>", self._on_select)

        right = card_frame(pane)
        right.grid(row=0, column=1, sticky="nsew")
        tk.Label(right, text="Department Details", font=FONT_SUBH,
                 bg=C_CARD, fg=C_HEADING, pady=8).pack(padx=12, anchor="w")
        separator(right)
        form = tk.Frame(right, bg=C_CARD); form.pack(padx=12, fill="x")
        self._vars = {}
        for i, f in enumerate(["Department Code *","Department Name *"]):
            tk.Label(form, text=f, font=FONT_SMALL, bg=C_CARD,
                     fg=C_TEXT_LIGHT, anchor="w").grid(row=i*2, column=0, sticky="w", pady=(8,0))
            var = tk.StringVar()
            tk.Entry(form, textvariable=var, font=FONT_BODY, width=28
                     ).grid(row=i*2+1, column=0, sticky="ew", pady=(2,0))
            self._vars[f] = var
        form.columnconfigure(0, weight=1)

        btn_f = tk.Frame(right, bg=C_CARD)
        btn_f.pack(padx=12, pady=12, fill="x")
        styled_button(btn_f, "➕ Add",    self.add_dept,
                      color=C_SUCCESS, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "✏️ Update", self.update_dept,
                      color=C_ACCENT, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "🗑 Delete",  self.delete_dept,
                      color=C_DANGER, width=10).pack(side="left", padx=3)
        styled_button(btn_f, "🔄 Clear",   self.clear_form,
                      color=C_TEXT_LIGHT, width=10).pack(side="left", padx=3)

        self.load_depts()

    def load_depts(self):
        search = getattr(self, "_search_var", None)
        search_txt = search.get().strip() if search else ""
        sql = """SELECT d.dept_id, d.dept_code, d.dept_name,
            (SELECT COUNT(*) FROM student WHERE dept_id=d.dept_id) AS students,
            (SELECT COUNT(*) FROM teacher WHERE dept_id=d.dept_id) AS teachers,
            (SELECT COUNT(*) FROM course  WHERE dept_id=d.dept_id) AS courses
            FROM department d"""
        params = []
        if search_txt:
            sql += " WHERE d.dept_name LIKE %s OR d.dept_code LIKE %s"
            params = [f"%{search_txt}%", f"%{search_txt}%"]
        sql += " ORDER BY d.dept_name"
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute(sql, params)
            rows = cur.fetchall(); cur.close(); conn.close()
            self._all_rows = {r[0]: r for r in rows}
            self._tv.delete(*self._tv.get_children())
            for r in rows:
                self._tv.insert("","end", iid=r[0], values=r)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def _on_select(self, event):
        sel = self._tv.selection()
        if not sel: return
        did = int(sel[0]); self._sel_id = did
        r = self._all_rows.get(did)
        if not r: return
        self._vars["Department Code *"].set(r[1])
        self._vars["Department Name *"].set(r[2])

    def add_dept(self):
        code = self._vars["Department Code *"].get().strip()
        name = self._vars["Department Name *"].get().strip()
        if not code or not name:
            messagebox.showwarning("Missing","Code and Name are required."); return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("INSERT INTO department(dept_code,dept_name) VALUES(%s,%s)",
                        (code, name))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Success",f"Department '{name}' added.")
            self.clear_form(); self.load_depts()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_dept(self):
        if not self._sel_id:
            messagebox.showwarning("Select","Select a department first."); return
        code = self._vars["Department Code *"].get().strip()
        name = self._vars["Department Name *"].get().strip()
        if not code or not name:
            messagebox.showwarning("Missing","Code and Name required."); return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("UPDATE department SET dept_code=%s,dept_name=%s WHERE dept_id=%s",
                        (code, name, self._sel_id))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Updated",f"Department updated.")
            self.clear_form(); self.load_depts()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_dept(self):
        if not self._sel_id:
            messagebox.showwarning("Select","Select a department first."); return
        name = self._vars["Department Name *"].get()
        if not messagebox.askyesno("Confirm",f"Delete department '{name}'?"): return
        try:
            conn = get_connection(); cur = conn.cursor()
            cur.execute("DELETE FROM department WHERE dept_id=%s",(self._sel_id,))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Deleted","Department deleted.")
            self.clear_form(); self.load_depts()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_form(self):
        self._sel_id = None
        for v in self._vars.values(): v.set("")
        self._tv.selection_remove(*self._tv.selection())

    def refresh(self):
        self.load_depts()



# ══════════════════════════════════════════════════════════════════════════════
# STUDENT PORTAL FRAME
# ══════════════════════════════════════════════════════════════════════════════

class StudentPortalFrame(tk.Frame):
    def __init__(self, parent, student_id):
        super().__init__(parent, bg=C_BG)
        self.student_id = student_id
        self._build_ui()

    def _build_ui(self):
        for w in self.winfo_children(): w.destroy()

        conn = get_connection(); cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT s.student_id, s.roll_no, s.name, s.email, s.phone, s.gender, s.dob, d.dept_name
            FROM student s LEFT JOIN department d ON s.dept_id=d.dept_id
            WHERE s.student_id=%s
        """, (self.student_id,))
        st = cur.fetchone()
        cur.close(); conn.close()

        if not st: return

        # Header banner
        banner = card_frame(self, padx=18, pady=16)
        banner.pack(fill="x", padx=20, pady=(16, 10))

        info_f = tk.Frame(banner, bg=C_CARD)
        info_f.pack(side="left")
        tk.Label(info_f, text=f"👋 Welcome, {st['name']}", font=FONT_TITLE, bg=C_CARD, fg=C_HEADING).pack(anchor="w")
        tk.Label(info_f, text=f"Roll No: {st['roll_no']}   |   Department: {st['dept_name'] or 'N/A'}   |   Email: {st['email'] or 'N/A'}",
                 font=FONT_BODY, bg=C_CARD, fg=C_TEXT_LIGHT).pack(anchor="w", pady=(2, 0))

        courses_summary = ar.get_student_attendance_summary(student_id=self.student_id)
        tot_classes = sum(c["total_classes"] or 0 for c in courses_summary)
        tot_attended = sum(c["classes_attended"] or 0 for c in courses_summary)
        overall_pct = round(tot_attended * 100.0 / tot_classes, 1) if tot_classes > 0 else 0.0

        badge_color = C_SUCCESS if overall_pct >= 75 else C_DANGER
        badge_text = "Good Standing" if overall_pct >= 75 else "Warning: Low Attendance"

        badge_f = tk.Frame(banner, bg=badge_color, padx=16, pady=8)
        badge_f.pack(side="right")
        tk.Label(badge_f, text=f"{overall_pct}%", font=("Segoe UI", 18, "bold"), bg=badge_color, fg=C_WHITE).pack()
        tk.Label(badge_f, text=badge_text, font=FONT_SMALL, bg=badge_color, fg=C_WHITE).pack()

        # Body: Enrolled Courses Attendance Table
        body = tk.Frame(self, bg=C_BG)
        body.pack(fill="both", expand=True, padx=20, pady=10)

        card = card_frame(body)
        card.pack(fill="both", expand=True)
        tk.Label(card, text="📚  Your Enrolled Courses & Attendance Performance",
                 font=FONT_SUBH, bg=C_CARD, fg=C_HEADING, pady=10).pack(anchor="w", padx=12)

        cols = ("code", "name", "total", "attended", "pct", "status")
        tf, tv = make_treeview(card, cols, heights=12)
        tf.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for c, t, w in [
            ("code", "Course Code", 100), ("name", "Course Name", 240),
            ("total", "Total Classes", 110), ("attended", "Classes Attended", 120),
            ("pct", "Attendance %", 120), ("status", "Academic Status", 150)
        ]:
            tv.heading(c, text=t)
            tv.column(c, width=w, anchor="center")

        tv.tag_configure("pass", foreground=C_SUCCESS)
        tv.tag_configure("defaulter", foreground=C_DANGER)

        for r in courses_summary:
            pct = float(r["attendance_pct"]) if r["attendance_pct"] is not None else 0.0
            tag = "pass" if pct >= 75 else "defaulter"
            stat = "Satisfactory" if pct >= 75 else "Deficient (<75%)"
            tv.insert("", "end", values=(r["course_code"], r["course_name"],
                                         r["total_classes"], r["classes_attended"],
                                         f"{pct:.1f}%", stat), tags=(tag,))

    def refresh(self):
        self._build_ui()


# ══════════════════════════════════════════════════════════════════════════════
# CHANGE PASSWORD DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class ChangePasswordDialog(tk.Toplevel):
    """Allows any logged-in user to change their own password."""
    def __init__(self, parent, user_id, username):
        super().__init__(parent)
        self.user_id  = user_id
        self.username = username
        self.title("🔑 Change Password")
        self.configure(bg=C_BG)
        center_window(self, 400, 420)
        self.resizable(False, False)
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        banner = tk.Frame(self, bg=C_PRIMARY, pady=14)
        banner.pack(fill="x")
        tk.Label(banner, text="🔐  Change Password",
                 font=("Segoe UI", 13, "bold"), bg=C_PRIMARY, fg=C_WHITE).pack()
        tk.Label(banner, text=f"Account: {self.username}",
                 font=FONT_SMALL, bg=C_PRIMARY, fg="#A0AEC0").pack(pady=(2, 0))

        card = card_frame(self, padx=16, pady=16)
        card.pack(padx=24, pady=16, fill="both", expand=True)

        tk.Label(card, text="Current Password", font=FONT_SUBH, bg=C_CARD, fg=C_HEADING
                 ).pack(anchor="w", pady=(5, 2))
        self._cur_entry = tk.Entry(card, font=FONT_BODY, show="•", width=28)
        self._cur_entry.pack(fill="x", pady=(0, 10))

        tk.Label(card, text="New Password", font=FONT_SUBH, bg=C_CARD, fg=C_HEADING
                 ).pack(anchor="w", pady=(5, 2))
        self._new_entry = tk.Entry(card, font=FONT_BODY, show="•", width=28)
        self._new_entry.pack(fill="x", pady=(0, 10))

        tk.Label(card, text="Confirm New Password", font=FONT_SUBH, bg=C_CARD, fg=C_HEADING
                 ).pack(anchor="w", pady=(5, 2))
        self._cfm_entry = tk.Entry(card, font=FONT_BODY, show="•", width=28)
        self._cfm_entry.pack(fill="x", pady=(0, 12))

        self._err_lbl = tk.Label(card, text="", font=FONT_SMALL, bg=C_CARD, fg=C_DANGER, wraplength=320)
        self._err_lbl.pack(pady=(0, 5))

        styled_button(card, "✔️ Update Password", self._save,
                      color=C_SUCCESS, width=22).pack(fill="x", pady=4)
        self.bind("<Return>", lambda e: self._save())

    def _save(self):
        cur_pwd = self._cur_entry.get()
        new_pwd = self._new_entry.get().strip()
        cfm_pwd = self._cfm_entry.get().strip()

        if not cur_pwd or not new_pwd or not cfm_pwd:
            self._err_lbl.config(text="All fields are required."); return
        if new_pwd != cfm_pwd:
            self._err_lbl.config(text="New passwords do not match."); return
        if len(new_pwd) < 6:
            self._err_lbl.config(text="New password must be at least 6 characters."); return

        try:
            conn = get_connection(); cur = conn.cursor(dictionary=True)
            cur.execute("SELECT user_id FROM users WHERE user_id=%s AND password_hash=%s",
                        (self.user_id, cur_pwd))
            row = cur.fetchone()
            if not row:
                cur.close(); conn.close()
                self._err_lbl.config(text="Current password is incorrect."); return

            cur.execute("UPDATE users SET password_hash=%s WHERE user_id=%s",
                        (new_pwd, self.user_id))
            conn.commit(); cur.close(); conn.close()
            messagebox.showinfo("Password Changed",
                "Your password has been updated successfully!", parent=self)
            self.destroy()
        except Exception as e:
            self._err_lbl.config(text=f"Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# LOGIN DIALOG
# ══════════════════════════════════════════════════════════════════════════════

class LoginDialog(tk.Toplevel):
    def __init__(self, parent, on_success):
        super().__init__(parent)
        self.on_success = on_success
        self.title("🔐 College Attendance System — Login")
        self.configure(bg=C_BG)
        center_window(self, 420, 490)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self._build_ui()

    def on_close(self):
        self.master.destroy()

    def _build_ui(self):
        banner = tk.Frame(self, bg=C_PRIMARY, pady=20)
        banner.pack(fill="x")
        tk.Label(banner, text="🎓 College Attendance System",
                 font=("Segoe UI", 14, "bold"), bg=C_PRIMARY, fg=C_WHITE).pack()
        tk.Label(banner, text="Sign in to access your account",
                 font=FONT_SMALL, bg=C_PRIMARY, fg="#A0AEC0").pack(pady=(2, 0))

        card = card_frame(self, padx=20, pady=20)
        card.pack(padx=30, pady=20, fill="both", expand=True)

        tk.Label(card, text="Username / Roll No", font=FONT_SUBH, bg=C_CARD, fg=C_HEADING).pack(anchor="w", pady=(5, 2))
        self._user_entry = tk.Entry(card, font=FONT_BODY, width=28)
        self._user_entry.pack(fill="x", pady=(0, 10))
        self._user_entry.insert(0, "admin")

        tk.Label(card, text="Password", font=FONT_SUBH, bg=C_CARD, fg=C_HEADING).pack(anchor="w", pady=(5, 2))
        self._pass_entry = tk.Entry(card, font=FONT_BODY, show="•", width=28)
        self._pass_entry.pack(fill="x", pady=(0, 10))
        self._pass_entry.insert(0, "admin123")

        tk.Label(card, text="Role", font=FONT_SUBH, bg=C_CARD, fg=C_HEADING).pack(anchor="w", pady=(5, 2))
        self._role_var = tk.StringVar(value="Admin")
        role_cb = ttk.Combobox(card, textvariable=self._role_var, values=["Admin", "Teacher", "Student"], font=FONT_BODY, state="readonly")
        role_cb.pack(fill="x", pady=(0, 15))

        self._err_lbl = tk.Label(card, text="", font=FONT_SMALL, bg=C_CARD, fg=C_DANGER)
        self._err_lbl.pack(pady=(0, 5))

        styled_button(card, "🔑 Sign In", self._login, color=C_ACCENT, width=20).pack(fill="x", pady=5)
        self.bind("<Return>", lambda e: self._login())

    def _login(self):
        uname = self._user_entry.get().strip()
        pwd = self._pass_entry.get().strip()
        role = self._role_var.get()
        if not uname or not pwd:
            self._err_lbl.config(text="Enter username and password.")
            return
        try:
            conn = get_connection(); cur = conn.cursor(dictionary=True)
            if role == "Student":
                cur.execute("""
                    SELECT u.user_id, u.username, u.role, u.student_id, s.name AS student_name, s.roll_no
                    FROM users u
                    LEFT JOIN student s ON u.student_id = s.student_id
                    WHERE (u.username=%s OR s.roll_no=%s) AND u.password_hash=%s AND u.role='Student'
                """, (uname, uname, pwd))
            else:
                cur.execute("""
                    SELECT u.user_id, u.username, u.role, u.teacher_id, t.name AS teacher_name
                    FROM users u
                    LEFT JOIN teacher t ON u.teacher_id = t.teacher_id
                    WHERE u.username=%s AND u.password_hash=%s AND u.role=%s
                """, (uname, pwd, role))
            user = cur.fetchone()
            cur.close(); conn.close()
            if user:
                self.on_success(user)
                self.destroy()
            else:
                self._err_lbl.config(text="Invalid credentials or role.")
        except Exception as e:
            self._err_lbl.config(text=f"DB Error: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN APPLICATION
# ══════════════════════════════════════════════════════════════════════════════

class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎓 College Attendance Management System")
        self.configure(bg=C_BG)
        center_window(self, 1280, 800)
        self.minsize(1100, 700)
        self.current_user = None

        # Configure ttk styles globally
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=C_BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        font=("Segoe UI", 10, "bold"),
                        padding=(16, 8),
                        background=C_PRIMARY,
                        foreground="#A0AEC0")
        style.map("TNotebook.Tab",
                  background=[("selected", C_ACCENT)],
                  foreground=[("selected", C_WHITE)])
        style.configure("TCombobox", font=FONT_BODY)
        style.configure("TScrollbar", background=C_BORDER, troughcolor=C_BG)

        self._check_connection()
        self.withdraw()
        self.show_login()

    def show_login(self):
        self.current_user = None
        LoginDialog(self, self.on_login_success)

    def on_login_success(self, user):
        self.current_user = user
        self.deiconify()
        self._build_ui()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            self.withdraw()
            self.show_login()

    def _check_connection(self):
        ok, msg = test_connection()
        if not ok:
            messagebox.showerror(
                "Database Connection Failed",
                f"Could not connect to MySQL:\n{msg}\n\n"
                "Please check db_config.py and ensure MySQL is running."
            )

    def _build_ui(self):
        for w in self.winfo_children():
            w.destroy()

        user = self.current_user or {"username": "Guest", "role": "Admin"}
        user_disp = user.get("student_name") or user.get("teacher_name") or user.get("username")
        role_disp = user.get("role", "Admin")

        # ── User Profile Top Bar ───────────────────────────────────────────────
        top_bar = tk.Frame(self, bg=C_PRIMARY, height=36)
        top_bar.pack(fill="x", side="top")
        tk.Label(top_bar, text="🎓 College Attendance System",
                 font=("Segoe UI", 11, "bold"), bg=C_PRIMARY, fg=C_WHITE,
                 padx=16).pack(side="left")

        u_frame = tk.Frame(top_bar, bg=C_PRIMARY)
        u_frame.pack(side="right", padx=12)
        tk.Label(u_frame, text=f"👤 Logged in as: {user_disp} ({role_disp})",
                 font=FONT_SMALL, bg=C_PRIMARY, fg="#E2E8F0").pack(side="left", padx=8)

        # Change Password button (all roles)
        def _open_change_pwd():
            uid  = (self.current_user or {}).get("user_id")
            uname = (self.current_user or {}).get("username", "")
            if uid:
                ChangePasswordDialog(self, uid, uname)
        styled_button(u_frame, "🔑 Change Password", _open_change_pwd,
                      color="#4A5568", width=15).pack(side="left", padx=4, pady=3)

        # Export Credentials PDF (Admin only)
        if role_disp == "Admin":
            def _export_creds():
                fp = filedialog.asksaveasfilename(
                    defaultextension=".pdf",
                    filetypes=[("PDF files", "*.pdf")],
                    initialfile=f"login_credentials_{date.today()}.pdf"
                )
                if not fp: return
                try:
                    ar.generate_credentials_pdf(fp)
                    messagebox.showinfo("Exported",
                        f"Credentials PDF saved to:\n{fp}")
                    os.startfile(fp)
                except Exception as e:
                    messagebox.showerror("Error", str(e))
            styled_button(u_frame, "📊 Export Credentials", _export_creds,
                          color="#6B46C1", width=17).pack(side="left", padx=4, pady=3)

        styled_button(u_frame, "🚪 Logout", self.logout,
                      color=C_DANGER, width=9).pack(side="left", padx=4, pady=3)

        # ── Tab bar ───────────────────────────────────────────────────────────
        self._nb = ttk.Notebook(self)
        self._nb.pack(fill="both", expand=True)

        if role_disp == "Student":
            sid = user.get("student_id")
            frame = StudentPortalFrame(self._nb, student_id=sid)
            self._nb.add(frame, text="🎓  My Attendance Portal")
            self._tab_frames = {"🎓  My Attendance Portal": frame}
        elif role_disp == "Teacher":
            tabs = [
                ("🏠  Dashboard",     DashboardFrame),
                ("✅  Attendance",    AttendanceFrame),
                ("📄  Reports",       ReportFrame),
            ]
            self._tab_frames = {}
            for label, FrameClass in tabs:
                frame = FrameClass(self._nb)
                self._nb.add(frame, text=label)
                self._tab_frames[label] = frame
        else:
            tabs = [
                ("🏠  Dashboard",     DashboardFrame),
                ("🏛️  Departments",  DepartmentFrame),
                ("👨‍🎓  Students",     StudentFrame),
                ("👩‍🏫  Teachers",     TeacherFrame),
                ("📚  Courses",       CourseFrame),
                ("✅  Attendance",    AttendanceFrame),
                ("📄  Reports",       ReportFrame),
            ]
            self._tab_frames = {}
            for label, FrameClass in tabs:
                frame = FrameClass(self._nb)
                self._nb.add(frame, text=label)
                self._tab_frames[label] = frame

        self._nb.bind("<<NotebookTabChanged>>", self._on_tab_change)

        # ── Status bar ───────────────────────────────────────────────────────
        status_bar = tk.Frame(self, bg=C_PRIMARY, height=24)
        status_bar.pack(fill="x", side="bottom")
        tk.Label(status_bar, text="✅ Connected to MySQL · college database",
                 font=FONT_SMALL, bg=C_PRIMARY, fg="#A0AEC0",
                 padx=12).pack(side="left")
        tk.Label(status_bar, text="College Attendance System v2.0",
                 font=FONT_SMALL, bg=C_PRIMARY, fg="#A0AEC0",
                 padx=12).pack(side="right")

    def _on_tab_change(self, event):
        try:
            selected_id = self._nb.select()
            if selected_id:
                tab_text = self._nb.tab(selected_id, "text").strip()
                frame = self._tab_frames.get(tab_text)
                if frame and hasattr(frame, "refresh"):
                    frame.refresh()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app = AttendanceApp()
    app.mainloop()


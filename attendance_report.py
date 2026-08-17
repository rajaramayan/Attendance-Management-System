"""
attendance_report.py
--------------------
Report generation module for the Student Attendance Management System.
Supports CSV and PDF exports using the csv and reportlab libraries.
"""

import csv
import io
import os
from datetime import datetime, date

from db_config import get_connection, get_cursor

# ── Optional PDF support ───────────────────────────────────────────────────────
try:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.platypus import (
        SimpleDocTemplate, Table, TableStyle, Paragraph,
        Spacer, HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


# ══════════════════════════════════════════════════════════════════════════════
# QUERY FUNCTIONS — return list-of-dicts
# ══════════════════════════════════════════════════════════════════════════════

def get_student_attendance_summary(course_id=None, student_id=None,
                                   start_date=None, end_date=None):
    """
    Student-wise attendance percentage per course.
    Optionally filter by course_id, student_id, or date range.
    Returns: [{'roll_no', 'student_name', 'course_code', 'course_name',
                'total_classes', 'classes_attended', 'attendance_pct'}, ...]
    """
    sql = """
        SELECT
            s.roll_no,
            s.name            AS student_name,
            c.course_code,
            c.course_name,
            COUNT(a.attendance_id)                                          AS total_classes,
            SUM(a.status IN ('Present','Late'))                             AS classes_attended,
            ROUND(
                SUM(a.status IN ('Present','Late')) * 100.0
                / NULLIF(COUNT(a.attendance_id), 0), 2
            )                                                               AS attendance_pct
        FROM enrollment e
        JOIN student s ON e.student_id = s.student_id
        JOIN course  c ON e.course_id  = c.course_id
        LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
    """
    conditions, params = [], []
    if course_id:
        conditions.append("e.course_id = %s");   params.append(course_id)
    if student_id:
        conditions.append("e.student_id = %s");  params.append(student_id)
    if start_date:
        conditions.append("(a.attendance_date IS NULL OR a.attendance_date >= %s)"); params.append(start_date)
    if end_date:
        conditions.append("(a.attendance_date IS NULL OR a.attendance_date <= %s)"); params.append(end_date)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " GROUP BY s.student_id, c.course_id ORDER BY c.course_code, s.roll_no"

    return _run_query(sql, params)


def get_daily_attendance(course_id, attendance_date):
    """
    All enrolled students and their status for a specific course+date.
    Returns: [{'roll_no', 'student_name', 'status'}, ...]
    """
    sql = """
        SELECT s.roll_no, s.name AS student_name,
               COALESCE(a.status, 'Not Marked') AS status
        FROM enrollment e
        JOIN student s ON e.student_id = s.student_id
        LEFT JOIN attendance a
            ON a.enrollment_id = e.enrollment_id
           AND a.attendance_date = %s
        WHERE e.course_id = %s
        ORDER BY s.roll_no
    """
    return _run_query(sql, [attendance_date, course_id])


def get_defaulter_list(threshold=75, course_id=None):
    """
    Students whose attendance_pct < threshold.
    Returns: [{'roll_no','student_name','course_code','course_name',
               'total_classes','classes_attended','attendance_pct'}, ...]
    """
    rows = get_student_attendance_summary(course_id=course_id)
    return [r for r in rows if r['attendance_pct'] is not None
            and float(r['attendance_pct']) < threshold]


def get_course_daily_summary(start_date=None, end_date=None):
    """
    Course-wise daily attendance count.
    Returns: [{'attendance_date','course_code','course_name','total','present','absent','late'}, ...]
    """
    sql = """
        SELECT
            a.attendance_date,
            c.course_code,
            c.course_name,
            COUNT(*) AS total,
            SUM(a.status='Present') AS present,
            SUM(a.status='Absent')  AS absent,
            SUM(a.status='Late')    AS late
        FROM attendance a
        JOIN enrollment e ON a.enrollment_id = e.enrollment_id
        JOIN course c     ON e.course_id = c.course_id
    """
    conditions, params = [], []
    if start_date:
        conditions.append("a.attendance_date >= %s"); params.append(start_date)
    if end_date:
        conditions.append("a.attendance_date <= %s"); params.append(end_date)
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)
    sql += " GROUP BY a.attendance_date, c.course_id ORDER BY a.attendance_date DESC, c.course_code"
    return _run_query(sql, params)


def get_date_range_report(start_date, end_date, course_id=None):
    """
    Detailed attendance for a date range.
    """
    return get_student_attendance_summary(
        course_id=course_id,
        start_date=start_date,
        end_date=end_date
    )


def get_dashboard_stats():
    """Return summary numbers for the dashboard."""
    conn = get_connection()
    cur  = get_cursor(conn, dictionary=True)
    stats = {}

    queries = {
        "total_students": "SELECT COUNT(*) AS v FROM student",
        "total_teachers": "SELECT COUNT(*) AS v FROM teacher",
        "total_courses":  "SELECT COUNT(*) AS v FROM course",
        "total_dept":     "SELECT COUNT(*) AS v FROM department",
        "today_classes":  "SELECT COUNT(DISTINCT e.course_id) AS v FROM attendance a JOIN enrollment e ON a.enrollment_id=e.enrollment_id WHERE a.attendance_date=CURDATE()",
        "today_present":  "SELECT COUNT(*) AS v FROM attendance WHERE attendance_date=CURDATE() AND status='Present'",
        "today_total":    "SELECT COUNT(*) AS v FROM attendance WHERE attendance_date=CURDATE()",
        "total_records":  "SELECT COUNT(*) AS v FROM attendance",
    }
    for key, q in queries.items():
        cur.execute(q)
        row = cur.fetchone()
        stats[key] = row['v'] if row else 0

    cur.execute("SELECT ROUND(COALESCE(SUM(status IN ('Present','Late'))*100.0/NULLIF(COUNT(attendance_id),0), 0), 1) AS v FROM attendance")
    row_pct = cur.fetchone()
    stats["avg_attendance_pct"] = row_pct['v'] if row_pct and row_pct['v'] is not None else 0.0

    # Avg attendance pct per course (all time)
    cur.execute("""
        SELECT c.course_name,
               ROUND(SUM(a.status IN ('Present','Late'))*100.0/NULLIF(COUNT(a.attendance_id),0),1) AS pct
        FROM enrollment e
        JOIN course c ON e.course_id=c.course_id
        LEFT JOIN attendance a ON a.enrollment_id=e.enrollment_id
        GROUP BY c.course_id
        ORDER BY pct DESC
    """)
    stats["course_pct"] = cur.fetchall()

    # Overall attendance status counts for Donut chart
    cur.execute("""
        SELECT
            COALESCE(SUM(status='Present'), 0) AS present,
            COALESCE(SUM(status='Absent'), 0)  AS absent,
            COALESCE(SUM(status='Late'), 0)    AS late
        FROM attendance
    """)
    stats["overall_status"] = cur.fetchone()

    # Recent 8 attendance records
    cur.execute("""
        SELECT a.attendance_date, s.name AS student, c.course_code, a.status
        FROM attendance a
        JOIN enrollment e ON a.enrollment_id=e.enrollment_id
        JOIN student s    ON e.student_id=s.student_id
        JOIN course c     ON e.course_id=c.course_id
        ORDER BY a.marked_at DESC LIMIT 8
    """)
    stats["recent"] = cur.fetchall()

    cur.close(); conn.close()
    return stats


get_overall_dashboard_stats = get_dashboard_stats


# ══════════════════════════════════════════════════════════════════════════════
# CLASS LOG FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def save_class_log(course_id, teacher_id, class_date, topic_taught):
    """
    Insert or update the class log entry for a given course and date.
    Uses INSERT ... ON DUPLICATE KEY UPDATE for idempotency.
    """
    topic_taught = topic_taught.strip()
    if not topic_taught:
        return
    conn = get_connection(); cur = conn.cursor()
    cur.execute("""
        INSERT INTO class_log (course_id, teacher_id, class_date, topic_taught)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            topic_taught = VALUES(topic_taught),
            teacher_id   = VALUES(teacher_id)
    """, (course_id, teacher_id, class_date, topic_taught))
    conn.commit()
    cur.close(); conn.close()


def get_class_log_for_date(course_id, class_date):
    """
    Fetch the existing topic_taught for a course+date (for pre-populating the entry field).
    Returns the topic string or empty string if not found.
    """
    conn = get_connection(); cur = get_cursor(conn, dictionary=True)
    cur.execute("""
        SELECT topic_taught FROM class_log
        WHERE course_id=%s AND class_date=%s
    """, (course_id, class_date))
    row = cur.fetchone()
    cur.close(); conn.close()
    return row["topic_taught"] if row else ""


def get_daily_class_log(target_date=None):
    """
    Fetch the daily summary table: what every teacher covered on a given date.
    Returns list-of-dicts with teacher, course, topic, and attendance stats.
    """
    if target_date is None:
        target_date = date.today().isoformat()
    conn = get_connection(); cur = get_cursor(conn, dictionary=True)
    cur.execute("""
        SELECT
            cl.class_date,
            t.name           AS teacher_name,
            t.teacher_code,
            c.course_code,
            c.course_name,
            cl.topic_taught,
            COUNT(a.attendance_id)                          AS total_students,
            COALESCE(SUM(a.status = 'Present'), 0)          AS present_count,
            COALESCE(SUM(a.status = 'Absent'), 0)           AS absent_count,
            ROUND(
                COALESCE(SUM(a.status IN ('Present','Late')),0) * 100.0
                / NULLIF(COUNT(a.attendance_id), 0), 1
            )                                               AS attendance_pct
        FROM class_log cl
        JOIN course  c ON cl.course_id  = c.course_id
        LEFT JOIN teacher t ON cl.teacher_id = t.teacher_id
        LEFT JOIN enrollment e ON e.course_id = c.course_id
        LEFT JOIN attendance a ON a.enrollment_id = e.enrollment_id
                               AND a.attendance_date = cl.class_date
        WHERE cl.class_date = %s
        GROUP BY cl.log_id, c.course_id, t.teacher_id
        ORDER BY t.name, c.course_name
    """, (target_date,))
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


def get_teacher_progress_report(teacher_id=None):
    """
    Fetch teacher progress: total classes logged, topics covered, latest topic, last active date.
    Optionally filter by teacher_id.
    Returns list-of-dicts.
    """
    conn = get_connection(); cur = get_cursor(conn, dictionary=True)
    where = "WHERE cl.teacher_id = %s" if teacher_id else ""
    params = (teacher_id,) if teacher_id else ()
    cur.execute(f"""
        SELECT
            t.teacher_code,
            t.name                AS teacher_name,
            d.dept_name,
            COUNT(cl.log_id)      AS total_classes_logged,
            MAX(cl.class_date)    AS last_active_date,
            (
                SELECT cl2.topic_taught
                FROM class_log cl2
                WHERE cl2.teacher_id = t.teacher_id
                ORDER BY cl2.class_date DESC
                LIMIT 1
            )                     AS latest_topic,
            GROUP_CONCAT(
                CONCAT(cl.class_date, ': ', cl.topic_taught)
                ORDER BY cl.class_date DESC
                SEPARATOR ' | '
            )                     AS all_topics_summary
        FROM teacher t
        LEFT JOIN class_log cl ON cl.teacher_id = t.teacher_id
        LEFT JOIN department d ON t.dept_id = d.dept_id
        {where}
        GROUP BY t.teacher_id
        ORDER BY total_classes_logged DESC, t.name
    """, params)
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows


# ══════════════════════════════════════════════════════════════════════════════
# EXPORT FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════


def generate_credentials_pdf(filepath):
    """
    Generate a printable PDF credential sheet listing:
      - All teacher accounts (username + default password)
      - All student accounts (username/roll_no + default password)
    """
    if not PDF_AVAILABLE:
        raise ImportError("reportlab is not installed. Run: pip install reportlab")

    conn = get_connection(); cur = get_cursor(conn, dictionary=True)

    # Fetch teacher credentials
    cur.execute("""
        SELECT u.username, u.password_hash AS password, t.name, t.teacher_code,
               d.dept_name, t.email, u.role
        FROM users u
        JOIN teacher t ON u.teacher_id = t.teacher_id
        LEFT JOIN department d ON t.dept_id = d.dept_id
        ORDER BY t.name
    """)
    teachers = cur.fetchall()

    # Fetch student credentials
    cur.execute("""
        SELECT u.username, u.password_hash AS password, s.name, s.roll_no,
               d.dept_name, s.email, u.role
        FROM users u
        JOIN student s ON u.student_id = s.student_id
        LEFT JOIN department d ON s.dept_id = d.dept_id
        ORDER BY s.roll_no
    """)
    students = cur.fetchall()
    cur.close(); conn.close()

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    NAVY   = colors.HexColor("#1A365D")
    ACCENT = colors.HexColor("#4F8EF7")
    GREEN  = colors.HexColor("#276749")
    story  = []

    # ── Cover Header ──────────────────────────────────────────────────────────
    story.append(Paragraph("<b>COLLEGE OF ENGINEERING &amp; TECHNOLOGY</b>",
        ParagraphStyle("CH", parent=styles["Heading1"], fontSize=16,
                       textColor=NAVY, alignment=TA_CENTER, spaceAfter=2)))
    story.append(Paragraph("ATTENDANCE MANAGEMENT SYSTEM — LOGIN CREDENTIALS",
        ParagraphStyle("CS", parent=styles["Normal"], fontSize=10,
                       textColor=colors.grey, alignment=TA_CENTER, spaceAfter=4)))
    story.append(Paragraph(
        f"<b>CONFIDENTIAL</b> — Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}",
        ParagraphStyle("CM", parent=styles["Normal"], fontSize=8,
                       textColor=colors.red, alignment=TA_CENTER, spaceAfter=10)))
    story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=16))

    # ── Teacher Credentials ───────────────────────────────────────────────────
    story.append(Paragraph("👩‍🏫  TEACHER LOGIN CREDENTIALS",
        ParagraphStyle("SH", parent=styles["Heading2"], fontSize=13,
                       textColor=NAVY, spaceAfter=8)))

    t_data = [["#", "Teacher Name", "Teacher Code", "Department",
               "Login Username", "Password", "Email"]]
    for i, t in enumerate(teachers, 1):
        t_data.append([
            str(i), t["name"], t["teacher_code"] or "—",
            t["dept_name"] or "—", t["username"],
            t["password"], t["email"] or "—"
        ])

    t_table = Table(t_data, colWidths=[1*cm, 4.5*cm, 2.5*cm, 3*cm, 3*cm, 2.5*cm, 3.5*cm])
    t_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  NAVY),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 8),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME",     (4, 1), (4, -1),  "Helvetica-Bold"),  # username bold
        ("TEXTCOLOR",    (5, 1), (5, -1),  GREEN),              # password green
        ("FONTNAME",     (5, 1), (5, -1),  "Helvetica-Bold"),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E0")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#EBF8FF")]),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    story.append(t_table)
    story.append(Spacer(1, 1*cm))

    # ── Student Credentials ───────────────────────────────────────────────────
    story.append(Paragraph("👨‍🎓  STUDENT LOGIN CREDENTIALS",
        ParagraphStyle("SH2", parent=styles["Heading2"], fontSize=13,
                       textColor=NAVY, spaceAfter=8)))

    s_data = [["#", "Student Name", "Roll No", "Department",
               "Login Username", "Password", "Email"]]
    for i, s in enumerate(students, 1):
        s_data.append([
            str(i), s["name"], s["roll_no"] or "—",
            s["dept_name"] or "—", s["username"],
            s["password"], s["email"] or "—"
        ])

    s_table = Table(s_data, colWidths=[1*cm, 4.5*cm, 2.5*cm, 3*cm, 3*cm, 2.5*cm, 3.5*cm])
    s_table.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0),  NAVY),
        ("TEXTCOLOR",    (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",     (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, -1), 8),
        ("ALIGN",        (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME",     (4, 1), (4, -1),  "Helvetica-Bold"),
        ("TEXTCOLOR",    (5, 1), (5, -1),  GREEN),
        ("FONTNAME",     (5, 1), (5, -1),  "Helvetica-Bold"),
        ("GRID",         (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E0")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [colors.white, colors.HexColor("#F0FFF4")]),
        ("TOPPADDING",   (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 4),
    ]))
    story.append(s_table)
    story.append(Spacer(1, 1*cm))

    # ── Footer note ───────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey, spaceAfter=6))
    story.append(Paragraph(
        "⚠️  This document is CONFIDENTIAL. Please distribute credentials individually and securely. "
        "Default passwords should be changed on first login.",
        ParagraphStyle("Note", parent=styles["Normal"], fontSize=7.5,
                       textColor=colors.grey, alignment=TA_CENTER)
    ))

    doc.build(story)
    return filepath


def export_to_csv(rows, filepath=None):
    """Write a list-of-dicts to a CSV file. Returns filepath or bytes if filepath is None."""
    if not rows:
        raise ValueError("No data to export.")
    headers = list(rows[0].keys())
    if filepath is None:
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
        return out.getvalue().encode("utf-8")

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    return filepath


def export_to_pdf(rows, filepath=None, title="Attendance Report",
                  subtitle="", orientation="portrait"):
    """
    Generate a styled PDF report using ReportLab.
    orientation: 'portrait' or 'landscape'
    """
    if not PDF_AVAILABLE:
        raise ImportError("reportlab is not installed. Run: pip install reportlab")
    if not rows:
        raise ValueError("No data to export.")

    target_dest = filepath if filepath else io.BytesIO()

    page_size = A4 if orientation == "portrait" else landscape(A4)
    doc = SimpleDocTemplate(
        target_dest, pagesize=page_size,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=2*cm,    bottomMargin=1.5*cm
    )

    styles = getSampleStyleSheet()
    PRIMARY_COLOR = colors.HexColor("#2D3748")
    ACCENT_COLOR  = colors.HexColor("#4F8EF7")
    SUCCESS_COLOR = colors.HexColor("#48BB78")
    DANGER_COLOR  = colors.HexColor("#FC8181")
    WARN_COLOR    = colors.HexColor("#ED8936")

    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Heading1"],
        fontSize=18, textColor=PRIMARY_COLOR,
        spaceAfter=4, alignment=TA_CENTER
    )
    sub_style = ParagraphStyle(
        "ReportSub", parent=styles["Normal"],
        fontSize=10, textColor=colors.grey,
        spaceAfter=2, alignment=TA_CENTER
    )
    meta_style = ParagraphStyle(
        "Meta", parent=styles["Normal"],
        fontSize=8, textColor=colors.grey,
        alignment=TA_RIGHT
    )

    story = [
        Paragraph("🎓 College Attendance Management System", title_style),
        Paragraph(title, ParagraphStyle("T2", parent=styles["Heading2"],
                                        fontSize=14, textColor=ACCENT_COLOR,
                                        alignment=TA_CENTER, spaceAfter=2)),
    ]
    if subtitle:
        story.append(Paragraph(subtitle, sub_style))
    story.append(Paragraph(
        f"Generated: {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        meta_style
    ))
    story.append(HRFlowable(width="100%", thickness=1,
                             color=ACCENT_COLOR, spaceAfter=10))

    # Build table data
    headers = [k.replace("_", " ").title() for k in rows[0].keys()]
    keys    = list(rows[0].keys())
    data    = [headers]
    for r in rows:
        row_data = []
        for k in keys:
            val = r.get(k)
            if val is None:
                val = "—"
            elif isinstance(val, (date, datetime)):
                val = val.strftime("%d %b %Y")
            row_data.append(str(val))
        data.append(row_data)

    avail_w = page_size[0] - 3*cm
    col_w   = avail_w / len(keys)

    table = Table(data, colWidths=[col_w]*len(keys), repeatRows=1)

    # Style the table
    ts = TableStyle([
        # Header
        ("BACKGROUND",    (0, 0), (-1, 0),  PRIMARY_COLOR),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0),  9),
        ("ALIGN",         (0, 0), (-1, 0),  "CENTER"),
        ("BOTTOMPADDING", (0, 0), (-1, 0),  8),
        ("TOPPADDING",    (0, 0), (-1, 0),  8),
        # Body
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8.5),
        ("GRID",          (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E0")),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
        ("TOPPADDING",    (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
        ("ALIGN",         (0, 1), (-1, -1), "CENTER"),
    ])

    # Highlight status column if present
    status_col = None
    if "status" in keys:
        status_col = keys.index("status")
    elif "attendance_pct" in keys:
        status_col = keys.index("attendance_pct")

    if status_col is not None:
        for i, row in enumerate(data[1:], start=1):
            val = row[status_col]
            if val in ("Present",) or (val.replace(".", "").isdigit() and float(val) >= 75):
                ts.add("TEXTCOLOR", (status_col, i), (status_col, i), SUCCESS_COLOR)
                ts.add("FONTNAME",  (status_col, i), (status_col, i), "Helvetica-Bold")
            elif val == "Absent" or (val.replace(".", "").isdigit() and float(val) < 75):
                ts.add("TEXTCOLOR", (status_col, i), (status_col, i), DANGER_COLOR)
                ts.add("FONTNAME",  (status_col, i), (status_col, i), "Helvetica-Bold")
            elif val == "Late":
                ts.add("TEXTCOLOR", (status_col, i), (status_col, i), WARN_COLOR)

    table.setStyle(ts)
    story.append(table)
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        f"Total Records: {len(rows)}", 
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=9,
                       textColor=colors.grey, alignment=TA_LEFT)
    ))

    doc.build(story)
    if filepath is None:
        return target_dest.getvalue()
    return filepath


def generate_defaulter_notice_pdf(roll_no_or_student_id, filepath):
    """
    Generate an official Defaulter Warning Letter PDF for a student with attendance < 75%.
    """
    if not PDF_AVAILABLE:
        raise ImportError("reportlab is not installed. Run: pip install reportlab")

    # Fetch student info
    conn = get_connection(); cur = get_cursor(conn, dictionary=True)
    cur.execute("""
        SELECT s.student_id, s.roll_no, s.name, s.email, s.phone, d.dept_name
        FROM student s LEFT JOIN department d ON s.dept_id = d.dept_id
        WHERE s.student_id = %s OR s.roll_no = %s
    """, (roll_no_or_student_id, roll_no_or_student_id))
    st = cur.fetchone()
    cur.close(); conn.close()

    if not st:
        raise ValueError("Student not found.")

    courses_data = get_student_attendance_summary(student_id=st["student_id"])

    doc = SimpleDocTemplate(
        filepath, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    NAVY = colors.HexColor("#1A365D")
    RED  = colors.HexColor("#C53030")

    story = []
    
    # Header
    story.append(Paragraph("<b>COLLEGE OF ENGINEERING & TECHNOLOGY</b>",
                 ParagraphStyle("H1", parent=styles["Heading1"], fontSize=16, textColor=NAVY, alignment=TA_CENTER, spaceAfter=2)))
    story.append(Paragraph("OFFICE OF THE ACADEMIC DEAN & ATTENDANCE CELL",
                 ParagraphStyle("H2", parent=styles["Normal"], fontSize=9, textColor=colors.grey, alignment=TA_CENTER, spaceAfter=10)))
    story.append(HRFlowable(width="100%", thickness=2, color=NAVY, spaceAfter=15))

    # Ref & Date
    story.append(Paragraph(f"<b>Ref No:</b> CET/ATT-WARN/{datetime.now().year}/{st['student_id']:03d}&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b>Date:</b> {date.today().strftime('%d %B %Y')}",
                 ParagraphStyle("Meta", parent=styles["Normal"], fontSize=9, spaceAfter=15)))

    # Title
    story.append(Paragraph("<b>OFFICIAL ACADEMIC WARNING NOTICE</b>",
                 ParagraphStyle("WarnTitle", parent=styles["Heading2"], fontSize=13, textColor=RED, alignment=TA_CENTER, spaceAfter=12)))

    # Recipient Box
    rec_text = f"""
    <b>To:</b><br/>
    <b>Student Name:</b> {st['name']}<br/>
    <b>Roll Number:</b> {st['roll_no']}<br/>
    <b>Department:</b> {st['dept_name'] or 'N/A'}<br/>
    <b>Email / Contact:</b> {st['email'] or 'N/A'} | {st['phone'] or 'N/A'}
    """
    story.append(Paragraph(rec_text, ParagraphStyle("Rec", parent=styles["Normal"], fontSize=9, leading=14, spaceAfter=12)))

    # Statement
    body_p = """
    This is an official notice to inform you that your attendance record in the current academic semester has fallen below the 
    mandatory minimum threshold of <b>75%</b>. As per college academic regulations, failure to maintain the required attendance 
    may lead to debarment from taking the final semester examinations.
    <br/><br/>
    Below is the breakdown of your course-wise attendance record:
    """
    story.append(Paragraph(body_p, ParagraphStyle("Body", parent=styles["Normal"], fontSize=9, leading=13, spaceAfter=12)))

    # Table
    table_data = [["Course Code", "Course Name", "Total Classes", "Classes Attended", "Att. %", "Status"]]
    for c in courses_data:
        pct = float(c["attendance_pct"]) if c["attendance_pct"] is not None else 0.0
        status_str = "DEFICIENT" if pct < 75 else "SATISFACTORY"
        table_data.append([
            c["course_code"],
            c["course_name"],
            str(c["total_classes"]),
            str(c["classes_attended"]),
            f"{pct:.1f}%",
            status_str
        ])

    t = Table(table_data, colWidths=[2.5*cm, 6.5*cm, 2.5*cm, 2.8*cm, 2*cm, 2.7*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(t)
    story.append(Spacer(1, 1*cm))

    # Directive
    dir_p = """
    <b>DIRECTIVE:</b> You are required to report to your Head of Department (HOD) and Academic Advisor within <b>3 working days</b> 
    from the date of this notice to submit a formal clarification. Continued non-attendance will result in disciplinary action.
    """
    story.append(Paragraph(dir_p, ParagraphStyle("Dir", parent=styles["Normal"], fontSize=9, leading=13, textColor=RED, spaceAfter=20)))

    # Signatures
    sig_table = Table([
        ["_________________________", "_________________________"],
        ["Attendance Coordinator", "Head of Department (HOD)"]
    ], colWidths=[9*cm, 9*cm])
    sig_table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#2D3748")),
    ]))
    story.append(Spacer(1, 1*cm))
    story.append(sig_table)

    doc.build(story)
    return filepath


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _run_query(sql, params=None):
    """Execute a SELECT query and return list-of-dicts."""
    conn = get_connection()
    cur  = get_cursor(conn, dictionary=True)
    cur.execute(sql, params or [])
    rows = cur.fetchall()
    cur.close(); conn.close()
    return rows

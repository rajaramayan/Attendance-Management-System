"""
app.py
------
Streamlit Web Application for Student Attendance Management System.
Connects to MySQL / Aiven DB, visualizes attendance metrics, handles attendance marking,
generates defaulter lists, and exports reports to CSV and PDF.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
import os

from db_config import get_connection, test_connection
import attendance_report as ar

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Attendance Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS Styling ────────────────────────────────────────────────────────
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #6B7280;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: #F3F4F6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2563EB;
    }
    .badge-present {
        background-color: #DEF7EC;
        color: #03543F;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-absent {
        background-color: #FDE8E8;
        color: #9B1C1C;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-late {
        background-color: #FEF08A;
        color: #713F12;
        padding: 4px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)


# ── Database Helpers ──────────────────────────────────────────────────────────
@st.cache_data(ttl=60)
def fetch_departments():
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT dept_id, dept_name, code FROM department ORDER BY dept_name", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=60)
def fetch_courses():
    try:
        conn = get_connection()
        query = """
            SELECT c.course_id, c.course_code, c.course_name, d.dept_name, t.name AS teacher_name
            FROM course c
            LEFT JOIN department d ON c.dept_id = d.dept_id
            LEFT JOIN teacher t ON c.teacher_id = t.teacher_id
            ORDER BY c.course_code
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=60)
def fetch_students():
    try:
        conn = get_connection()
        query = """
            SELECT s.student_id, s.roll_no, s.name, s.email, s.semester, d.dept_name
            FROM student s
            LEFT JOIN department d ON s.dept_id = d.dept_id
            ORDER BY s.roll_no
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


# ── Sidebar Navigation ────────────────────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/illustrations/100/graduation-cap.png", width=70)
st.sidebar.title("🎓 Navigation")
menu = st.sidebar.radio(
    "Select Module:",
    [
        "📊 Dashboard Overview",
        "📝 Mark / Edit Attendance",
        "📈 Attendance Reports & Defaulters",
        "👨‍🎓 Student & Course Directory",
        "⚙️ Database & Connection Status",
    ],
)

st.sidebar.markdown("---")
# Quick DB status indicator in sidebar
is_connected, conn_msg = test_connection()
if is_connected:
    st.sidebar.success("🟢 DB Connected")
else:
    st.sidebar.error("🔴 DB Disconnected")


# ── Header Banner ─────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🎓 Student Attendance Management System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Web-based Dashboard for Tracking, Marking, and Reporting Student Attendance</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 1: DASHBOARD OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if menu == "📊 Dashboard Overview":
    st.subheader("📊 Dashboard Analytics")

    if not is_connected:
        st.warning(f"⚠️ Cannot load database metrics: {conn_msg}")
        st.info("💡 Please configure your database connection in Streamlit Secrets (`.streamlit/secrets.toml`).")
    else:
        try:
            stats = ar.get_overall_dashboard_stats()
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Students", stats.get("total_students", 0))
            with col2:
                st.metric("Total Courses", stats.get("total_courses", 0))
            with col3:
                st.metric("Total Attendance Logs", stats.get("total_records", 0))
            with col4:
                avg_pct = stats.get("avg_attendance_pct", 0)
                st.metric("Overall Attendance %", f"{avg_pct}%")

            st.markdown("---")

            # Chart: Attendance Summary per Course
            st.subheader("📚 Course-wise Attendance Overview")
            summary_data = ar.get_student_attendance_summary()
            if summary_data:
                df_summary = pd.DataFrame(summary_data)
                
                # Plot Attendance Percentage by Course
                df_course_avg = df_summary.groupby(["course_code", "course_name"])["attendance_pct"].mean().reset_index()
                st.bar_chart(
                    data=df_course_avg,
                    x="course_code",
                    y="attendance_pct",
                    x_label="Course Code",
                    y_label="Attendance (%)",
                    use_container_width=True
                )

                st.subheader("📋 Student Attendance Summary")
                st.dataframe(df_summary, use_container_width=True)
            else:
                st.info("No attendance records found yet.")

        except Exception as e:
            st.error(f"Error fetching dashboard metrics: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 2: MARK / EDIT ATTENDANCE
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "📝 Mark / Edit Attendance":
    st.subheader("📝 Mark / Update Daily Attendance")

    if not is_connected:
        st.error(f"Cannot connect to database: {conn_msg}")
    else:
        courses_df = fetch_courses()
        if courses_df.empty:
            st.warning("No courses available. Please add courses first.")
        else:
            col_c, col_d = st.columns(2)
            with col_c:
                course_opts = {f"{row['course_code']} - {row['course_name']}": row['course_id'] for _, row in courses_df.iterrows()}
                selected_course_label = st.selectbox("Select Course:", list(course_opts.keys()))
                selected_course_id = course_opts[selected_course_label]

            with col_d:
                selected_date = st.date_input("Select Date:", value=date.today())

            st.markdown("---")

            # Fetch students enrolled in this course
            try:
                conn = get_connection()
                query = """
                    SELECT e.enrollment_id, s.roll_no, s.name, COALESCE(a.status, 'Present') as status, a.remarks
                    FROM enrollment e
                    JOIN student s ON e.student_id = s.student_id
                    LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id AND a.attendance_date = %s
                    WHERE e.course_id = %s
                    ORDER BY s.roll_no
                """
                cursor = conn.cursor(dictionary=True)
                cursor.execute(query, (selected_date, selected_course_id))
                enrolled_students = cursor.fetchall()
                conn.close()

                if not enrolled_students:
                    st.info(f"No students enrolled in this course.")
                else:
                    st.write(f"**Enrolled Students ({len(enrolled_students)}):**")
                    
                    with st.form("mark_attendance_form"):
                        attendance_data = {}
                        remarks_data = {}
                        
                        for student in enrolled_students:
                            c1, c2, c3 = st.columns([2, 2, 3])
                            with c1:
                                st.write(f"**{student['roll_no']}** - {student['name']}")
                            with c2:
                                status_choice = st.radio(
                                    f"Status for {student['roll_no']}",
                                    ["Present", "Absent", "Late"],
                                    index=["Present", "Absent", "Late"].index(student['status']) if student['status'] in ["Present", "Absent", "Late"] else 0,
                                    horizontal=True,
                                    key=f"status_{student['enrollment_id']}"
                                )
                                attendance_data[student['enrollment_id']] = status_choice
                            with c3:
                                remark_val = st.text_input(
                                    f"Remarks for {student['roll_no']}",
                                    value=student['remarks'] or "",
                                    key=f"remark_{student['enrollment_id']}"
                                )
                                remarks_data[student['enrollment_id']] = remark_val
                            st.divider()

                        submit_btn = st.form_submit_button("💾 Save Attendance", type="primary")

                        if submit_btn:
                            try:
                                conn = get_connection()
                                cur = conn.cursor()
                                for enr_id, status in attendance_data.items():
                                    rem = remarks_data.get(enr_id, "")
                                    sql = """
                                        INSERT INTO attendance (enrollment_id, attendance_date, status, remarks)
                                        VALUES (%s, %s, %s, %s)
                                        ON DUPLICATE KEY UPDATE status=%s, remarks=%s
                                    """
                                    cur.execute(sql, (enr_id, selected_date, status, rem, status, rem))
                                conn.commit()
                                conn.close()
                                st.success("✅ Attendance saved successfully!")
                                st.cache_data.clear()
                            except Exception as ex:
                                st.error(f"Failed to save attendance: {ex}")

            except Exception as ex:
                st.error(f"Error loading enrollment records: {ex}")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 3: ATTENDANCE REPORTS & DEFAULTERS
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "📈 Attendance Reports & Defaulters":
    st.subheader("📈 Attendance Reports & Low Attendance Alerts")

    if not is_connected:
        st.error(f"Cannot connect to database: {conn_msg}")
    else:
        tab1, tab2 = st.tabs(["⚠️ Defaulter List (< Threshold)", "📄 Detailed Attendance Report"])

        with tab1:
            st.write("### 🚨 Low Attendance Defaulter List")
            threshold = st.slider("Select Attendance Threshold (%):", min_value=50, max_value=90, value=75, step=5)
            
            defaulters = ar.get_defaulter_list(threshold=threshold)
            if defaulters:
                st.warning(f"Found {len(defaulters)} student(s) below {threshold}% attendance.")
                df_def = pd.DataFrame(defaulters)
                st.dataframe(df_def, use_container_width=True)
                
                # Export Options
                col_csv, col_pdf = st.columns(2)
                with col_csv:
                    csv_bytes = ar.export_to_csv(defaulters)
                    st.download_button(
                        label="📥 Download Defaulter CSV",
                        data=csv_bytes,
                        file_name=f"defaulters_below_{threshold}pct.csv",
                        mime="text/csv"
                    )
                with col_pdf:
                    if ar.PDF_AVAILABLE:
                        pdf_bytes = ar.export_to_pdf(defaulters, title=f"Defaulter List (Below {threshold}%)")
                        st.download_button(
                            label="📥 Download Defaulter PDF",
                            data=pdf_bytes,
                            file_name=f"defaulters_below_{threshold}pct.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.info("PDF Export unavailable (reportlab package required).")
            else:
                st.success(f"🎉 Excellent! No students have attendance below {threshold}%.")

        with tab2:
            st.write("### 📊 Complete Student Attendance Report")
            all_summary = ar.get_student_attendance_summary()
            if all_summary:
                df_all = pd.DataFrame(all_summary)
                st.dataframe(df_all, use_container_width=True)

                c_csv, c_pdf = st.columns(2)
                with c_csv:
                    csv_b = ar.export_to_csv(all_summary)
                    st.download_button(
                        label="📥 Export Complete Summary CSV",
                        data=csv_b,
                        file_name="student_attendance_summary.csv",
                        mime="text/csv"
                    )
                with c_pdf:
                    if ar.PDF_AVAILABLE:
                        pdf_b = ar.export_to_pdf(all_summary, title="Overall Attendance Summary")
                        st.download_button(
                            label="📥 Export Complete Summary PDF",
                            data=pdf_b,
                            file_name="student_attendance_summary.pdf",
                            mime="application/pdf"
                        )
            else:
                st.info("No attendance records found.")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 4: STUDENT & COURSE DIRECTORY
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "👨‍🎓 Student & Course Directory":
    st.subheader("👨‍🎓 Directory Information")

    if not is_connected:
        st.error(f"Cannot connect to database: {conn_msg}")
    else:
        st_tab, crs_tab, dept_tab = st.tabs(["👨‍🎓 Students", "📚 Courses", "🏢 Departments"])

        with st_tab:
            st.write("### Registered Students")
            students_df = fetch_students()
            if not students_df.empty:
                st.dataframe(students_df, use_container_width=True)
            else:
                st.info("No student records found.")

        with crs_tab:
            st.write("### Active Courses")
            courses_df = fetch_courses()
            if not courses_df.empty:
                st.dataframe(courses_df, use_container_width=True)
            else:
                st.info("No course records found.")

        with dept_tab:
            st.write("### Departments")
            depts_df = fetch_departments()
            if not depts_df.empty:
                st.dataframe(depts_df, use_container_width=True)
            else:
                st.info("No department records found.")


# ══════════════════════════════════════════════════════════════════════════════
# MODULE 5: DATABASE & CONNECTION STATUS
# ══════════════════════════════════════════════════════════════════════════════
elif menu == "⚙️ Database & Connection Status":
    st.subheader("⚙️ Database Connection & Configuration")

    st.write("### Diagnostic Test")
    test_ok, test_msg = test_connection()

    if test_ok:
        st.success(f"✅ {test_msg}")
    else:
        st.error(f"❌ {test_msg}")

    st.markdown("---")
    st.write("### 🔑 Streamlit Secrets Format")
    st.code("""
[connections.mysql]
dialect = "mysql"
host = "mysql-27ea9885-attendance-management-systemnew.b.aivencloud.com"
port = 25561
database = "college"
username = "avnadmin"
password = "YOUR_DATABASE_PASSWORD"
query = { charset = "utf8mb4" }
    """, language="toml")

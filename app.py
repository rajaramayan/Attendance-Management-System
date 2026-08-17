"""
app.py
------
Streamlit Web Application for Student Attendance Management System.
Matches the full Tkinter desktop application (main_app.py) feature-for-feature with 7 tabs:
1. 🏠 Dashboard
2. 🏢 Departments
3. 👨‍🎓 Students
4. 👩‍🏫 Teachers
5. 📚 Courses
6. ✔️ Attendance
7. 📊 Reports
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime
import os

from db_config import get_connection, test_connection, get_cursor
import attendance_report as ar

# ── Page Configuration ────────────────────────────────────────────────────────
st.set_page_config(
    page_title="College Attendance Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Session State Initialisation ─────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_user" not in st.session_state:
    st.session_state["current_user"] = ""
if "current_role" not in st.session_state:
    st.session_state["current_role"] = ""
# Stored admin credentials (changeable at runtime)
if "admin_password" not in st.session_state:
    st.session_state["admin_password"] = "admin123"

# ── Custom CSS Styling (Dark/Navy header theme matching main_app.py) ──────────
st.markdown("""
    <style>
    /* Top Header Bar */
    .top-header {
        background-color: #1E293B;
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .top-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #F8FAFC;
    }
    .top-sub {
        font-size: 0.85rem;
        color: #94A3B8;
    }
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #0F172A;
        padding: 6px;
        border-radius: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        border-radius: 6px;
        padding: 8px 16px;
        font-weight: 600;
        font-size: 0.95rem;
        color: #94A3B8;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2563EB !important;
        color: #FFFFFF !important;
    }
    /* Metric Card */
    .stat-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)


# ── Login Page ───────────────────────────────────────────────────────────────
def show_login_page():
    st.markdown("""
        <style>
        .login-wrapper {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 75vh;
        }
        .login-card {
            background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
            border: 1px solid #334155;
            border-radius: 16px;
            padding: 48px 40px;
            width: 100%;
            max-width: 420px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.4);
        }
        .login-logo {
            font-size: 3rem;
            text-align: center;
            margin-bottom: 8px;
        }
        .login-title {
            text-align: center;
            font-size: 1.5rem;
            font-weight: 700;
            color: #F8FAFC;
            margin-bottom: 4px;
        }
        .login-subtitle {
            text-align: center;
            font-size: 0.85rem;
            color: #94A3B8;
            margin-bottom: 32px;
        }
        div[data-testid="stForm"] {
            background: transparent;
        }
        </style>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.6, 1])
    with center:
        st.markdown('<div class="login-logo">🎓</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-title">College Attendance System</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Sign in to continue</div>', unsafe_allow_html=True)

        with st.form("login_form", clear_on_submit=False):
            username = st.text_input("Username", placeholder="Enter username", label_visibility="visible")
            password = st.text_input("Password", type="password", placeholder="Enter password", label_visibility="visible")
            submitted = st.form_submit_button("🔐 Sign In", use_container_width=True)

        if submitted:
            # Validate against DB teachers table OR admin account
            if username == "admin" and password == st.session_state["admin_password"]:
                st.session_state["logged_in"] = True
                st.session_state["current_user"] = "admin"
                st.session_state["current_role"] = "Admin"
                st.rerun()
            else:
                # Check teacher credentials in DB
                try:
                    conn = get_connection()
                    cur = get_cursor(conn, dictionary=True)
                    cur.execute(
                        "SELECT teacher_id, name, teacher_code FROM teacher WHERE teacher_code = %s AND password = %s",
                        (username, password)
                    )
                    teacher = cur.fetchone()
                    cur.close(); conn.close()
                    if teacher:
                        st.session_state["logged_in"] = True
                        st.session_state["current_user"] = teacher["name"]
                        st.session_state["current_role"] = "Teacher"
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password. Please try again.")
                except Exception:
                    # DB check failed — only allow admin fallback
                    if username == "admin" and password == st.session_state["admin_password"]:
                        st.session_state["logged_in"] = True
                        st.session_state["current_user"] = "admin"
                        st.session_state["current_role"] = "Admin"
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password.")

        st.markdown("""
            <div style="text-align:center; margin-top:24px; color:#475569; font-size:0.8rem;">
                Default admin: <b style='color:#94A3B8'>admin</b> / <b style='color:#94A3B8'>admin123</b>
            </div>
        """, unsafe_allow_html=True)


# ── Auth Gate ─────────────────────────────────────────────────────────────────
if not st.session_state["logged_in"]:
    show_login_page()
    st.stop()


# ── DB Data Helpers ───────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def fetch_departments():
    try:
        conn = get_connection()
        df = pd.read_sql("SELECT dept_id, dept_name, code FROM department ORDER BY dept_name", conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=30)
def fetch_teachers():
    try:
        conn = get_connection()
        query = """
            SELECT t.teacher_id, t.teacher_code, t.name, t.email, t.phone, d.dept_name
            FROM teacher t
            LEFT JOIN department d ON t.dept_id = d.dept_id
            ORDER BY t.name
        """
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=30)
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


@st.cache_data(ttl=30)
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


# ── Top Bar Header ────────────────────────────────────────────────────────────
head_col1, head_col2, head_col3, head_col4 = st.columns([3, 1, 1, 0.8])
with head_col1:
    st.markdown("""
        <div class="top-header">
            <div>
                <div class="top-title">&#127891; College Attendance System</div>
                <div class="top-sub">System Date: """ + datetime.now().strftime("%A, %d %B %Y") + """</div>
            </div>
            <div style="font-size:0.9rem; color:#CBD5E1;">
                &#128100; Logged in as: <b>""" + st.session_state["current_user"] + """ (""" + st.session_state["current_role"] + """)</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

with head_col2:
    if ar.PDF_AVAILABLE:
        try:
            cred_pdf = ar.generate_credentials_pdf(filepath=None)
            st.download_button(
                "🪪 Export Credentials",
                data=cred_pdf,
                file_name="login_credentials.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        except Exception:
            st.button("🪪 Export Credentials", disabled=True, use_container_width=True)

with head_col3:
    if st.button("🔑 Change Password", use_container_width=True):
        st.session_state["show_pw_dialog"] = True

with head_col4:
    if st.button("🚪 Logout", use_container_width=True, type="secondary"):
        st.session_state["logged_in"] = False
        st.session_state["current_user"] = ""
        st.session_state["current_role"] = ""
        st.rerun()

if st.session_state.get("show_pw_dialog"):
    with st.expander("🔐 Change Password Form", expanded=True):
        with st.form("pw_change_form"):
            curr_pw = st.text_input("Current Password", type="password")
            new_pw = st.text_input("New Password", type="password")
            confirm_pw = st.text_input("Confirm New Password", type="password")
            if st.form_submit_button("Update Password"):
                if curr_pw != st.session_state["admin_password"]:
                    st.error("Current password is incorrect.")
                elif new_pw != confirm_pw:
                    st.error("New passwords do not match.")
                elif len(new_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    st.session_state["admin_password"] = new_pw
                    st.success("Password updated successfully!")
                    st.session_state["show_pw_dialog"] = False

# Quick connection diagnostic check
is_connected, conn_msg = test_connection()
if not is_connected:
    st.error(f"🔴 Database Disconnected: {conn_msg}. Please configure Streamlit Secrets (`.streamlit/secrets.toml`).")


# ── 7 Main Tabs (Matching main_app.py) ────────────────────────────────────────
tab_dash, tab_dept, tab_stud, tab_tchr, tab_crs, tab_att, tab_rep = st.tabs([
    "🏠 Dashboard",
    "🏢 Departments",
    "👨‍🎓 Students",
    "👩‍🏫 Teachers",
    "📚 Courses",
    "✔️ Attendance",
    "📊 Reports"
])


# ==============================================================================
# TAB 1: DASHBOARD
# ==============================================================================
with tab_dash:
    st.subheader("🎓 College Attendance Management System")
    
    if is_connected:
        try:
            stats = ar.get_overall_dashboard_stats()
            
            # Top Stat Cards
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.metric("🎓 Students", stats.get("total_students", 0))
            with c2:
                st.metric("👩‍🏫 Teachers", stats.get("total_teachers", 0))
            with c3:
                st.metric("📚 Courses", stats.get("total_courses", 0))
            with c4:
                st.metric("🏢 Departments", stats.get("total_dept", 0))
            with c5:
                today_tot = stats.get("today_total", 0)
                today_pres = stats.get("today_present", 0)
                today_pct = round(today_pres * 100.0 / today_tot, 1) if today_tot > 0 else 0
                st.metric("📅 Today's Att. %", f"{today_pct}%")

            st.markdown("---")

            col_left, col_right = st.columns([1.5, 1])

            with col_left:
                st.write("#### 📊 Course Attendance %")
                summary_data = ar.get_student_attendance_summary()
                if summary_data:
                    df_summary = pd.DataFrame(summary_data)
                    df_course_avg = df_summary.groupby(["course_code", "course_name"])["attendance_pct"].mean().reset_index()
                    st.bar_chart(
                        data=df_course_avg,
                        x="course_code",
                        y="attendance_pct",
                        x_label="Course Code",
                        y_label="Attendance (%)"
                    )
                else:
                    st.info("No attendance data available.")

            with col_right:
                st.write("#### 🕒 Recent Attendance")
                recent = stats.get("recent", [])
                if recent:
                    df_recent = pd.DataFrame(recent)
                    st.dataframe(df_recent, use_container_width=True)
                else:
                    st.info("No recent attendance records.")

        except Exception as ex:
            st.error(f"Error loading dashboard stats: {ex}")


# ==============================================================================
# TAB 2: DEPARTMENTS
# ==============================================================================
with tab_dept:
    st.subheader("🏢 Department Management")
    if is_connected:
        dept_df = fetch_departments()
        st.dataframe(dept_df, use_container_width=True)

        with st.expander("➕ Add New Department"):
            with st.form("add_dept_form"):
                d_name = st.text_input("Department Name (e.g. Computer Science)")
                d_code = st.text_input("Department Code (e.g. CSE)")
                if st.form_submit_button("Add Department"):
                    if d_name and d_code:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute("INSERT INTO department (dept_name, code) VALUES (%s, %s)", (d_name, d_code))
                            conn.commit()
                            conn.close()
                            st.success(f"Department '{d_name}' added successfully!")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Failed to add department: {e}")
                    else:
                        st.warning("Please enter both Department Name and Code.")


# ==============================================================================
# TAB 3: STUDENTS
# ==============================================================================
with tab_stud:
    st.subheader("👨‍🎓 Student Management")
    if is_connected:
        stud_df = fetch_students()
        st.dataframe(stud_df, use_container_width=True)

        with st.expander("➕ Register New Student"):
            with st.form("add_student_form"):
                r_no = st.text_input("Roll Number (e.g. CS104)")
                s_name = st.text_input("Student Full Name")
                s_email = st.text_input("Email Address")
                s_sem = st.selectbox("Semester", [1, 2, 3, 4, 5, 6, 7, 8])
                
                dept_df = fetch_departments()
                d_map = {row['dept_name']: row['dept_id'] for _, row in dept_df.iterrows()} if not dept_df.empty else {}
                s_dept = st.selectbox("Department", list(d_map.keys()) if d_map else ["None"])

                if st.form_submit_button("Save Student"):
                    if r_no and s_name:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT INTO student (roll_no, name, email, semester, dept_id) VALUES (%s, %s, %s, %s, %s)",
                                (r_no, s_name, s_email, s_sem, d_map.get(s_dept))
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"Student '{s_name}' added successfully!")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Failed to add student: {e}")
                    else:
                        st.warning("Please provide Roll Number and Student Name.")


# ==============================================================================
# TAB 4: TEACHERS
# ==============================================================================
with tab_tchr:
    st.subheader("👩‍🏫 Teacher Management")
    if is_connected:
        tchr_df = fetch_teachers()
        st.dataframe(tchr_df, use_container_width=True)

        with st.expander("➕ Register New Teacher"):
            with st.form("add_teacher_form"):
                t_code = st.text_input("Teacher Code (e.g. TCH05)")
                t_name = st.text_input("Teacher Name")
                t_email = st.text_input("Teacher Email")
                t_phone = st.text_input("Phone Number")
                
                dept_df = fetch_departments()
                d_map = {row['dept_name']: row['dept_id'] for _, row in dept_df.iterrows()} if not dept_df.empty else {}
                t_dept = st.selectbox("Department", list(d_map.keys()) if d_map else ["None"])

                if st.form_submit_button("Save Teacher"):
                    if t_name:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT INTO teacher (teacher_code, name, email, phone, dept_id) VALUES (%s, %s, %s, %s, %s)",
                                (t_code, t_name, t_email, t_phone, d_map.get(t_dept))
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"Teacher '{t_name}' added successfully!")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Failed to add teacher: {e}")
                    else:
                        st.warning("Please provide Teacher Name.")


# ==============================================================================
# TAB 5: COURSES
# ==============================================================================
with tab_crs:
    st.subheader("📚 Course Management")
    if is_connected:
        crs_df = fetch_courses()
        st.dataframe(crs_df, use_container_width=True)

        with st.expander("➕ Add New Course"):
            with st.form("add_course_form"):
                c_code = st.text_input("Course Code (e.g. CS303)")
                c_name = st.text_input("Course Name (e.g. Operating Systems)")

                dept_df = fetch_departments()
                d_map = {row['dept_name']: row['dept_id'] for _, row in dept_df.iterrows()} if not dept_df.empty else {}
                c_dept = st.selectbox("Department", list(d_map.keys()) if d_map else ["None"])

                tchr_df = fetch_teachers()
                t_map = {row['name']: row['teacher_id'] for _, row in tchr_df.iterrows()} if not tchr_df.empty else {}
                c_tchr = st.selectbox("Assigned Teacher", list(t_map.keys()) if t_map else ["None"])

                if st.form_submit_button("Save Course"):
                    if c_code and c_name:
                        try:
                            conn = get_connection()
                            cur = conn.cursor()
                            cur.execute(
                                "INSERT INTO course (course_code, course_name, dept_id, teacher_id) VALUES (%s, %s, %s, %s)",
                                (c_code, c_name, d_map.get(c_dept), t_map.get(c_tchr))
                            )
                            conn.commit()
                            conn.close()
                            st.success(f"Course '{c_code}' added successfully!")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Failed to add course: {e}")
                    else:
                        st.warning("Please provide Course Code and Course Name.")


# ==============================================================================
# TAB 6: ATTENDANCE
# ==============================================================================
with tab_att:
    st.subheader("✔️ Mark & Manage Daily Attendance")
    if is_connected:
        courses_df = fetch_courses()
        if courses_df.empty:
            st.warning("No active courses found.")
        else:
            c1, c2 = st.columns(2)
            with c1:
                c_opts = {f"{row['course_code']} - {row['course_name']}": row['course_id'] for _, row in courses_df.iterrows()}
                sel_c_label = st.selectbox("Select Course:", list(c_opts.keys()), key="att_c_sel")
                sel_c_id = c_opts[sel_c_label]
            with c2:
                sel_date = st.date_input("Select Attendance Date:", value=date.today(), key="att_d_sel")

            st.markdown("---")

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
                cursor = get_cursor(conn, dictionary=True)
                cursor.execute(query, (sel_date, sel_c_id))
                enrolled_students = cursor.fetchall()
                conn.close()

                if not enrolled_students:
                    st.info("No students enrolled in this course.")
                else:
                    st.write(f"**Enrolled Students Count: {len(enrolled_students)}**")
                    with st.form("mark_att_grid"):
                        att_map = {}
                        rem_map = {}
                        for st_row in enrolled_students:
                            col_s1, col_s2, col_s3 = st.columns([2, 2, 3])
                            with col_s1:
                                st.write(f"**{st_row['roll_no']}** - {st_row['name']}")
                            with col_s2:
                                init_idx = ["Present", "Absent", "Late"].index(st_row['status']) if st_row['status'] in ["Present", "Absent", "Late"] else 0
                                status_val = st.radio(
                                    f"Status_{st_row['enrollment_id']}",
                                    ["Present", "Absent", "Late"],
                                    index=init_idx,
                                    horizontal=True,
                                    label_visibility="collapsed"
                                )
                                att_map[st_row['enrollment_id']] = status_val
                            with col_s3:
                                rem_val = st.text_input(
                                    f"Remarks_{st_row['enrollment_id']}",
                                    value=st_row['remarks'] or "",
                                    label_visibility="collapsed",
                                    placeholder="Remarks (optional)"
                                )
                                rem_map[st_row['enrollment_id']] = rem_val
                            st.divider()

                        if st.form_submit_button("💾 Save Attendance Records", type="primary"):
                            try:
                                conn = get_connection()
                                cur = conn.cursor()
                                for enr_id, status in att_map.items():
                                    rem = rem_map.get(enr_id, "")
                                    sql = """
                                        INSERT INTO attendance (enrollment_id, attendance_date, status, remarks)
                                        VALUES (%s, %s, %s, %s)
                                        ON DUPLICATE KEY UPDATE status=%s, remarks=%s
                                    """
                                    cur.execute(sql, (enr_id, sel_date, status, rem, status, rem))
                                conn.commit()
                                conn.close()
                                st.success("✅ Attendance updated successfully!")
                                st.cache_data.clear()
                            except Exception as ex:
                                st.error(f"Failed to update attendance: {ex}")

            except Exception as ex:
                st.error(f"Error loading enrollment records: {ex}")


# ==============================================================================
# TAB 7: REPORTS
# ==============================================================================
with tab_rep:
    st.subheader("📊 Reports & Export Tools")
    if is_connected:
        rep_t1, rep_t2 = st.tabs(["📄 Attendance Summary Report", "⚠️ Low Attendance Defaulter Alerts"])

        with rep_t1:
            all_summary = ar.get_student_attendance_summary()
            if all_summary:
                df_summary_all = pd.DataFrame(all_summary)
                st.dataframe(df_summary_all, use_container_width=True)

                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    csv_bytes = ar.export_to_csv(all_summary)
                    st.download_button(
                        "📥 Export Summary CSV",
                        data=csv_bytes,
                        file_name="student_attendance_summary.csv",
                        mime="text/csv"
                    )
                with col_dl2:
                    if ar.PDF_AVAILABLE:
                        pdf_bytes = ar.export_to_pdf(all_summary, title="Student Attendance Summary Report")
                        st.download_button(
                            "📥 Export Summary PDF",
                            data=pdf_bytes,
                            file_name="student_attendance_summary.pdf",
                            mime="application/pdf"
                        )
                    else:
                        st.info("PDF Export requires reportlab library.")
            else:
                st.info("No attendance records found.")

        with rep_t2:
            thresh = st.slider("Attendance Threshold (%):", 50, 90, 75, 5)
            defaulters = ar.get_defaulter_list(threshold=thresh)
            if defaulters:
                st.warning(f"Found {len(defaulters)} student(s) with attendance below {thresh}%.")
                st.dataframe(pd.DataFrame(defaulters), use_container_width=True)

                cd1, cd2 = st.columns(2)
                with cd1:
                    csv_def = ar.export_to_csv(defaulters)
                    st.download_button(
                        "📥 Export Defaulter CSV",
                        data=csv_def,
                        file_name=f"defaulters_below_{thresh}pct.csv",
                        mime="text/csv"
                    )
                with cd2:
                    if ar.PDF_AVAILABLE:
                        pdf_def = ar.export_to_pdf(defaulters, title=f"Defaulter List (Below {thresh}%)")
                        st.download_button(
                            "📥 Export Defaulter PDF",
                            data=pdf_def,
                            file_name=f"defaulters_below_{thresh}pct.pdf",
                            mime="application/pdf"
                        )
            else:
                st.success(f"No students have attendance below {thresh}%. Excellent record!")

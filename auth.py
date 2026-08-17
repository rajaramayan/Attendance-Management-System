"""
auth.py
-------
Authentication helpers for the College Attendance System.
Handles: admin first-run setup, teacher/student signup, login, password change.
Passwords are stored as SHA-256 hashes.
"""

import hashlib
import secrets
import string
from db_config import get_connection, get_cursor


# ── Hashing ───────────────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()


def generate_password(length: int = 12) -> str:
    chars = string.ascii_letters + string.digits + "!@#$"
    return "".join(secrets.choice(chars) for _ in range(length))


# ── Admin first-run check ─────────────────────────────────────────────────────

def admin_exists() -> bool:
    """Return True if any Admin user row exists in the users table."""
    try:
        conn = get_connection()
        cur = get_cursor(conn, dictionary=True)
        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE role = 'Admin'")
        row = cur.fetchone()
        cur.close(); conn.close()
        cnt = row["cnt"] if row and isinstance(row, dict) else (row[0] if row else 0)
        return cnt > 0
    except Exception:
        return False


def create_admin(username: str, plain_password: str) -> bool:
    """Insert admin row. Returns True on success."""
    try:
        conn = get_connection()
        cur = get_cursor(conn)
        cur.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'Admin')",
            (username, hash_password(plain_password))
        )
        conn.commit()
        cur.close(); conn.close()
        return True
    except Exception:
        return False


# ── Login ─────────────────────────────────────────────────────────────────────

def login(username: str, plain_password: str):
    """
    Returns dict with keys: success, role, display_name, user_id
    or None on failure.
    """
    try:
        conn = get_connection()
        cur = get_cursor(conn, dictionary=True)
        cur.execute(
            """SELECT u.user_id, u.username, u.role, u.teacher_id, u.student_id,
                      t.name AS teacher_name, s.name AS student_name
               FROM users u
               LEFT JOIN teacher t ON u.teacher_id = t.teacher_id
               LEFT JOIN student s ON u.student_id  = s.student_id
               WHERE u.username = %s AND u.password_hash = %s""",
            (username, hash_password(plain_password))
        )
        row = cur.fetchone()
        cur.close(); conn.close()

        if not row:
            return None

        # Support both DictCursor (pymysql) and plain tuple cursor
        if isinstance(row, dict):
            role = row["role"]
            user_id = row["user_id"]
            display = (row.get("teacher_name") or row.get("student_name") or row["username"])
            teacher_id = row.get("teacher_id")
            student_id = row.get("student_id")
        else:
            user_id, uname, role, teacher_id, student_id, teacher_name, student_name = row
            display = teacher_name or student_name or uname

        return {
            "success": True,
            "user_id": user_id,
            "role": role,
            "display_name": display,
            "teacher_id": teacher_id,
            "student_id": student_id,
        }
    except Exception:
        return None


# ── Signup ────────────────────────────────────────────────────────────────────

def username_taken(username: str) -> bool:
    try:
        conn = get_connection()
        cur = get_cursor(conn, dictionary=True)
        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE username = %s", (username,))
        row = cur.fetchone()
        cur.close(); conn.close()
        cnt = row["cnt"] if isinstance(row, dict) else row[0]
        return cnt > 0
    except Exception:
        return False


def signup_teacher(username: str, plain_password: str, teacher_code: str) -> tuple:
    """
    Signup a teacher. They must provide their teacher_code which must
    already exist in the teacher table and NOT yet have a users row.
    Returns (True, "") or (False, error_message).
    """
    try:
        conn = get_connection()
        cur = get_cursor(conn, dictionary=True)

        # Find teacher by code
        cur.execute("SELECT teacher_id, name FROM teacher WHERE teacher_code = %s", (teacher_code,))
        teacher = cur.fetchone()
        if not teacher:
            cur.close(); conn.close()
            return False, "Teacher code not found. Please contact admin."

        t_id = teacher["teacher_id"] if isinstance(teacher, dict) else teacher[0]

        # Check teacher not already registered
        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE teacher_id = %s", (t_id,))
        row = cur.fetchone()
        cnt = row["cnt"] if isinstance(row, dict) else row[0]
        if cnt > 0:
            cur.close(); conn.close()
            return False, "This teacher code is already registered. Please log in."

        if username_taken(username):
            cur.close(); conn.close()
            return False, "Username already taken. Choose a different one."

        cur.execute(
            "INSERT INTO users (username, password_hash, role, teacher_id) VALUES (%s, %s, 'Teacher', %s)",
            (username, hash_password(plain_password), t_id)
        )
        conn.commit()
        cur.close(); conn.close()
        return True, ""
    except Exception as e:
        return False, str(e)


def signup_student(username: str, plain_password: str, roll_no: str) -> tuple:
    """
    Signup a student using their roll number which must already exist
    in the student table and NOT yet have a users row.
    Returns (True, "") or (False, error_message).
    """
    try:
        conn = get_connection()
        cur = get_cursor(conn, dictionary=True)

        cur.execute("SELECT student_id, name FROM student WHERE roll_no = %s", (roll_no,))
        student = cur.fetchone()
        if not student:
            cur.close(); conn.close()
            return False, "Roll number not found. Please contact admin."

        s_id = student["student_id"] if isinstance(student, dict) else student[0]

        cur.execute("SELECT COUNT(*) AS cnt FROM users WHERE student_id = %s", (s_id,))
        row = cur.fetchone()
        cnt = row["cnt"] if isinstance(row, dict) else row[0]
        if cnt > 0:
            cur.close(); conn.close()
            return False, "This roll number is already registered. Please log in."

        if username_taken(username):
            cur.close(); conn.close()
            return False, "Username already taken. Choose a different one."

        cur.execute(
            "INSERT INTO users (username, password_hash, role, student_id) VALUES (%s, %s, 'Student', %s)",
            (username, hash_password(plain_password), s_id)
        )
        conn.commit()
        cur.close(); conn.close()
        return True, ""
    except Exception as e:
        return False, str(e)


# ── Change Password ───────────────────────────────────────────────────────────

def change_password(user_id: int, old_plain: str, new_plain: str) -> tuple:
    """
    Verify old password and update to new one.
    Returns (True, "") or (False, error_message).
    """
    try:
        conn = get_connection()
        cur = get_cursor(conn, dictionary=True)
        cur.execute(
            "SELECT password_hash FROM users WHERE user_id = %s",
            (user_id,)
        )
        row = cur.fetchone()
        if not row:
            cur.close(); conn.close()
            return False, "User not found."

        stored_hash = row["password_hash"] if isinstance(row, dict) else row[0]
        if stored_hash != hash_password(old_plain):
            cur.close(); conn.close()
            return False, "Current password is incorrect."

        cur.execute(
            "UPDATE users SET password_hash = %s WHERE user_id = %s",
            (hash_password(new_plain), user_id)
        )
        conn.commit()
        cur.close(); conn.close()
        return True, ""
    except Exception as e:
        return False, str(e)

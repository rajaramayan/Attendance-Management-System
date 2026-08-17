import os
import streamlit as st

# Try PyMySQL first, then fallback to mysql.connector
try:
    import pymysql
    HAS_PYMYSQL = True
except ImportError:
    HAS_PYMYSQL = False

try:
    import mysql.connector
    HAS_MYSQL_CONNECTOR = True
except ImportError:
    HAS_MYSQL_CONNECTOR = False


def get_connection():
    # Default fallback credentials for Aiven Cloud MySQL
    host = os.getenv("DB_HOST", "mysql-27ea9885-attendance-management-systemnew.b.aivencloud.com")
    port = int(os.getenv("DB_PORT", 25561))
    user = os.getenv("DB_USER", "avnadmin")
    password = os.getenv("DB_PASSWORD", "YOUR_DB_PASSWORD")
    database = os.getenv("DB_NAME", "college")
    ssl_ca = "ca.pem" if os.path.exists("ca.pem") else None

    # Check if Streamlit secrets exist
    try:
        if hasattr(st, "secrets") and "connections" in st.secrets and "mysql" in st.secrets["connections"]:
            mysql_conf = st.secrets["connections"]["mysql"]
            host = mysql_conf.get("host", host)
            port = int(mysql_conf.get("port", port))
            user = mysql_conf.get("username", user)
            password = mysql_conf.get("password", password)
            database = mysql_conf.get("database", database)
    except Exception:
        pass

    # Try connecting with PyMySQL first (most reliable in cloud containers)
    if HAS_PYMYSQL:
        try:
            kwargs = {
                "host": host,
                "port": port,
                "user": user,
                "password": password,
                "database": database,
                "cursorclass": pymysql.cursors.DictCursor,
            }
            if ssl_ca and os.path.exists(ssl_ca):
                kwargs["ssl"] = {"ca": ssl_ca}
            return pymysql.connect(**kwargs)
        except Exception:
            pass

    # Fallback to mysql.connector
    if HAS_MYSQL_CONNECTOR:
        kwargs = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }
        if ssl_ca and os.path.exists(ssl_ca):
            kwargs["ssl_ca"] = ssl_ca
            kwargs["ssl_verify_cert"] = True
        return mysql.connector.connect(**kwargs)

    raise RuntimeError("Neither pymysql nor mysql-connector-python is available to connect to MySQL.")


def test_connection():
    try:
        connection = get_connection()
        connection.close()
        return True, "Connected to MySQL successfully!"
    except Exception as e:
        return False, str(e)


def get_cursor(conn, dictionary=False):
    if dictionary:
        try:
            return conn.cursor(dictionary=True)
        except TypeError:
            return conn.cursor()
    return conn.cursor()
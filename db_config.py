import os
import mysql.connector
from mysql.connector.errors import Error
import streamlit as st


def get_connection():
    host = os.getenv("DB_HOST", "localhost")
    port = int(os.getenv("DB_PORT", 25561))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    database = os.getenv("DB_NAME", "college")
    ssl_ca = "ca.pem" if os.path.exists("ca.pem") else None

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


def test_connection():
    try:
        connection = get_connection()

        if connection.is_connected():
            connection.close()
            return True, "Connected to MySQL successfully!"

        return False, "Connection failed."

    except Error as e:
        return False, str(e)
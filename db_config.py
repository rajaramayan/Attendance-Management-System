import mysql.connector
from mysql.connector.errors import Error
import streamlit as st


def get_connection():
    return mysql.connector.connect(
        host=st.secrets["connections"]["mysql"]["host"],
        port=int(st.secrets["connections"]["mysql"]["port"]),
        user=st.secrets["connections"]["mysql"]["username"],
        password=st.secrets["connections"]["mysql"]["password"],
        database=st.secrets["connections"]["mysql"]["database"],
        ssl_ca="ca.pem",
        ssl_verify_cert=True,
    )


def test_connection():
    try:
        connection = get_connection()

        if connection.is_connected():
            connection.close()
            return True, "Connected to Aiven MySQL successfully!"

        return False, "Connection failed."

    except Error as e:
        return False, str(e)
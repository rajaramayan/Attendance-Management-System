import os
import mysql.connector

connection = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "root"),
    password=os.getenv("DB_PASSWORD", "YOUR_DB_PASSWORD"),
    database=os.getenv("DB_NAME", "college")
)

if connection.is_connected():
    print("Connected to college database successfully!")

connection.close()
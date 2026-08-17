import os
import mysql.connector

connection = mysql.connector.connect(
    host=os.getenv("DB_HOST", "mysql-27ea9885-attendance-management-systemnew.b.aivencloud.com"),
    port=int(os.getenv("DB_PORT", 25561)),
    user=os.getenv("DB_USER", "avnadmin"),
    password=os.getenv("DB_PASSWORD", "YOUR_DB_PASSWORD"),
    database=os.getenv("DB_NAME", "college"),
    ssl_ca="ca.pem",
    ssl_verify_cert=True,
    ssl_verify_identity=True
)

if connection.is_connected():
    print("Connected to Aiven MySQL successfully!")

connection.close()
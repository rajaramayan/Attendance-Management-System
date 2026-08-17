# Attendance Management System

A comprehensive Attendance Management System built with Python, MySQL, Tkinter GUI, and Streamlit Web Dashboard.

## 🚀 Features

- **Desktop Application (Tkinter)**: Manage students, teachers, courses, departments, enrollments, and attendance records with an intuitive desktop interface.
- **Web Dashboard (Streamlit)**: Interactive web interface for reporting, statistics, and viewing attendance logs.
- **Database Support**: Built-in support for local MySQL and cloud MySQL (such as Aiven) with SSL certificate support.
- **Role-Based Access**: Manage user accounts and permissions seamlessly.

## 📁 Repository Structure

```
├── app.py                     # Main Streamlit web application
├── attendance_report.py        # PDF & CSV reporting library
├── main_app.py                # Main Tkinter desktop application
├── student_form.py            # Student management form interface
├── db_config.py               # Centralized MySQL connection handler
├── setup_db.py                # Database initialization & seed script
├── validate.py                # Validation script for database setup
├── db_setup.sql               # Database schema definition
├── college_backup.sql         # Sample database dump
├── ca.pem                     # SSL CA certificate for cloud MySQL
├── requirements.txt           # Python dependencies
└── .streamlit/
    └── secrets.toml.example   # Streamlit credentials template
```

## 🛠️ Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/rajaramayan/Attendance-Management-System.git
   cd Attendance-Management-System
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Database Credentials**:
   Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and update your database credentials:
   ```toml
   [connections.mysql]
   dialect = "mysql"
   host = "your-db-host"
   port = 25561
   database = "college"
   username = "your-username"
   password = "your-password"
   query = { charset = "utf8mb4" }
   ```

4. **Initialize Database**:
   ```bash
   python setup_db.py
   ```

5. **Run Applications**:
   - **Streamlit Web Dashboard**: `streamlit run app.py`
   - **Desktop App**: `python main_app.py`

## 📜 License

This project is open-source and available under the MIT License.

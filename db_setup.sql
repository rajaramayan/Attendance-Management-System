-- ============================================================
-- STUDENT ATTENDANCE MANAGEMENT SYSTEM
-- Database: college
-- Schema Version: 2.0 (Normalized to 3NF)
-- ============================================================

USE college;

-- ============================================================
-- DROP EXISTING TABLES (order matters due to FK constraints)
-- ============================================================
SET FOREIGN_KEY_CHECKS = 0;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS enrollment;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS teacher;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS department;
SET FOREIGN_KEY_CHECKS = 1;


-- ============================================================
-- TABLE 1: DEPARTMENT
-- Stores college departments. No FK dependencies.
-- ============================================================
CREATE TABLE department (
    dept_id    INT AUTO_INCREMENT PRIMARY KEY,
    dept_name  VARCHAR(100) NOT NULL UNIQUE,
    dept_code  VARCHAR(10)  NOT NULL UNIQUE
);


-- ============================================================
-- TABLE 2: STUDENT
-- Extended from original. dept_id links to department (3NF:
-- dept_name not duplicated here).
-- ============================================================
CREATE TABLE student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no    VARCHAR(20)  NOT NULL UNIQUE,
    name       VARCHAR(100) NOT NULL,
    address    VARCHAR(255),
    dob        DATE,
    phone      VARCHAR(15),
    email      VARCHAR(100),
    gender     ENUM('Male','Female','Other') DEFAULT 'Male',
    dept_id    INT,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE SET NULL
);


-- ============================================================
-- TABLE 3: TEACHER
-- Teacher belongs to one department.
-- ============================================================
CREATE TABLE teacher (
    teacher_id   INT AUTO_INCREMENT PRIMARY KEY,
    teacher_code VARCHAR(20)  NOT NULL UNIQUE,
    name         VARCHAR(100) NOT NULL,
    email        VARCHAR(100),
    phone        VARCHAR(15),
    specialization VARCHAR(100),
    dept_id      INT,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES department(dept_id) ON DELETE SET NULL
);


-- ============================================================
-- TABLE 4: COURSE
-- Each course belongs to a department and is taught by one teacher.
-- Teacher's name not stored here (3NF).
-- ============================================================
CREATE TABLE course (
    course_id   INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20)  NOT NULL UNIQUE,
    course_name VARCHAR(150) NOT NULL,
    credits     INT          DEFAULT 3,
    semester    VARCHAR(10),
    dept_id     INT,
    teacher_id  INT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id)   REFERENCES department(dept_id) ON DELETE SET NULL,
    FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id) ON DELETE SET NULL
);


-- ============================================================
-- TABLE 5: ENROLLMENT  (Junction: Student ↔ Course)
-- Records which students are enrolled in which courses.
-- ============================================================
CREATE TABLE enrollment (
    enrollment_id   INT AUTO_INCREMENT PRIMARY KEY,
    student_id      INT  NOT NULL,
    course_id       INT  NOT NULL,
    enrollment_date DATE DEFAULT (CURRENT_DATE),
    UNIQUE KEY uq_enrollment (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id)  REFERENCES course(course_id)   ON DELETE CASCADE
);


-- ============================================================
-- TABLE 6: ATTENDANCE
-- One record per enrollment per date. Status: Present/Absent/Late.
-- ============================================================
CREATE TABLE attendance (
    attendance_id   INT AUTO_INCREMENT PRIMARY KEY,
    enrollment_id   INT  NOT NULL,
    attendance_date DATE NOT NULL,
    status          ENUM('Present','Absent','Late') DEFAULT 'Absent',
    remarks         VARCHAR(200),
    marked_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_attendance (enrollment_id, attendance_date),
    FOREIGN KEY (enrollment_id) REFERENCES enrollment(enrollment_id) ON DELETE CASCADE
);


-- ============================================================
-- USEFUL VIEWS
-- ============================================================

-- View: Full attendance details (joins all tables)
CREATE OR REPLACE VIEW vw_attendance_detail AS
SELECT
    a.attendance_id,
    a.attendance_date,
    a.status,
    a.remarks,
    s.roll_no,
    s.name       AS student_name,
    c.course_code,
    c.course_name,
    t.name       AS teacher_name,
    d.dept_name
FROM attendance a
JOIN enrollment  e ON a.enrollment_id = e.enrollment_id
JOIN student     s ON e.student_id    = s.student_id
JOIN course      c ON e.course_id     = c.course_id
LEFT JOIN teacher t ON c.teacher_id   = t.teacher_id
LEFT JOIN department d ON s.dept_id   = d.dept_id;


-- View: Student attendance percentage per course
CREATE OR REPLACE VIEW vw_attendance_pct AS
SELECT
    s.student_id,
    s.roll_no,
    s.name       AS student_name,
    c.course_id,
    c.course_code,
    c.course_name,
    COUNT(a.attendance_id)                            AS total_classes,
    SUM(a.status = 'Present' OR a.status = 'Late')    AS classes_attended,
    ROUND(
        SUM(a.status = 'Present' OR a.status = 'Late')
        * 100.0 / NULLIF(COUNT(a.attendance_id), 0), 2
    )                                                  AS attendance_pct
FROM enrollment e
JOIN student s  ON e.student_id = s.student_id
JOIN course  c  ON e.course_id  = c.course_id
LEFT JOIN attendance a ON e.enrollment_id = a.enrollment_id
GROUP BY s.student_id, c.course_id;


-- ============================================================
-- SEED DATA
-- ============================================================

-- Departments
INSERT INTO department (dept_name, dept_code) VALUES
('Computer Science',          'CS'),
('Electronics Engineering',   'EC'),
('Mechanical Engineering',    'ME'),
('Civil Engineering',         'CE'),
('Business Administration',   'BA');

-- Teachers
INSERT INTO teacher (teacher_code, name, email, phone, specialization, dept_id) VALUES
('TCH001', 'Dr. Rajesh Kumar',   'rajesh@college.edu',  '9800000001', 'Database Systems',        1),
('TCH002', 'Prof. Sunita Sharma','sunita@college.edu',  '9800000002', 'Digital Electronics',     2),
('TCH003', 'Mr. Anil Thapa',     'anil@college.edu',    '9800000003', 'Thermodynamics',          3),
('TCH004', 'Ms. Priya Poudel',   'priya@college.edu',   '9800000004', 'Structural Analysis',     4),
('TCH005', 'Dr. Suman Adhikari', 'suman@college.edu',   '9800000005', 'Marketing Management',    5);

-- Students
INSERT INTO student (roll_no, name, address, dob, phone, email, gender, dept_id) VALUES
('CS101', 'Aarav Shrestha',   'Kathmandu',   '2002-03-15', '9811111111', 'aarav@mail.com',   'Male',   1),
('CS102', 'Bipasha Rai',      'Lalitpur',    '2002-07-22', '9811111112', 'bipasha@mail.com', 'Female', 1),
('CS103', 'Chetan Gurung',    'Bhaktapur',   '2003-01-10', '9811111113', 'chetan@mail.com',  'Male',   1),
('CS104', 'Dipika Tamang',    'Pokhara',     '2002-11-05', '9811111114', 'dipika@mail.com',  'Female', 1),
('CS105', 'Eshan Magar',      'Chitwan',     '2003-04-18', '9811111115', 'eshan@mail.com',   'Male',   1),
('EC101', 'Fiona Limbu',      'Biratnagar',  '2002-09-30', '9822222221', 'fiona@mail.com',   'Female', 2),
('EC102', 'Ganesh Karki',     'Dharan',      '2003-02-14', '9822222222', 'ganesh@mail.com',  'Male',   2),
('ME101', 'Hari Basnet',      'Butwal',      '2002-06-25', '9833333331', 'hari@mail.com',    'Male',   3),
('ME102', 'Indira Khadka',    'Bhairahawa',  '2003-08-12', '9833333332', 'indira@mail.com',  'Female', 3),
('BA101', 'Jagat Pandey',     'Birgunj',     '2002-12-01', '9844444441', 'jagat@mail.com',   'Male',   5);

-- Courses
INSERT INTO course (course_code, course_name, credits, semester, dept_id, teacher_id) VALUES
('CS301', 'Database Management Systems', 4, 'VI',  1, 1),
('CS302', 'Data Structures & Algorithms', 4, 'VI', 1, 1),
('EC301', 'Digital Signal Processing',   4, 'VI',  2, 2),
('ME301', 'Thermodynamics II',            3, 'VI',  3, 3),
('BA301', 'Marketing Management',         3, 'VI',  5, 5);

-- Enrollments (CS students in CS courses, etc.)
INSERT INTO enrollment (student_id, course_id, enrollment_date) VALUES
(1, 1, '2026-01-15'), (2, 1, '2026-01-15'), (3, 1, '2026-01-15'), (4, 1, '2026-01-15'), (5, 1, '2026-01-15'),
(1, 2, '2026-01-15'), (2, 2, '2026-01-15'), (3, 2, '2026-01-15'), (4, 2, '2026-01-15'), (5, 2, '2026-01-15'),
(6, 3, '2026-01-15'), (7, 3, '2026-01-15'),
(8, 4, '2026-01-15'), (9, 4, '2026-01-15'),
(10,5, '2026-01-15');

-- Sample attendance (last 10 weekdays for enrolled students)
INSERT INTO attendance (enrollment_id, attendance_date, status) VALUES
-- CS301 enrollments (1-5)
(1,'2026-08-04','Present'),(2,'2026-08-04','Present'),(3,'2026-08-04','Absent'),(4,'2026-08-04','Present'),(5,'2026-08-04','Late'),
(1,'2026-08-05','Present'),(2,'2026-08-05','Absent'),(3,'2026-08-05','Present'),(4,'2026-08-05','Present'),(5,'2026-08-05','Present'),
(1,'2026-08-06','Present'),(2,'2026-08-06','Present'),(3,'2026-08-06','Present'),(4,'2026-08-06','Absent'),(5,'2026-08-06','Present'),
(1,'2026-08-07','Absent'),(2,'2026-08-07','Present'),(3,'2026-08-07','Present'),(4,'2026-08-07','Present'),(5,'2026-08-07','Present'),
(1,'2026-08-11','Present'),(2,'2026-08-11','Present'),(3,'2026-08-11','Absent'),(4,'2026-08-11','Present'),(5,'2026-08-11','Present'),
-- CS302 enrollments (6-10)
(6,'2026-08-04','Present'),(7,'2026-08-04','Present'),(8,'2026-08-04','Present'),(9,'2026-08-04','Absent'),(10,'2026-08-04','Present'),
(6,'2026-08-05','Present'),(7,'2026-08-05','Late'),(8,'2026-08-05','Present'),(9,'2026-08-05','Present'),(10,'2026-08-05','Absent'),
(6,'2026-08-06','Absent'),(7,'2026-08-06','Present'),(8,'2026-08-06','Present'),(9,'2026-08-06','Present'),(10,'2026-08-06','Present'),
-- EC301 (11,12)
(11,'2026-08-04','Present'),(12,'2026-08-04','Absent'),
(11,'2026-08-05','Present'),(12,'2026-08-05','Present'),
-- ME301 (13,14)
(13,'2026-08-04','Present'),(14,'2026-08-04','Present'),
(13,'2026-08-05','Absent'),(14,'2026-08-05','Present'),
-- BA301 (15)
(15,'2026-08-04','Present'),
(15,'2026-08-05','Present');


-- ============================================================
-- TABLE 7: USERS (Authentication & Access Control)
-- ============================================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(128) NOT NULL,
    role          ENUM('Admin','Teacher','Student') NOT NULL DEFAULT 'Student',
    teacher_id    INT NULL,
    student_id    INT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id) ON DELETE SET NULL,
    FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE SET NULL
);

-- Seed Users (Admin, Teachers, Students)
INSERT INTO users (username, password_hash, role, teacher_id, student_id) VALUES
('admin',   'admin123',   'Admin',   NULL, NULL),
('rajesh',  'teacher123', 'Teacher', 1,    NULL),
('sunita',  'teacher123', 'Teacher', 2,    NULL),
('anil',    'teacher123', 'Teacher', 3,    NULL),
('priya',   'teacher123', 'Teacher', 4,    NULL),
('suman',   'teacher123', 'Teacher', 5,    NULL),
-- Student Accounts (Username = Roll No, Password = student123)
('CS101',   'student123', 'Student', NULL, 1),
('CS102',   'student123', 'Student', NULL, 2),
('CS103',   'student123', 'Student', NULL, 3),
('CS104',   'student123', 'Student', NULL, 4),
('CS105',   'student123', 'Student', NULL, 5),
('EC101',   'student123', 'Student', NULL, 6),
('EC102',   'student123', 'Student', NULL, 7),
('ME101',   'student123', 'Student', NULL, 8),
('ME102',   'student123', 'Student', NULL, 9),
-- ============================================================
-- TABLE 8: CLASS LOG (Topic Taught per Class)
-- ============================================================
DROP TABLE IF EXISTS class_log;
CREATE TABLE class_log (
    log_id          INT AUTO_INCREMENT PRIMARY KEY,
    course_id       INT NOT NULL,
    teacher_id      INT NULL,
    class_date      DATE NOT NULL,
    topic_taught    VARCHAR(500) NOT NULL,
    logged_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_course_date (course_id, class_date),
    FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id) ON DELETE SET NULL
);

-- Seed Class Logs
INSERT INTO class_log (course_id, teacher_id, class_date, topic_taught) VALUES
(1, 1, '2026-08-04', 'Introduction to Relational Databases and SQL Basics'),
(1, 1, '2026-08-05', 'ER Diagrams and Database Normalization (1NF, 2NF, 3NF)'),
(1, 1, '2026-08-06', 'SQL Join Operations (INNER, LEFT, RIGHT, FULL)'),
(1, 1, '2026-08-07', 'Aggregate Functions, GROUP BY, and HAVING Clauses'),
(1, 1, '2026-08-11', 'Database Indexing and B-Tree Indexes Performance'),
(2, 1, '2026-08-04', 'Arrays, Linked Lists, and Memory Allocation'),
(2, 1, '2026-08-05', 'Stack and Queue Data Structures Implementation'),
(2, 1, '2026-08-06', 'Binary Search Trees (BST) Insertion and Traversal'),
(3, 2, '2026-08-04', 'Discrete-Time Signals and Fourier Transform (DFT)'),
(3, 2, '2026-08-05', 'Fast Fourier Transform (FFT) Algorithm and Sampling'),
(4, 3, '2026-08-04', 'First Law of Thermodynamics and Heat Transfer'),
(4, 3, '2026-08-05', 'Second Law of Thermodynamics and Carnot Engine Cycle'),
(5, 5, '2026-08-04', 'Principles of Digital Marketing and Customer Behavior'),
(5, 5, '2026-08-05', 'Brand Positioning Strategies and Market Segmentation');




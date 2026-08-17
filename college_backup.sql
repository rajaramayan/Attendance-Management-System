-- MySQL dump 10.13  Distrib 26.7.0, for Win64 (x86_64)
--
-- Host: localhost    Database: college
-- ------------------------------------------------------
-- Server version	26.7.0

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `attendance`
--

DROP TABLE IF EXISTS `attendance`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `attendance` (
  `attendance_id` int NOT NULL AUTO_INCREMENT,
  `enrollment_id` int NOT NULL,
  `attendance_date` date NOT NULL,
  `status` enum('Present','Absent','Late') DEFAULT 'Absent',
  `remarks` varchar(200) DEFAULT NULL,
  `marked_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`attendance_id`),
  UNIQUE KEY `uq_attendance` (`enrollment_id`,`attendance_date`),
  CONSTRAINT `attendance_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `enrollment` (`enrollment_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=66 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `attendance`
--

LOCK TABLES `attendance` WRITE;
/*!40000 ALTER TABLE `attendance` DISABLE KEYS */;
INSERT INTO `attendance` VALUES (1,1,'2026-08-04','Present',NULL,'2026-08-16 09:57:05'),(2,2,'2026-08-04','Present',NULL,'2026-08-16 09:57:05'),(3,3,'2026-08-04','Absent',NULL,'2026-08-16 09:57:05'),(4,4,'2026-08-04','Present',NULL,'2026-08-16 09:57:05'),(5,5,'2026-08-04','Late',NULL,'2026-08-16 09:57:05'),(6,1,'2026-08-05','Present',NULL,'2026-08-16 09:57:05'),(7,2,'2026-08-05','Absent',NULL,'2026-08-16 09:57:05'),(8,3,'2026-08-05','Present',NULL,'2026-08-16 09:57:05'),(9,4,'2026-08-05','Present',NULL,'2026-08-16 09:57:05'),(10,5,'2026-08-05','Present',NULL,'2026-08-16 09:57:05'),(11,1,'2026-08-06','Present',NULL,'2026-08-16 09:57:05'),(12,2,'2026-08-06','Present',NULL,'2026-08-16 09:57:05'),(13,3,'2026-08-06','Present',NULL,'2026-08-16 09:57:05'),(14,4,'2026-08-06','Absent',NULL,'2026-08-16 09:57:05'),(15,5,'2026-08-06','Present',NULL,'2026-08-16 09:57:05'),(16,1,'2026-08-07','Absent',NULL,'2026-08-16 09:57:05'),(17,2,'2026-08-07','Present',NULL,'2026-08-16 09:57:05'),(18,3,'2026-08-07','Present',NULL,'2026-08-16 09:57:05'),(19,4,'2026-08-07','Present',NULL,'2026-08-16 09:57:05'),(20,5,'2026-08-07','Present',NULL,'2026-08-16 09:57:05'),(21,1,'2026-08-11','Present',NULL,'2026-08-16 09:57:05'),(22,2,'2026-08-11','Present',NULL,'2026-08-16 09:57:05'),(23,3,'2026-08-11','Absent',NULL,'2026-08-16 09:57:05'),(24,4,'2026-08-11','Present',NULL,'2026-08-16 09:57:05'),(25,5,'2026-08-11','Present',NULL,'2026-08-16 09:57:05'),(26,6,'2026-08-04','Present',NULL,'2026-08-16 09:57:05'),(27,7,'2026-08-04','Present',NULL,'2026-08-16 09:57:05'),(28,8,'2026-08-04','Present',NULL,'2026-08-16 09:57:05'),(29,9,'2026-08-04','Absent',NULL,'2026-08-16 09:57:05'),(30,10,'2026-08-04','Present',NULL,'2026-08-16 09:57:05'),(31,6,'2026-08-05','Present',NULL,'2026-08-16 09:57:05'),(32,7,'2026-08-05','Late',NULL,'2026-08-16 09:57:05'),(33,8,'2026-08-05','Present',NULL,'2026-08-16 09:57:05'),(34,9,'2026-08-05','Present',NULL,'2026-08-16 09:57:05'),(35,10,'2026-08-05','Absent',NULL,'2026-08-16 09:57:05'),(36,6,'2026-08-06','Absent',NULL,'2026-08-16 09:57:05'),(37,7,'2026-08-06','Present',NULL,'2026-08-16 09:57:05'),(38,8,'2026-08-06','Present',NULL,'2026-08-16 09:57:05'),(39,9,'2026-08-06','Present',NULL,'2026-08-16 09:57:05'),(40,10,'2026-08-06','Present',NULL,'2026-08-16 09:57:05'),(41,11,'2026-08-04','Present',NULL,'2026-08-16 09:57:05'),(42,12,'2026-08-04','Absent',NULL,'2026-08-16 09:57:05'),(43,11,'2026-08-05','Present',NULL,'2026-08-16 09:57:05'),(44,12,'2026-08-05','Present',NULL,'2026-08-16 09:57:05'),(45,13,'2026-08-04','Present',NULL,'2026-08-16 09:57:05'),(46,14,'2026-08-04','Present',NULL,'2026-08-16 09:57:05'),(47,13,'2026-08-05','Absent',NULL,'2026-08-16 09:57:05'),(48,14,'2026-08-05','Present',NULL,'2026-08-16 09:57:05'),(49,15,'2026-08-04','Present',NULL,'2026-08-16 09:57:05'),(50,15,'2026-08-05','Present',NULL,'2026-08-16 09:57:05'),(51,1,'2026-08-16','Present',NULL,'2026-08-16 10:03:06'),(52,2,'2026-08-16','Present',NULL,'2026-08-16 10:03:06'),(53,3,'2026-08-16','Present',NULL,'2026-08-16 10:03:06'),(54,4,'2026-08-16','Present',NULL,'2026-08-16 10:03:06'),(55,5,'2026-08-16','Present',NULL,'2026-08-16 10:03:06'),(56,6,'2026-08-16','Present',NULL,'2026-08-16 10:09:20'),(57,7,'2026-08-16','Present',NULL,'2026-08-16 10:09:20'),(58,8,'2026-08-16','Present',NULL,'2026-08-16 10:09:20'),(59,9,'2026-08-16','Present',NULL,'2026-08-16 10:09:20'),(60,10,'2026-08-16','Present',NULL,'2026-08-16 10:09:20');
/*!40000 ALTER TABLE `attendance` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `class_log`
--

DROP TABLE IF EXISTS `class_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_log` (
  `log_id` int NOT NULL AUTO_INCREMENT,
  `course_id` int NOT NULL,
  `teacher_id` int DEFAULT NULL,
  `class_date` date NOT NULL,
  `topic_taught` varchar(500) NOT NULL,
  `logged_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`log_id`),
  UNIQUE KEY `uq_course_date` (`course_id`,`class_date`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `class_log_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE,
  CONSTRAINT `class_log_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`teacher_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_log`
--

LOCK TABLES `class_log` WRITE;
/*!40000 ALTER TABLE `class_log` DISABLE KEYS */;
INSERT INTO `class_log` VALUES (1,1,1,'2026-08-04','Introduction to Relational Databases and SQL Basics','2026-08-16 09:57:05'),(2,1,1,'2026-08-05','ER Diagrams and Database Normalization (1NF, 2NF, 3NF)','2026-08-16 09:57:05'),(3,1,1,'2026-08-06','SQL Join Operations (INNER, LEFT, RIGHT, FULL)','2026-08-16 09:57:05'),(4,1,1,'2026-08-07','Aggregate Functions, GROUP BY, and HAVING Clauses','2026-08-16 09:57:05'),(5,1,1,'2026-08-11','Database Indexing and B-Tree Indexes Performance','2026-08-16 09:57:05'),(6,2,1,'2026-08-04','Arrays, Linked Lists, and Memory Allocation','2026-08-16 09:57:05'),(7,2,1,'2026-08-05','Stack and Queue Data Structures Implementation','2026-08-16 09:57:05'),(8,2,1,'2026-08-06','Binary Search Trees (BST) Insertion and Traversal','2026-08-16 09:57:05'),(9,3,2,'2026-08-04','Discrete-Time Signals and Fourier Transform (DFT)','2026-08-16 09:57:05'),(10,3,2,'2026-08-05','Fast Fourier Transform (FFT) Algorithm and Sampling','2026-08-16 09:57:05'),(11,4,3,'2026-08-04','First Law of Thermodynamics and Heat Transfer','2026-08-16 09:57:05'),(12,4,3,'2026-08-05','Second Law of Thermodynamics and Carnot Engine Cycle','2026-08-16 09:57:05'),(13,5,5,'2026-08-04','Principles of Digital Marketing and Customer Behavior','2026-08-16 09:57:05'),(14,5,5,'2026-08-05','Brand Positioning Strategies and Market Segmentation','2026-08-16 09:57:05'),(15,1,NULL,'2026-08-16','ER diagram','2026-08-16 10:03:06'),(16,2,1,'2026-08-16','Graph, Time complexity','2026-08-16 10:09:20');
/*!40000 ALTER TABLE `class_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `course`
--

DROP TABLE IF EXISTS `course`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `course` (
  `course_id` int NOT NULL AUTO_INCREMENT,
  `course_code` varchar(20) NOT NULL,
  `course_name` varchar(150) NOT NULL,
  `credits` int DEFAULT '3',
  `semester` varchar(10) DEFAULT NULL,
  `dept_id` int DEFAULT NULL,
  `teacher_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`course_id`),
  UNIQUE KEY `course_code` (`course_code`),
  KEY `dept_id` (`dept_id`),
  KEY `teacher_id` (`teacher_id`),
  CONSTRAINT `course_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`) ON DELETE SET NULL,
  CONSTRAINT `course_ibfk_2` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`teacher_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `course`
--

LOCK TABLES `course` WRITE;
/*!40000 ALTER TABLE `course` DISABLE KEYS */;
INSERT INTO `course` VALUES (1,'CS301','Database Management Systems',4,'VI',1,1,'2026-08-16 09:57:05'),(2,'CS302','Data Structures & Algorithms',4,'VI',1,1,'2026-08-16 09:57:05'),(3,'EC301','Digital Signal Processing',4,'VI',2,2,'2026-08-16 09:57:05'),(4,'ME301','Thermodynamics II',3,'VI',3,3,'2026-08-16 09:57:05'),(5,'BA301','Marketing Management',3,'VI',5,5,'2026-08-16 09:57:05');
/*!40000 ALTER TABLE `course` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `department`
--

DROP TABLE IF EXISTS `department`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `department` (
  `dept_id` int NOT NULL AUTO_INCREMENT,
  `dept_name` varchar(100) NOT NULL,
  `dept_code` varchar(10) NOT NULL,
  PRIMARY KEY (`dept_id`),
  UNIQUE KEY `dept_name` (`dept_name`),
  UNIQUE KEY `dept_code` (`dept_code`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `department`
--

LOCK TABLES `department` WRITE;
/*!40000 ALTER TABLE `department` DISABLE KEYS */;
INSERT INTO `department` VALUES (1,'Computer Science','CS'),(2,'Electronics Engineering','EC'),(3,'Mechanical Engineering','ME'),(4,'Civil Engineering','CE'),(5,'Business Administration','BA');
/*!40000 ALTER TABLE `department` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enrollment`
--

DROP TABLE IF EXISTS `enrollment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enrollment` (
  `enrollment_id` int NOT NULL AUTO_INCREMENT,
  `student_id` int NOT NULL,
  `course_id` int NOT NULL,
  `enrollment_date` date DEFAULT (curdate()),
  PRIMARY KEY (`enrollment_id`),
  UNIQUE KEY `uq_enrollment` (`student_id`,`course_id`),
  KEY `course_id` (`course_id`),
  CONSTRAINT `enrollment_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE CASCADE,
  CONSTRAINT `enrollment_ibfk_2` FOREIGN KEY (`course_id`) REFERENCES `course` (`course_id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enrollment`
--

LOCK TABLES `enrollment` WRITE;
/*!40000 ALTER TABLE `enrollment` DISABLE KEYS */;
INSERT INTO `enrollment` VALUES (1,1,1,'2026-08-16'),(2,2,1,'2026-08-16'),(3,3,1,'2026-08-16'),(4,4,1,'2026-08-16'),(5,5,1,'2026-08-16'),(6,1,2,'2026-08-16'),(7,2,2,'2026-08-16'),(8,3,2,'2026-08-16'),(9,4,2,'2026-08-16'),(10,5,2,'2026-08-16'),(11,6,3,'2026-08-16'),(12,7,3,'2026-08-16'),(13,8,4,'2026-08-16'),(14,9,4,'2026-08-16'),(15,10,5,'2026-08-16');
/*!40000 ALTER TABLE `enrollment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `student`
--

DROP TABLE IF EXISTS `student`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `student` (
  `student_id` int NOT NULL AUTO_INCREMENT,
  `roll_no` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `address` varchar(255) DEFAULT NULL,
  `dob` date DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `gender` enum('Male','Female','Other') DEFAULT 'Male',
  `dept_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`student_id`),
  UNIQUE KEY `roll_no` (`roll_no`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `student_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `student`
--

LOCK TABLES `student` WRITE;
/*!40000 ALTER TABLE `student` DISABLE KEYS */;
INSERT INTO `student` VALUES (1,'CS101','Aarav Shrestha','Kathmandu','2002-03-15','9811111111','aarav@mail.com','Male',1,'2026-08-16 09:57:05'),(2,'CS102','Bipasha Rai','Lalitpur','2002-07-22','9811111112','bipasha@mail.com','Female',1,'2026-08-16 09:57:05'),(3,'CS103','Chetan Gurung','Bhaktapur','2003-01-10','9811111113','chetan@mail.com','Male',1,'2026-08-16 09:57:05'),(4,'CS104','Dipika Tamang','Pokhara','2002-11-05','9811111114','dipika@mail.com','Female',1,'2026-08-16 09:57:05'),(5,'CS105','Eshan Magar','Chitwan','2003-04-18','9811111115','eshan@mail.com','Male',1,'2026-08-16 09:57:05'),(6,'EC101','Fiona Limbu','Biratnagar','2002-09-30','9822222221','fiona@mail.com','Female',2,'2026-08-16 09:57:05'),(7,'EC102','Ganesh Karki','Dharan','2003-02-14','9822222222','ganesh@mail.com','Male',2,'2026-08-16 09:57:05'),(8,'ME101','Hari Basnet','Butwal','2002-06-25','9833333331','hari@mail.com','Male',3,'2026-08-16 09:57:05'),(9,'ME102','Indira Khadka','Bhairahawa','2003-08-12','9833333332','indira@mail.com','Female',3,'2026-08-16 09:57:05'),(10,'BA101','Jagat Pandey','Birgunj','2002-12-01','9844444441','jagat@mail.com','Male',5,'2026-08-16 09:57:05');
/*!40000 ALTER TABLE `student` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `teacher`
--

DROP TABLE IF EXISTS `teacher`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `teacher` (
  `teacher_id` int NOT NULL AUTO_INCREMENT,
  `teacher_code` varchar(20) NOT NULL,
  `name` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `phone` varchar(15) DEFAULT NULL,
  `specialization` varchar(100) DEFAULT NULL,
  `dept_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`teacher_id`),
  UNIQUE KEY `teacher_code` (`teacher_code`),
  KEY `dept_id` (`dept_id`),
  CONSTRAINT `teacher_ibfk_1` FOREIGN KEY (`dept_id`) REFERENCES `department` (`dept_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `teacher`
--

LOCK TABLES `teacher` WRITE;
/*!40000 ALTER TABLE `teacher` DISABLE KEYS */;
INSERT INTO `teacher` VALUES (1,'TCH001','Dr. Rajesh Kumar','rajesh@college.edu','9800000001','Database Systems',1,'2026-08-16 09:57:05'),(2,'TCH002','Prof. Sunita Sharma','sunita@college.edu','9800000002','Digital Electronics',2,'2026-08-16 09:57:05'),(3,'TCH003','Mr. Anil Thapa','anil@college.edu','9800000003','Thermodynamics',3,'2026-08-16 09:57:05'),(4,'TCH004','Ms. Priya Poudel','priya@college.edu','9800000004','Structural Analysis',4,'2026-08-16 09:57:05'),(5,'TCH005','Dr. Suman Adhikari','suman@college.edu','9800000005','Marketing Management',5,'2026-08-16 09:57:05');
/*!40000 ALTER TABLE `teacher` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(128) NOT NULL,
  `role` enum('Admin','Teacher','Student') NOT NULL DEFAULT 'Student',
  `teacher_id` int DEFAULT NULL,
  `student_id` int DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `username` (`username`),
  KEY `teacher_id` (`teacher_id`),
  KEY `student_id` (`student_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`teacher_id`) REFERENCES `teacher` (`teacher_id`) ON DELETE SET NULL,
  CONSTRAINT `users_ibfk_2` FOREIGN KEY (`student_id`) REFERENCES `student` (`student_id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=17 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'admin','SriKrishna14@','Admin',NULL,NULL,'2026-08-16 09:57:05'),(2,'rajesh','teacher123','Teacher',1,NULL,'2026-08-16 09:57:05'),(3,'sunita','teacher123','Teacher',2,NULL,'2026-08-16 09:57:05'),(4,'anil','teacher123','Teacher',3,NULL,'2026-08-16 09:57:05'),(5,'priya','teacher123','Teacher',4,NULL,'2026-08-16 09:57:05'),(6,'suman','teacher123','Teacher',5,NULL,'2026-08-16 09:57:05'),(7,'CS101','student123','Student',NULL,1,'2026-08-16 09:57:05'),(8,'CS102','student123','Student',NULL,2,'2026-08-16 09:57:05'),(9,'CS103','student123','Student',NULL,3,'2026-08-16 09:57:05'),(10,'CS104','student123','Student',NULL,4,'2026-08-16 09:57:05'),(11,'CS105','student123','Student',NULL,5,'2026-08-16 09:57:05'),(12,'EC101','student123','Student',NULL,6,'2026-08-16 09:57:05'),(13,'EC102','student123','Student',NULL,7,'2026-08-16 09:57:05'),(14,'ME101','student123','Student',NULL,8,'2026-08-16 09:57:05'),(15,'ME102','student123','Student',NULL,9,'2026-08-16 09:57:05'),(16,'BA101','student123','Student',NULL,10,'2026-08-16 09:57:05');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Temporary view structure for view `vw_attendance_detail`
--

DROP TABLE IF EXISTS `vw_attendance_detail`;
/*!50001 DROP VIEW IF EXISTS `vw_attendance_detail`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_attendance_detail` AS SELECT 
 1 AS `attendance_id`,
 1 AS `attendance_date`,
 1 AS `status`,
 1 AS `remarks`,
 1 AS `roll_no`,
 1 AS `student_name`,
 1 AS `course_code`,
 1 AS `course_name`,
 1 AS `teacher_name`,
 1 AS `dept_name`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `vw_attendance_pct`
--

DROP TABLE IF EXISTS `vw_attendance_pct`;
/*!50001 DROP VIEW IF EXISTS `vw_attendance_pct`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `vw_attendance_pct` AS SELECT 
 1 AS `student_id`,
 1 AS `roll_no`,
 1 AS `student_name`,
 1 AS `course_id`,
 1 AS `course_code`,
 1 AS `course_name`,
 1 AS `total_classes`,
 1 AS `classes_attended`,
 1 AS `attendance_pct`*/;
SET character_set_client = @saved_cs_client;

--
-- Dumping events for database 'college'
--

--
-- Dumping routines for database 'college'
--

--
-- Final view structure for view `vw_attendance_detail`
--

/*!50001 DROP VIEW IF EXISTS `vw_attendance_detail`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 SQL SECURITY DEFINER */
/*!50001 VIEW `vw_attendance_detail` AS select `a`.`attendance_id` AS `attendance_id`,`a`.`attendance_date` AS `attendance_date`,`a`.`status` AS `status`,`a`.`remarks` AS `remarks`,`s`.`roll_no` AS `roll_no`,`s`.`name` AS `student_name`,`c`.`course_code` AS `course_code`,`c`.`course_name` AS `course_name`,`t`.`name` AS `teacher_name`,`d`.`dept_name` AS `dept_name` from (((((`attendance` `a` join `enrollment` `e` on((`a`.`enrollment_id` = `e`.`enrollment_id`))) join `student` `s` on((`e`.`student_id` = `s`.`student_id`))) join `course` `c` on((`e`.`course_id` = `c`.`course_id`))) left join `teacher` `t` on((`c`.`teacher_id` = `t`.`teacher_id`))) left join `department` `d` on((`s`.`dept_id` = `d`.`dept_id`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `vw_attendance_pct`
--

/*!50001 DROP VIEW IF EXISTS `vw_attendance_pct`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 SQL SECURITY DEFINER */
/*!50001 VIEW `vw_attendance_pct` AS select `s`.`student_id` AS `student_id`,`s`.`roll_no` AS `roll_no`,`s`.`name` AS `student_name`,`c`.`course_id` AS `course_id`,`c`.`course_code` AS `course_code`,`c`.`course_name` AS `course_name`,count(`a`.`attendance_id`) AS `total_classes`,sum((`a`.`status` in ('Present','Late'))) AS `classes_attended`,round(((sum((`a`.`status` in ('Present','Late'))) * 100.0) / nullif(count(`a`.`attendance_id`),0)),2) AS `attendance_pct` from (((`enrollment` `e` join `student` `s` on((`e`.`student_id` = `s`.`student_id`))) join `course` `c` on((`e`.`course_id` = `c`.`course_id`))) left join `attendance` `a` on((`e`.`enrollment_id` = `a`.`enrollment_id`))) group by `s`.`student_id`,`c`.`course_id` */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-16 20:18:02

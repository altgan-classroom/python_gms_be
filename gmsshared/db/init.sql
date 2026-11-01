-- MySQL dump 10.13  Distrib 8.0.46, for Linux (aarch64)
--
-- Host: localhost    Database: gms
-- ------------------------------------------------------
-- Server version	8.0.46

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
-- Table structure for table `_acct_chart_of_accounts`
--

DROP TABLE IF EXISTS `_acct_chart_of_accounts`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_acct_chart_of_accounts` (
  `id` int NOT NULL,
  `name` varchar(100) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `type` varchar(50) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_acct_chart_of_accounts`
--

/*!40000 ALTER TABLE `_acct_chart_of_accounts` DISABLE KEYS */;
/*!40000 ALTER TABLE `_acct_chart_of_accounts` ENABLE KEYS */;

--
-- Table structure for table `_acct_ledger`
--

DROP TABLE IF EXISTS `_acct_ledger`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_acct_ledger` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `user_id` bigint DEFAULT NULL,
  `account_id` int NOT NULL,
  `txn_date` datetime NOT NULL,
  `amount` float NOT NULL DEFAULT '0',
  `credit` tinyint(1) NOT NULL DEFAULT '1',
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `user_id` (`user_id`),
  KEY `account_id` (`account_id`),
  CONSTRAINT `_acct_ledger_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `_acct_ledger_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=557350 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_acct_ledger`
--

/*!40000 ALTER TABLE `_acct_ledger` DISABLE KEYS */;
/*!40000 ALTER TABLE `_acct_ledger` ENABLE KEYS */;

--
-- Table structure for table `_ref_billing_type`
--

DROP TABLE IF EXISTS `_ref_billing_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_billing_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `order` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_billing_type`
--

/*!40000 ALTER TABLE `_ref_billing_type` DISABLE KEYS */;
INSERT INTO `_ref_billing_type` VALUES (1,'Recurring',NULL,'2024-04-16 02:51:10','2024-04-16 02:51:10',2),(2,'Paid in Full',NULL,'2024-04-16 02:51:10','2024-04-16 02:51:10',1),(3,'Session packs',NULL,'2024-04-16 02:51:10','2024-04-16 02:51:10',3),(4,'Free',NULL,'2024-04-16 02:51:10','2024-04-16 02:51:10',4);
/*!40000 ALTER TABLE `_ref_billing_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_cancel_reason_type`
--

DROP TABLE IF EXISTS `_ref_cancel_reason_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_cancel_reason_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_cancel_reason_type`
--

/*!40000 ALTER TABLE `_ref_cancel_reason_type` DISABLE KEYS */;
INSERT INTO `_ref_cancel_reason_type` VALUES (1,'Cost','Membership too expensive','2024-04-16 02:52:16','2024-04-16 02:52:16'),(2,'Moving','Relocation to a new area','2024-04-16 02:52:16','2024-04-16 02:52:16'),(3,'Location','Inconvenient gym location','2024-04-16 02:52:16','2024-04-16 02:52:16'),(4,'Health Challenges','Injury or medical condition','2024-04-16 02:52:16','2024-04-16 02:52:16'),(5,'Too Busy','Family or work obligations','2024-04-16 02:52:16','2024-04-16 02:52:16'),(6,'Dissatisfaction with Offerings','Unhappy with gym facilities or group sessions','2024-04-16 02:52:16','2024-04-16 02:52:16'),(7,'Lack of Accountability','No gym buddy or accountability partner','2024-04-16 02:52:16','2024-04-16 02:52:16'),(8,'Uncomfortable with Workouts','Intimidate or unfamiliar with workouts','2024-04-16 02:52:16','2024-04-16 02:52:16'),(9,'Membership Change','Moving to a different membership plan','2025-02-21 10:29:05','2025-02-21 10:29:05'),(10,'Other','Miscellaneous Reasons','2025-02-21 10:29:05','2025-02-21 10:29:05');
/*!40000 ALTER TABLE `_ref_cancel_reason_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_class_type`
--

DROP TABLE IF EXISTS `_ref_class_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_class_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=12 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_class_type`
--

/*!40000 ALTER TABLE `_ref_class_type` DISABLE KEYS */;
INSERT INTO `_ref_class_type` VALUES (1,'Bootcamp','2024-04-16 02:51:17','2024-04-16 02:51:17'),(2,'Boxing / Kickboxing','2024-04-16 02:51:17','2024-04-16 02:51:17'),(3,'Cardio','2024-04-16 02:51:17','2024-04-16 02:51:17'),(4,'Crossfit','2024-04-16 02:51:17','2024-04-16 02:51:17'),(5,'HIIT','2024-04-16 02:51:17','2024-04-16 02:51:17'),(6,'Martial Arts','2024-04-16 02:51:17','2024-04-16 02:51:17'),(7,'Semi-Private','2024-04-16 02:51:17','2024-04-16 02:51:17'),(8,'Spinning','2024-04-16 02:51:17','2024-04-16 02:51:17'),(9,'Strength Training','2024-04-16 02:51:17','2024-04-16 02:51:17'),(10,'Yoga / Pilates','2024-04-16 02:51:17','2024-04-16 02:51:17'),(11,'Private Training','2024-09-26 02:17:33','2024-09-26 02:17:33');
/*!40000 ALTER TABLE `_ref_class_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_door_access_vendor`
--

DROP TABLE IF EXISTS `_ref_door_access_vendor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_door_access_vendor` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `authentication_type` varchar(50) NOT NULL,
  `api_url` varchar(200) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_door_access_vendor`
--

/*!40000 ALTER TABLE `_ref_door_access_vendor` DISABLE KEYS */;
INSERT INTO `_ref_door_access_vendor` VALUES (1,'Kisi','','api_key','https://api.kisi.io','2025-10-06 06:07:01','2025-10-06 06:07:01');
/*!40000 ALTER TABLE `_ref_door_access_vendor` ENABLE KEYS */;

--
-- Table structure for table `_ref_door_access_vendor_auth`
--

DROP TABLE IF EXISTS `_ref_door_access_vendor_auth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_door_access_vendor_auth` (
  `id` int NOT NULL AUTO_INCREMENT,
  `vendor_id` int NOT NULL,
  `display_name` varchar(100) DEFAULT NULL,
  `field_name` varchar(50) NOT NULL,
  `field_type` varchar(50) NOT NULL,
  `field_validation_rules_json` json DEFAULT NULL,
  `field_help_text` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `vendor_id` (`vendor_id`),
  CONSTRAINT `_ref_door_access_vendor_auth_ibfk_1` FOREIGN KEY (`vendor_id`) REFERENCES `_ref_door_access_vendor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_door_access_vendor_auth`
--

/*!40000 ALTER TABLE `_ref_door_access_vendor_auth` DISABLE KEYS */;
INSERT INTO `_ref_door_access_vendor_auth` VALUES (1,1,'Integration Key','api_key','textbox','{\"required\": true, \"maxLength\": 32, \"minLength\": 32}','API KEY to use Kisi API','2025-10-06 06:07:01','2025-10-06 06:07:01');
/*!40000 ALTER TABLE `_ref_door_access_vendor_auth` ENABLE KEYS */;

--
-- Table structure for table `_ref_duration_type`
--

DROP TABLE IF EXISTS `_ref_duration_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_duration_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_duration_type`
--

/*!40000 ALTER TABLE `_ref_duration_type` DISABLE KEYS */;
INSERT INTO `_ref_duration_type` VALUES (1,'day(s)',NULL,'2024-04-16 02:51:10','2024-04-16 02:51:10'),(2,'week(s)',NULL,'2024-04-16 02:51:10','2024-04-16 02:51:10'),(3,'month(s)',NULL,'2024-04-16 02:51:10','2024-04-16 02:51:10'),(4,'year(s)',NULL,'2024-04-16 02:51:10','2024-04-16 02:51:10');
/*!40000 ALTER TABLE `_ref_duration_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_freeze_reason_type`
--

DROP TABLE IF EXISTS `_ref_freeze_reason_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_freeze_reason_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_freeze_reason_type`
--

/*!40000 ALTER TABLE `_ref_freeze_reason_type` DISABLE KEYS */;
INSERT INTO `_ref_freeze_reason_type` VALUES (1,'Vacation',NULL,'2024-04-16 02:52:17','2024-04-16 02:52:17'),(2,'Medical',NULL,'2024-04-16 02:52:17','2024-04-16 02:52:17');
/*!40000 ALTER TABLE `_ref_freeze_reason_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_gender_type`
--

DROP TABLE IF EXISTS `_ref_gender_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_gender_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_gender_type`
--

/*!40000 ALTER TABLE `_ref_gender_type` DISABLE KEYS */;
INSERT INTO `_ref_gender_type` VALUES (1,'Male',NULL,'2024-04-16 02:51:10','2024-04-16 02:51:10'),(2,'Female',NULL,'2024-04-16 02:51:10','2024-04-16 02:51:10');
/*!40000 ALTER TABLE `_ref_gender_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_gym_type`
--

DROP TABLE IF EXISTS `_ref_gym_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_gym_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_gym_type`
--

/*!40000 ALTER TABLE `_ref_gym_type` DISABLE KEYS */;
INSERT INTO `_ref_gym_type` VALUES (1,'Health Club',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11'),(2,'Group Training only',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11'),(3,'Semi Private',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11'),(4,'Personal Training',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11'),(5,'Martial Arts',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11'),(6,'Spin Studio',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11'),(7,'Yoga/Pilates',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11');
/*!40000 ALTER TABLE `_ref_gym_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_invoice_item_status_type`
--

DROP TABLE IF EXISTS `_ref_invoice_item_status_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_invoice_item_status_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `order` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_invoice_item_status_type`
--

/*!40000 ALTER TABLE `_ref_invoice_item_status_type` DISABLE KEYS */;
INSERT INTO `_ref_invoice_item_status_type` VALUES (1,'Pending',NULL,'2025-05-09 04:50:42','2025-05-09 04:50:42',NULL),(2,'Processed',NULL,'2025-05-09 04:50:42','2025-05-09 04:50:42',NULL),(3,'Cancelled',NULL,'2025-05-09 04:50:42','2025-05-09 04:50:42',NULL);
/*!40000 ALTER TABLE `_ref_invoice_item_status_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_invoice_status_type`
--

DROP TABLE IF EXISTS `_ref_invoice_status_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_invoice_status_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `order` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_invoice_status_type`
--

/*!40000 ALTER TABLE `_ref_invoice_status_type` DISABLE KEYS */;
INSERT INTO `_ref_invoice_status_type` VALUES (1,'Pending',NULL,'2025-05-09 04:50:43','2025-05-09 04:50:43',NULL),(2,'Paid',NULL,'2025-05-09 04:50:43','2025-05-09 04:50:43',NULL),(3,'Past Due',NULL,'2025-05-09 04:50:43','2025-05-09 04:50:43',NULL),(4,'Void',NULL,'2025-05-09 04:50:43','2025-05-09 04:50:43',NULL);
/*!40000 ALTER TABLE `_ref_invoice_status_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_invoice_type`
--

DROP TABLE IF EXISTS `_ref_invoice_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_invoice_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `order` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_invoice_type`
--

/*!40000 ALTER TABLE `_ref_invoice_type` DISABLE KEYS */;
INSERT INTO `_ref_invoice_type` VALUES (1,'Invoice',NULL,'2025-05-09 04:50:42','2025-05-09 04:50:42',NULL),(2,'Credit Memo',NULL,'2025-05-09 04:50:42','2025-05-09 04:50:42',NULL),(3,'Writeoff',NULL,'2025-05-09 04:50:42','2025-05-09 04:50:42',NULL);
/*!40000 ALTER TABLE `_ref_invoice_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_location_type`
--

DROP TABLE IF EXISTS `_ref_location_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_location_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_location_type`
--

/*!40000 ALTER TABLE `_ref_location_type` DISABLE KEYS */;
INSERT INTO `_ref_location_type` VALUES (1,'Physical','2024-04-16 02:51:16','2024-04-16 02:51:16'),(2,'Virtual','2024-04-16 02:51:16','2024-04-16 02:51:16'),(3,'Both','2024-04-16 02:51:16','2024-04-16 02:51:16');
/*!40000 ALTER TABLE `_ref_location_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_member_status_type`
--

DROP TABLE IF EXISTS `_ref_member_status_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_member_status_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_member_status_type`
--

/*!40000 ALTER TABLE `_ref_member_status_type` DISABLE KEYS */;
INSERT INTO `_ref_member_status_type` VALUES (1,'Active',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11'),(2,'Frozen',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11'),(3,'Cancelled',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11'),(4,'Non-Renewed',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11'),(5,'Ending Soon',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11'),(6,'Pending',NULL,'2024-04-16 02:51:11','2024-04-16 02:51:11');
/*!40000 ALTER TABLE `_ref_member_status_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_membership_status_type`
--

DROP TABLE IF EXISTS `_ref_membership_status_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_membership_status_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_membership_status_type`
--

/*!40000 ALTER TABLE `_ref_membership_status_type` DISABLE KEYS */;
INSERT INTO `_ref_membership_status_type` VALUES (1,'Active',NULL,'2024-04-16 02:51:17','2024-04-16 02:51:17'),(2,'Cancelled',NULL,'2024-04-16 02:51:17','2024-04-16 02:51:17'),(3,'Frozen',NULL,'2024-04-16 02:51:17','2024-04-16 02:51:17'),(4,'Renewed',NULL,'2025-05-23 05:12:05','2025-05-23 05:12:05'),(5,'Not Started',NULL,'2025-05-23 05:12:05','2025-05-23 05:12:05');
/*!40000 ALTER TABLE `_ref_membership_status_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_membership_type`
--

DROP TABLE IF EXISTS `_ref_membership_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_membership_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(300) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_membership_type`
--

/*!40000 ALTER TABLE `_ref_membership_type` DISABLE KEYS */;
INSERT INTO `_ref_membership_type` VALUES (1,'Full Membership','Pick this if you would consider this to be a full membership. It is typically a longer term commitment that is either paid in full or a recurring payment plan.','2024-04-16 02:52:09','2024-04-16 02:52:09'),(2,'Challenge','Pick this if you are offering a short-term (for example, 6 weeks), goal oriented plan that includes access to the gym for fitness, nutrition, and accountability with the goal to sign them up for a full membership half way through the challenge because they love the results and facility so much.','2024-04-16 02:52:09','2024-04-16 02:52:09'),(3,'Limited time pass','Pick this if you are offering access to the gym\'\'s facilities for limited time period. It\'\'s best suited for those who are visiting the area temporarily, or only need access for a short time. Perfect for day passes, week passes, guests, or free trials.','2024-04-16 02:52:09','2024-04-16 02:52:09');
/*!40000 ALTER TABLE `_ref_membership_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_objective_type`
--

DROP TABLE IF EXISTS `_ref_objective_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_objective_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_objective_type`
--

/*!40000 ALTER TABLE `_ref_objective_type` DISABLE KEYS */;
INSERT INTO `_ref_objective_type` VALUES (1,'Weight Loss',NULL,'2024-04-16 02:51:12','2024-04-16 02:51:12'),(2,'Athletic Performance',NULL,'2024-04-16 02:51:12','2024-04-16 02:51:12'),(3,'Overall Health',NULL,'2024-04-16 02:51:12','2024-04-16 02:51:12'),(4,'Rehab',NULL,'2024-04-16 02:51:12','2024-04-16 02:51:12'),(5,'Other',NULL,'2024-04-16 02:51:12','2024-04-16 02:51:12');
/*!40000 ALTER TABLE `_ref_objective_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_payment_category_type`
--

DROP TABLE IF EXISTS `_ref_payment_category_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_payment_category_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_payment_category_type`
--

/*!40000 ALTER TABLE `_ref_payment_category_type` DISABLE KEYS */;
INSERT INTO `_ref_payment_category_type` VALUES (1,'Cancellation Fee',NULL,'2024-04-16 02:51:44','2024-04-16 02:51:44'),(2,'Late Fee',NULL,'2024-04-16 02:51:44','2024-04-16 02:51:44'),(3,'No Show Fee',NULL,'2024-04-16 02:51:44','2024-04-16 02:51:44'),(4,'Other',NULL,'2024-04-16 02:51:44','2024-04-16 02:51:44');
/*!40000 ALTER TABLE `_ref_payment_category_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_payment_method_type`
--

DROP TABLE IF EXISTS `_ref_payment_method_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_payment_method_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_payment_method_type`
--

/*!40000 ALTER TABLE `_ref_payment_method_type` DISABLE KEYS */;
INSERT INTO `_ref_payment_method_type` VALUES (1,'Credit Card',NULL,'2024-04-16 02:51:18','2024-04-16 02:51:18'),(2,'Debit Card',NULL,'2024-04-16 02:51:18','2024-04-16 02:51:18'),(3,'ACH',NULL,'2024-04-16 02:51:18','2024-04-16 02:51:18');
/*!40000 ALTER TABLE `_ref_payment_method_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_payment_status_type`
--

DROP TABLE IF EXISTS `_ref_payment_status_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_payment_status_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_payment_status_type`
--

/*!40000 ALTER TABLE `_ref_payment_status_type` DISABLE KEYS */;
INSERT INTO `_ref_payment_status_type` VALUES (1,'Past Due',NULL,'2024-04-16 02:51:12','2024-04-16 02:51:12'),(2,'Paid to Date',NULL,'2024-04-16 02:51:12','2024-04-16 02:51:12');
/*!40000 ALTER TABLE `_ref_payment_status_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_payment_transaction_type`
--

DROP TABLE IF EXISTS `_ref_payment_transaction_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_payment_transaction_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_payment_transaction_type`
--

/*!40000 ALTER TABLE `_ref_payment_transaction_type` DISABLE KEYS */;
INSERT INTO `_ref_payment_transaction_type` VALUES (1,'Sale Transaction',NULL,'2024-04-16 02:51:49','2024-04-16 02:51:49'),(2,'Refund Transaction',NULL,'2024-04-16 02:51:49','2024-04-16 02:51:49'),(3,'Retry Sale Transaction',NULL,'2024-04-16 02:51:49','2024-04-16 02:51:49');
/*!40000 ALTER TABLE `_ref_payment_transaction_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_payrix_disbursement_status_type`
--

DROP TABLE IF EXISTS `_ref_payrix_disbursement_status_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_payrix_disbursement_status_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_payrix_disbursement_status_type`
--

/*!40000 ALTER TABLE `_ref_payrix_disbursement_status_type` DISABLE KEYS */;
INSERT INTO `_ref_payrix_disbursement_status_type` VALUES (1,'Requested','The request for this Disbursement has been received','2025-04-09 11:28:49','2025-04-09 11:28:49'),(2,'Processing','This Disbursement is being processed to be paid out','2025-04-09 11:28:49','2025-04-09 11:28:49'),(3,'Processed','This Disbursement has been paid by ACH to the bank account referenced in the Disbursement data','2025-04-09 11:28:49','2025-04-09 11:28:49'),(4,'Failed','A problem occurred and the payment processor has failed to process this Disbursement','2025-04-09 11:28:49','2025-04-09 11:28:49'),(5,'Denied','This Disbursement has been refused','2025-04-09 11:28:49','2025-04-09 11:28:49'),(6,'Returned','This Disbursement has been returned','2025-04-09 11:28:49','2025-04-09 11:28:49');
/*!40000 ALTER TABLE `_ref_payrix_disbursement_status_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_payrix_onboard_status_type`
--

DROP TABLE IF EXISTS `_ref_payrix_onboard_status_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_payrix_onboard_status_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=100 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_payrix_onboard_status_type`
--

/*!40000 ALTER TABLE `_ref_payrix_onboard_status_type` DISABLE KEYS */;
INSERT INTO `_ref_payrix_onboard_status_type` VALUES (1,'Not Ready',NULL,'2024-04-16 02:51:18','2024-04-16 02:51:18'),(2,'Ready',NULL,'2024-04-16 02:51:18','2024-04-16 02:51:18'),(3,'Boarded',NULL,'2024-04-16 02:51:18','2024-04-16 02:51:18'),(4,'Manual',NULL,'2024-04-16 02:51:18','2024-04-16 02:51:18'),(5,'Denied',NULL,'2024-04-16 02:51:18','2024-04-16 02:51:18'),(98,'Queued',NULL,'2024-04-16 02:51:18','2024-04-16 02:51:18'),(99,'Failed',NULL,'2024-04-16 02:51:18','2024-04-16 02:51:18');
/*!40000 ALTER TABLE `_ref_payrix_onboard_status_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_payrix_payment_method_type`
--

DROP TABLE IF EXISTS `_ref_payrix_payment_method_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_payrix_payment_method_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_payrix_payment_method_type`
--

/*!40000 ALTER TABLE `_ref_payrix_payment_method_type` DISABLE KEYS */;
INSERT INTO `_ref_payrix_payment_method_type` VALUES (1,'Amex','Amercian Express','2025-07-27 02:51:13','2025-07-27 02:51:13'),(2,'Visa','Visa','2025-07-27 02:51:13','2025-07-27 02:51:13'),(3,'MasterCard','MasterCard','2025-07-27 02:12:34','2025-07-27 02:12:34'),(4,'Diners','Diners Club','2025-07-27 02:12:34','2025-07-27 02:12:34'),(5,'Discover','Discover','2025-07-27 02:12:34','2025-07-27 02:12:34'),(7,'ACH','Checking Account','2025-07-27 02:12:34','2025-07-27 02:12:34'),(8,'ACH','Savings Account','2025-07-27 02:12:34','2025-07-27 02:12:34'),(9,'ACH','Corporate Checking Account','2025-07-27 02:12:34','2025-07-27 02:12:34'),(10,'ACH','Corporate Savings Account','2025-07-27 02:12:34','2025-07-27 02:12:34');
/*!40000 ALTER TABLE `_ref_payrix_payment_method_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_payrix_resource_type`
--

DROP TABLE IF EXISTS `_ref_payrix_resource_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_payrix_resource_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_payrix_resource_type`
--

/*!40000 ALTER TABLE `_ref_payrix_resource_type` DISABLE KEYS */;
INSERT INTO `_ref_payrix_resource_type` VALUES (1,'Merchant',NULL,'2024-04-16 02:51:19','2024-04-16 02:51:19'),(2,'Customer',NULL,'2024-04-16 02:51:19','2024-04-16 02:51:19'),(3,'Token',NULL,'2024-04-16 02:51:19','2024-04-16 02:51:19'),(4,'Transaction',NULL,'2024-04-16 02:51:19','2024-04-16 02:51:19');
/*!40000 ALTER TABLE `_ref_payrix_resource_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_payrix_transaction_error_mapping`
--

DROP TABLE IF EXISTS `_ref_payrix_transaction_error_mapping`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_payrix_transaction_error_mapping` (
  `id` int NOT NULL AUTO_INCREMENT,
  `error` varchar(300) NOT NULL,
  `decline` varchar(10) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=36 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_payrix_transaction_error_mapping`
--

/*!40000 ALTER TABLE `_ref_payrix_transaction_error_mapping` DISABLE KEYS */;
INSERT INTO `_ref_payrix_transaction_error_mapping` VALUES (1,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Invalid unauth transaction\', \'errorCode\': \'invalid_reverse_auth\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(2,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Address was not provided, please reattempt transaction.\', \'errorCode\': \'generic_decline\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(3,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Expired Card\', \'errorCode\': \'expired_card\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(4,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Closed Account\', \'errorCode\': \'closed_account\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(5,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Insufficient Funds\', \'errorCode\': \'nsf\'}','Soft','2025-08-25 16:34:23','2025-08-25 16:34:23'),(6,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Generic Authorization Decline\', \'errorCode\': \'generic_decline\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(7,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \"Transaction declined: No \'To\' Account Specified\", \'errorCode\': \'missing_to_account\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(8,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Pick Up Card - Stolen\', \'errorCode\': \'stolen_card\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(9,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Restricted Card\', \'errorCode\': \'restricted_card\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(10,'{\'field\': \'address1\', \'code\': 15, \'severity\': 2, \'msg\': \'Address mismatch, please reattempt transaction.\', \'errorCode\': \'generic_decline\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(11,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Re-try Transaction\', \'errorCode\': \'reenter_transaction\'}','Soft','2025-08-25 16:34:23','2025-08-25 16:34:23'),(12,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Pick Up Card, Special Conditions\', \'errorCode\': \'pickup_card\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(13,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Issuer or Switch Inoperative (MasterCard)\', \'errorCode\': \'issuer_not_available\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(14,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Suspected Fraud\', \'errorCode\': \'fraudulent\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(15,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Transaction not Permitted to Cardholder\', \'errorCode\': \'transaction_not_allowed\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(16,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Invalid CVV\', \'errorCode\': \'invalid_cvv\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(17,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Invalid Account Number\', \'errorCode\': \'invalid_account\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(18,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Invalid Transaction\', \'errorCode\': \'transaction_not_allowed\'}','Soft','2025-08-25 16:34:23','2025-08-25 16:34:23'),(19,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Pick Up Card - Lost\', \'errorCode\': \'lost_card\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(20,'{\'field\': \'total\', \'code\': 15, \'severity\': 2, \'msg\': \'This field only accepts integers between 0 and 9000000000\', \'errorCode\': \'invalid_range\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(21,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'E-check processing disabled for this account\', \'errorCode\': \'account_return_error\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(22,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Exceeds Withdrawal Limit\', \'errorCode\': \'withdrawal_limit_exceeded\'}','Soft','2025-08-25 16:34:23','2025-08-25 16:34:23'),(23,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Invalid refund transaction\', \'errorCode\': \'invalid_refund\'}','Soft','2025-08-25 16:34:23','2025-08-25 16:34:23'),(24,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Invalid Transaction, Contact Issuer. Card Already Active (Gift Card)\', \'errorCode\': \'card_already_active\'}','Soft','2025-08-25 16:34:23','2025-08-25 16:34:23'),(25,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Refer to Card Issuer\', \'errorCode\': \'call_issuer\'}','Soft','2025-08-25 16:34:23','2025-08-25 16:34:23'),(26,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Pick Up Card\', \'errorCode\': \'pickup_card\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(27,'{\'field\': \'fundingCurrency\', \'code\': 15, \'severity\': 2, \'msg\': \'No mid available for txn funding currency\', \'errorCode\': \'funding_currency_error\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(28,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Exceeds Withdrawal Frequency Limit\', \'errorCode\': \'withdrawal_count_limit_exceeded\'}','Soft','2025-08-25 16:34:23','2025-08-25 16:34:23'),(29,'{\'field\': \'total\', \'code\': 15, \'severity\': 2, \'msg\': \'Transaction total exceeds upper limit\', \'errorCode\': \'txn_limit_exceeded\'}','Soft','2025-08-25 16:34:23','2025-08-25 16:34:23'),(30,'{\'field\': None, \'code\': 15, \'severity\': 2, \'msg\': \'Transaction declined: Allowable Number of PIN Tries Exceeded\', \'errorCode\': \'pin_try_exceeded\'}','Soft','2025-08-25 16:34:23','2025-08-25 16:34:23'),(31,'{\'code\': 15, \'severity\': 3, \'msg\': \'The related merchants record is inactive\', \'errorCode\': \'record_change_disabled\'}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(32,'{\"code\":15,\"severity\":2,\"field\":null,\"msg\":\"Address was not provided, please reattempt transaction.\",\"errorCode\":\"generic_decline\"}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(33,'{\"code\":15,\"severity\":2,\"field\":\"address1\",\"msg\":\"Address was not provided, please reattempt transaction.\",\"errorCode\":\"generic_decline\"}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(34,'{\"code\":15,\"severity\":2,\"field\":\"payment.cvv\",\"msg\":\"Card Verification (CVV) was not provided, please reattempt transaction.\",\"errorCode\":\"generic_decline\"}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23'),(35,'{\"code\":15,\"severity\":2,\"field\":null,\"msg\":\"Transaction declined: Suspected Fraud\",\"errorCode\":\"fraudulent\"}','Hard','2025-08-25 16:34:23','2025-08-25 16:34:23');
/*!40000 ALTER TABLE `_ref_payrix_transaction_error_mapping` ENABLE KEYS */;

--
-- Table structure for table `_ref_payrix_transaction_status_type`
--

DROP TABLE IF EXISTS `_ref_payrix_transaction_status_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_payrix_transaction_status_type` (
  `id` int NOT NULL,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_payrix_transaction_status_type`
--

/*!40000 ALTER TABLE `_ref_payrix_transaction_status_type` DISABLE KEYS */;
INSERT INTO `_ref_payrix_transaction_status_type` VALUES (0,'Pending',NULL,'2024-04-16 02:51:24','2024-04-16 02:51:24'),(1,'Approved',NULL,'2024-04-16 02:51:24','2024-04-16 02:51:24'),(2,'Failed',NULL,'2024-04-16 02:51:24','2024-04-16 02:51:24'),(3,'Captured',NULL,'2024-04-16 02:51:24','2024-04-16 02:51:24'),(4,'Settled',NULL,'2024-04-16 02:51:24','2024-04-16 02:51:24'),(5,'Returned',NULL,'2024-04-16 02:51:24','2024-04-16 02:51:24'),(6,'Forgiven',NULL,'2024-11-27 12:18:46','2024-11-27 12:18:46'),(7,'Cancelled',NULL,'2025-06-11 04:42:12','2025-06-11 04:42:12');
/*!40000 ALTER TABLE `_ref_payrix_transaction_status_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_payrix_transaction_type`
--

DROP TABLE IF EXISTS `_ref_payrix_transaction_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_payrix_transaction_type` (
  `id` int NOT NULL,
  `name` varchar(50) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_payrix_transaction_type`
--

/*!40000 ALTER TABLE `_ref_payrix_transaction_type` DISABLE KEYS */;
INSERT INTO `_ref_payrix_transaction_type` VALUES (0,'None',NULL,'2024-04-16 02:51:38','2024-04-16 02:51:38'),(1,'Credit Card - Sale Transaction',NULL,'2024-04-16 02:51:38','2024-04-16 02:51:38'),(2,'Credit Card - Auth Transaction',NULL,'2024-04-16 02:51:38','2024-04-16 02:51:38'),(3,'Credit Card - Capture Transaction',NULL,'2024-04-16 02:51:38','2024-04-16 02:51:38'),(4,'Credit Card - Reverse Authorization',NULL,'2024-04-16 02:51:38','2024-04-16 02:51:38'),(5,'Credit Card - Refund Transaction',NULL,'2024-04-16 02:51:38','2024-04-16 02:51:38'),(7,'ACH - Sale Transaction',NULL,'2024-04-16 02:51:38','2024-04-16 02:51:38'),(8,'ACH - Refund Transaction',NULL,'2024-04-16 02:51:38','2024-04-16 02:51:38'),(11,'ACH - Redeposit Transaction',NULL,'2024-04-16 02:51:38','2024-04-16 02:51:38'),(12,'ACH - Account Verification Transaction',NULL,'2024-04-16 02:51:38','2024-04-16 02:51:38');
/*!40000 ALTER TABLE `_ref_payrix_transaction_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_permission_type`
--

DROP TABLE IF EXISTS `_ref_permission_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_permission_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `display_name` varchar(50) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_permission_type`
--

/*!40000 ALTER TABLE `_ref_permission_type` DISABLE KEYS */;
INSERT INTO `_ref_permission_type` VALUES (1,'VIEW_METRICS','View Metrics',NULL,'2024-04-16 02:51:13','2024-04-16 02:51:13'),(2,'EDIT_METRICS','Edit Metrics',NULL,'2024-04-16 02:51:13','2024-04-16 02:51:13'),(3,'VIEW_BOARDS','View Boards',NULL,'2024-04-16 02:51:13','2024-04-16 02:51:13'),(4,'VIEW_INSIGHTS','View Insights',NULL,'2024-04-16 02:51:13','2024-04-16 02:51:13'),(5,'EDIT_SETTINGS','Edit Settings',NULL,'2024-04-16 02:51:13','2024-04-16 02:51:13');
/*!40000 ALTER TABLE `_ref_permission_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_plan_status_type`
--

DROP TABLE IF EXISTS `_ref_plan_status_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_plan_status_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_plan_status_type`
--

/*!40000 ALTER TABLE `_ref_plan_status_type` DISABLE KEYS */;
INSERT INTO `_ref_plan_status_type` VALUES (1,'Active',NULL,'2024-04-16 02:51:13','2024-04-16 02:51:13'),(2,'Grandfathered',NULL,'2024-04-16 02:51:13','2024-04-16 02:51:13'),(3,'Cancelled',NULL,'2024-06-23 02:12:34','2024-06-23 02:12:34');
/*!40000 ALTER TABLE `_ref_plan_status_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_plan_type`
--

DROP TABLE IF EXISTS `_ref_plan_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_plan_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_plan_type`
--

/*!40000 ALTER TABLE `_ref_plan_type` DISABLE KEYS */;
INSERT INTO `_ref_plan_type` VALUES (1,'Semi-private',NULL,'2024-04-16 02:51:14','2024-04-16 02:51:14'),(2,'Large Group',NULL,'2024-04-16 02:51:14','2024-04-16 02:51:14'),(3,'Personal Training',NULL,'2024-04-16 02:51:14','2024-04-16 02:51:14'),(4,'Open Gym',NULL,'2024-04-16 02:51:14','2024-04-16 02:51:14'),(5,'Other',NULL,'2024-04-16 02:52:12','2024-04-16 02:52:12');
/*!40000 ALTER TABLE `_ref_plan_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_product_category_type`
--

DROP TABLE IF EXISTS `_ref_product_category_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_product_category_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `order` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_product_category_type`
--

/*!40000 ALTER TABLE `_ref_product_category_type` DISABLE KEYS */;
INSERT INTO `_ref_product_category_type` VALUES (1,'Membership',NULL,'2025-05-09 04:50:42','2025-05-09 04:50:42',NULL),(2,'Retail',NULL,'2025-05-09 04:50:42','2025-05-09 04:50:42',NULL),(3,'Fees',NULL,'2025-05-09 04:50:42','2025-05-09 04:50:42',NULL);
/*!40000 ALTER TABLE `_ref_product_category_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_registration_times_type`
--

DROP TABLE IF EXISTS `_ref_registration_times_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_registration_times_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_registration_times_type`
--

/*!40000 ALTER TABLE `_ref_registration_times_type` DISABLE KEYS */;
INSERT INTO `_ref_registration_times_type` VALUES (1,'Immediately','2024-04-16 02:51:19','2024-04-16 02:51:19'),(2,'At start time','2024-04-16 02:51:19','2024-04-16 02:51:19'),(3,'Minute(s) before','2024-04-16 02:51:19','2024-04-16 02:51:19'),(4,'Hour(s) before','2024-04-16 02:51:19','2024-04-16 02:51:19'),(5,'Week(s) before','2024-04-16 02:51:19','2024-04-16 02:51:19'),(6,'Day(s) before','2025-03-05 06:48:06','2025-03-05 06:48:06');
/*!40000 ALTER TABLE `_ref_registration_times_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_relationship_status_type`
--

DROP TABLE IF EXISTS `_ref_relationship_status_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_relationship_status_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_relationship_status_type`
--

/*!40000 ALTER TABLE `_ref_relationship_status_type` DISABLE KEYS */;
INSERT INTO `_ref_relationship_status_type` VALUES (1,'Single','2024-04-16 02:51:14','2024-04-16 02:51:14'),(2,'Married','2024-04-16 02:51:14','2024-04-16 02:51:14'),(3,'In a Relationship','2024-04-16 02:51:14','2024-04-16 02:51:14'),(4,'Divorced','2024-04-16 02:51:14','2024-04-16 02:51:14'),(5,'Widowed','2024-04-16 02:51:14','2024-04-16 02:51:14');
/*!40000 ALTER TABLE `_ref_relationship_status_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_relationship_type`
--

DROP TABLE IF EXISTS `_ref_relationship_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_relationship_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(30) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_relationship_type`
--

/*!40000 ALTER TABLE `_ref_relationship_type` DISABLE KEYS */;
INSERT INTO `_ref_relationship_type` VALUES (1,'Spouse / Partner',NULL,'2024-04-16 02:51:15','2024-04-16 02:51:15'),(2,'Family',NULL,'2024-04-16 02:51:15','2024-04-16 02:51:15'),(3,'Friend',NULL,'2024-04-16 02:51:15','2024-04-16 02:51:15'),(4,'Other',NULL,'2024-04-16 02:51:15','2024-04-16 02:51:15');
/*!40000 ALTER TABLE `_ref_relationship_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_revenue_share`
--

DROP TABLE IF EXISTS `_ref_revenue_share`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_revenue_share` (
  `id` int NOT NULL AUTO_INCREMENT,
  `model_id` smallint NOT NULL,
  `name` varchar(60) NOT NULL,
  `lower` float DEFAULT NULL,
  `upper` float DEFAULT NULL,
  `environment` varchar(5) NOT NULL,
  `payrix_group_id` varchar(50) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `revenue_share_fee` float DEFAULT '0',
  `payrix_fee_ids` json DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_revenue_share`
--

/*!40000 ALTER TABLE `_ref_revenue_share` DISABLE KEYS */;
INSERT INTO `_ref_revenue_share` VALUES (1,1,'Model 1 - Tier 1 ($0-$20k/mo = 9.99%)',0,20000,'test','t1_org_673edf07e633e725b897053',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(2,1,'Model 1 - Tier 2 ($20,001 - $40k/mo = 6.99%)',20001,40000,'test','t1_org_673edf13c0132b6ed2481fd ',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(3,1,'Model 1 - Tier 3 ($40,001 - $60k/mo = 4.99%)',40001,60000,'test','t1_org_673edf230f53b9c9929398e ',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(4,1,'Model 1 - Tier 4 ($60,001+/mo = 3.99%)',60001,10000000,'test','t1_org_673edf2f25f633dd3f96393',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(5,2,'Model 2 - Tier 1 ($0-$20k/mo = 13.99%)',0,20000,'test','t1_org_673edf3a412cfe97543ea85',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(6,2,'Model 2 - Tier 2 ($20,001-$40k/mo = 8.49%)',20001,40000,'test','t1_org_673edf491b4fa5e9665670d',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(7,2,'Model 2 - Tier 3 ($40,001-$60k/mo = 5.99%)',40001,60000,'test','t1_org_673edf547c66915ee4d9dd9',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(8,2,'Model 2 - Tier 4 ($60,001+/mo = 4.99%)',60001,10000000,'test','t1_org_673edf5f04b2d080f72d3c2',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(9,3,'Model 3 - Tier 1 ($0-$10K/mo = 14.99%)',0,10000,'test','t1_org_673cbf804eed9e255a4bc3e',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(10,3,'Model 3 - Tier 2 ($10,001-$20K/mo = 9.99%)',10001,20000,'test','t1_org_673cbf87a6b438fd93099f0',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(11,3,'Model 3 - Tier 3 ($20,001-$30K/mo = 3.99%)',20001,30000,'test','t1_org_673cbf9d4fdc308049f0aeb',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(12,3,'Model 3 - Tier 4 ($30,001-$40K/mo = 0.99%)',30001,10000000,'test','t1_org_673cbfaaeeb81923e85feb2',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(13,4,'Beta',0,10000000,'test','t1_org_657c934651aa68d2cb35c26',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(14,5,'Next Day Funding',0,10000000,'test','t1_org_673edf68a7847d4f9c61fbb',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',0,NULL),(15,1,'Model 1 - Tier 1 ($0-$20k/mo = 9.99%)',0,20000,'prod','p1_org_66cd14bd839e106c06b5cef',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',11.41,'[\"p1_fee_66cd19b0d2d016b0500b7d4\", \"p1_fee_66cd1937288879ec76a4f86\"]'),(16,1,'Model 1 - Tier 2 ($20,001 - $40k/mo = 6.99%)',20001,40000,'prod','p1_org_66cd14e87f9be9077671e32 ',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',8.41,'[\"p1_fee_66cd1ba9eb1628dc5feb883\", \"p1_fee_66cd1b4a43b6a8210d90f5b\"]'),(17,1,'Model 1 - Tier 3 ($40,001 - $60k/mo = 4.99%)',40001,60000,'prod','p1_org_66cd15076b4a975bee2bd02 ',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',6.41,'[\"p1_fee_66cdc62ee43803982ccbb93\", \"p1_fee_66cdc5efbfba368d3369a69\"]'),(18,1,'Model 1 - Tier 4 ($60,001+/mo = 3.99%)',60001,10000000,'prod','p1_org_66cd1527daf808c497a9040',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',5.41,'[\"p1_fee_66cdc793d9b4cb160ca1e52\", \"p1_fee_66cdc737acd10e2d5e93e7d\"]'),(19,2,'Model 2 - Tier 1 ($0-$20k/mo = 13.99%)',0,20000,'prod','p1_org_66cd1559ea7a84fe422934b',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',15.41,'[\"p1_fee_66cdc8eaad14d0c0851012c\", \"p1_fee_66cdc8a5a2249acfc74e7e9\"]'),(20,2,'Model 2 - Tier 2 ($20,001-$40k/mo = 8.49%)',20001,40000,'prod','p1_org_66cd157c59a60b11d84f192',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',9.91,'[\"p1_fee_66cdcd8eb1f2b57dea960f4\", \"p1_fee_66cdcd43037eb4aa0f60f00\"]'),(21,2,'Model 2 - Tier 3 ($40,001-$60k/mo = 5.99%)',40001,60000,'prod','p1_org_66cd15ac84c37088f75b467',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',7.41,'[\"p1_fee_66cdceaaf3e93da096ebcfd\", \"p1_fee_66cdce64b6e28e283f48925\"]'),(22,2,'Model 2 - Tier 4 ($60,001+/mo = 4.99%)',60001,10000000,'prod','p1_org_66cd1625b100f92cae5a3f1',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',6.41,'[\"p1_fee_66cdd00d852eac57a4c5895\", \"p1_fee_66cdcfcfbc1a8e4267a5847\"]'),(23,3,'Model 3 - Tier 1 ($0-$10K/mo = 14.99%)',0,10000,'prod','p1_org_673cbb3ac3d348dfd009ce0',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',16.41,'[\"p1_fee_675dd51a6763cd652a63590\", \"p1_fee_675dd56ebf4d058571ed3ae\"]'),(24,3,'Model 3 - Tier 2 ($10,001-$20K/mo = 9.99%)',10001,20000,'prod','p1_org_673cbb9e19926b870429201',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',11.41,'[\"p1_fee_675dd68dbbf45976ebe1733\", \"p1_fee_675dd6c78b3c96e58a09e4a\"]'),(25,3,'Model 3 - Tier 3 ($20,001-$30K/mo = 3.99%)',20001,30000,'prod','p1_org_673cbc26a314633f9a115de',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',5.41,'[\"p1_fee_675dd7b3c20990474d00dbe\", \"p1_fee_675dd82ecab867217ba4288\"]'),(26,3,'Model 3 - Tier 4 ($30,001-$40K/mo = 0.99%)',30001,10000000,'prod','p1_org_673cbc4f2cd916a87b2737e',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',2.41,'[\"p1_fee_675dd92b94f83f6416d9f53\", \"p1_fee_675dd9b83dd2b71318ae16b\"]'),(27,4,'Beta',0,10000000,'prod','p1_org_65b91e9594d394630eca6bb',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',1.42,'[\"p1_fee_65b9229a25537102ec27f22\", \"p1_fee_65b920cebd36fd6f270d5e1\"]'),(28,5,'Next Day Funding',0,10000000,'prod','p1_org_66e99a017e358730710b4d3',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',NULL,NULL),(29,6,'Non-GL Client (3.99% Processing Rate)',0,10000000,'prod','p1_org_6745039ec972a1113a37143',1,'2024-12-06 11:19:05','2024-12-06 11:19:05',1.82,'[\"p1_fee_674733bb75e0a9406db1df1\", \"p1_fee_67450535b744cac1d7b37b6\"]'),(30,7,'Wolf 7% Franchise Fee',0,10000000,'prod','p1_org_67532cecba6912c12d5efb0',1,'2025-01-08 05:55:17','2025-01-08 05:55:17',9.42,'[\"p1_fee_67532fff6cf60508be10085\", \"p1_fee_67533096a96c213ed2e146d\"]');
/*!40000 ALTER TABLE `_ref_revenue_share` ENABLE KEYS */;

--
-- Table structure for table `_ref_role_type`
--

DROP TABLE IF EXISTS `_ref_role_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_role_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(20) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_staff` tinyint(1) NOT NULL,
  `access_token_timeout_hrs` int NOT NULL DEFAULT '8',
  `refresh_token_timeout_days` int NOT NULL DEFAULT '180',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_role_type`
--

/*!40000 ALTER TABLE `_ref_role_type` DISABLE KEYS */;
INSERT INTO `_ref_role_type` VALUES (1,'Owner',NULL,'2024-04-16 02:51:15','2024-04-16 02:51:15',1,8,180),(2,'User',NULL,'2024-04-16 02:51:15','2024-04-16 02:51:15',0,8,180),(3,'Coach',NULL,'2024-04-16 02:51:15','2024-04-16 02:51:15',1,8,180),(4,'Manager',NULL,'2024-04-16 02:51:15','2024-04-16 02:51:15',1,8,180),(5,'Staff',NULL,'2024-04-16 02:51:15','2024-04-16 02:51:15',1,8,180),(6,'Member',NULL,'2024-04-16 02:51:15','2024-04-16 02:51:15',0,8,180),(7,'Kiosk','Kiosk User','2024-12-20 16:13:32','2024-12-20 16:13:32',1,2160,180);
/*!40000 ALTER TABLE `_ref_role_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_shirt_fit_type`
--

DROP TABLE IF EXISTS `_ref_shirt_fit_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_shirt_fit_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_shirt_fit_type`
--

/*!40000 ALTER TABLE `_ref_shirt_fit_type` DISABLE KEYS */;
INSERT INTO `_ref_shirt_fit_type` VALUES (1,'unisex','2024-04-16 02:51:15','2024-04-16 02:51:15'),(2,'female','2024-04-16 02:51:15','2024-04-16 02:51:15');
/*!40000 ALTER TABLE `_ref_shirt_fit_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_shirt_size_type`
--

DROP TABLE IF EXISTS `_ref_shirt_size_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_shirt_size_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_shirt_size_type`
--

/*!40000 ALTER TABLE `_ref_shirt_size_type` DISABLE KEYS */;
INSERT INTO `_ref_shirt_size_type` VALUES (1,'XS','2024-04-16 02:51:16','2024-04-16 02:51:16'),(2,'S','2024-04-16 02:51:16','2024-04-16 02:51:16'),(3,'M','2024-04-16 02:51:16','2024-04-16 02:51:16'),(4,'L','2024-04-16 02:51:16','2024-04-16 02:51:16'),(5,'XL','2024-04-16 02:51:16','2024-04-16 02:51:16'),(6,'XXL','2024-04-16 02:51:16','2024-04-16 02:51:16');
/*!40000 ALTER TABLE `_ref_shirt_size_type` ENABLE KEYS */;

--
-- Table structure for table `_ref_timezone_type`
--

DROP TABLE IF EXISTS `_ref_timezone_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `_ref_timezone_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(60) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `iana_tzdata` varchar(50) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `_ref_timezone_type`
--

/*!40000 ALTER TABLE `_ref_timezone_type` DISABLE KEYS */;
INSERT INTO `_ref_timezone_type` VALUES (1,'GMT-05:00 (EST) / GMT-04:00 (EDT) (US/Canada Eastern)','2024-04-16 02:51:18','2024-04-16 02:51:18','America/New_York'),(2,'GMT-06:00 (CST) / GMT-05:00 (CDT) (US/Canada Central)','2024-04-16 02:51:18','2024-04-16 02:51:18','America/Chicago'),(3,'GMT-07:00 (MST) / GMT-06:00 (MDT) (US/Canada Mountain)','2024-04-16 02:51:18','2024-04-16 02:51:18','America/Denver'),(4,'GMT-08:00 (PST) / GMT-07:00 (PDT) (US/Canada Pacific)','2024-04-16 02:51:18','2024-04-16 02:51:18','America/Los_Angeles'),(5,'GMT-09:00 (AKST) / GMT-08:00 (AKDT) (US/Alaska)','2024-04-16 02:51:18','2024-04-16 02:51:18','America/Anchorage'),(6,'GMT-10:00 (HST) (US/Hawaii)','2024-04-16 02:52:38','2024-04-16 02:52:38','Pacific/Honolulu');
/*!40000 ALTER TABLE `_ref_timezone_type` ENABLE KEYS */;

--
-- Table structure for table `alembic_version`
--

DROP TABLE IF EXISTS `alembic_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `alembic_version` (
  `version_num` varchar(32) NOT NULL,
  PRIMARY KEY (`version_num`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `alembic_version`
--

/*!40000 ALTER TABLE `alembic_version` DISABLE KEYS */;
/*!40000 ALTER TABLE `alembic_version` ENABLE KEYS */;

--
-- Table structure for table `batch_processing_log`
--

DROP TABLE IF EXISTS `batch_processing_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `batch_processing_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  `membership_id` bigint DEFAULT NULL,
  `process_name` varchar(50) NOT NULL,
  `message` varchar(200) DEFAULT NULL,
  `data` json DEFAULT NULL,
  `error` varchar(500) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=196114 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `batch_processing_log`
--

/*!40000 ALTER TABLE `batch_processing_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `batch_processing_log` ENABLE KEYS */;

--
-- Table structure for table `class`
--

DROP TABLE IF EXISTS `class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(255) DEFAULT NULL,
  `attendance_cap` int NOT NULL,
  `all_day_event` tinyint(1) NOT NULL DEFAULT '0',
  `start_time` datetime NOT NULL,
  `end_time` datetime DEFAULT NULL,
  `recurring` tinyint(1) NOT NULL DEFAULT '0',
  `exdate` varchar(512) DEFAULT NULL,
  `class_url` varchar(255) DEFAULT NULL,
  `waitlist` tinyint(1) DEFAULT '1',
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `location_id` bigint NOT NULL,
  `room_id` bigint NOT NULL,
  `main_coach_id` bigint DEFAULT NULL,
  `assistant_coach_id` bigint DEFAULT NULL,
  `location_type_id` int NOT NULL,
  `class_type_id` int NOT NULL,
  `registration_start_time_type_id` int DEFAULT NULL,
  `registration_start_time_value` int DEFAULT NULL,
  `registration_end_time_type_id` int DEFAULT NULL,
  `registration_end_time_value` int DEFAULT NULL,
  `late_cancellation_time_type_id` int DEFAULT NULL,
  `late_cancellation_time_value` int DEFAULT NULL,
  `class_cancellation_time` datetime DEFAULT NULL,
  `frequency` int DEFAULT NULL,
  `by_weekday` varchar(60) DEFAULT NULL,
  `recurrence_end_date` datetime DEFAULT NULL,
  `private_training` tinyint(1) DEFAULT '0',
  `no_show_credit` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `assistant_coach_id` (`assistant_coach_id`),
  KEY `class_type_id` (`class_type_id`),
  KEY `late_cancellation_time_type_id` (`late_cancellation_time_type_id`),
  KEY `location_id` (`location_id`),
  KEY `location_type_id` (`location_type_id`),
  KEY `main_coach_id` (`main_coach_id`),
  KEY `registration_end_time_type_id` (`registration_end_time_type_id`),
  KEY `registration_start_time_type_id` (`registration_start_time_type_id`),
  KEY `room_id` (`room_id`),
  CONSTRAINT `class_ibfk_1` FOREIGN KEY (`assistant_coach_id`) REFERENCES `user` (`id`),
  CONSTRAINT `class_ibfk_2` FOREIGN KEY (`class_type_id`) REFERENCES `_ref_class_type` (`id`),
  CONSTRAINT `class_ibfk_3` FOREIGN KEY (`late_cancellation_time_type_id`) REFERENCES `_ref_registration_times_type` (`id`),
  CONSTRAINT `class_ibfk_4` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `class_ibfk_5` FOREIGN KEY (`location_type_id`) REFERENCES `_ref_location_type` (`id`),
  CONSTRAINT `class_ibfk_6` FOREIGN KEY (`main_coach_id`) REFERENCES `user` (`id`),
  CONSTRAINT `class_ibfk_7` FOREIGN KEY (`registration_end_time_type_id`) REFERENCES `_ref_registration_times_type` (`id`),
  CONSTRAINT `class_ibfk_8` FOREIGN KEY (`registration_start_time_type_id`) REFERENCES `_ref_registration_times_type` (`id`),
  CONSTRAINT `class_ibfk_9` FOREIGN KEY (`room_id`) REFERENCES `room` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11287 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class`
--

/*!40000 ALTER TABLE `class` DISABLE KEYS */;
/*!40000 ALTER TABLE `class` ENABLE KEYS */;

--
-- Table structure for table `class_access_group`
--

DROP TABLE IF EXISTS `class_access_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_access_group` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `name` varchar(50) NOT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `create_datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `door_access_group_id` varchar(100) DEFAULT NULL,
  `door_access_group_status` int DEFAULT '0',
  `door_access_access_times_flag` tinyint(1) DEFAULT '0',
  `door_access_access_times` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `class_access_group_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=103 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_access_group`
--

/*!40000 ALTER TABLE `class_access_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `class_access_group` ENABLE KEYS */;

--
-- Table structure for table `class_access_group_class`
--

DROP TABLE IF EXISTS `class_access_group_class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_access_group_class` (
  `class_access_group_id` bigint NOT NULL,
  `class_id` bigint NOT NULL,
  KEY `class_access_group_id` (`class_access_group_id`),
  KEY `class_id` (`class_id`),
  CONSTRAINT `class_access_group_class_ibfk_1` FOREIGN KEY (`class_access_group_id`) REFERENCES `class_access_group` (`id`),
  CONSTRAINT `class_access_group_class_ibfk_2` FOREIGN KEY (`class_id`) REFERENCES `class` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_access_group_class`
--

/*!40000 ALTER TABLE `class_access_group_class` DISABLE KEYS */;
/*!40000 ALTER TABLE `class_access_group_class` ENABLE KEYS */;

--
-- Table structure for table `class_access_group_door`
--

DROP TABLE IF EXISTS `class_access_group_door`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_access_group_door` (
  `class_access_group_id` bigint NOT NULL,
  `door_id` bigint NOT NULL,
  KEY `class_access_group_id` (`class_access_group_id`),
  KEY `door_id` (`door_id`),
  CONSTRAINT `class_access_group_door_ibfk_1` FOREIGN KEY (`class_access_group_id`) REFERENCES `class_access_group` (`id`),
  CONSTRAINT `class_access_group_door_ibfk_2` FOREIGN KEY (`door_id`) REFERENCES `door_access_door` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_access_group_door`
--

/*!40000 ALTER TABLE `class_access_group_door` DISABLE KEYS */;
/*!40000 ALTER TABLE `class_access_group_door` ENABLE KEYS */;

--
-- Table structure for table `class_access_group_format`
--

DROP TABLE IF EXISTS `class_access_group_format`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_access_group_format` (
  `class_access_group_id` bigint NOT NULL,
  `plan_type_id` int NOT NULL,
  KEY `class_access_group_id` (`class_access_group_id`),
  KEY `plan_type_id` (`plan_type_id`),
  CONSTRAINT `class_access_group_format_ibfk_1` FOREIGN KEY (`class_access_group_id`) REFERENCES `class_access_group` (`id`),
  CONSTRAINT `class_access_group_format_ibfk_2` FOREIGN KEY (`plan_type_id`) REFERENCES `_ref_plan_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_access_group_format`
--

/*!40000 ALTER TABLE `class_access_group_format` DISABLE KEYS */;
/*!40000 ALTER TABLE `class_access_group_format` ENABLE KEYS */;

--
-- Table structure for table `class_access_group_plan`
--

DROP TABLE IF EXISTS `class_access_group_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_access_group_plan` (
  `class_access_group_id` bigint NOT NULL,
  `plan_id` bigint NOT NULL,
  KEY `class_access_group_id` (`class_access_group_id`),
  KEY `plan_id` (`plan_id`),
  CONSTRAINT `class_access_group_plan_ibfk_1` FOREIGN KEY (`class_access_group_id`) REFERENCES `class_access_group` (`id`),
  CONSTRAINT `class_access_group_plan_ibfk_2` FOREIGN KEY (`plan_id`) REFERENCES `plan` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_access_group_plan`
--

/*!40000 ALTER TABLE `class_access_group_plan` DISABLE KEYS */;
/*!40000 ALTER TABLE `class_access_group_plan` ENABLE KEYS */;

--
-- Table structure for table `class_plan`
--

DROP TABLE IF EXISTS `class_plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `class_plan` (
  `class_id` bigint NOT NULL,
  `plan_id` bigint NOT NULL,
  PRIMARY KEY (`class_id`,`plan_id`),
  KEY `plan_id` (`plan_id`),
  CONSTRAINT `class_plan_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `class` (`id`),
  CONSTRAINT `class_plan_ibfk_2` FOREIGN KEY (`plan_id`) REFERENCES `plan` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `class_plan`
--

/*!40000 ALTER TABLE `class_plan` DISABLE KEYS */;
/*!40000 ALTER TABLE `class_plan` ENABLE KEYS */;

--
-- Table structure for table `door_access_door`
--

DROP TABLE IF EXISTS `door_access_door`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `door_access_door` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `name` varchar(30) NOT NULL,
  `door_location` varchar(50) DEFAULT NULL,
  `active` tinyint(1) NOT NULL DEFAULT '1',
  `door_access_door_status` int NOT NULL,
  `vendor_door_id` bigint DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `door_access_door_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `door_access_door`
--

/*!40000 ALTER TABLE `door_access_door` DISABLE KEYS */;
/*!40000 ALTER TABLE `door_access_door` ENABLE KEYS */;

--
-- Table structure for table `door_access_location_auth`
--

DROP TABLE IF EXISTS `door_access_location_auth`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `door_access_location_auth` (
  `id` int NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `field_id` int NOT NULL,
  `field_value` varchar(100) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `field_id` (`field_id`),
  CONSTRAINT `door_access_location_auth_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `door_access_location_auth_ibfk_2` FOREIGN KEY (`field_id`) REFERENCES `_ref_door_access_vendor_auth` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `door_access_location_auth`
--

/*!40000 ALTER TABLE `door_access_location_auth` DISABLE KEYS */;
/*!40000 ALTER TABLE `door_access_location_auth` ENABLE KEYS */;

--
-- Table structure for table `door_access_log`
--

DROP TABLE IF EXISTS `door_access_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `door_access_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `resource` int NOT NULL,
  `resource_id` varchar(50) DEFAULT NULL,
  `request_type` int NOT NULL,
  `request_url` varchar(250) NOT NULL,
  `request_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `request_payload` json DEFAULT NULL,
  `response_payload` json DEFAULT NULL,
  `response_status_code` int DEFAULT NULL,
  `response_elapsed_sec` float DEFAULT NULL,
  `error` varchar(1000) DEFAULT NULL,
  `location_id` bigint DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13256 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `door_access_log`
--

/*!40000 ALTER TABLE `door_access_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `door_access_log` ENABLE KEYS */;

--
-- Table structure for table `door_access_updates_log`
--

DROP TABLE IF EXISTS `door_access_updates_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `door_access_updates_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `vendor_id` int NOT NULL,
  `vendor_location_id` varchar(50) DEFAULT NULL,
  `actor_id` varchar(50) DEFAULT NULL,
  `event_id` varchar(50) DEFAULT NULL,
  `event_type` int DEFAULT NULL,
  `error_code` varchar(15) DEFAULT NULL,
  `event_payload` json DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `door_access_updates_log`
--

/*!40000 ALTER TABLE `door_access_updates_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `door_access_updates_log` ENABLE KEYS */;

--
-- Table structure for table `gym`
--

DROP TABLE IF EXISTS `gym`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `gym` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `logo_url` varchar(255) DEFAULT NULL,
  `company_name` varchar(50) DEFAULT NULL,
  `company_website` varchar(255) DEFAULT NULL,
  `location_type_id` int NOT NULL DEFAULT '1',
  `timezone_type_id` int NOT NULL DEFAULT '1',
  `session_or_class` int NOT NULL DEFAULT '1',
  `registration_start_time_type_id` int NOT NULL DEFAULT '1',
  `registration_start_time_value` int DEFAULT NULL,
  `registration_end_time_type_id` int NOT NULL DEFAULT '1',
  `registration_end_value` int DEFAULT NULL,
  `late_cancellation_enforcement` tinyint(1) NOT NULL DEFAULT '1',
  `late_cancellation_time_type_id` int NOT NULL DEFAULT '1',
  `cancellation_penalty` int DEFAULT NULL,
  `no_show_penalties` tinyint(1) NOT NULL DEFAULT '0',
  `no_show_time_penalty` int DEFAULT NULL,
  `waitlist_availability` tinyint(1) NOT NULL DEFAULT '1',
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `late_cancellation_time_type_id` (`late_cancellation_time_type_id`),
  KEY `location_type_id` (`location_type_id`),
  KEY `registration_end_time_type_id` (`registration_end_time_type_id`),
  KEY `registration_start_time_type_id` (`registration_start_time_type_id`),
  KEY `timezone_type_id` (`timezone_type_id`),
  CONSTRAINT `gym_ibfk_1` FOREIGN KEY (`late_cancellation_time_type_id`) REFERENCES `_ref_registration_times_type` (`id`),
  CONSTRAINT `gym_ibfk_2` FOREIGN KEY (`location_type_id`) REFERENCES `_ref_location_type` (`id`),
  CONSTRAINT `gym_ibfk_3` FOREIGN KEY (`registration_end_time_type_id`) REFERENCES `_ref_registration_times_type` (`id`),
  CONSTRAINT `gym_ibfk_4` FOREIGN KEY (`registration_start_time_type_id`) REFERENCES `_ref_registration_times_type` (`id`),
  CONSTRAINT `gym_ibfk_5` FOREIGN KEY (`timezone_type_id`) REFERENCES `_ref_timezone_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=178 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `gym`
--

/*!40000 ALTER TABLE `gym` DISABLE KEYS */;
INSERT INTO `gym` VALUES (43,'Riverside Strength',NULL,NULL,NULL,1,1,1,1,NULL,1,NULL,1,1,NULL,0,NULL,1,'2024-09-25 20:52:15','2024-09-25 20:52:15');
/*!40000 ALTER TABLE `gym` ENABLE KEYS */;

--
-- Table structure for table `invoice`
--

DROP TABLE IF EXISTS `invoice`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `invoice_type_id` int NOT NULL DEFAULT '1',
  `for_invoice_id` bigint DEFAULT NULL,
  `processed_user_id` bigint DEFAULT NULL,
  `product_category_type_id` int DEFAULT '1',
  `notes` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `invoice_status_type_id` int NOT NULL DEFAULT '1',
  `void_datetime` datetime DEFAULT NULL,
  `void_by` bigint DEFAULT NULL,
  `description` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `user_id` (`user_id`),
  KEY `invoice_type_id` (`invoice_type_id`),
  KEY `for_invoice_id` (`for_invoice_id`),
  KEY `processed_user_id` (`processed_user_id`),
  KEY `invoice_ibfk_6` (`product_category_type_id`),
  KEY `invoice_ibfk_7` (`invoice_status_type_id`),
  KEY `invoice_ibfk_8` (`void_by`),
  CONSTRAINT `invoice_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `invoice_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`),
  CONSTRAINT `invoice_ibfk_3` FOREIGN KEY (`invoice_type_id`) REFERENCES `_ref_invoice_type` (`id`),
  CONSTRAINT `invoice_ibfk_4` FOREIGN KEY (`for_invoice_id`) REFERENCES `invoice` (`id`),
  CONSTRAINT `invoice_ibfk_6` FOREIGN KEY (`product_category_type_id`) REFERENCES `_ref_product_category_type` (`id`),
  CONSTRAINT `invoice_ibfk_7` FOREIGN KEY (`invoice_status_type_id`) REFERENCES `_ref_invoice_status_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=97443 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice`
--

/*!40000 ALTER TABLE `invoice` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoice` ENABLE KEYS */;

--
-- Table structure for table `invoice_item`
--

DROP TABLE IF EXISTS `invoice_item`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `invoice_item` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `invoice_id` bigint NOT NULL,
  `description` varchar(300) DEFAULT NULL,
  `amount` float NOT NULL DEFAULT '0',
  `discount` float NOT NULL DEFAULT '0',
  `tax` float NOT NULL DEFAULT '0',
  `total_amount` float NOT NULL DEFAULT '0',
  `due_date` date DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `invoice_item_status_type_id` int DEFAULT '1',
  `product_id` bigint DEFAULT NULL,
  `discount_percent` float DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `invoice_id` (`invoice_id`),
  KEY `location_id` (`location_id`),
  KEY `user_id` (`user_id`),
  KEY `invoice_item_ibfk_4` (`invoice_item_status_type_id`),
  CONSTRAINT `invoice_item_ibfk_1` FOREIGN KEY (`invoice_id`) REFERENCES `invoice` (`id`),
  CONSTRAINT `invoice_item_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `invoice_item_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`),
  CONSTRAINT `invoice_item_ibfk_4` FOREIGN KEY (`invoice_item_status_type_id`) REFERENCES `_ref_invoice_item_status_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=99443 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `invoice_item`
--

/*!40000 ALTER TABLE `invoice_item` DISABLE KEYS */;
/*!40000 ALTER TABLE `invoice_item` ENABLE KEYS */;

--
-- Table structure for table `location`
--

DROP TABLE IF EXISTS `location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `location` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `address_1` varchar(50) DEFAULT NULL,
  `address_2` varchar(50) DEFAULT NULL,
  `city` varchar(50) DEFAULT NULL,
  `state` varchar(50) DEFAULT NULL,
  `zip` varchar(10) DEFAULT NULL,
  `country` varchar(50) DEFAULT NULL,
  `area_sft` int DEFAULT NULL,
  `active` tinyint(1) DEFAULT NULL,
  `primary` tinyint(1) DEFAULT NULL,
  `cs_phone` varchar(20) DEFAULT NULL,
  `cs_email` varchar(100) DEFAULT NULL,
  `payrix_merchant_id` varchar(50) DEFAULT NULL,
  `payrix_onboarding_status` int DEFAULT '1',
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `other_gym_type` varchar(50) DEFAULT NULL,
  `gym_id` bigint NOT NULL,
  `location_type_id` int NOT NULL,
  `sales_tax` float DEFAULT NULL,
  `timezone_type_id` int DEFAULT '1',
  `registration_start_time_type_id` int DEFAULT NULL,
  `registration_start_time_value` int DEFAULT NULL,
  `registration_end_time_type_id` int DEFAULT NULL,
  `registration_end_time_value` int DEFAULT NULL,
  `late_cancellation_time_type_id` int DEFAULT NULL,
  `late_cancellation_time_value` int DEFAULT NULL,
  `waitlist` tinyint(1) DEFAULT NULL,
  `no_show_time_penalty` int DEFAULT NULL,
  `payrix_entity_id` varchar(50) DEFAULT NULL,
  `revenue_share_enabled` tinyint(1) NOT NULL,
  `revenue_share_model_id` smallint DEFAULT NULL,
  `payrix_group_id` varchar(50) DEFAULT NULL,
  `kiosk_enabled` tinyint(1) DEFAULT NULL,
  `checkin_type` int DEFAULT '3',
  `accent_color` varchar(10) DEFAULT NULL,
  `kiosk_user_id` bigint DEFAULT NULL,
  `logo_url` varchar(200) DEFAULT NULL,
  `no_show_credit` tinyint(1) DEFAULT '1',
  `payments` tinyint(1) DEFAULT '1',
  `late_cancellation` tinyint(1) DEFAULT '0',
  `is_dea` tinyint(1) NOT NULL DEFAULT '1',
  `block_registrations_on_balance_due` tinyint(1) NOT NULL DEFAULT '0',
  `class_access_group` tinyint(1) NOT NULL DEFAULT '0',
  `no_show_enabled_datetime` datetime DEFAULT NULL,
  `door_access` tinyint(1) DEFAULT '0',
  `door_access_auth_status` int NOT NULL DEFAULT '0',
  `door_access_auth_error` json DEFAULT NULL,
  `door_access_vendor_id` int DEFAULT NULL,
  `door_access_place_id` bigint DEFAULT NULL,
  `door_access_unlock_doors` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `gym_id` (`gym_id`),
  KEY `location_type_id` (`location_type_id`),
  KEY `timezone_type_id` (`timezone_type_id`),
  KEY `registration_end_time_type_id` (`registration_end_time_type_id`),
  KEY `registration_start_time_type_id` (`registration_start_time_type_id`),
  KEY `late_cancellation_time_type_id` (`late_cancellation_time_type_id`),
  KEY `kiosk_user_id` (`kiosk_user_id`),
  KEY `location_ibfk_8` (`door_access_vendor_id`),
  CONSTRAINT `location_ibfk_1` FOREIGN KEY (`gym_id`) REFERENCES `gym` (`id`),
  CONSTRAINT `location_ibfk_2` FOREIGN KEY (`location_type_id`) REFERENCES `_ref_location_type` (`id`),
  CONSTRAINT `location_ibfk_3` FOREIGN KEY (`timezone_type_id`) REFERENCES `_ref_timezone_type` (`id`),
  CONSTRAINT `location_ibfk_4` FOREIGN KEY (`registration_end_time_type_id`) REFERENCES `_ref_registration_times_type` (`id`),
  CONSTRAINT `location_ibfk_5` FOREIGN KEY (`registration_start_time_type_id`) REFERENCES `_ref_registration_times_type` (`id`),
  CONSTRAINT `location_ibfk_6` FOREIGN KEY (`late_cancellation_time_type_id`) REFERENCES `_ref_registration_times_type` (`id`),
  CONSTRAINT `location_ibfk_7` FOREIGN KEY (`kiosk_user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `location_ibfk_8` FOREIGN KEY (`door_access_vendor_id`) REFERENCES `_ref_door_access_vendor` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=178 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `location`
--

/*!40000 ALTER TABLE `location` DISABLE KEYS */;
INSERT INTO `location` VALUES (43,'Riverside Strength','100 Example Street','','Springfield','TX','75001','United States',NULL,1,1,'+10000000000','frontdesk@demo.gym','p1_mer_demo43',3,'2024-09-25 20:52:15','2025-11-10 00:06:08',NULL,43,1,8.25,1,5,2,2,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,NULL,1,1,'#AABBCC',8893,NULL,1,1,0,1,0,1,NULL,1,1,NULL,1,28887,1);
/*!40000 ALTER TABLE `location` ENABLE KEYS */;

--
-- Table structure for table `location_gym_type`
--

DROP TABLE IF EXISTS `location_gym_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `location_gym_type` (
  `location_id` bigint NOT NULL,
  `gym_type_id` int NOT NULL,
  PRIMARY KEY (`location_id`,`gym_type_id`),
  KEY `gym_type_id` (`gym_type_id`),
  CONSTRAINT `location_gym_type_ibfk_1` FOREIGN KEY (`gym_type_id`) REFERENCES `_ref_gym_type` (`id`),
  CONSTRAINT `location_gym_type_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `location_gym_type`
--

/*!40000 ALTER TABLE `location_gym_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `location_gym_type` ENABLE KEYS */;

--
-- Table structure for table `member_class`
--

DROP TABLE IF EXISTS `member_class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_class` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `class_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `class_time` datetime NOT NULL,
  `member_registered_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `member_waitlist` smallint DEFAULT NULL,
  `member_cancelled_time` datetime DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `member_checked_in_time` datetime DEFAULT NULL,
  `membership_id` bigint DEFAULT NULL,
  `cancel_rebook_email_time` datetime DEFAULT NULL,
  `cancel_reason` varchar(200) DEFAULT NULL,
  `no_show_credited` tinyint(1) DEFAULT '0',
  `cancelled_by` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `class_id` (`class_id`),
  KEY `location_id` (`location_id`),
  KEY `membership_id` (`membership_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `member_class_ibfk_1` FOREIGN KEY (`class_id`) REFERENCES `class` (`id`),
  CONSTRAINT `member_class_ibfk_2` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `member_class_ibfk_5` FOREIGN KEY (`membership_id`) REFERENCES `membership` (`id`),
  CONSTRAINT `member_class_ibfk_6` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=249324 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member_class`
--

/*!40000 ALTER TABLE `member_class` DISABLE KEYS */;
/*!40000 ALTER TABLE `member_class` ENABLE KEYS */;

--
-- Table structure for table `member_opengym`
--

DROP TABLE IF EXISTS `member_opengym`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_opengym` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `class_id` bigint DEFAULT NULL,
  `user_id` bigint NOT NULL,
  `membership_id` bigint DEFAULT NULL,
  `class_time` datetime DEFAULT NULL,
  `member_registered_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `member_waitlist` smallint DEFAULT '0',
  `member_cancelled_time` datetime DEFAULT NULL,
  `member_checked_in_time` datetime DEFAULT NULL,
  `cancel_rebook_email_time` datetime DEFAULT NULL,
  `cancel_reason` varchar(200) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `membership_id` (`membership_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `member_opengym_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `member_opengym_ibfk_2` FOREIGN KEY (`membership_id`) REFERENCES `membership` (`id`),
  CONSTRAINT `member_opengym_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=23541 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member_opengym`
--

/*!40000 ALTER TABLE `member_opengym` DISABLE KEYS */;
/*!40000 ALTER TABLE `member_opengym` ENABLE KEYS */;

--
-- Table structure for table `member_payment_history`
--

DROP TABLE IF EXISTS `member_payment_history`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_payment_history` (
  `id` bigint NOT NULL,
  `location_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `payment_method_id` bigint DEFAULT NULL,
  `membership_id` bigint DEFAULT NULL,
  `payment_number` int DEFAULT NULL,
  `total_amount` float DEFAULT NULL,
  `amount` float DEFAULT NULL,
  `signup_fee` float DEFAULT NULL,
  `tax` float DEFAULT NULL,
  `surcharge` float DEFAULT NULL,
  `discount` float DEFAULT NULL,
  `processed_date` datetime NOT NULL,
  `payrix_transaction_id` varchar(50) DEFAULT NULL,
  `payrix_transaction_status` int DEFAULT '1',
  `payrix_transaction_error` varchar(500) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `payment_category_type_id` int DEFAULT NULL,
  `description` varchar(250) DEFAULT NULL,
  `for_payment_id` bigint DEFAULT NULL,
  `payment_transaction_type` int DEFAULT '1',
  `renewal_count` int DEFAULT NULL,
  `processed_by` bigint DEFAULT NULL,
  `notes` varchar(250) DEFAULT NULL,
  `v2_payment_id` bigint DEFAULT NULL,
  `revenue_share_fee` float NOT NULL DEFAULT '0',
  `payrix_disbursement_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `payment_method_id` (`payment_method_id`),
  KEY `user_id` (`user_id`),
  KEY `membership_id` (`membership_id`),
  KEY `payment_transaction_type` (`payment_transaction_type`),
  KEY `payment_category_type_id` (`payment_category_type_id`),
  KEY `for_payment_id` (`for_payment_id`),
  CONSTRAINT `member_payment_history_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `member_payment_history_ibfk_2` FOREIGN KEY (`payment_method_id`) REFERENCES `member_payment_method` (`id`),
  CONSTRAINT `member_payment_history_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`),
  CONSTRAINT `member_payment_history_ibfk_4` FOREIGN KEY (`membership_id`) REFERENCES `membership` (`id`),
  CONSTRAINT `member_payment_history_ibfk_5` FOREIGN KEY (`payment_transaction_type`) REFERENCES `_ref_payment_transaction_type` (`id`),
  CONSTRAINT `member_payment_history_ibfk_6` FOREIGN KEY (`payment_category_type_id`) REFERENCES `_ref_payment_category_type` (`id`),
  CONSTRAINT `member_payment_history_ibfk_7` FOREIGN KEY (`for_payment_id`) REFERENCES `member_payment_history` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member_payment_history`
--

/*!40000 ALTER TABLE `member_payment_history` DISABLE KEYS */;
/*!40000 ALTER TABLE `member_payment_history` ENABLE KEYS */;

--
-- Table structure for table `member_payment_history_v2`
--

DROP TABLE IF EXISTS `member_payment_history_v2`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_payment_history_v2` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `payment_method_id` bigint DEFAULT NULL,
  `total_amount` float NOT NULL DEFAULT '0',
  `processed_date` datetime DEFAULT NULL,
  `processed_by` bigint DEFAULT NULL,
  `payment_transaction_type_id` int DEFAULT '1',
  `payrix_transaction_id` varchar(50) DEFAULT NULL,
  `payrix_transaction_status` int DEFAULT NULL,
  `payrix_transaction_error` varchar(500) DEFAULT NULL,
  `payrix_onboarding_status` int NOT NULL DEFAULT '98',
  `for_payment_id` bigint DEFAULT NULL,
  `invoice_id` bigint DEFAULT NULL,
  `notes` varchar(250) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `invoice_item_ids` json DEFAULT NULL,
  `amount` float NOT NULL DEFAULT '0',
  `discount` float NOT NULL DEFAULT '0',
  `tax` float NOT NULL DEFAULT '0',
  `scheduled_date` date DEFAULT NULL,
  `original_total_amount` float NOT NULL DEFAULT '0',
  `v1_payment_id` bigint DEFAULT NULL,
  `revenue_share_fee` float DEFAULT '0',
  `payrix_disbursement_id` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `user_id` (`user_id`),
  KEY `payment_method_id` (`payment_method_id`),
  KEY `payment_transaction_type_id` (`payment_transaction_type_id`),
  KEY `for_payment_id` (`for_payment_id`),
  KEY `invoice_id` (`invoice_id`),
  CONSTRAINT `member_payment_history_v2_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `member_payment_history_v2_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`),
  CONSTRAINT `member_payment_history_v2_ibfk_5` FOREIGN KEY (`payment_transaction_type_id`) REFERENCES `_ref_payment_transaction_type` (`id`),
  CONSTRAINT `member_payment_history_v2_ibfk_6` FOREIGN KEY (`for_payment_id`) REFERENCES `member_payment_history_v2` (`id`),
  CONSTRAINT `member_payment_history_v2_ibfk_7` FOREIGN KEY (`invoice_id`) REFERENCES `invoice` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=100041 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member_payment_history_v2`
--

/*!40000 ALTER TABLE `member_payment_history_v2` DISABLE KEYS */;
/*!40000 ALTER TABLE `member_payment_history_v2` ENABLE KEYS */;

--
-- Table structure for table `member_payment_method`
--

DROP TABLE IF EXISTS `member_payment_method`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_payment_method` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `name` varchar(50) DEFAULT NULL,
  `method` int DEFAULT NULL,
  `last_4_digits_card` varchar(5) DEFAULT NULL,
  `last_4_digits_account` varchar(5) DEFAULT NULL,
  `last_4_digits_routing` varchar(5) DEFAULT NULL,
  `expiration` varchar(8) DEFAULT NULL,
  `token` varchar(50) DEFAULT NULL,
  `inactive` tinyint(1) DEFAULT NULL,
  `payrix_token_id` varchar(50) DEFAULT NULL,
  `payrix_onboarding_status` int DEFAULT '1',
  `payrix_onboarding_error` varchar(100) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `default_method` tinyint(1) DEFAULT NULL,
  `zipcode` varchar(10) DEFAULT NULL,
  `payrix_zipcode_onboarding_status` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `member_payment_method_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `member_payment_method_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=25523 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member_payment_method`
--

/*!40000 ALTER TABLE `member_payment_method` DISABLE KEYS */;
/*!40000 ALTER TABLE `member_payment_method` ENABLE KEYS */;

--
-- Table structure for table `member_payment_schedule`
--

DROP TABLE IF EXISTS `member_payment_schedule`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_payment_schedule` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `membership_id` bigint DEFAULT NULL,
  `payment_number` int DEFAULT NULL,
  `total_amount` float DEFAULT NULL,
  `amount` float DEFAULT NULL,
  `signup_fee` float DEFAULT NULL,
  `tax` float DEFAULT NULL,
  `surcharge` float DEFAULT NULL,
  `discount` float DEFAULT NULL,
  `scheduled_date` date NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `payrix_onboarding_status` int DEFAULT '1',
  `payrix_onboarding_error` varchar(250) DEFAULT NULL,
  `payment_category_type_id` int DEFAULT NULL,
  `description` varchar(250) DEFAULT NULL,
  `payment_transaction_type` int DEFAULT '1',
  `for_payment_id` bigint DEFAULT NULL,
  `sessions_count` int DEFAULT NULL,
  `price_per_session` float DEFAULT NULL,
  `renewal_count` int DEFAULT NULL,
  `notes` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `user_id` (`user_id`),
  KEY `payrix_onboarding_status` (`payrix_onboarding_status`),
  KEY `payment_transaction_type` (`payment_transaction_type`),
  KEY `payment_category_type_id` (`payment_category_type_id`),
  CONSTRAINT `member_payment_schedule_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `member_payment_schedule_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`),
  CONSTRAINT `member_payment_schedule_ibfk_4` FOREIGN KEY (`payrix_onboarding_status`) REFERENCES `_ref_payrix_onboard_status_type` (`id`),
  CONSTRAINT `member_payment_schedule_ibfk_5` FOREIGN KEY (`payment_transaction_type`) REFERENCES `_ref_payment_transaction_type` (`id`),
  CONSTRAINT `member_payment_schedule_ibfk_6` FOREIGN KEY (`payment_category_type_id`) REFERENCES `_ref_payment_category_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=519841 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member_payment_schedule`
--

/*!40000 ALTER TABLE `member_payment_schedule` DISABLE KEYS */;
/*!40000 ALTER TABLE `member_payment_schedule` ENABLE KEYS */;

--
-- Table structure for table `member_payment_schedule_temp`
--

DROP TABLE IF EXISTS `member_payment_schedule_temp`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_payment_schedule_temp` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `plan_id` bigint DEFAULT NULL,
  `membership_id` varchar(50) DEFAULT NULL,
  `payment_number` int DEFAULT NULL,
  `plan_start_date` date DEFAULT NULL,
  `plan_end_date` date DEFAULT NULL,
  `auto_renewal` tinyint(1) DEFAULT NULL,
  `discount_percent_per_payment` float DEFAULT NULL,
  `discount_amount_per_payment` float DEFAULT NULL,
  `salesperson_id` bigint DEFAULT NULL,
  `total_amount` float DEFAULT NULL,
  `amount` float DEFAULT NULL,
  `signup_fee` float DEFAULT NULL,
  `tax` float DEFAULT NULL,
  `surcharge` float DEFAULT NULL,
  `discount` float DEFAULT NULL,
  `scheduled_date` date DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `sessions_count` int DEFAULT NULL,
  `price_per_session` float DEFAULT NULL,
  `apply_discount_to_all_payments` tinyint(1) DEFAULT NULL,
  `split_payments` json DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `member_payment_schedule_temp_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `member_payment_schedule_temp_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=504816 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member_payment_schedule_temp`
--

/*!40000 ALTER TABLE `member_payment_schedule_temp` DISABLE KEYS */;
/*!40000 ALTER TABLE `member_payment_schedule_temp` ENABLE KEYS */;

--
-- Table structure for table `member_profile`
--

DROP TABLE IF EXISTS `member_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `member_profile` (
  `user_id` bigint NOT NULL,
  `location_id` bigint NOT NULL,
  `member_status_type_id` int DEFAULT NULL,
  `payment_status_type_id` int DEFAULT NULL,
  `objective_type_id` int DEFAULT NULL,
  `start_date` datetime DEFAULT NULL,
  `last_check_in` datetime DEFAULT NULL,
  `cp_phone_calls` tinyint(1) DEFAULT NULL,
  `cp_email` tinyint(1) DEFAULT NULL,
  `cp_sms` tinyint(1) DEFAULT NULL,
  `cp_in_app_message` tinyint(1) DEFAULT NULL,
  `favourite_gym_clothing_website` varchar(50) DEFAULT NULL,
  `favourite_website` varchar(50) DEFAULT NULL,
  `favourite_restaurant` varchar(50) DEFAULT NULL,
  `payrix_customer_id` varchar(50) DEFAULT NULL,
  `payrix_onboarding_status` int DEFAULT '1',
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `outstanding_balance` float DEFAULT '0',
  `door_access_user_id` varchar(100) DEFAULT NULL,
  `door_access_credential` varchar(100) DEFAULT NULL,
  `door_access_credential_id` varchar(100) DEFAULT NULL,
  `door_access_credential_status` int DEFAULT '1',
  `door_access_auth_info` json DEFAULT NULL,
  `door_access_auth_status` int DEFAULT NULL,
  PRIMARY KEY (`user_id`,`location_id`),
  KEY `location_id` (`location_id`),
  KEY `member_status_type_id` (`member_status_type_id`),
  KEY `payment_status_type_id` (`payment_status_type_id`),
  CONSTRAINT `member_profile_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `member_profile_ibfk_2` FOREIGN KEY (`member_status_type_id`) REFERENCES `_ref_member_status_type` (`id`),
  CONSTRAINT `member_profile_ibfk_3` FOREIGN KEY (`payment_status_type_id`) REFERENCES `_ref_payment_status_type` (`id`),
  CONSTRAINT `member_profile_ibfk_4` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `member_profile`
--

/*!40000 ALTER TABLE `member_profile` DISABLE KEYS */;
INSERT INTO `member_profile` VALUES (8984,43,1,NULL,NULL,'2025-01-03 11:07:07',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8984',3,'2025-01-03 11:07:07','2026-01-01 10:33:29',43.3,NULL,NULL,NULL,1,NULL,NULL),(8985,43,1,NULL,NULL,'2025-01-03 11:07:07',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8985',3,'2025-01-03 11:07:07','2026-01-01 10:33:29',0.0000101089,NULL,NULL,NULL,1,NULL,1),(8986,43,1,NULL,NULL,'2025-01-03 11:07:08',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8986',3,'2025-01-03 11:07:07','2026-01-01 10:33:30',-0.00000686645,NULL,NULL,NULL,1,NULL,NULL),(8987,43,1,NULL,NULL,'2025-01-03 11:07:08',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8987',3,'2025-01-03 11:07:08','2026-01-01 10:33:30',119.08,NULL,NULL,NULL,1,NULL,NULL),(8988,43,1,NULL,NULL,'2025-01-03 11:07:09',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8988',3,'2025-01-03 11:07:08','2025-10-30 21:20:52',0,NULL,NULL,NULL,1,NULL,NULL),(8989,43,1,NULL,NULL,'2025-01-03 11:07:09',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8989',3,'2025-01-03 11:07:08','2025-10-30 21:20:52',0,NULL,NULL,NULL,1,NULL,NULL),(8990,43,1,NULL,NULL,'2025-01-03 11:07:09',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8990',3,'2025-01-03 11:07:09','2026-01-01 10:33:30',0.0000138855,NULL,NULL,NULL,1,NULL,NULL),(8991,43,1,NULL,NULL,'2025-01-03 11:07:10',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8991',3,'2025-01-03 11:07:09','2026-01-01 10:33:30',13.62,NULL,NULL,NULL,1,NULL,NULL),(8992,43,1,NULL,NULL,'2025-01-03 11:07:10',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8992',3,'2025-01-03 11:07:09','2026-01-01 10:33:30',0.0000110245,NULL,NULL,NULL,1,NULL,NULL),(8993,43,1,NULL,NULL,'2025-01-03 11:07:10',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8993',3,'2025-01-03 11:07:10','2026-01-01 10:33:30',238.16,NULL,NULL,NULL,1,NULL,NULL),(8994,43,1,NULL,NULL,'2025-01-03 11:07:11',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8994',3,'2025-01-03 11:07:10','2026-01-01 10:33:30',-0.00000534058,NULL,NULL,NULL,1,NULL,NULL),(8995,43,1,NULL,NULL,'2025-01-03 11:07:11',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8995',3,'2025-01-03 11:07:11','2025-11-11 19:12:07',-30,NULL,NULL,NULL,1,NULL,NULL),(8996,43,1,NULL,NULL,'2025-01-03 11:07:11',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8996',3,'2025-01-03 11:07:11','2025-10-30 21:20:53',0,NULL,NULL,NULL,1,NULL,NULL),(8997,43,1,NULL,NULL,'2025-01-03 11:07:12',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8997',3,'2025-01-03 11:07:11','2025-10-30 21:20:53',0,NULL,NULL,NULL,1,NULL,NULL),(8998,43,1,NULL,NULL,'2025-01-03 11:07:12',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8998',3,'2025-01-03 11:07:12','2026-01-01 10:33:30',0.00000827789,NULL,NULL,NULL,1,NULL,1),(8999,43,1,NULL,NULL,'2025-01-03 11:07:13',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo8999',3,'2025-01-03 11:07:12','2025-10-30 21:20:54',0,NULL,NULL,NULL,1,NULL,NULL),(9000,43,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'p1_cus_demo9000',3,'2025-01-03 11:07:12','2025-10-30 21:20:54',0,NULL,NULL,NULL,1,NULL,NULL),(9001,43,1,NULL,NULL,'2025-01-03 11:07:13',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9001',3,'2025-01-03 11:07:13','2026-01-01 10:33:30',80.1,NULL,NULL,NULL,1,NULL,NULL),(9002,43,1,NULL,NULL,'2025-01-03 11:07:14',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9002',3,'2025-01-03 11:07:13','2026-01-01 10:33:30',75.78,NULL,NULL,NULL,1,NULL,1),(9003,43,1,NULL,NULL,'2025-01-03 11:07:14',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9003',3,'2025-01-03 11:07:14','2026-01-01 10:33:30',0.0000100708,NULL,NULL,NULL,1,NULL,NULL),(9004,43,1,NULL,NULL,'2025-01-03 11:07:14',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9004',3,'2025-01-03 11:07:14','2025-10-30 21:20:55',108.25,NULL,NULL,NULL,1,NULL,NULL),(9005,43,1,NULL,NULL,'2025-01-03 11:07:15',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9005',3,'2025-01-03 11:07:14','2025-10-30 21:20:55',0,NULL,NULL,NULL,1,NULL,NULL),(9006,43,1,NULL,NULL,'2025-01-03 11:07:15',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9006',3,'2025-01-03 11:07:15','2026-01-01 10:33:30',54.12,NULL,NULL,NULL,1,NULL,1),(9007,43,1,NULL,NULL,'2025-01-03 11:07:15',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9007',3,'2025-01-03 11:07:15','2026-01-01 10:33:30',162.36,NULL,NULL,NULL,1,NULL,NULL),(9008,43,1,NULL,NULL,NULL,NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9008',3,'2025-01-03 11:07:15','2026-01-01 10:33:30',-0.00000213623,NULL,NULL,NULL,1,NULL,NULL),(9009,43,1,NULL,NULL,'2025-01-03 11:07:16',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9009',3,'2025-01-03 11:07:16','2026-01-01 10:33:31',-0.0000146484,NULL,NULL,NULL,1,NULL,NULL),(9010,43,1,NULL,NULL,'2025-01-03 11:07:17',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9010',3,'2025-01-03 11:07:16','2026-01-01 10:33:31',-0.0000146484,NULL,NULL,NULL,1,NULL,NULL),(9011,43,1,NULL,NULL,'2025-01-03 11:07:17',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9011',3,'2025-01-03 11:07:16','2025-10-30 21:20:56',0,NULL,NULL,NULL,1,NULL,NULL),(9012,43,1,NULL,NULL,'2025-01-03 11:07:17',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9012',3,'2025-01-03 11:07:17','2026-01-01 10:33:31',173.2,NULL,NULL,NULL,1,NULL,NULL),(9013,43,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'p1_cus_demo9013',3,'2025-01-03 11:07:17','2025-10-30 21:20:57',0,NULL,NULL,NULL,1,NULL,NULL),(9014,43,1,NULL,NULL,'2025-01-03 11:07:18',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9014',3,'2025-01-03 11:07:18','2026-01-01 10:33:31',-0.0000138855,NULL,NULL,NULL,1,NULL,1),(9015,43,1,NULL,NULL,'2025-01-03 11:07:18',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9015',3,'2025-01-03 11:07:18','2025-12-30 23:09:05',0,NULL,NULL,NULL,1,NULL,NULL),(9016,43,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'p1_cus_demo9016',3,'2025-01-03 11:07:18','2025-12-28 10:15:54',0,NULL,NULL,NULL,1,NULL,NULL),(9017,43,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'p1_cus_demo9017',3,'2025-01-03 11:07:19','2026-01-01 10:33:31',-0.00000610352,NULL,NULL,NULL,1,NULL,NULL),(9018,43,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'p1_cus_demo9018',3,'2025-01-03 11:07:19','2026-01-01 10:33:31',-0.0000157166,NULL,NULL,NULL,1,NULL,1),(9019,43,1,NULL,NULL,'2025-01-03 11:07:20',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9019',3,'2025-01-03 11:07:19','2026-01-01 10:33:31',9.08001,NULL,NULL,NULL,1,NULL,NULL),(9020,43,1,NULL,NULL,'2025-01-03 11:07:20',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9020',3,'2025-01-03 11:07:20','2026-01-01 10:33:31',59.54,NULL,NULL,NULL,1,NULL,NULL),(9021,43,1,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'p1_cus_demo9021',3,'2025-01-03 11:07:20','2026-01-01 10:33:31',-0.0000732422,NULL,NULL,NULL,1,NULL,NULL),(9022,43,1,NULL,NULL,'2025-01-03 11:07:21',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9022',3,'2025-01-03 11:07:20','2026-01-01 10:33:31',0.0000100708,NULL,NULL,NULL,1,NULL,1),(9023,43,1,NULL,NULL,'2025-01-03 11:07:21',NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo9023',3,'2025-01-03 11:07:21','2026-01-01 10:33:31',55.23,NULL,NULL,NULL,1,NULL,NULL),(13545,43,1,NULL,NULL,NULL,NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo13545',3,'2025-04-02 20:03:01','2025-04-02 21:16:47',0,NULL,NULL,NULL,1,NULL,NULL),(34183,43,1,NULL,NULL,NULL,NULL,0,0,0,0,NULL,NULL,NULL,'p1_cus_demo34183',3,'2025-09-10 16:26:28','2025-09-10 16:26:29',0,NULL,NULL,NULL,1,NULL,NULL);
/*!40000 ALTER TABLE `member_profile` ENABLE KEYS */;

--
-- Table structure for table `membership`
--

DROP TABLE IF EXISTS `membership`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membership` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `plan_id` bigint NOT NULL,
  `signup_fee` float DEFAULT NULL,
  `plan_start_date` date NOT NULL,
  `plan_end_date` date DEFAULT NULL,
  `auto_renewal` tinyint(1) DEFAULT NULL,
  `discount_percent_per_payment` float DEFAULT NULL,
  `discount_amount_per_payment` float DEFAULT NULL,
  `membership_status_type_id` int NOT NULL,
  `salesperson_id` bigint DEFAULT NULL,
  `sessions_count` int DEFAULT NULL,
  `freeze_from` date DEFAULT NULL,
  `freeze_to` date DEFAULT NULL,
  `freeze_reason_type_id` int DEFAULT NULL,
  `unfreeze_date` date DEFAULT NULL,
  `cancel_date` date DEFAULT NULL,
  `cancel_reason_type_id` int DEFAULT NULL,
  `non_renewal` tinyint(1) DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `freeze_by` bigint DEFAULT NULL,
  `freeze_date` date DEFAULT NULL,
  `unfreeze_by` bigint DEFAULT NULL,
  `cancelled_by` bigint DEFAULT NULL,
  `cancelled_date` datetime DEFAULT NULL,
  `new_contract_value` float DEFAULT NULL,
  `renewal_count` int DEFAULT NULL,
  `apply_discount_to_all_payments` tinyint(1) DEFAULT NULL,
  `final_payment_date` date DEFAULT NULL,
  `split_payments` json DEFAULT NULL,
  `cancel_description` varchar(100) DEFAULT NULL,
  `next_billing_date` date DEFAULT NULL,
  `next_billing_amount` float DEFAULT '0',
  `apply_next_billing_date_to_all_invoices` tinyint(1) DEFAULT '0',
  `previous_membership_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `plan_id` (`plan_id`),
  KEY `user_id` (`user_id`),
  KEY `freeze_reason_type_id` (`freeze_reason_type_id`),
  KEY `cancel_reason_type_id` (`cancel_reason_type_id`),
  KEY `membership_ibfk_6` (`previous_membership_id`),
  CONSTRAINT `membership_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `membership_ibfk_2` FOREIGN KEY (`plan_id`) REFERENCES `plan` (`id`),
  CONSTRAINT `membership_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`),
  CONSTRAINT `membership_ibfk_4` FOREIGN KEY (`freeze_reason_type_id`) REFERENCES `_ref_freeze_reason_type` (`id`),
  CONSTRAINT `membership_ibfk_5` FOREIGN KEY (`cancel_reason_type_id`) REFERENCES `_ref_cancel_reason_type` (`id`),
  CONSTRAINT `membership_ibfk_6` FOREIGN KEY (`previous_membership_id`) REFERENCES `membership` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30781 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `membership`
--

/*!40000 ALTER TABLE `membership` DISABLE KEYS */;
INSERT INTO `membership` VALUES (6185,43,9010,683,0,'2025-02-01','2026-02-01',1,NULL,15,2,NULL,0,NULL,NULL,NULL,NULL,'2025-01-21',1,0,'2025-01-08 19:14:42','2025-01-21 15:34:24',NULL,NULL,NULL,1798,'2025-01-21 15:34:23',1044.68,0,0,'2026-01-31','[]',NULL,NULL,NULL,0,NULL),(6538,43,9014,682,0,'2025-01-18','2026-01-18',1,NULL,4,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-13 21:25:27','2025-12-20 10:00:07',NULL,NULL,NULL,NULL,NULL,730.62,0,1,'2026-01-17','[]',NULL,'2026-01-03',27.06,0,NULL),(6539,43,9014,1203,0,'2026-04-18','2027-04-18',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-13 21:30:57','2025-09-06 08:18:28',NULL,NULL,NULL,NULL,NULL,25,0,0,NULL,'[]',NULL,'2027-04-19',25,0,NULL),(6553,43,9017,1195,0,'2025-01-13','2025-02-09',1,0,0,2,NULL,0,NULL,NULL,NULL,NULL,'2025-01-22',1,0,'2025-01-13 23:22:38','2025-01-22 20:07:46',NULL,NULL,NULL,1798,'2025-01-22 20:07:46',129.9,0,0,'2025-01-13','[]',NULL,NULL,NULL,0,NULL),(6555,43,9017,1203,0,'2025-10-01','2026-10-01',1,0,0,2,NULL,0,NULL,NULL,NULL,NULL,'2025-02-11',1,0,'2025-01-13 23:25:41','2025-02-11 23:21:24',NULL,NULL,NULL,1798,'2025-02-11 23:21:24',25,0,0,NULL,'[]',NULL,NULL,NULL,0,NULL),(6559,43,8994,683,0,'2025-01-17','2026-01-17',1,NULL,15,2,NULL,0,NULL,NULL,NULL,NULL,'2025-01-13',2,0,'2025-01-13 23:42:33','2025-01-14 00:28:47',NULL,NULL,NULL,1798,'2025-01-14 00:28:47',1044.68,0,0,'2026-01-16','[]',NULL,NULL,NULL,0,NULL),(6573,43,8994,683,0,'2025-01-17','2026-01-17',1,15,0,2,NULL,0,NULL,NULL,NULL,NULL,'2025-01-13',2,0,'2025-01-14 00:29:13','2025-01-14 00:30:34',NULL,NULL,NULL,1798,'2025-01-14 00:30:33',901.74,0,1,'2026-01-16','[]',NULL,NULL,NULL,0,NULL),(6575,43,8994,683,0,'2025-01-17','2026-01-17',1,20,0,2,NULL,0,NULL,NULL,NULL,NULL,'2025-07-23',1,0,'2025-01-14 00:31:08','2025-07-24 01:52:05',NULL,NULL,NULL,1798,'2025-07-24 01:52:05',848.68,0,1,'2026-01-16','[]','None',NULL,NULL,0,NULL),(6672,43,9002,683,0,'2024-07-01','2026-07-01',1,NULL,NULL,2,NULL,0,NULL,NULL,NULL,NULL,'2025-07-17',1,0,'2025-01-15 15:38:37','2025-07-18 02:50:34',NULL,NULL,NULL,1798,'2025-07-18 02:50:34',NULL,2,0,'2026-06-17',NULL,'None',NULL,NULL,0,NULL),(6685,43,9004,1195,0,'2024-06-02','2026-02-07',1,NULL,20,2,NULL,0,NULL,NULL,NULL,NULL,'2025-06-06',1,0,'2025-01-15 15:38:38','2025-06-06 19:08:27',NULL,NULL,NULL,1798,'2025-06-06 19:08:26',NULL,2,1,'2026-01-29',NULL,'None',NULL,NULL,0,NULL),(6695,43,8995,1195,0,'2024-08-27','2026-02-09',1,NULL,65,2,NULL,0,NULL,NULL,NULL,NULL,'2025-02-18',1,0,'2025-01-15 15:38:38','2025-02-18 17:40:11',NULL,NULL,NULL,1798,'2025-02-18 17:40:11',NULL,2,1,'2026-02-02',NULL,NULL,NULL,NULL,0,NULL),(6710,43,9001,999,0,'2024-12-09','2025-02-08',1,NULL,35,2,NULL,0,NULL,NULL,NULL,NULL,'2025-02-06',1,0,'2025-01-15 15:38:39','2025-02-06 17:26:17',NULL,NULL,NULL,1798,'2025-02-06 17:26:17',NULL,1,1,'2025-02-06',NULL,NULL,NULL,NULL,0,NULL),(6711,43,9000,683,0,'2024-01-09','2026-01-08',1,NULL,20,2,NULL,0,NULL,NULL,NULL,NULL,'2025-04-16',1,0,'2025-01-15 15:38:39','2025-04-16 19:24:23',NULL,NULL,NULL,1798,'2025-04-16 19:24:23',NULL,1,1,'2026-01-08',NULL,'None',NULL,NULL,0,NULL),(6712,43,9009,683,0,'2024-09-09','2026-09-09',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-15 15:38:39','2025-12-11 10:00:03',NULL,NULL,NULL,NULL,NULL,NULL,2,0,'2025-08-21',NULL,NULL,'2026-01-08',75.78,0,NULL),(6717,43,9016,1195,0,'2023-06-29','2026-02-04',1,NULL,20,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-15 15:38:40','2025-12-28 10:00:04',NULL,NULL,NULL,NULL,NULL,NULL,2,1,'2026-01-09',NULL,NULL,'2026-01-25',108.25,0,NULL),(6721,43,9011,683,0,'2024-08-14','2025-08-13',1,NULL,5,2,NULL,0,NULL,NULL,NULL,NULL,'2025-04-16',1,0,'2025-01-15 15:38:40','2025-04-16 19:23:39',NULL,NULL,NULL,1798,'2025-04-16 19:23:39',NULL,1,1,'2025-07-26',NULL,'None',NULL,NULL,0,NULL),(6727,43,8993,683,0,'2024-08-12','2026-08-12',1,NULL,15,2,NULL,0,NULL,NULL,NULL,NULL,'2025-08-28',3,0,'2025-01-15 15:38:41','2025-08-28 18:05:41',NULL,NULL,NULL,1798,'2025-08-28 18:05:41',NULL,2,1,'2026-07-26',NULL,'None',NULL,NULL,0,NULL),(6735,43,8987,683,0,'2023-06-29','2026-06-29',0,NULL,15,2,NULL,0,NULL,NULL,NULL,NULL,'2025-11-14',5,NULL,'2025-01-15 15:38:41','2025-11-14 14:34:12',NULL,NULL,NULL,1798,'2025-11-14 00:00:00',NULL,2,1,'2026-06-29',NULL,'None','2025-11-17',59.54,0,NULL),(6736,43,8991,683,0,'2024-11-13','2025-11-12',1,NULL,NULL,2,NULL,0,NULL,NULL,NULL,NULL,'2025-03-11',1,0,'2025-01-15 15:38:41','2025-03-12 00:09:29',NULL,NULL,NULL,1798,'2025-03-12 00:09:29',NULL,1,0,'2025-10-20',NULL,'None',NULL,NULL,0,NULL),(6737,43,9006,683,0,'2023-11-13','2026-11-13',1,NULL,20,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-15 15:38:41','2025-12-22 10:00:10',NULL,NULL,NULL,NULL,NULL,NULL,2,1,'2025-10-20',NULL,NULL,'2026-01-19',54.12,0,NULL),(6749,43,8985,683,0,'2023-06-29','2026-06-29',1,NULL,15,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-15 15:38:42','2025-12-17 10:00:05',NULL,NULL,NULL,NULL,NULL,NULL,2,1,'2026-06-03',NULL,NULL,'2026-01-14',59.54,0,NULL),(6758,43,9013,1195,0,'2024-06-17','2026-01-25',1,NULL,20,2,NULL,0,NULL,NULL,NULL,NULL,'2025-07-09',10,0,'2025-01-15 15:38:43','2025-07-09 18:09:25',NULL,NULL,NULL,1798,'2025-07-09 18:09:25',NULL,2,1,'2026-01-16',NULL,'None',NULL,NULL,0,NULL),(6759,43,9005,683,0,'2023-10-17','2025-10-16',1,NULL,NULL,2,NULL,0,NULL,NULL,NULL,NULL,'2025-03-10',1,0,'2025-01-15 15:38:43','2025-03-10 20:54:04',NULL,NULL,NULL,1798,'2025-03-10 20:54:04',NULL,1,0,'2025-09-26',NULL,'None',NULL,NULL,0,NULL),(6763,43,9018,1195,0,'2024-11-18','2025-02-09',1,NULL,70,2,NULL,0,NULL,NULL,NULL,NULL,'2025-02-06',1,0,'2025-01-15 15:38:43','2025-02-06 15:25:24',NULL,NULL,NULL,1798,'2025-02-06 15:25:24',NULL,1,1,'2025-01-18',NULL,NULL,NULL,NULL,0,NULL),(6764,43,9014,683,0,'2024-12-18','2025-12-17',1,NULL,20,2,NULL,0,NULL,NULL,NULL,NULL,'2025-01-27',1,0,'2025-01-15 15:38:43','2025-01-27 18:27:55',NULL,NULL,NULL,1798,'2025-01-27 18:27:55',NULL,1,1,'2025-11-22',NULL,NULL,NULL,NULL,0,NULL),(6765,43,9015,683,0,'2023-09-18','2025-09-17',1,NULL,NULL,2,NULL,0,NULL,NULL,NULL,NULL,'2025-07-19',2,0,'2025-01-15 15:38:43','2025-07-19 09:30:00',NULL,NULL,NULL,1798,'2025-07-19 09:30:00',NULL,1,0,'2025-08-30',NULL,'None',NULL,NULL,0,NULL),(6772,43,9003,683,0,'2024-06-19','2026-06-19',0,NULL,15,2,NULL,0,NULL,NULL,NULL,NULL,'2025-12-23',5,NULL,'2025-01-15 15:38:44','2025-12-23 19:27:29',NULL,NULL,NULL,1798,'2025-12-23 00:00:00',NULL,2,1,'2026-06-07',NULL,'None','2026-01-18',59.54,0,NULL),(6773,43,9019,683,0,'2024-06-19','2026-06-19',0,NULL,15,2,NULL,0,NULL,NULL,NULL,NULL,'2025-09-08',1,NULL,'2025-01-15 15:38:44','2025-09-08 19:03:38',NULL,NULL,NULL,1798,'2025-09-08 00:00:00',NULL,2,1,'2026-06-07',NULL,'None','2025-09-28',59.54,0,NULL),(6783,43,9007,683,0,'2023-09-21','2025-09-20',1,NULL,20,2,NULL,0,NULL,NULL,NULL,NULL,'2025-03-27',1,0,'2025-01-15 15:38:44','2025-03-27 13:30:28',NULL,NULL,NULL,1798,'2025-03-27 13:30:28',NULL,1,1,'2025-09-02',NULL,'None',NULL,NULL,0,NULL),(6784,43,9008,683,0,'2024-11-21','2025-11-20',1,NULL,15,2,NULL,0,NULL,NULL,NULL,NULL,'2025-01-21',1,0,'2025-01-15 15:38:44','2025-01-21 16:14:01',NULL,NULL,NULL,1798,'2025-01-21 16:14:01',NULL,1,1,'2025-10-28',NULL,NULL,NULL,NULL,0,NULL),(6792,43,8984,683,0,'2024-08-23','2025-08-22',1,NULL,30,2,NULL,0,NULL,NULL,NULL,NULL,'2025-02-17',1,0,'2025-01-15 15:38:45','2025-02-17 18:37:05',NULL,NULL,NULL,1798,'2025-02-17 18:37:05',NULL,1,1,'2025-08-07',NULL,NULL,NULL,NULL,0,NULL),(6793,43,8989,683,0,'2023-06-29','2025-06-28',1,NULL,15,2,NULL,0,NULL,NULL,NULL,NULL,'2025-03-10',1,0,'2025-01-15 15:38:45','2025-03-10 20:58:43',NULL,NULL,NULL,1798,'2025-03-10 20:58:43',NULL,1,1,'2025-06-12',NULL,'None',NULL,NULL,0,NULL),(6799,43,8998,1195,0,'2024-01-04','2025-01-29',1,NULL,35,2,NULL,0,NULL,NULL,NULL,NULL,'2025-01-21',1,0,'2025-01-15 15:38:45','2025-01-21 18:40:03',NULL,NULL,NULL,1798,'2025-01-21 18:40:03',NULL,1,1,'2025-01-24',NULL,NULL,NULL,NULL,0,NULL),(6805,43,8986,683,0,'2024-01-25','2026-01-25',1,NULL,20,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-15 15:38:46','2025-12-27 10:00:04',NULL,NULL,NULL,NULL,NULL,NULL,2,1,'2026-01-24',NULL,NULL,'2026-01-24',54.12,0,NULL),(6812,43,8990,683,0,'2023-06-29','2026-06-29',1,NULL,15,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-15 15:38:46','2025-12-28 10:00:04',NULL,NULL,NULL,NULL,NULL,NULL,2,1,'2026-06-14',NULL,NULL,'2026-01-25',59.54,0,NULL),(6825,43,8996,683,0,'2024-08-30','2025-08-29',1,NULL,25,2,NULL,0,NULL,NULL,NULL,NULL,'2025-03-10',1,0,'2025-01-15 15:38:47','2025-03-10 21:08:21',NULL,NULL,NULL,1798,'2025-03-10 21:08:21',NULL,1,1,'2025-08-11',NULL,'None',NULL,NULL,0,NULL),(6826,43,8999,683,0,'2024-09-27','2025-09-26',1,NULL,10,2,NULL,0,NULL,NULL,NULL,NULL,'2025-07-18',2,0,'2025-01-15 15:38:47','2025-07-18 20:23:32',NULL,NULL,NULL,1798,'2025-07-18 20:23:32',NULL,1,1,'2025-09-08',NULL,'None',NULL,NULL,0,NULL),(6833,43,8992,683,0,'2024-07-29','2026-07-29',1,NULL,15,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-15 15:38:48','2025-12-31 10:00:04',NULL,NULL,NULL,NULL,NULL,NULL,2,1,'2026-07-15',NULL,NULL,'2026-01-28',59.54,0,NULL),(6837,43,9012,999,0,'2024-03-30','2026-01-28',1,NULL,0,2,NULL,0,NULL,NULL,NULL,NULL,'2025-03-10',1,0,'2025-01-15 15:38:48','2025-03-10 21:22:28',NULL,NULL,NULL,1798,'2025-03-10 21:22:28',NULL,2,1,'2026-01-01',NULL,'None',NULL,NULL,0,NULL),(6843,43,8988,683,0,'2024-07-31','2025-07-30',1,NULL,NULL,2,NULL,0,NULL,NULL,NULL,NULL,'2025-03-10',1,0,'2025-01-15 15:38:48','2025-03-10 21:11:39',NULL,NULL,NULL,1798,'2025-03-10 21:11:39',NULL,1,0,'2025-07-18',NULL,'None',NULL,NULL,0,NULL),(6853,43,8997,1195,0,'2024-09-23','2026-02-08',1,NULL,NULL,2,NULL,0,NULL,NULL,NULL,NULL,'2025-03-10',1,0,'2025-01-15 15:38:49','2025-03-10 21:12:47',NULL,NULL,NULL,1798,'2025-03-10 21:12:47',NULL,2,0,'2026-01-22',NULL,'None',NULL,NULL,0,NULL),(7238,43,9010,682,0,'2025-02-01','2026-02-01',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-21 15:34:52','2025-12-20 10:00:07',NULL,NULL,NULL,NULL,NULL,847.53,0,0,'2026-01-31','[]',NULL,'2026-01-03',31.39,0,NULL),(7239,43,9010,1203,0,'2025-04-25','2026-04-25',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-21 15:35:19','2025-09-06 08:18:28',NULL,NULL,NULL,NULL,NULL,25,0,0,NULL,'[]',NULL,'2026-04-26',25,0,NULL),(7253,43,9008,682,20,'2025-02-20','2026-05-24',1,0,0,2,NULL,0,NULL,NULL,NULL,'2025-06-16','2025-07-17',2,0,'2025-01-21 16:15:12','2025-07-17 20:11:31',NULL,NULL,0,1798,'2025-07-17 20:11:30',869.18,0,0,'2026-05-18','[]','None',NULL,NULL,0,NULL),(7255,43,9008,1203,0,'2025-03-01','2026-03-01',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-21 16:17:35','2025-09-06 08:18:28',NULL,NULL,NULL,NULL,NULL,25,0,0,NULL,'[]',NULL,'2026-03-02',25,0,NULL),(7273,43,8998,682,0,'2025-01-21','2026-01-21',1,100,0,2,NULL,0,NULL,NULL,NULL,NULL,'2025-02-15',1,0,'2025-01-21 18:40:16','2025-02-15 16:09:22',NULL,NULL,NULL,1798,'2025-02-15 16:09:22',NULL,NULL,1,NULL,'[]',NULL,NULL,NULL,0,NULL),(7340,43,9017,1195,0,'2025-01-24','2025-02-20',1,0,0,2,NULL,0,NULL,NULL,NULL,NULL,'2025-01-22',1,0,'2025-01-22 20:09:15','2025-01-22 20:09:38',NULL,NULL,NULL,1798,'2025-01-22 20:09:38',129.9,0,0,'2025-01-24','[]',NULL,NULL,NULL,0,NULL),(8340,43,9018,682,0,'2025-02-12','2026-02-12',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-02-06 15:26:03','2025-12-31 10:00:04',NULL,NULL,NULL,NULL,NULL,847.53,0,0,'2026-02-11','[]',NULL,'2026-01-14',31.39,0,NULL),(8341,43,9018,1203,0,'2025-04-25','2026-04-25',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-02-06 15:26:25','2025-09-06 08:18:29',NULL,NULL,NULL,NULL,NULL,25,0,0,NULL,'[]',NULL,'2026-04-26',25,0,NULL),(8350,43,8994,1203,0,'2025-04-25','2026-04-25',1,0,0,2,NULL,0,NULL,NULL,NULL,NULL,'2025-07-23',1,0,'2025-02-06 17:08:34','2025-07-24 01:52:11',NULL,NULL,NULL,1798,'2025-07-24 01:52:11',25,0,0,NULL,'[]','None',NULL,NULL,0,NULL),(8354,43,9001,682,0,'2025-04-25','2026-04-25',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-02-06 17:26:49','2025-12-19 10:00:09',NULL,NULL,NULL,NULL,NULL,847.53,0,0,'2026-04-24','[]',NULL,'2026-01-02',31.39,0,NULL),(8355,43,9001,1203,0,'2025-04-06','2026-04-06',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-02-06 17:28:14','2025-09-06 08:18:28',NULL,NULL,NULL,NULL,NULL,25,0,0,NULL,'[]',NULL,'2026-04-07',25,0,NULL),(8747,43,8998,683,0,'2025-02-24','2026-02-24',0,NULL,15,2,NULL,0,NULL,NULL,NULL,NULL,'2025-12-02',5,NULL,'2025-02-15 16:10:05','2025-12-02 14:35:47',NULL,NULL,NULL,1798,'2025-12-02 00:00:00',833.56,0,1,'2026-02-23','[]','None','2025-12-29',59.54,0,NULL),(8865,43,9003,1203,0,'2025-04-25','2026-04-25',0,0,0,2,NULL,0,NULL,NULL,NULL,NULL,'2025-12-23',5,NULL,'2025-02-18 15:13:23','2025-12-23 19:27:36',NULL,NULL,NULL,1798,'2025-12-23 00:00:00',25,0,0,NULL,'[]','None','2026-04-26',25,0,NULL),(8888,43,9009,1203,0,'2025-04-25','2026-04-25',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-02-18 17:23:30','2025-09-06 08:18:28',NULL,NULL,NULL,NULL,NULL,25,0,0,NULL,'[]',NULL,'2026-04-26',25,0,NULL),(8889,43,8985,1203,0,'2025-04-25','2026-04-25',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-02-18 17:26:16','2025-09-06 08:18:27',NULL,NULL,NULL,NULL,NULL,25,0,0,NULL,'[]',NULL,'2026-04-26',25,0,NULL),(8908,43,8986,1203,0,'2025-04-25','2026-04-25',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-02-18 19:59:09','2025-09-06 08:18:27',NULL,NULL,NULL,NULL,NULL,25,0,0,NULL,'[]',NULL,'2026-04-26',25,0,NULL),(9884,43,8991,683,0,'2025-03-13','2026-03-13',1,NULL,15,2,NULL,0,NULL,NULL,NULL,NULL,'2025-06-13',10,0,'2025-03-12 00:10:17','2025-06-13 10:00:00',NULL,NULL,NULL,1798,'2025-06-13 10:00:00',833.56,0,1,'2026-03-12','[]','None',NULL,NULL,0,NULL),(20332,43,9002,683,0,'2025-07-17','2026-07-17',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-07-18 02:51:18','2026-01-01 10:00:12',NULL,NULL,NULL,NULL,NULL,1050.09,0,0,'2026-07-16','[]',NULL,'2026-01-29',75.78,0,NULL),(29640,43,8998,3380,0,'2025-12-02','2035-12-02',1,0,0,1,NULL,0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-12-02 14:35:55','2025-12-02 14:36:06',NULL,NULL,NULL,NULL,NULL,NULL,NULL,0,NULL,'[]',NULL,NULL,NULL,0,NULL);
/*!40000 ALTER TABLE `membership` ENABLE KEYS */;

--
-- Table structure for table `membership_freeze`
--

DROP TABLE IF EXISTS `membership_freeze`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membership_freeze` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `membership_id` bigint NOT NULL,
  `freeze_from` date DEFAULT NULL,
  `freeze_to` date DEFAULT NULL,
  `freeze_date` date DEFAULT NULL,
  `freeze_reason_type_id` int DEFAULT NULL,
  `freeze_by` bigint DEFAULT NULL,
  `unfreeze_date` date DEFAULT NULL,
  `unfreeze_by` bigint DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `user_id` (`user_id`),
  KEY `membership_id` (`membership_id`),
  KEY `freeze_reason_type_id` (`freeze_reason_type_id`),
  CONSTRAINT `membership_edit_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `membership_edit_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`),
  CONSTRAINT `membership_edit_ibfk_3` FOREIGN KEY (`membership_id`) REFERENCES `membership` (`id`),
  CONSTRAINT `membership_edit_ibfk_4` FOREIGN KEY (`freeze_reason_type_id`) REFERENCES `_ref_freeze_reason_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1582 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `membership_freeze`
--

/*!40000 ALTER TABLE `membership_freeze` DISABLE KEYS */;
/*!40000 ALTER TABLE `membership_freeze` ENABLE KEYS */;

--
-- Table structure for table `membership_session`
--

DROP TABLE IF EXISTS `membership_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `membership_session` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `user_id` bigint NOT NULL,
  `membership_id` bigint NOT NULL,
  `sessions_count` int DEFAULT NULL,
  `price_per_session` float DEFAULT NULL,
  `sessions_purchase_date` date DEFAULT NULL,
  `updated_by` bigint DEFAULT NULL,
  `notes` varchar(250) DEFAULT NULL,
  `total_amount` float DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `membership_id` (`membership_id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `membership_session_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `membership_session_ibfk_2` FOREIGN KEY (`membership_id`) REFERENCES `membership` (`id`),
  CONSTRAINT `membership_session_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `member_profile` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2274 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `membership_session`
--

/*!40000 ALTER TABLE `membership_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `membership_session` ENABLE KEYS */;

--
-- Table structure for table `payrix_disbursement`
--

DROP TABLE IF EXISTS `payrix_disbursement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payrix_disbursement` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `payrix_disbursement_id` varchar(50) NOT NULL,
  `payrix_disbursement_status_type_id` int NOT NULL,
  `payrix_created` datetime NOT NULL,
  `payrix_processed` datetime DEFAULT NULL,
  `amount` float DEFAULT NULL,
  `sales` float DEFAULT '0',
  `e_check_sales` float DEFAULT '0',
  `refunds` float DEFAULT '0',
  `e_check_refunds` float DEFAULT '0',
  `chargebacks` float DEFAULT '0',
  `e_check_chargebacks` float DEFAULT '0',
  `remainder` float DEFAULT '0',
  `remainder_used` float DEFAULT '0',
  `other_events` float DEFAULT '0',
  `auth_fees` float DEFAULT '0',
  `payout_fees` float DEFAULT '0',
  `capture_fees` float DEFAULT '0',
  `interchange_fees` float DEFAULT '0',
  `refund_fees` float DEFAULT '0',
  `chargeback_fees` float DEFAULT '0',
  `e_check_sale_fees` float DEFAULT '0',
  `e_check_refund_fees` float DEFAULT '0',
  `e_check_chargeback_fees` float DEFAULT '0',
  `other_fees` float DEFAULT '0',
  `in_process` tinyint(1) NOT NULL DEFAULT '0',
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `go_fees` float DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `payrix_disbursement_ibfk_2` (`payrix_disbursement_status_type_id`),
  CONSTRAINT `payrix_disbursement_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `payrix_disbursement_ibfk_2` FOREIGN KEY (`payrix_disbursement_status_type_id`) REFERENCES `_ref_payrix_disbursement_status_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=54003 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payrix_disbursement`
--

/*!40000 ALTER TABLE `payrix_disbursement` DISABLE KEYS */;
/*!40000 ALTER TABLE `payrix_disbursement` ENABLE KEYS */;

--
-- Table structure for table `payrix_fee`
--

DROP TABLE IF EXISTS `payrix_fee`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payrix_fee` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint NOT NULL,
  `payrix_entity_id` varchar(50) NOT NULL,
  `payrix_disbursement_id` varchar(50) NOT NULL,
  `payrix_transaction_id` varchar(50) NOT NULL,
  `payrix_fee_id` varchar(50) NOT NULL,
  `description` varchar(200) NOT NULL,
  `amount` float NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1125311 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payrix_fee`
--

/*!40000 ALTER TABLE `payrix_fee` DISABLE KEYS */;
/*!40000 ALTER TABLE `payrix_fee` ENABLE KEYS */;

--
-- Table structure for table `payrix_log`
--

DROP TABLE IF EXISTS `payrix_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payrix_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `resource` int NOT NULL,
  `resource_id` varchar(50) DEFAULT NULL,
  `request_type` varchar(10) DEFAULT NULL,
  `request_url` varchar(250) NOT NULL,
  `request_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `request_payload` json DEFAULT NULL,
  `response_payload` json DEFAULT NULL,
  `response_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `response_status_code` int DEFAULT NULL,
  `error` varchar(1000) DEFAULT NULL,
  `location_id` bigint DEFAULT NULL,
  `user_id` bigint DEFAULT NULL,
  `payment_id` bigint DEFAULT NULL,
  `payment_method_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=143709 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payrix_log`
--

/*!40000 ALTER TABLE `payrix_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `payrix_log` ENABLE KEYS */;

--
-- Table structure for table `payrix_updates_log`
--

DROP TABLE IF EXISTS `payrix_updates_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `payrix_updates_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `payrix_resource` int NOT NULL,
  `payrix_request_payload` json DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `payrix_transaction_id` varchar(50) DEFAULT NULL,
  `payrix_transaction_status` int DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=210282 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `payrix_updates_log`
--

/*!40000 ALTER TABLE `payrix_updates_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `payrix_updates_log` ENABLE KEYS */;

--
-- Table structure for table `plan`
--

DROP TABLE IF EXISTS `plan`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plan` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `duration` float DEFAULT NULL,
  `signup_fee` float DEFAULT NULL,
  `recurring_amount` float DEFAULT NULL,
  `recurring_interval` float DEFAULT NULL,
  `classes_per_week` int DEFAULT NULL,
  `unlimited` tinyint(1) DEFAULT NULL,
  `auto_renewal` tinyint(1) DEFAULT NULL,
  `paid_in_full_price` float DEFAULT NULL,
  `limit_total_classes` tinyint(1) DEFAULT NULL,
  `class_or_session_pack_price` float DEFAULT NULL,
  `pass_limit` int DEFAULT NULL,
  `pass_expiration` int DEFAULT NULL,
  `trial` tinyint(1) DEFAULT NULL,
  `challenge` tinyint(1) DEFAULT NULL,
  `grandfathered` tinyint(1) DEFAULT NULL,
  `check_in_required` tinyint(1) DEFAULT NULL,
  `booking_required` tinyint(1) DEFAULT NULL,
  `min_age` int DEFAULT NULL,
  `max_age` int DEFAULT NULL,
  `access_for_24_hrs` tinyint(1) DEFAULT NULL,
  `revenue_rate` float DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `location_id` bigint NOT NULL,
  `duration_type_id` int DEFAULT '1',
  `billing_type_id` int NOT NULL,
  `recurring_duration_type_id` int DEFAULT '1',
  `pass_expiration_duration_type_id` int DEFAULT '1',
  `plan_status_type_id` int DEFAULT NULL,
  `sessions_count` int DEFAULT NULL,
  `sessions_limit_times` int DEFAULT NULL,
  `sessions_limit_every` int DEFAULT NULL,
  `sessions_limit_duration_type_id` int DEFAULT '1',
  `membership_type_id` int DEFAULT NULL,
  `first_of_month` tinyint(1) DEFAULT NULL,
  `taxable` tinyint(1) DEFAULT NULL,
  `apply_weekly_registration_limits` tinyint(1) DEFAULT NULL,
  `weekly_limit_times` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `billing_type_id` (`billing_type_id`),
  KEY `duration_type_id` (`duration_type_id`),
  KEY `location_id` (`location_id`),
  KEY `pass_expiration_duration_type_id` (`pass_expiration_duration_type_id`),
  KEY `plan_status_type_id` (`plan_status_type_id`),
  KEY `recurring_duration_type_id` (`recurring_duration_type_id`),
  KEY `membership_type_id` (`membership_type_id`),
  KEY `sessions_limit_duration_type_id` (`sessions_limit_duration_type_id`),
  CONSTRAINT `plan_ibfk_1` FOREIGN KEY (`billing_type_id`) REFERENCES `_ref_billing_type` (`id`),
  CONSTRAINT `plan_ibfk_2` FOREIGN KEY (`duration_type_id`) REFERENCES `_ref_duration_type` (`id`),
  CONSTRAINT `plan_ibfk_3` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `plan_ibfk_4` FOREIGN KEY (`pass_expiration_duration_type_id`) REFERENCES `_ref_duration_type` (`id`),
  CONSTRAINT `plan_ibfk_5` FOREIGN KEY (`plan_status_type_id`) REFERENCES `_ref_plan_status_type` (`id`),
  CONSTRAINT `plan_ibfk_6` FOREIGN KEY (`recurring_duration_type_id`) REFERENCES `_ref_duration_type` (`id`),
  CONSTRAINT `plan_ibfk_7` FOREIGN KEY (`membership_type_id`) REFERENCES `_ref_membership_type` (`id`),
  CONSTRAINT `plan_ibfk_8` FOREIGN KEY (`sessions_limit_duration_type_id`) REFERENCES `_ref_duration_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3472 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plan`
--

/*!40000 ALTER TABLE `plan` DISABLE KEYS */;
INSERT INTO `plan` VALUES (682,'Standard','24 Hour Access',12,20,29,14,0,1,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2024-09-26 18:30:41','2025-10-30 21:24:45',43,3,1,1,NULL,1,NULL,NULL,NULL,1,1,0,1,0,0),(683,'Standard Grandfathered Monthly','OG members only',12,20,70,28,0,1,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2024-09-26 18:33:25','2025-10-30 21:24:52',43,3,1,1,NULL,1,NULL,NULL,NULL,1,1,0,1,0,0),(999,'Month to Month','',52,20,80,28,0,1,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2024-12-04 20:14:53','2025-10-30 21:23:56',43,2,1,1,NULL,1,NULL,NULL,NULL,1,1,0,1,0,0),(1000,'Day Pass','',NULL,0,NULL,NULL,0,1,0,NULL,0,10,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2024-12-04 20:15:32','2025-10-30 21:23:34',43,NULL,3,NULL,NULL,1,1,NULL,NULL,1,3,0,1,0,0),(1001,'Week Pass','',1,0,NULL,NULL,0,0,0,35,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2024-12-04 20:17:14','2025-10-30 21:25:09',43,2,2,NULL,NULL,1,NULL,7,7,1,3,0,1,0,0),(1002,'Personal Training 2x/wk','',3,0,480,28,0,0,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2024-12-04 20:19:18','2025-10-30 21:24:03',43,3,1,1,NULL,1,NULL,2,7,1,1,0,0,0,0),(1003,'Actions Personal Training 3x/wk','',3,0,720,28,0,0,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2024-12-04 20:19:48','2025-10-30 21:21:06',43,3,1,1,NULL,1,NULL,3,7,1,1,0,0,0,0),(1195,'Couple 24 hr access','Couple Standard Gym Access',52,20,120,28,0,1,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-08 18:53:41','2025-10-30 21:22:24',43,2,1,1,NULL,1,NULL,NULL,NULL,1,1,0,1,0,0),(1203,'Annual fee','Maintenance fee',1,0,NULL,NULL,0,1,1,25,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-09 17:11:27','2025-10-30 21:21:34',43,4,2,NULL,NULL,1,NULL,NULL,NULL,1,1,0,0,0,0),(1214,'Couple Every 2 weeks','Couple plan billed every 2 weeks',1,20,55,14,0,1,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-14 16:23:34','2025-10-30 21:22:35',43,4,1,1,NULL,1,NULL,NULL,NULL,1,1,0,1,0,0),(1230,'Seasonal','Membership with experation date',3,20,NULL,NULL,0,1,0,150,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-15 23:51:06','2025-10-30 21:24:19',43,3,2,NULL,NULL,1,NULL,NULL,NULL,1,3,0,1,0,0),(1440,'family','3 people',1,0,130,28,0,1,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-03-07 14:34:30','2025-12-01 21:41:02',43,4,1,1,NULL,3,NULL,NULL,NULL,1,1,0,1,0,0),(2256,'family 5','family pack of five 120 for couple 35 for each additional person.',12,0,225,28,0,1,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-06-13 17:09:25','2025-06-13 17:12:56',43,3,1,1,NULL,1,NULL,NULL,NULL,1,1,1,1,0,0),(3009,'Custom Family Add on Plan bi wekly','family plan for multiple members billed biweekly',12,20,75,14,0,1,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-09-05 21:34:44','2025-10-30 21:22:44',43,3,1,1,NULL,1,NULL,NULL,NULL,1,1,0,1,0,0),(3041,'standard grandfathered monthlyy','',12,20,70,1,0,1,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-09-15 13:00:29','2025-10-30 21:25:01',43,3,1,3,NULL,1,NULL,NULL,NULL,1,1,0,1,0,0),(3042,'Copy - family','3 people',1,0,130,28,0,1,1,NULL,0,NULL,NULL,NULL,NULL,NULL,1,0,0,NULL,NULL,0,0,'2025-09-15 13:01:43','2025-10-02 18:12:49',43,4,1,1,1,3,NULL,NULL,NULL,1,1,0,1,0,0),(3043,'Copy - family 5','family pack of five 120 for couple 35 for each additional person.',12,0,225,28,0,1,1,NULL,0,NULL,NULL,NULL,NULL,NULL,1,0,0,NULL,NULL,0,0,'2025-09-15 13:02:06','2025-10-02 18:12:34',43,3,1,1,1,3,NULL,NULL,NULL,1,1,1,1,0,0),(3144,'Schreiner Discount','',30,20,50,1,0,1,0,NULL,0,NULL,NULL,NULL,NULL,NULL,0,0,0,NULL,NULL,0,0,'2025-10-02 18:15:16','2025-10-08 21:29:18',43,1,1,3,1,3,NULL,NULL,NULL,1,1,0,1,0,0),(3185,'Schreiner Discount','',6,20,50,28,0,1,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-10-08 21:31:35','2025-10-30 21:24:11',43,3,1,1,NULL,1,NULL,NULL,NULL,1,1,0,1,0,0),(3201,'Copy - Actions Personal Training 3x/wk','',3,0,780,28,0,0,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-10-14 13:39:19','2025-10-30 21:22:00',43,3,1,1,NULL,1,NULL,3,7,1,1,0,0,0,0),(3210,'Copy - Personal Training 2x/wk','',3,0,480,30,0,0,1,NULL,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-10-16 17:48:08','2025-10-30 21:22:16',43,3,1,1,NULL,1,NULL,2,7,1,1,0,0,0,0),(3255,'10 personal training paid in full','',1,60,NULL,NULL,0,0,1,650,0,NULL,NULL,NULL,NULL,1,0,NULL,NULL,NULL,NULL,NULL,NULL,'2025-10-28 16:55:38','2025-10-30 21:20:51',43,3,2,NULL,NULL,1,NULL,10,30,1,1,0,1,0,0),(3320,'Free Membership','',1,NULL,NULL,NULL,0,1,1,NULL,0,NULL,NULL,NULL,NULL,NULL,0,0,0,NULL,NULL,0,0,'2025-11-13 16:24:20','2025-11-13 16:24:20',43,4,4,1,1,NULL,NULL,NULL,NULL,1,1,0,1,0,0),(3321,'CURRENT Personal training 2x a week','',3,0,NULL,NULL,0,1,1,520,0,NULL,NULL,NULL,NULL,NULL,0,0,0,NULL,NULL,0,0,'2025-11-14 19:07:35','2025-11-14 19:07:35',43,3,2,1,1,NULL,NULL,NULL,NULL,1,1,0,1,0,0),(3322,'CURRENT personal training 3x a week','',3,0,NULL,NULL,0,1,1,780,0,NULL,NULL,NULL,NULL,NULL,0,0,0,NULL,NULL,0,0,'2025-11-14 19:08:36','2025-11-14 19:08:36',43,3,2,1,1,NULL,NULL,NULL,NULL,1,1,0,1,0,0),(3380,'Copy - Free Membership','',10,NULL,NULL,NULL,0,1,1,NULL,0,NULL,NULL,NULL,NULL,NULL,0,0,0,NULL,NULL,0,0,'2025-12-01 21:39:02','2025-12-01 21:39:02',43,4,4,1,1,NULL,NULL,NULL,NULL,1,1,0,0,0,0),(3435,'family with add on','',1,20,160,30,0,1,1,NULL,0,NULL,NULL,NULL,NULL,NULL,0,0,0,NULL,NULL,0,0,'2025-12-09 17:55:38','2025-12-09 17:55:38',43,4,1,1,1,NULL,NULL,NULL,NULL,1,1,0,1,0,0),(3444,'3 day pass','',3,0,NULL,NULL,0,1,1,30,0,NULL,NULL,NULL,NULL,NULL,0,0,0,NULL,NULL,0,0,'2025-12-12 17:37:46','2025-12-12 17:37:46',43,1,2,1,1,NULL,NULL,NULL,NULL,1,1,0,1,0,0);
/*!40000 ALTER TABLE `plan` ENABLE KEYS */;

--
-- Table structure for table `plan_location`
--

DROP TABLE IF EXISTS `plan_location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plan_location` (
  `plan_id` bigint NOT NULL,
  `location_id` bigint NOT NULL,
  PRIMARY KEY (`plan_id`,`location_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `plan_location_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `plan_location_ibfk_2` FOREIGN KEY (`plan_id`) REFERENCES `plan` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plan_location`
--

/*!40000 ALTER TABLE `plan_location` DISABLE KEYS */;
/*!40000 ALTER TABLE `plan_location` ENABLE KEYS */;

--
-- Table structure for table `plan_plan_type`
--

DROP TABLE IF EXISTS `plan_plan_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `plan_plan_type` (
  `plan_id` bigint NOT NULL,
  `plan_type_id` int NOT NULL,
  PRIMARY KEY (`plan_id`,`plan_type_id`),
  KEY `plan_type_id` (`plan_type_id`),
  CONSTRAINT `plan_plan_type_ibfk_1` FOREIGN KEY (`plan_id`) REFERENCES `plan` (`id`),
  CONSTRAINT `plan_plan_type_ibfk_2` FOREIGN KEY (`plan_type_id`) REFERENCES `_ref_plan_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `plan_plan_type`
--

/*!40000 ALTER TABLE `plan_plan_type` DISABLE KEYS */;
/*!40000 ALTER TABLE `plan_plan_type` ENABLE KEYS */;

--
-- Table structure for table `report`
--

DROP TABLE IF EXISTS `report`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `report` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL,
  `description` varchar(200) DEFAULT NULL,
  `dashboard_id` varchar(100) NOT NULL,
  `sheet_id` varchar(100) NOT NULL,
  `visual_id` varchar(100) NOT NULL,
  `environment` varchar(5) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report`
--

/*!40000 ALTER TABLE `report` DISABLE KEYS */;
/*!40000 ALTER TABLE `report` ENABLE KEYS */;

--
-- Table structure for table `report_role`
--

DROP TABLE IF EXISTS `report_role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `report_role` (
  `report_id` bigint NOT NULL,
  `role_type_id` int NOT NULL,
  PRIMARY KEY (`report_id`,`role_type_id`),
  KEY `fk_role` (`role_type_id`),
  CONSTRAINT `fk_report` FOREIGN KEY (`report_id`) REFERENCES `report` (`id`),
  CONSTRAINT `fk_role` FOREIGN KEY (`role_type_id`) REFERENCES `_ref_role_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `report_role`
--

/*!40000 ALTER TABLE `report_role` DISABLE KEYS */;
/*!40000 ALTER TABLE `report_role` ENABLE KEYS */;

--
-- Table structure for table `role_permission`
--

DROP TABLE IF EXISTS `role_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `role_permission` (
  `role_type_id` int NOT NULL,
  `permission_type_id` int NOT NULL,
  PRIMARY KEY (`role_type_id`,`permission_type_id`),
  KEY `permission_type_id` (`permission_type_id`),
  CONSTRAINT `role_permission_ibfk_1` FOREIGN KEY (`permission_type_id`) REFERENCES `_ref_permission_type` (`id`),
  CONSTRAINT `role_permission_ibfk_2` FOREIGN KEY (`role_type_id`) REFERENCES `_ref_role_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `role_permission`
--

/*!40000 ALTER TABLE `role_permission` DISABLE KEYS */;
/*!40000 ALTER TABLE `role_permission` ENABLE KEYS */;

--
-- Table structure for table `room`
--

DROP TABLE IF EXISTS `room`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `room` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `sft` int DEFAULT NULL,
  `capacity` int DEFAULT NULL,
  `notes` text,
  `location_id` bigint NOT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `room_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=195 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `room`
--

/*!40000 ALTER TABLE `room` DISABLE KEYS */;
/*!40000 ALTER TABLE `room` ENABLE KEYS */;

--
-- Table structure for table `schema_migrations`
--

DROP TABLE IF EXISTS `schema_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `schema_migrations` (
  `version` varchar(128) NOT NULL,
  PRIMARY KEY (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `schema_migrations`
--

/*!40000 ALTER TABLE `schema_migrations` DISABLE KEYS */;
/*!40000 ALTER TABLE `schema_migrations` ENABLE KEYS */;

--
-- Table structure for table `update_log`
--

DROP TABLE IF EXISTS `update_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `update_log` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `location_id` bigint DEFAULT NULL,
  `target_user_id` bigint DEFAULT NULL,
  `actor_user_id` bigint DEFAULT NULL,
  `request_url` varchar(255) DEFAULT NULL,
  `method` varchar(255) DEFAULT NULL,
  `request_body` json DEFAULT NULL,
  `response` json DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `location_id` (`location_id`),
  KEY `target_user_id` (`target_user_id`),
  KEY `actor_user_id` (`actor_user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=582316 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `update_log`
--

/*!40000 ALTER TABLE `update_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `update_log` ENABLE KEYS */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `active` tinyint(1) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `verified` tinyint(1) NOT NULL,
  `verified_on` datetime DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `role_type_id` int NOT NULL,
  `deactivated_on` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `role_type_id` (`role_type_id`),
  CONSTRAINT `user_ibfk_1` FOREIGN KEY (`role_type_id`) REFERENCES `_ref_role_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=38742 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1798,'owner@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,'2026-06-20 03:21:02',1,NULL,'2024-09-25 20:52:15','2026-06-20 03:21:02',1,NULL),(1799,'u1799@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,'2025-12-26 20:59:57',1,'2024-09-25 20:52:15','2024-09-25 20:52:15','2025-12-26 20:59:58',4,NULL),(8984,'u8984@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:07','2025-01-03 11:07:07',6,NULL),(8985,'u8985@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,'2025-12-01 21:09:48',1,NULL,'2025-01-03 11:07:07','2025-12-01 21:09:49',6,NULL),(8986,'u8986@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:07','2025-01-03 11:07:07',6,NULL),(8987,'u8987@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:08','2025-01-03 11:07:08',6,NULL),(8988,'u8988@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:08','2025-01-03 11:07:08',6,NULL),(8989,'u8989@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:08','2025-01-03 11:07:08',6,NULL),(8990,'u8990@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:09','2025-01-03 11:07:09',6,NULL),(8991,'u8991@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:09','2025-01-03 11:07:09',6,NULL),(8992,'u8992@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:09','2025-01-03 11:07:09',6,NULL),(8993,'u8993@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:10','2025-01-03 11:07:10',6,NULL),(8994,'u8994@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:10','2025-01-03 11:07:10',6,NULL),(8995,'u8995@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:11','2025-01-03 11:07:11',6,NULL),(8996,'u8996@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:11','2025-01-03 11:07:11',6,NULL),(8997,'u8997@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:11','2025-01-03 11:07:11',6,NULL),(8998,'u8998@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,'2025-12-02 14:33:32',1,'2025-12-02 14:31:50','2025-01-03 11:07:12','2025-12-02 14:33:32',6,NULL),(8999,'u8999@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:12','2025-01-03 11:07:12',6,NULL),(9000,'u9000@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:12','2025-02-17 23:46:47',6,NULL),(9001,'u9001@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:13','2025-01-03 11:07:13',6,NULL),(9002,'u9002@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,'2025-12-11 23:54:51',1,NULL,'2025-01-03 11:07:13','2025-12-11 23:54:52',6,NULL),(9003,'u9003@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:13','2025-01-03 11:07:13',6,NULL),(9004,'u9004@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:14','2025-01-03 11:07:14',6,NULL),(9005,'u9005@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:14','2025-01-03 11:07:14',6,NULL),(9006,'u9006@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,'2025-12-17 20:20:50',1,NULL,'2025-01-03 11:07:15','2025-12-17 20:20:50',6,NULL),(9007,'u9007@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:15','2025-01-03 11:07:15',6,NULL),(9008,'u9008@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:15','2025-10-23 12:55:38',6,NULL),(9009,'u9009@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:16','2025-01-03 11:07:16',6,NULL),(9010,'u9010@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:16','2025-01-03 11:07:16',6,NULL),(9011,'u9011@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:16','2025-01-03 11:07:16',6,NULL),(9012,'u9012@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:17','2025-01-03 11:07:17',6,NULL),(9013,'u9013@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:17','2025-02-17 22:00:02',6,NULL),(9014,'u9014@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,'2025-12-08 14:10:51',1,NULL,'2025-01-03 11:07:18','2025-12-08 14:10:51',6,NULL),(9015,'u9015@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:18','2025-01-03 11:07:18',6,NULL),(9016,'u9016@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:18','2025-02-17 21:51:31',6,NULL),(9017,'u9017@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:19','2025-01-13 23:23:20',6,NULL),(9018,'u9018@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,'2025-12-04 19:42:14',1,'2025-12-04 19:40:52','2025-01-03 11:07:19','2025-12-04 19:42:15',6,NULL),(9019,'u9019@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:19','2025-01-03 11:07:19',6,NULL),(9020,'u9020@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:20','2025-01-03 11:07:20',6,NULL),(9021,'u9021@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:20','2025-02-11 22:33:33',6,NULL),(9022,'u9022@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,'2025-12-07 22:03:04',1,NULL,'2025-01-03 11:07:20','2025-12-07 22:03:04',6,NULL),(9023,'u9023@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-01-03 11:07:21','2025-01-03 11:07:21',6,NULL),(13545,'u13545@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,'2026-01-02 01:26:30',1,'2025-10-29 13:45:39','2025-04-02 20:03:01','2026-01-02 01:26:30',4,NULL),(34183,'u34183@demo.gym','$2b$12$g0Fke0W/w/eKMbvpf//00Oi8r2QH3Se/OwudRZqrxw2zraCbr62Na',1,NULL,1,NULL,'2025-09-10 16:26:28','2025-11-14 23:58:32',5,NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;

--
-- Table structure for table `user_location`
--

DROP TABLE IF EXISTS `user_location`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_location` (
  `user_id` bigint NOT NULL,
  `location_id` bigint NOT NULL,
  PRIMARY KEY (`user_id`,`location_id`),
  KEY `location_id` (`location_id`),
  CONSTRAINT `user_location_ibfk_1` FOREIGN KEY (`location_id`) REFERENCES `location` (`id`),
  CONSTRAINT `user_location_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `user_location_ibfk_3` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_location`
--

/*!40000 ALTER TABLE `user_location` DISABLE KEYS */;
INSERT INTO `user_location` VALUES (1798,43),(1799,43),(8984,43),(8985,43),(8986,43),(8987,43),(8988,43),(8989,43),(8990,43),(8991,43),(8992,43),(8993,43),(8994,43),(8995,43),(8996,43),(8997,43),(8998,43),(8999,43),(9000,43),(9001,43),(9002,43),(9003,43),(9004,43),(9005,43),(9006,43),(9007,43),(9008,43),(9009,43),(9010,43),(9011,43),(9012,43),(9013,43),(9014,43),(9015,43),(9016,43),(9017,43),(9018,43),(9019,43),(9020,43),(9021,43),(9022,43),(9023,43),(13545,43),(34183,43);
/*!40000 ALTER TABLE `user_location` ENABLE KEYS */;

--
-- Table structure for table `user_profile`
--

DROP TABLE IF EXISTS `user_profile`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_profile` (
  `first_name` varchar(50) DEFAULT NULL,
  `last_name` varchar(50) DEFAULT NULL,
  `middle_name` varchar(50) DEFAULT NULL,
  `preferred_name` varchar(50) DEFAULT NULL,
  `photo_url` varchar(255) DEFAULT NULL,
  `birth_date` date DEFAULT NULL,
  `address_street` varchar(255) DEFAULT NULL,
  `address_city` varchar(255) DEFAULT NULL,
  `address_state` varchar(20) DEFAULT NULL,
  `address_zip` varchar(10) DEFAULT NULL,
  `address_country` varchar(20) DEFAULT NULL,
  `phone_number` varchar(20) DEFAULT NULL,
  `emergency_first_name` varchar(50) DEFAULT NULL,
  `emergency_last_name` varchar(50) DEFAULT NULL,
  `emergency_phone_number` varchar(50) DEFAULT NULL,
  `guardian_first_name` varchar(50) DEFAULT NULL,
  `guardian_last_name` varchar(50) DEFAULT NULL,
  `guardian_phone_number` varchar(50) DEFAULT NULL,
  `gender_type_id` int DEFAULT NULL,
  `emergency_relationship_type_id` int DEFAULT NULL,
  `relationship_status_type_id` int DEFAULT NULL,
  `have_children` tinyint(1) DEFAULT NULL,
  `shirt_size_type_id` int DEFAULT NULL,
  `shirt_fit_type_id` int DEFAULT NULL,
  `create_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_datetime` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `about` varchar(280) DEFAULT NULL,
  `start_date` datetime DEFAULT NULL,
  `accepted_terms_conditions_datetime` datetime DEFAULT NULL,
  `accepted_privacy_policy_datetime` datetime DEFAULT NULL,
  `address_street_2` varchar(100) DEFAULT NULL,
  `user_id` bigint NOT NULL,
  PRIMARY KEY (`user_id`),
  KEY `relationship_status_type_id` (`relationship_status_type_id`),
  KEY `shirt_fit_type_id` (`shirt_fit_type_id`),
  KEY `shirt_size_type_id` (`shirt_size_type_id`),
  CONSTRAINT `fk_user_profile_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`),
  CONSTRAINT `user_profile_ibfk_1` FOREIGN KEY (`relationship_status_type_id`) REFERENCES `_ref_relationship_status_type` (`id`),
  CONSTRAINT `user_profile_ibfk_2` FOREIGN KEY (`shirt_fit_type_id`) REFERENCES `_ref_shirt_fit_type` (`id`),
  CONSTRAINT `user_profile_ibfk_3` FOREIGN KEY (`shirt_size_type_id`) REFERENCES `_ref_shirt_size_type` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_profile`
--

/*!40000 ALTER TABLE `user_profile` DISABLE KEYS */;
INSERT INTO `user_profile` VALUES ('Jordan','Blake',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001',NULL,'+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-09-25 20:52:15','2025-10-29 13:43:55',NULL,NULL,'2024-09-25 20:52:15','2024-09-25 20:52:15',NULL,1798),('Front','Desk',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001',NULL,'+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2024-09-25 20:52:15','2024-09-25 20:52:15',NULL,NULL,NULL,NULL,NULL,1799),('Avery','Stone',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:07','2025-01-03 11:07:07',NULL,NULL,NULL,NULL,NULL,8984),('Blair','Hughes',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:07','2025-01-03 11:07:07',NULL,NULL,NULL,NULL,NULL,8985),('Casey','Morgan',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:07','2025-01-03 11:07:07',NULL,NULL,NULL,NULL,NULL,8986),('Dana','Brooks',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:08','2025-01-03 11:07:08',NULL,NULL,NULL,NULL,NULL,8987),('Eli','Warren',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:08','2025-01-03 11:07:08',NULL,NULL,NULL,NULL,NULL,8988),('Frankie','Hale',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:08','2025-01-03 11:07:08',NULL,NULL,NULL,NULL,NULL,8989),('Gray','Porter',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:09','2025-01-03 11:07:09',NULL,NULL,NULL,NULL,NULL,8990),('Harper','Quinn',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:09','2025-01-03 11:07:09',NULL,NULL,NULL,NULL,NULL,8991),('Indy','Reeves',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:09','2025-01-03 11:07:09',NULL,NULL,NULL,NULL,NULL,8992),('Jamie','Sutton',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:10','2025-01-03 11:07:10',NULL,NULL,NULL,NULL,NULL,8993),('Kai','Turner',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:10','2025-01-03 11:07:10',NULL,NULL,NULL,NULL,NULL,8994),('Lane','Vaughn',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:11','2025-01-03 11:07:11',NULL,NULL,NULL,NULL,NULL,8995),('Micah','Walsh',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:11','2025-01-03 11:07:11',NULL,NULL,NULL,NULL,NULL,8996),('Noel','Young',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:11','2025-01-03 11:07:11',NULL,NULL,NULL,NULL,NULL,8997),('Oakley','Price',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:12','2025-01-03 11:07:12',NULL,NULL,NULL,NULL,NULL,8998),('Parker','Reid',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:12','2025-01-03 11:07:12',NULL,NULL,NULL,NULL,NULL,8999),('Quinn','Foster',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001',NULL,'+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:12','2025-02-17 23:46:37',NULL,NULL,NULL,NULL,NULL,9000),('Reese','Garner',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:13','2025-01-03 11:07:13',NULL,NULL,NULL,NULL,NULL,9001),('Sage','Holland',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:13','2025-01-03 11:07:13',NULL,NULL,NULL,NULL,NULL,9002),('Tatum','Irwin',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:13','2025-01-03 11:07:13',NULL,NULL,NULL,NULL,NULL,9003),('Umber','Jennings',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:14','2025-01-03 11:07:14',NULL,NULL,NULL,NULL,NULL,9004),('Val','Keller',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:14','2025-01-03 11:07:14',NULL,NULL,NULL,NULL,NULL,9005),('Wren','Lawson',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:15','2025-01-03 11:07:15',NULL,NULL,NULL,NULL,NULL,9006),('Xen','Mercer',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:15','2025-01-03 11:07:15',NULL,NULL,NULL,NULL,NULL,9007),('Yael','Nolan',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:15','2025-10-23 12:55:38',NULL,NULL,NULL,NULL,NULL,9008),('Zion','Osborne',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:16','2025-01-03 11:07:16',NULL,NULL,NULL,NULL,NULL,9009),('Arden','Pike',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:16','2025-01-03 11:07:16',NULL,NULL,NULL,NULL,NULL,9010),('Bay','Ramsey',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:16','2025-01-03 11:07:16',NULL,NULL,NULL,NULL,NULL,9011),('Corin','Shaw',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:17','2025-01-03 11:07:17',NULL,NULL,NULL,NULL,NULL,9012),('Drew','Tate',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001',NULL,'+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:17','2025-02-17 22:00:02',NULL,NULL,NULL,NULL,NULL,9013),('Emery','Upton',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:18','2025-01-03 11:07:18',NULL,NULL,NULL,NULL,NULL,9014),('Finley','Vance',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:18','2025-01-03 11:07:18',NULL,NULL,NULL,NULL,NULL,9015),('Gale','Whitaker',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001',NULL,'+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:18','2025-02-17 21:51:31',NULL,NULL,NULL,NULL,NULL,9016),('Hollis','York',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001',NULL,'+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:19','2025-01-13 23:23:20',NULL,NULL,NULL,NULL,NULL,9017),('Ira','Abbott',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001',NULL,'+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:19','2025-01-21 14:51:43',NULL,NULL,NULL,NULL,NULL,9018),('Jules','Barton',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:19','2025-01-03 11:07:19',NULL,NULL,NULL,NULL,NULL,9019),('Kit','Carver',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:20','2025-01-03 11:07:20',NULL,NULL,NULL,NULL,NULL,9020),('Logan','Dalton',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001',NULL,'+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:20','2025-02-11 22:33:33',NULL,NULL,NULL,NULL,NULL,9021),('Marlow','Ellis',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','USA','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:20','2025-01-03 11:07:20',NULL,NULL,NULL,NULL,NULL,9022),('Nico','Fleming',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001',NULL,'+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'2025-01-03 11:07:21','2025-01-03 11:07:21',NULL,NULL,NULL,NULL,NULL,9023),('Ollie','Grant',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001','United States','+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,'2025-04-02 20:03:01','2025-10-29 13:45:39',NULL,NULL,'2025-10-29 13:45:39','2025-10-29 13:45:39',NULL,13545),('Peyton','Hayes',NULL,NULL,NULL,'2000-01-01','100 Example Street','Springfield','TX','75001',NULL,'+10000000000',NULL,NULL,NULL,NULL,NULL,NULL,1,NULL,NULL,NULL,NULL,NULL,'2025-09-10 16:26:28','2025-11-14 23:58:32',NULL,'2003-02-03 00:00:00',NULL,NULL,NULL,34183);
/*!40000 ALTER TABLE `user_profile` ENABLE KEYS */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-09-17 12:20:27

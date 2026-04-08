-- MySQL dump 10.13  Distrib 8.4.8, for Linux (aarch64)
--
-- Host: localhost    Database: guardia_db
-- ------------------------------------------------------
-- Server version	8.4.8

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
-- Table structure for table `assiduite`
--

DROP TABLE IF EXISTS `assiduite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `assiduite` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_eleve` int NOT NULL,
  `id_responsable` int NOT NULL,
  `type` enum('absent','retard','présent','excusé') NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_eleve` (`id_eleve`),
  KEY `id_responsable` (`id_responsable`),
  CONSTRAINT `assiduite_ibfk_1` FOREIGN KEY (`id_eleve`) REFERENCES `eleve` (`id`) ON DELETE CASCADE,
  CONSTRAINT `assiduite_ibfk_2` FOREIGN KEY (`id_responsable`) REFERENCES `user` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `assiduite`
--

LOCK TABLES `assiduite` WRITE;
/*!40000 ALTER TABLE `assiduite` DISABLE KEYS */;
/*!40000 ALTER TABLE `assiduite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `batiment`
--

DROP TABLE IF EXISTS `batiment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `batiment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(50) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `batiment`
--

LOCK TABLES `batiment` WRITE;
/*!40000 ALTER TABLE `batiment` DISABLE KEYS */;
INSERT INTO `batiment` VALUES (1,'Batiment A'),(2,'Batiment B');
/*!40000 ALTER TABLE `batiment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `classe`
--

DROP TABLE IF EXISTS `classe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `classe` (
  `id` int NOT NULL AUTO_INCREMENT,
  `niveau` int NOT NULL,
  `suffixe` varchar(10) DEFAULT NULL,
  `annee` int NOT NULL,
  `id_prof_principal` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_prof_principal` (`id_prof_principal`),
  CONSTRAINT `classe_ibfk_1` FOREIGN KEY (`id_prof_principal`) REFERENCES `prof` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `classe`
--

LOCK TABLES `classe` WRITE;
/*!40000 ALTER TABLE `classe` DISABLE KEYS */;
INSERT INTO `classe` VALUES (1,10,'A',2026,NULL),(2,10,'B',2026,NULL),(3,11,'A',2026,NULL),(4,12,'A',2026,NULL),(5,12,'B',2026,NULL);
/*!40000 ALTER TABLE `classe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `communication`
--

DROP TABLE IF EXISTS `communication`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `communication` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_user` int NOT NULL,
  `cible` enum('parent','élève','prof','tous','classe') NOT NULL,
  `id_cible` int DEFAULT NULL,
  `objet` varchar(255) DEFAULT NULL,
  `contenu` text,
  `date_debut` datetime DEFAULT NULL,
  `date_fin` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_user` (`id_user`),
  CONSTRAINT `communication_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `communication`
--

LOCK TABLES `communication` WRITE;
/*!40000 ALTER TABLE `communication` DISABLE KEYS */;
/*!40000 ALTER TABLE `communication` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cours`
--

DROP TABLE IF EXISTS `cours`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cours` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_matiere` int NOT NULL,
  `id_prof` int NOT NULL,
  `id_classe` int NOT NULL,
  `debut` datetime NOT NULL,
  `fin` datetime NOT NULL,
  `etat` enum('planifie','en cours','termine','annule') NOT NULL,
  `id_salle` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_matiere` (`id_matiere`),
  KEY `id_prof` (`id_prof`),
  KEY `id_classe` (`id_classe`),
  KEY `id_salle` (`id_salle`),
  CONSTRAINT `cours_ibfk_1` FOREIGN KEY (`id_matiere`) REFERENCES `matiere` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `cours_ibfk_2` FOREIGN KEY (`id_prof`) REFERENCES `prof` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `cours_ibfk_3` FOREIGN KEY (`id_classe`) REFERENCES `classe` (`id`) ON DELETE CASCADE,
  CONSTRAINT `cours_ibfk_4` FOREIGN KEY (`id_salle`) REFERENCES `salle` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cours`
--

LOCK TABLES `cours` WRITE;
/*!40000 ALTER TABLE `cours` DISABLE KEYS */;
INSERT INTO `cours` VALUES (1,1,1,4,'2026-01-14 14:00:00','2026-01-14 16:00:00','planifie',4),(2,1,1,3,'2026-01-15 08:00:00','2026-01-15 10:00:00','planifie',6),(3,2,1,1,'2026-01-16 10:00:00','2026-01-16 12:00:00','planifie',6),(4,2,1,4,'2026-01-15 08:00:00','2026-01-15 10:00:00','planifie',5),(5,3,2,3,'2026-01-15 08:00:00','2026-01-15 10:00:00','planifie',8),(6,3,2,5,'2026-01-14 14:00:00','2026-01-14 16:00:00','planifie',9),(7,7,2,1,'2026-01-15 08:00:00','2026-01-15 10:00:00','planifie',6),(8,7,2,5,'2026-01-12 08:00:00','2026-01-12 10:00:00','planifie',3),(9,4,3,4,'2026-01-16 10:00:00','2026-01-16 12:00:00','planifie',7),(10,4,3,2,'2026-01-14 14:00:00','2026-01-14 16:00:00','planifie',8),(11,5,3,1,'2026-01-14 14:00:00','2026-01-14 16:00:00','planifie',8),(12,5,3,4,'2026-01-16 10:00:00','2026-01-16 12:00:00','planifie',7),(13,6,4,2,'2026-01-14 14:00:00','2026-01-14 16:00:00','planifie',9),(14,6,4,3,'2026-01-12 08:00:00','2026-01-12 10:00:00','planifie',4),(15,1,4,1,'2026-01-13 10:00:00','2026-01-13 12:00:00','planifie',5),(16,1,4,2,'2026-01-14 14:00:00','2026-01-14 16:00:00','planifie',2),(17,8,5,1,'2026-01-15 08:00:00','2026-01-15 10:00:00','planifie',5),(18,8,5,5,'2026-01-16 10:00:00','2026-01-16 12:00:00','planifie',7),(19,9,5,2,'2026-01-12 08:00:00','2026-01-12 10:00:00','planifie',4),(20,9,5,1,'2026-01-15 08:00:00','2026-01-15 10:00:00','planifie',7);
/*!40000 ALTER TABLE `cours` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devoir`
--

DROP TABLE IF EXISTS `devoir`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `devoir` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_classe` int NOT NULL,
  `id_matiere` int NOT NULL,
  `type` enum('exercice','controle','expose','projet','soutenance','autre') NOT NULL,
  `date_limite` datetime NOT NULL,
  `consigne` text,
  `id_prof` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_classe` (`id_classe`),
  KEY `id_matiere` (`id_matiere`),
  KEY `id_prof` (`id_prof`),
  CONSTRAINT `devoir_ibfk_1` FOREIGN KEY (`id_classe`) REFERENCES `classe` (`id`) ON DELETE CASCADE,
  CONSTRAINT `devoir_ibfk_2` FOREIGN KEY (`id_matiere`) REFERENCES `matiere` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `devoir_ibfk_3` FOREIGN KEY (`id_prof`) REFERENCES `prof` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devoir`
--

LOCK TABLES `devoir` WRITE;
/*!40000 ALTER TABLE `devoir` DISABLE KEYS */;
/*!40000 ALTER TABLE `devoir` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `devoir_status`
--

DROP TABLE IF EXISTS `devoir_status`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `devoir_status` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_devoir` int NOT NULL,
  `id_eleve` int NOT NULL,
  `status` tinyint(1) DEFAULT NULL,
  `fichier` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_devoir` (`id_devoir`),
  KEY `id_eleve` (`id_eleve`),
  CONSTRAINT `devoir_status_ibfk_1` FOREIGN KEY (`id_devoir`) REFERENCES `devoir` (`id`) ON DELETE CASCADE,
  CONSTRAINT `devoir_status_ibfk_2` FOREIGN KEY (`id_eleve`) REFERENCES `eleve` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `devoir_status`
--

LOCK TABLES `devoir_status` WRITE;
/*!40000 ALTER TABLE `devoir_status` DISABLE KEYS */;
/*!40000 ALTER TABLE `devoir_status` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `direction`
--

DROP TABLE IF EXISTS `direction`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `direction` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_user` int NOT NULL,
  `role` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_user` (`id_user`),
  CONSTRAINT `direction_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `direction`
--

LOCK TABLES `direction` WRITE;
/*!40000 ALTER TABLE `direction` DISABLE KEYS */;
/*!40000 ALTER TABLE `direction` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `eleve`
--

DROP TABLE IF EXISTS `eleve`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `eleve` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_user` int NOT NULL,
  `id_classe` int DEFAULT NULL,
  `id_responsable` int DEFAULT NULL,
  `groupe` varchar(1) DEFAULT NULL,
  `date_naissance` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_user` (`id_user`),
  KEY `id_classe` (`id_classe`),
  KEY `fk_eleve_responsable` (`id_responsable`),
  CONSTRAINT `eleve_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `eleve_ibfk_2` FOREIGN KEY (`id_classe`) REFERENCES `classe` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_eleve_responsable` FOREIGN KEY (`id_responsable`) REFERENCES `parent` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `eleve`
--

LOCK TABLES `eleve` WRITE;
/*!40000 ALTER TABLE `eleve` DISABLE KEYS */;
INSERT INTO `eleve` VALUES (1,7,1,NULL,'A','2008-01-01'),(2,9,1,NULL,'A','2008-02-02'),(3,11,1,NULL,'A','2008-03-03'),(4,13,2,NULL,'A','2008-04-04'),(5,15,2,NULL,'A','2008-05-05'),(6,17,2,NULL,'A','2008-06-06'),(7,19,3,NULL,'A','2008-07-07'),(8,21,3,NULL,'A','2008-08-08'),(9,23,3,NULL,'A','2008-09-09'),(10,25,4,NULL,'A','2008-10-10'),(11,27,4,NULL,'A','2008-11-11'),(12,29,4,NULL,'A','2008-12-12'),(13,31,5,NULL,'A','2008-01-13'),(14,33,5,NULL,'A','2008-02-14'),(15,35,5,NULL,'A','2008-03-15');
/*!40000 ALTER TABLE `eleve` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `employe`
--

DROP TABLE IF EXISTS `employe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `employe` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_user` int NOT NULL,
  `role` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_user` (`id_user`),
  CONSTRAINT `employe_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `employe`
--

LOCK TABLES `employe` WRITE;
/*!40000 ALTER TABLE `employe` DISABLE KEYS */;
/*!40000 ALTER TABLE `employe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `etage`
--

DROP TABLE IF EXISTS `etage`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `etage` (
  `id` int NOT NULL AUTO_INCREMENT,
  `numero` int NOT NULL,
  `id_batiment` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_batiment` (`id_batiment`),
  CONSTRAINT `etage_ibfk_1` FOREIGN KEY (`id_batiment`) REFERENCES `batiment` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `etage`
--

LOCK TABLES `etage` WRITE;
/*!40000 ALTER TABLE `etage` DISABLE KEYS */;
INSERT INTO `etage` VALUES (1,1,1),(2,1,2);
/*!40000 ALTER TABLE `etage` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evaluation`
--

DROP TABLE IF EXISTS `evaluation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evaluation` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_eleve` int NOT NULL,
  `id_matiere` int NOT NULL,
  `note` decimal(4,2) NOT NULL,
  `note_max` decimal(4,2) NOT NULL,
  `coefficient` int NOT NULL,
  `date` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_eleve` (`id_eleve`),
  KEY `id_matiere` (`id_matiere`),
  CONSTRAINT `evaluation_ibfk_1` FOREIGN KEY (`id_eleve`) REFERENCES `eleve` (`id`) ON DELETE CASCADE,
  CONSTRAINT `evaluation_ibfk_2` FOREIGN KEY (`id_matiere`) REFERENCES `matiere` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=178 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evaluation`
--

LOCK TABLES `evaluation` WRITE;
/*!40000 ALTER TABLE `evaluation` DISABLE KEYS */;
INSERT INTO `evaluation` VALUES (1,1,2,6.77,20.00,2,'2025-11-25 00:00:00'),(2,2,2,16.28,20.00,2,'2025-11-25 00:00:00'),(3,3,2,7.16,20.00,2,'2025-11-25 00:00:00'),(4,1,2,7.98,10.00,1,'2025-11-08 00:00:00'),(5,2,2,5.42,10.00,1,'2025-11-08 00:00:00'),(6,3,2,4.97,10.00,1,'2025-11-08 00:00:00'),(7,1,2,19.51,20.00,1,'2026-03-10 00:00:00'),(8,2,2,8.25,20.00,1,'2026-03-10 00:00:00'),(9,3,2,11.55,20.00,1,'2026-03-10 00:00:00'),(10,1,1,7.50,10.00,1,'2025-10-20 00:00:00'),(11,2,1,5.31,10.00,1,'2025-10-20 00:00:00'),(12,3,1,8.07,10.00,1,'2025-10-20 00:00:00'),(13,1,1,4.18,10.00,1,'2025-12-10 00:00:00'),(14,2,1,9.47,10.00,1,'2025-12-10 00:00:00'),(15,3,1,8.27,10.00,1,'2025-12-10 00:00:00'),(16,1,1,16.72,20.00,2,'2025-11-08 00:00:00'),(17,2,1,6.59,20.00,2,'2025-11-08 00:00:00'),(18,3,1,19.65,20.00,2,'2025-11-08 00:00:00'),(19,1,1,9.03,20.00,1,'2026-02-03 00:00:00'),(20,2,1,15.16,20.00,1,'2026-02-03 00:00:00'),(21,3,1,14.83,20.00,1,'2026-02-03 00:00:00'),(22,1,9,3.66,10.00,2,'2026-01-15 00:00:00'),(23,2,9,8.32,10.00,2,'2026-01-15 00:00:00'),(24,3,9,3.76,10.00,2,'2026-01-15 00:00:00'),(25,1,9,15.08,20.00,2,'2026-04-02 00:00:00'),(26,2,9,12.06,20.00,2,'2026-04-02 00:00:00'),(27,3,9,12.54,20.00,2,'2026-04-02 00:00:00'),(28,1,9,8.89,10.00,1,'2026-03-10 00:00:00'),(29,2,9,8.31,10.00,1,'2026-03-10 00:00:00'),(30,3,9,4.41,10.00,1,'2026-03-10 00:00:00'),(31,1,7,7.82,20.00,1,'2025-10-20 00:00:00'),(32,2,7,10.63,20.00,1,'2025-10-20 00:00:00'),(33,3,7,16.32,20.00,1,'2025-10-20 00:00:00'),(34,1,7,12.87,20.00,1,'2025-11-08 00:00:00'),(35,2,7,14.95,20.00,1,'2025-11-08 00:00:00'),(36,3,7,18.15,20.00,1,'2025-11-08 00:00:00'),(37,1,5,17.23,20.00,1,'2025-11-08 00:00:00'),(38,2,5,7.47,20.00,1,'2025-11-08 00:00:00'),(39,3,5,11.91,20.00,1,'2025-11-08 00:00:00'),(40,1,5,9.06,10.00,1,'2026-04-02 00:00:00'),(41,2,5,3.03,10.00,1,'2026-04-02 00:00:00'),(42,3,5,3.33,10.00,1,'2026-04-02 00:00:00'),(43,1,5,3.72,10.00,2,'2025-11-25 00:00:00'),(44,2,5,5.23,10.00,2,'2025-11-25 00:00:00'),(45,3,5,6.51,10.00,2,'2025-11-25 00:00:00'),(46,1,8,7.56,10.00,1,'2025-11-25 00:00:00'),(47,2,8,7.54,10.00,1,'2025-11-25 00:00:00'),(48,3,8,9.14,10.00,1,'2025-11-25 00:00:00'),(49,1,8,11.13,20.00,1,'2025-12-10 00:00:00'),(50,2,8,18.94,20.00,1,'2025-12-10 00:00:00'),(51,3,8,15.85,20.00,1,'2025-12-10 00:00:00'),(52,1,8,7.68,20.00,2,'2026-04-02 00:00:00'),(53,2,8,7.73,20.00,2,'2026-04-02 00:00:00'),(54,3,8,10.26,20.00,2,'2026-04-02 00:00:00'),(55,4,9,3.78,10.00,2,'2025-10-20 00:00:00'),(56,5,9,3.38,10.00,2,'2025-10-20 00:00:00'),(57,6,9,3.95,10.00,2,'2025-10-20 00:00:00'),(58,4,9,13.16,20.00,1,'2026-03-10 00:00:00'),(59,5,9,8.12,20.00,1,'2026-03-10 00:00:00'),(60,6,9,9.18,20.00,1,'2026-03-10 00:00:00'),(61,4,9,12.68,20.00,1,'2026-02-03 00:00:00'),(62,5,9,7.33,20.00,1,'2026-02-03 00:00:00'),(63,6,9,11.26,20.00,1,'2026-02-03 00:00:00'),(64,4,9,3.26,10.00,1,'2025-10-05 00:00:00'),(65,5,9,3.15,10.00,1,'2025-10-05 00:00:00'),(66,6,9,4.17,10.00,1,'2025-10-05 00:00:00'),(67,4,6,6.15,10.00,2,'2026-03-10 00:00:00'),(68,5,6,9.34,10.00,2,'2026-03-10 00:00:00'),(69,6,6,9.01,10.00,2,'2026-03-10 00:00:00'),(70,4,6,13.40,20.00,2,'2025-11-08 00:00:00'),(71,5,6,7.86,20.00,2,'2025-11-08 00:00:00'),(72,6,6,18.51,20.00,2,'2025-11-08 00:00:00'),(73,4,1,10.91,20.00,2,'2025-12-10 00:00:00'),(74,5,1,19.13,20.00,2,'2025-12-10 00:00:00'),(75,6,1,15.52,20.00,2,'2025-12-10 00:00:00'),(76,4,1,5.52,10.00,1,'2026-04-02 00:00:00'),(77,5,1,3.45,10.00,1,'2026-04-02 00:00:00'),(78,6,1,5.66,10.00,1,'2026-04-02 00:00:00'),(79,4,1,6.04,10.00,2,'2025-10-20 00:00:00'),(80,5,1,5.08,10.00,2,'2025-10-20 00:00:00'),(81,6,1,3.92,10.00,2,'2025-10-20 00:00:00'),(82,4,4,6.95,10.00,1,'2026-01-15 00:00:00'),(83,5,4,9.05,10.00,1,'2026-01-15 00:00:00'),(84,6,4,3.62,10.00,1,'2026-01-15 00:00:00'),(85,4,4,4.76,10.00,2,'2026-03-10 00:00:00'),(86,5,4,8.97,10.00,2,'2026-03-10 00:00:00'),(87,6,4,8.57,10.00,2,'2026-03-10 00:00:00'),(88,4,4,9.54,10.00,1,'2025-11-25 00:00:00'),(89,5,4,6.16,10.00,1,'2025-11-25 00:00:00'),(90,6,4,8.30,10.00,1,'2025-11-25 00:00:00'),(91,7,1,19.46,20.00,1,'2026-03-10 00:00:00'),(92,8,1,6.91,20.00,1,'2026-03-10 00:00:00'),(93,9,1,11.68,20.00,1,'2026-03-10 00:00:00'),(94,7,1,6.90,10.00,2,'2025-10-20 00:00:00'),(95,8,1,3.39,10.00,2,'2025-10-20 00:00:00'),(96,9,1,4.32,10.00,2,'2025-10-20 00:00:00'),(97,7,1,5.62,10.00,2,'2026-01-15 00:00:00'),(98,8,1,4.95,10.00,2,'2026-01-15 00:00:00'),(99,9,1,7.24,10.00,2,'2026-01-15 00:00:00'),(100,7,6,6.86,10.00,2,'2025-11-08 00:00:00'),(101,8,6,9.66,10.00,2,'2025-11-08 00:00:00'),(102,9,6,5.75,10.00,2,'2025-11-08 00:00:00'),(103,7,6,5.87,10.00,1,'2026-01-15 00:00:00'),(104,8,6,4.90,10.00,1,'2026-01-15 00:00:00'),(105,9,6,5.43,10.00,1,'2026-01-15 00:00:00'),(106,7,6,19.26,20.00,1,'2026-04-02 00:00:00'),(107,8,6,9.17,20.00,1,'2026-04-02 00:00:00'),(108,9,6,8.12,20.00,1,'2026-04-02 00:00:00'),(109,7,6,7.45,10.00,2,'2026-03-10 00:00:00'),(110,8,6,6.17,10.00,2,'2026-03-10 00:00:00'),(111,9,6,4.57,10.00,2,'2026-03-10 00:00:00'),(112,7,3,13.07,20.00,1,'2025-10-20 00:00:00'),(113,8,3,8.37,20.00,1,'2025-10-20 00:00:00'),(114,9,3,11.30,20.00,1,'2025-10-20 00:00:00'),(115,7,3,16.50,20.00,1,'2025-11-08 00:00:00'),(116,8,3,19.94,20.00,1,'2025-11-08 00:00:00'),(117,9,3,7.72,20.00,1,'2025-11-08 00:00:00'),(118,10,5,16.09,20.00,2,'2026-01-15 00:00:00'),(119,11,5,15.68,20.00,2,'2026-01-15 00:00:00'),(120,12,5,9.54,20.00,2,'2026-01-15 00:00:00'),(121,10,5,7.56,20.00,1,'2025-10-20 00:00:00'),(122,11,5,16.20,20.00,1,'2025-10-20 00:00:00'),(123,12,5,6.80,20.00,1,'2025-10-20 00:00:00'),(124,10,1,5.21,10.00,1,'2026-04-02 00:00:00'),(125,11,1,4.81,10.00,1,'2026-04-02 00:00:00'),(126,12,1,8.94,10.00,1,'2026-04-02 00:00:00'),(127,10,1,16.70,20.00,2,'2025-12-10 00:00:00'),(128,11,1,18.52,20.00,2,'2025-12-10 00:00:00'),(129,12,1,11.66,20.00,2,'2025-12-10 00:00:00'),(130,10,1,13.37,20.00,2,'2026-03-10 00:00:00'),(131,11,1,10.52,20.00,2,'2026-03-10 00:00:00'),(132,12,1,7.24,20.00,2,'2026-03-10 00:00:00'),(133,10,2,15.03,20.00,1,'2025-12-10 00:00:00'),(134,11,2,11.31,20.00,1,'2025-12-10 00:00:00'),(135,12,2,10.33,20.00,1,'2025-12-10 00:00:00'),(136,10,2,7.93,20.00,1,'2026-03-10 00:00:00'),(137,11,2,11.05,20.00,1,'2026-03-10 00:00:00'),(138,12,2,9.55,20.00,1,'2026-03-10 00:00:00'),(139,10,2,3.88,10.00,1,'2026-04-02 00:00:00'),(140,11,2,8.28,10.00,1,'2026-04-02 00:00:00'),(141,12,2,3.92,10.00,1,'2026-04-02 00:00:00'),(142,10,4,11.04,20.00,2,'2025-10-05 00:00:00'),(143,11,4,8.37,20.00,2,'2025-10-05 00:00:00'),(144,12,4,13.83,20.00,2,'2025-10-05 00:00:00'),(145,10,4,9.94,20.00,2,'2025-12-10 00:00:00'),(146,11,4,9.86,20.00,2,'2025-12-10 00:00:00'),(147,12,4,18.51,20.00,2,'2025-12-10 00:00:00'),(148,13,3,8.89,10.00,1,'2025-12-10 00:00:00'),(149,14,3,3.38,10.00,1,'2025-12-10 00:00:00'),(150,15,3,8.89,10.00,1,'2025-12-10 00:00:00'),(151,13,3,7.63,20.00,2,'2025-11-08 00:00:00'),(152,14,3,19.40,20.00,2,'2025-11-08 00:00:00'),(153,15,3,18.24,20.00,2,'2025-11-08 00:00:00'),(154,13,3,16.29,20.00,1,'2026-01-15 00:00:00'),(155,14,3,13.55,20.00,1,'2026-01-15 00:00:00'),(156,15,3,6.73,20.00,1,'2026-01-15 00:00:00'),(157,13,3,9.21,20.00,1,'2025-10-05 00:00:00'),(158,14,3,10.09,20.00,1,'2025-10-05 00:00:00'),(159,15,3,18.17,20.00,1,'2025-10-05 00:00:00'),(160,13,8,12.56,20.00,1,'2025-11-08 00:00:00'),(161,14,8,9.95,20.00,1,'2025-11-08 00:00:00'),(162,15,8,11.63,20.00,1,'2025-11-08 00:00:00'),(163,13,8,8.06,10.00,1,'2026-03-10 00:00:00'),(164,14,8,6.41,10.00,1,'2026-03-10 00:00:00'),(165,15,8,9.63,10.00,1,'2026-03-10 00:00:00'),(166,13,8,7.14,10.00,1,'2025-11-25 00:00:00'),(167,14,8,4.94,10.00,1,'2025-11-25 00:00:00'),(168,15,8,3.62,10.00,1,'2025-11-25 00:00:00'),(169,13,7,17.72,20.00,2,'2026-04-02 00:00:00'),(170,14,7,11.49,20.00,2,'2026-04-02 00:00:00'),(171,15,7,18.95,20.00,2,'2026-04-02 00:00:00'),(172,13,7,3.87,10.00,1,'2026-02-03 00:00:00'),(173,14,7,5.32,10.00,1,'2026-02-03 00:00:00'),(174,15,7,7.81,10.00,1,'2026-02-03 00:00:00'),(175,13,7,10.08,20.00,1,'2025-10-05 00:00:00'),(176,14,7,8.98,20.00,1,'2025-10-05 00:00:00'),(177,15,7,7.85,20.00,1,'2025-10-05 00:00:00');
/*!40000 ALTER TABLE `evaluation` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `evenement`
--

DROP TABLE IF EXISTS `evenement`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `evenement` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(100) NOT NULL,
  `nom` varchar(150) NOT NULL,
  `responsable` varchar(150) DEFAULT NULL,
  `date` datetime NOT NULL,
  `invites` text,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `evenement`
--

LOCK TABLES `evenement` WRITE;
/*!40000 ALTER TABLE `evenement` DISABLE KEYS */;
/*!40000 ALTER TABLE `evenement` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `information`
--

DROP TABLE IF EXISTS `information`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `information` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_user` int NOT NULL,
  `numero` varchar(15) DEFAULT NULL,
  `mail` varchar(150) DEFAULT NULL,
  `adresse` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_user` (`id_user`),
  CONSTRAINT `information_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `information`
--

LOCK TABLES `information` WRITE;
/*!40000 ALTER TABLE `information` DISABLE KEYS */;
/*!40000 ALTER TABLE `information` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `log`
--

DROP TABLE IF EXISTS `log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `action` varchar(100) NOT NULL,
  `target_type` varchar(50) DEFAULT NULL,
  `target_id` int DEFAULT NULL,
  `ip_address` varchar(45) DEFAULT NULL,
  `user_agent` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `log_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `log`
--

LOCK TABLES `log` WRITE;
/*!40000 ALTER TABLE `log` DISABLE KEYS */;
/*!40000 ALTER TABLE `log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `mail`
--

DROP TABLE IF EXISTS `mail`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `mail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_expediteur` int NOT NULL,
  `id_destinataire` int NOT NULL,
  `objet` varchar(255) DEFAULT NULL,
  `contenu` text,
  `date` datetime NOT NULL DEFAULT (now()),
  PRIMARY KEY (`id`),
  KEY `id_expediteur` (`id_expediteur`),
  KEY `id_destinataire` (`id_destinataire`),
  CONSTRAINT `mail_ibfk_1` FOREIGN KEY (`id_expediteur`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `mail_ibfk_2` FOREIGN KEY (`id_destinataire`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `mail`
--

LOCK TABLES `mail` WRITE;
/*!40000 ALTER TABLE `mail` DISABLE KEYS */;
/*!40000 ALTER TABLE `mail` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `matiere`
--

DROP TABLE IF EXISTS `matiere`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `matiere` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `matiere`
--

LOCK TABLES `matiere` WRITE;
/*!40000 ALTER TABLE `matiere` DISABLE KEYS */;
INSERT INTO `matiere` VALUES (1,'Mathematiques'),(2,'Physique-Chimie'),(3,'Francais'),(4,'Histoire-Geographie'),(5,'Anglais'),(6,'Informatique'),(7,'Philosophie'),(8,'SVT'),(9,'EPS');
/*!40000 ALTER TABLE `matiere` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `menu`
--

DROP TABLE IF EXISTS `menu`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` datetime NOT NULL,
  `entree` varchar(150) DEFAULT NULL,
  `plat` varchar(150) DEFAULT NULL,
  `dessert` varchar(150) DEFAULT NULL,
  `special` tinyint(1) DEFAULT NULL,
  `special_info` varchar(255) DEFAULT NULL,
  `id_evenement` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_evenement` (`id_evenement`),
  CONSTRAINT `menu_ibfk_1` FOREIGN KEY (`id_evenement`) REFERENCES `evenement` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu`
--

LOCK TABLES `menu` WRITE;
/*!40000 ALTER TABLE `menu` DISABLE KEYS */;
/*!40000 ALTER TABLE `menu` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parent`
--

DROP TABLE IF EXISTS `parent`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parent` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_user` int NOT NULL,
  `id_eleve` int NOT NULL,
  `id_information` int DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id_user` (`id_user`),
  KEY `id_eleve` (`id_eleve`),
  KEY `id_information` (`id_information`),
  CONSTRAINT `parent_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `user` (`id`) ON DELETE CASCADE,
  CONSTRAINT `parent_ibfk_2` FOREIGN KEY (`id_eleve`) REFERENCES `eleve` (`id`) ON DELETE CASCADE,
  CONSTRAINT `parent_ibfk_3` FOREIGN KEY (`id_information`) REFERENCES `information` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parent`
--

LOCK TABLES `parent` WRITE;
/*!40000 ALTER TABLE `parent` DISABLE KEYS */;
INSERT INTO `parent` VALUES (1,8,1,NULL),(2,10,2,NULL),(3,12,3,NULL),(4,14,4,NULL),(5,16,5,NULL),(6,18,6,NULL),(7,20,7,NULL),(8,22,8,NULL),(9,24,9,NULL),(10,26,10,NULL),(11,28,11,NULL),(12,30,12,NULL),(13,32,13,NULL),(14,34,14,NULL),(15,36,15,NULL);
/*!40000 ALTER TABLE `parent` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prof`
--

DROP TABLE IF EXISTS `prof`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prof` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_user` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_user` (`id_user`),
  CONSTRAINT `prof_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prof`
--

LOCK TABLES `prof` WRITE;
/*!40000 ALTER TABLE `prof` DISABLE KEYS */;
INSERT INTO `prof` VALUES (1,2),(2,3),(3,4),(4,5),(5,6);
/*!40000 ALTER TABLE `prof` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prof_matiere`
--

DROP TABLE IF EXISTS `prof_matiere`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prof_matiere` (
  `id_prof` int NOT NULL,
  `id_matiere` int NOT NULL,
  PRIMARY KEY (`id_prof`,`id_matiere`),
  KEY `id_matiere` (`id_matiere`),
  CONSTRAINT `prof_matiere_ibfk_1` FOREIGN KEY (`id_prof`) REFERENCES `prof` (`id`),
  CONSTRAINT `prof_matiere_ibfk_2` FOREIGN KEY (`id_matiere`) REFERENCES `matiere` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prof_matiere`
--

LOCK TABLES `prof_matiere` WRITE;
/*!40000 ALTER TABLE `prof_matiere` DISABLE KEYS */;
INSERT INTO `prof_matiere` VALUES (1,1),(4,1),(1,2),(2,3),(3,4),(3,5),(4,6),(2,7),(5,8),(5,9);
/*!40000 ALTER TABLE `prof_matiere` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `salle`
--

DROP TABLE IF EXISTS `salle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `salle` (
  `id` int NOT NULL AUTO_INCREMENT,
  `nom` varchar(100) NOT NULL,
  `id_etage` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id_etage` (`id_etage`),
  CONSTRAINT `salle_ibfk_1` FOREIGN KEY (`id_etage`) REFERENCES `etage` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `salle`
--

LOCK TABLES `salle` WRITE;
/*!40000 ALTER TABLE `salle` DISABLE KEYS */;
INSERT INTO `salle` VALUES (1,'101',1),(2,'102',1),(3,'103',1),(4,'201',1),(5,'202',1),(6,'Labo 1',2),(7,'Labo 2',2),(8,'Salle Info',2),(9,'Gymnase',2);
/*!40000 ALTER TABLE `salle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `session`
--

DROP TABLE IF EXISTS `session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `session` (
  `id` int NOT NULL AUTO_INCREMENT,
  `suid` varchar(36) NOT NULL,
  `id_user` int NOT NULL,
  `expire_le` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `suid` (`suid`),
  KEY `id_user` (`id_user`),
  CONSTRAINT `session_ibfk_1` FOREIGN KEY (`id_user`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `session`
--

LOCK TABLES `session` WRITE;
/*!40000 ALTER TABLE `session` DISABLE KEYS */;
/*!40000 ALTER TABLE `session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `type` enum('élève','employé','parent','administrateur') NOT NULL,
  `nom` varchar(100) NOT NULL,
  `prenom` varchar(100) NOT NULL,
  `username` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  `mail_interne` varchar(150) DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL,
  `setup_token` varchar(100) DEFAULT NULL,
  `setup_token_expires` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `mail_interne` (`mail_interne`),
  UNIQUE KEY `setup_token` (`setup_token`)
) ENGINE=InnoDB AUTO_INCREMENT=37 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'administrateur','Admin','Guardia','admin','$2b$12$9tsvTNgV7b5P2ZGY.kYJs.0H6usi/HVSJnr9O1yZrfkSsfRXq8yd6','admin@guardiaschool.fr',1,NULL,NULL),(2,'employé','Dupont','Marc','marc.dupont','$2b$12$wH4fpn15O0sdNS7L8LEA7.bXUr1B46fvOjWccVAcwYm7Jto1KLiva','marc.dupont@guardiaschool.fr',1,NULL,NULL),(3,'employé','Leroy','Sophie','sophie.leroy','$2b$12$9TZvwdIQMfRoxqDheSy8k.wivDkeaDV./BL0Wk9sdYEeCD2GiFrmO','sophie.leroy@guardiaschool.fr',1,NULL,NULL),(4,'employé','Martin','Pierre','pierre.martin','$2b$12$vb8x2gWkMScfeZ71ujMguekunAVnje9l2W6eYfiyClqRQfeFOgQvm','pierre.martin@guardiaschool.fr',1,NULL,NULL),(5,'employé','Bernard','Claire','claire.bernard','$2b$12$bVvpZv1urQDF3cm/Git9V.S5U6Gaoh.CEelsy4wSosPPGzBCt17Fi','claire.bernard@guardiaschool.fr',1,NULL,NULL),(6,'employé','Moreau','Julie','julie.moreau','$2b$12$FKbCsZRatLrRoYNZBzLFqufd6K2XhMCZ1srkPqMTgxvKW7u8hO4Ru','julie.moreau@guardiaschool.fr',1,NULL,NULL),(7,'élève','Dubois','Lucas','lucas.dubois','$2b$12$X1.6965LIqRMVbABc7260.RQg9b20mnGC45srUnIJoVrPoPoyJyQ6','lucas.dubois@guardiaschool.fr',1,NULL,NULL),(8,'parent','Dubois','Parent-Lucas','lucas.duboisparent','$2b$12$MJHEKstgpZwUrrgwOdemL.CKEJ1pV0nfJt4RPUtHB1R4oILaidEKC','lucas.dubois.parent@guardiaschool.fr',1,NULL,NULL),(9,'élève','Petit','Emma','emma.petit','$2b$12$j/OBeMAkn93l1hxRm9h9oO5ST0.ksc.3KBDGdhr7hC7OMmvz90N7S','emma.petit@guardiaschool.fr',1,NULL,NULL),(10,'parent','Petit','Parent-Emma','emma.petitparent','$2b$12$64sgaIhjKBPUpLGUaureQu8D2xOTtBAg7UE56sDuimxvwXA45F1hi','emma.petit.parent@guardiaschool.fr',1,NULL,NULL),(11,'élève','Robert','Noah','noah.robert','$2b$12$EVOkxHklAKDWkA28Vv1xVOEdvQ/CFicT4yO576k1fvhC8ZxLx7K8C','noah.robert@guardiaschool.fr',1,NULL,NULL),(12,'parent','Robert','Parent-Noah','noah.robertparent','$2b$12$7YXCU9GidcaDjlNzAWan/O00lnLpyRzafsjUKYtnlltEw8y/8bXLe','noah.robert.parent@guardiaschool.fr',1,NULL,NULL),(13,'élève','Richard','Lea','lea.richard','$2b$12$h359VBifd5ZuCw3EbRwnIeCU8oeeWyJ.xle46zFmHXSgB1izkSLmG','lea.richard@guardiaschool.fr',1,NULL,NULL),(14,'parent','Richard','Parent-Lea','lea.richardparent','$2b$12$Pniri8URmZBKIVfqNk/lcOhlHJkx20a7ieYEFXvyMpvWTg6H3h86u','lea.richard.parent@guardiaschool.fr',1,NULL,NULL),(15,'élève','Thomas','Hugo','hugo.thomas','$2b$12$779xYEybXllenX2bJ3s1J.vc2EfB.lVBoRUgujNP3CMeM1XXVk/V6','hugo.thomas@guardiaschool.fr',1,NULL,NULL),(16,'parent','Thomas','Parent-Hugo','hugo.thomasparent','$2b$12$V3gQiMwKrV9.vmbPAAb0Huw1e65ZL8O7R6hu2ipor5N8hoWFiaMPC','hugo.thomas.parent@guardiaschool.fr',1,NULL,NULL),(17,'élève','Simon','Camille','camille.simon','$2b$12$SQq5vN10qNE0nK0/fACDF.hUuHgoStuvSQGGng1H7dhWwQrjhit7q','camille.simon@guardiaschool.fr',1,NULL,NULL),(18,'parent','Simon','Parent-Camille','camille.simonparent','$2b$12$jnqJyfwVBC5m0OMQMBdkxe//OcDU6FS3833MeSXTuvMVLY7bK3j9O','camille.simon.parent@guardiaschool.fr',1,NULL,NULL),(19,'élève','Laurent','Antoine','antoine.laurent','$2b$12$ZM.AAy9Ec4IWoKDmvEGLTeG/lPKWvuIAEOnxR25m3kCSdS0LvXchu','antoine.laurent@guardiaschool.fr',1,NULL,NULL),(20,'parent','Laurent','Parent-Antoine','antoine.laurentparent','$2b$12$h.rF75/GyFAGwvbdP9kWrejblaFyEh1luBkN7eTNNgYg8JPRS7cMe','antoine.laurent.parent@guardiaschool.fr',1,NULL,NULL),(21,'élève','Michel','Chloe','chloe.michel','$2b$12$Crw.ghm2q0CJQxjXj06jp.qTy6d/urtBSunw80nk6ScCXSfv3QuYC','chloe.michel@guardiaschool.fr',1,NULL,NULL),(22,'parent','Michel','Parent-Chloe','chloe.michelparent','$2b$12$k3GtEq0O0OZXgc8XVqyNc.0wpKNFpsDY7I.YzhLFi4GifzDo6h8Ke','chloe.michel.parent@guardiaschool.fr',1,NULL,NULL),(23,'élève','Garcia','Raphael','raphael.garcia','$2b$12$mqvzDMiNJrW0T2Hv8HrvpODyelRZI2wQBJkVj/zfFlMNqC6vlN.eS','raphael.garcia@guardiaschool.fr',1,NULL,NULL),(24,'parent','Garcia','Parent-Raphael','raphael.garciaparent','$2b$12$MoWsDOuxXEZgv1EkoHWW4uie3QqjN/XZCpNMPokcgXbX5esqRVz5G','raphael.garcia.parent@guardiaschool.fr',1,NULL,NULL),(25,'élève','Martinez','Manon','manon.martinez','$2b$12$35kr4NcyVHaudtiRNS5QYuWZcyyb5cmF7mDrGd4pQoFUrVGcyNyh2','manon.martinez@guardiaschool.fr',1,NULL,NULL),(26,'parent','Martinez','Parent-Manon','manon.martinezparent','$2b$12$LOnom07KEiaAaBB/t7UT9uvpvaFDS4tg2xXSCB3G94pL6cYa1WCxu','manon.martinez.parent@guardiaschool.fr',1,NULL,NULL),(27,'élève','Lefebvre','Ethan','ethan.lefebvre','$2b$12$.vV1ZtxP.wROyzEsXs4NXOMt7H56IK9y4viTqQ7XAnXp4hov3Hatm','ethan.lefebvre@guardiaschool.fr',1,NULL,NULL),(28,'parent','Lefebvre','Parent-Ethan','ethan.lefebvreparent','$2b$12$izjd.zmeUwUz7rYOU7WiRudpWtTLsREtOG7zL45mEK7R295HtFEQi','ethan.lefebvre.parent@guardiaschool.fr',1,NULL,NULL),(29,'élève','Roux','Inès','inès.roux','$2b$12$kRARatQFi9Y6bV/nAW24JuBO3ho6NBQQqVlbVdeTPxBHteCtSYfDq','inès.roux@guardiaschool.fr',1,NULL,NULL),(30,'parent','Roux','Parent-Inès','inès.rouxparent','$2b$12$9eTg78G1hsolzSaC7Dh6duYhpm6J8H1an9Jv.SGsU6skVG7JKIB3K','inès.roux.parent@guardiaschool.fr',1,NULL,NULL),(31,'élève','Fontaine','Tom','tom.fontaine','$2b$12$Xz6rPxqtabJgWKNjDqjuLOXQgC45/mo9mBXSAJKsb6nyxKb9Wo5Xe','tom.fontaine@guardiaschool.fr',1,NULL,NULL),(32,'parent','Fontaine','Parent-Tom','tom.fontaineparent','$2b$12$7DqpDFOtYSUod466iMK1u.86lR.pr6PLfqtJgI8SI6.MZOMdBMnFS','tom.fontaine.parent@guardiaschool.fr',1,NULL,NULL),(33,'élève','Chevalier','Jade','jade.chevalier','$2b$12$RbS9G2pRuQrR8Pe9l0/fJOib7z4pnxtmjq4ZwEf5Qod0t4CYYdjiy','jade.chevalier@guardiaschool.fr',1,NULL,NULL),(34,'parent','Chevalier','Parent-Jade','jade.chevalierparent','$2b$12$0Xu17DwvqGG47YyT0Mlmd.Xt.qBGrGX7bomwXw9/7GwTjVtJbb1dy','jade.chevalier.parent@guardiaschool.fr',1,NULL,NULL),(35,'élève','Bonnet','Louis','louis.bonnet','$2b$12$veOW7tQ0N4vmrtk2buvEWOmqf4gCpVUMgsqb3pXPg8AttkliU5The','louis.bonnet@guardiaschool.fr',1,NULL,NULL),(36,'parent','Bonnet','Parent-Louis','louis.bonnetparent','$2b$12$byXeuRtQt3gyErjGL/hpwOrzNLvnvNVGqIo9J.q33levYHyrSJ04G','louis.bonnet.parent@guardiaschool.fr',1,NULL,NULL);
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-06 21:13:46

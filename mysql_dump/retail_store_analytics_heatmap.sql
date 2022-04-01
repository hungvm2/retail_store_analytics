-- MySQL dump 10.13  Distrib 8.0.28, for Linux (x86_64)
--
-- Host: localhost    Database: retail_store_analytics
-- ------------------------------------------------------
-- Server version	8.0.28-0ubuntu0.20.04.3

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `heatmap`
--

DROP TABLE IF EXISTS `heatmap`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `heatmap` (
  `id_heatmap` int NOT NULL AUTO_INCREMENT,
  `timestamp` timestamp NOT NULL,
  `id_camera` int NOT NULL,
  `data` json NOT NULL,
  PRIMARY KEY (`id_heatmap`),
  KEY `fk_heatmap_1_idx` (`id_camera`),
  CONSTRAINT `fk_heatmap_1` FOREIGN KEY (`id_camera`) REFERENCES `camera` (`id_camera`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `heatmap`
--

LOCK TABLES `heatmap` WRITE;
/*!40000 ALTER TABLE `heatmap` DISABLE KEYS */;
INSERT INTO `heatmap` VALUES (1,'2022-03-31 05:35:46',1,'{\"3-6\": 3, \"3-7\": 2, \"10:15\": 10, \"69-60\": 3}'),(2,'2022-03-31 05:40:00',1,'{\"3-6\": 3, \"3-7\": 2, \"10:15\": 10, \"69-60\": 3}'),(3,'2022-03-31 05:45:00',1,'{\"3-6\": 3, \"3-7\": 2, \"69-60\": 3}'),(4,'2022-03-31 05:55:00',1,'{\"3-6\": 2, \"3-7\": 2, \"69-60\": 3}'),(5,'2022-03-31 05:55:00',2,'{\"3-6\": 2, \"3-7\": 2, \"69-60\": 3}');
/*!40000 ALTER TABLE `heatmap` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2022-04-01 11:27:12

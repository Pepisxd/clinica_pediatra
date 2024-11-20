-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: diagnosticos
-- ------------------------------------------------------
-- Server version	9.0.1

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
-- Table structure for table `cita`
--

DROP TABLE IF EXISTS `cita`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cita` (
  `ID_Cita` int NOT NULL AUTO_INCREMENT,
  `ID_Paciente` int NOT NULL,
  `ID_Medico` int NOT NULL,
  `Fecha` date NOT NULL,
  `Hora` time NOT NULL,
  `Estado` enum('Pendiente','Confirmada','Cancelada','Completada') NOT NULL DEFAULT 'Pendiente',
  `Motivo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ID_Cita`),
  KEY `ID_Medico` (`ID_Medico`),
  KEY `ID_Paciente` (`ID_Paciente`),
  CONSTRAINT `cita_ibfk_1` FOREIGN KEY (`ID_Medico`) REFERENCES `usuario` (`ID_Usuario`),
  CONSTRAINT `cita_ibfk_2` FOREIGN KEY (`ID_Paciente`) REFERENCES `paciente` (`ID_Paciente`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cita`
--

LOCK TABLES `cita` WRITE;
/*!40000 ALTER TABLE `cita` DISABLE KEYS */;
INSERT INTO `cita` VALUES (14,7,2,'2024-11-11','09:45:00','Cancelada','Vacunacion'),(15,7,2,'2024-12-12','09:15:00','Cancelada','Vacunacion'),(17,3,2,'2024-11-26','17:00:00','Confirmada','Fiebre'),(18,2,2,'2024-11-24','12:00:00','Pendiente','Vacunacion'),(20,24,5,'2024-11-14','11:00:00','Pendiente','Revisión bronquiolitis'),(21,24,5,'2024-11-27','12:00:00','Confirmada','Control de peso'),(22,3,2,'2024-11-15','16:00:00','Confirmada','Seguimiento gastroenteritis'),(23,3,2,'2024-11-19','14:00:00','Pendiente','Control rutinario'),(24,1,3,'2024-11-25','01:00:00','Pendiente','Revision'),(25,25,2,'2024-11-24','06:00:00','Cancelada','Chequeo'),(26,25,2,'2024-11-15','12:00:00','Confirmada','aaaaa');
/*!40000 ALTER TABLE `cita` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `diagnostico`
--

DROP TABLE IF EXISTS `diagnostico`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagnostico` (
  `ID_Diagnostico` int NOT NULL AUTO_INCREMENT,
  `ID_Paciente` int DEFAULT NULL,
  `ID_Medico` int DEFAULT NULL,
  `ID_Enfermedad` int DEFAULT NULL,
  `Fecha_Diagnostico` varchar(20) DEFAULT NULL,
  `Observaciones` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`ID_Diagnostico`),
  KEY `ID_Paciente` (`ID_Paciente`),
  KEY `ID_Medico` (`ID_Medico`),
  KEY `ID_Enfermedad` (`ID_Enfermedad`),
  CONSTRAINT `diagnostico_ibfk_1` FOREIGN KEY (`ID_Paciente`) REFERENCES `paciente` (`ID_Paciente`),
  CONSTRAINT `diagnostico_ibfk_2` FOREIGN KEY (`ID_Medico`) REFERENCES `usuario` (`ID_Usuario`),
  CONSTRAINT `diagnostico_ibfk_3` FOREIGN KEY (`ID_Enfermedad`) REFERENCES `enfermedad` (`ID_Enfermedad`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diagnostico`
--

LOCK TABLES `diagnostico` WRITE;
/*!40000 ALTER TABLE `diagnostico` DISABLE KEYS */;
INSERT INTO `diagnostico` VALUES (1,1,2,NULL,'2024-01-15','Otitis media aguda del oído derecho. Control en 48 horas. editado'),(3,3,2,3,'2024-02-15','Gastroenteritis aguda. Vigilar estado de hidratación.'),(4,24,2,9,'2024-11-15','aaaaaaaaa'),(5,25,2,8,'2024-11-15','SANGRE222');
/*!40000 ALTER TABLE `diagnostico` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `diagnostico_sintoma`
--

DROP TABLE IF EXISTS `diagnostico_sintoma`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `diagnostico_sintoma` (
  `ID_Diagnostico` int NOT NULL,
  `ID_Sintoma` int NOT NULL,
  PRIMARY KEY (`ID_Diagnostico`,`ID_Sintoma`),
  KEY `ID_Sintoma` (`ID_Sintoma`),
  CONSTRAINT `diagnostico_sintoma_ibfk_1` FOREIGN KEY (`ID_Diagnostico`) REFERENCES `diagnostico` (`ID_Diagnostico`),
  CONSTRAINT `diagnostico_sintoma_ibfk_2` FOREIGN KEY (`ID_Sintoma`) REFERENCES `sintoma` (`ID_Sintoma`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `diagnostico_sintoma`
--

LOCK TABLES `diagnostico_sintoma` WRITE;
/*!40000 ALTER TABLE `diagnostico_sintoma` DISABLE KEYS */;
INSERT INTO `diagnostico_sintoma` VALUES (4,1),(4,6),(4,11);
/*!40000 ALTER TABLE `diagnostico_sintoma` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enfermedad`
--

DROP TABLE IF EXISTS `enfermedad`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enfermedad` (
  `ID_Enfermedad` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(45) NOT NULL,
  `Descripcion` varchar(100) DEFAULT NULL,
  `Gravedad` int DEFAULT NULL,
  PRIMARY KEY (`ID_Enfermedad`)
) ENGINE=InnoDB AUTO_INCREMENT=39 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enfermedad`
--

LOCK TABLES `enfermedad` WRITE;
/*!40000 ALTER TABLE `enfermedad` DISABLE KEYS */;
INSERT INTO `enfermedad` VALUES (2,'Bronquiolitis','Infección viral de las vías respiratorias inferiores',3),(3,'Gastroenteritis Aguda','Inflamación del estómago e intestinos',2),(4,'Amigdalitis','Infección de las amígdalas',2),(8,'Neumonía','Infección en los pulmones que provoca inflamación en los sacos de aire',3),(9,'Rinofaringitis','Infección viral del tracto respiratorio superior',1),(10,'Faringitis estreptocócica','Infección bacteriana de la garganta causada por estreptococos',2),(11,'Conjuntivitis','Inflamación de la membrana que cubre el ojo y el interior del párpado',1),(12,'Sarampión','Enfermedad viral contagiosa caracterizada por erupciones en la piel',3),(13,'Rubeola','Infección viral leve con erupción cutánea y fiebre',2),(15,'Diarrea infecciosa','Infección intestinal que causa diarrea y deshidratación',2),(16,'Anemia ferropénica','Trastorno causado por niveles bajos de hierro en sangre',2),(17,'Celulitis','Infección bacteriana de la piel y tejidos subyacentes',3),(18,'Escabiosis','Infestación de la piel por ácaros que causa picazón intensa',1),(19,'Hepatitis A','Infección viral del hígado que puede causar ictericia y fatiga',3),(20,'Tos ferina','Infección respiratoria bacteriana que causa tos severa',3),(21,'Parotiditis (Paperas)','Infección viral que inflama las glándulas salivales',2),(22,'Impetigo','Infección bacteriana superficial de la piel',1),(23,'Difteria','Infección bacteriana grave que afecta la garganta y las vías respiratorias',4),(24,'Poliomielitis','Enfermedad viral que puede causar parálisis',4),(25,'Bronquitis','Inflamación de los bronquios causada por infección viral o bacteriana',2),(26,'Anemia','sangre',1),(27,'Varicela','Puntos rojos, debilidad',2);
/*!40000 ALTER TABLE `enfermedad` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `enfermedad_sintoma`
--

DROP TABLE IF EXISTS `enfermedad_sintoma`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `enfermedad_sintoma` (
  `ID_Enfermedad` int NOT NULL,
  `ID_Sintoma` int NOT NULL,
  PRIMARY KEY (`ID_Enfermedad`,`ID_Sintoma`),
  KEY `ID_Sintoma` (`ID_Sintoma`),
  CONSTRAINT `enfermedad_sintoma_ibfk_1` FOREIGN KEY (`ID_Enfermedad`) REFERENCES `enfermedad` (`ID_Enfermedad`),
  CONSTRAINT `enfermedad_sintoma_ibfk_2` FOREIGN KEY (`ID_Sintoma`) REFERENCES `sintoma` (`ID_Sintoma`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `enfermedad_sintoma`
--

LOCK TABLES `enfermedad_sintoma` WRITE;
/*!40000 ALTER TABLE `enfermedad_sintoma` DISABLE KEYS */;
INSERT INTO `enfermedad_sintoma` VALUES (3,1),(4,2),(9,2),(10,2),(11,2),(18,2),(2,3),(3,3),(4,3),(8,3),(9,3),(10,3),(12,3),(13,3),(15,3),(17,3),(19,3),(20,3),(21,3),(23,3),(24,3),(25,3),(4,5),(16,5),(19,5),(21,5),(3,6),(15,6),(2,7),(4,7),(8,7),(10,7),(20,7),(23,7),(25,7),(9,8),(12,8),(13,8),(11,9),(3,10),(15,10),(12,11),(13,11),(18,11),(22,11),(24,12),(11,13),(2,16),(8,16),(20,16),(23,16),(25,16),(16,17),(17,18),(22,18),(19,19),(21,20);
/*!40000 ALTER TABLE `enfermedad_sintoma` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `paciente`
--

DROP TABLE IF EXISTS `paciente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `paciente` (
  `ID_Paciente` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(45) NOT NULL,
  `Apellidos` varchar(45) NOT NULL,
  `Fecha_Nacimiento` varchar(45) DEFAULT NULL,
  `Direccion` varchar(45) DEFAULT NULL,
  `Correo` varchar(45) DEFAULT NULL,
  `Telefono` varchar(18) DEFAULT NULL,
  `Numero_Social` varchar(50) DEFAULT NULL,
  `ID_Medico` int DEFAULT NULL,
  PRIMARY KEY (`ID_Paciente`),
  KEY `ID_Medico` (`ID_Medico`),
  CONSTRAINT `paciente_ibfk_1` FOREIGN KEY (`ID_Medico`) REFERENCES `usuario` (`ID_Usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=26 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `paciente`
--

LOCK TABLES `paciente` WRITE;
/*!40000 ALTER TABLE `paciente` DISABLE KEYS */;
INSERT INTO `paciente` VALUES (1,'Lucas','Pérez','2020-05-15','Calle 123','padre.lucas@email.com','555-0101','NSS001',3),(2,'Ana','López','2021-08-22','Av. Principal 456','padre.ana@email.com','555-0102','NSS002',2),(3,'Roberto','Martínez','2022-11-30','Plaza Central 789','padre.roberto@email.com','555-0103','NSS003',2),(7,'pepe','oroz','2022-11-30','casa11','a@a.com','555-0102','NSS100',NULL),(24,'Abril','Dominguez','2024-11-12','Calle salado','Abril.padre@email.com','555-1234','NS0010',2),(25,'Gerardo','Dominguez','2017-04-09','Calle Aqua','Gera.padre@email.com','555-2424','NS008',2);
/*!40000 ALTER TABLE `paciente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `prueba`
--

DROP TABLE IF EXISTS `prueba`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `prueba` (
  `ID_Prueba` int NOT NULL AUTO_INCREMENT,
  `ID_Medico` int NOT NULL,
  `ID_Diagnostico` int NOT NULL,
  `Tipo` tinyint NOT NULL,
  `Nombre` varchar(100) NOT NULL,
  `Descripcion` text,
  `Resultado` text,
  PRIMARY KEY (`ID_Prueba`),
  CONSTRAINT `prueba_chk_1` CHECK ((`Tipo` in (1,2)))
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `prueba`
--

LOCK TABLES `prueba` WRITE;
/*!40000 ALTER TABLE `prueba` DISABLE KEYS */;
INSERT INTO `prueba` VALUES (2,2,2,1,'Prueba de Orina','Análisis para detectar infecciones urinarias.','Sin infecciones'),(4,2,2,1,'Prueba de Orina','Análisis para detectar infecciones urinarias.','Sin infecciones'),(11,2,1,1,'Prueba fisica','aaaa','Negativo'),(12,2,5,1,'Probando','aaaa','Positivo');
/*!40000 ALTER TABLE `prueba` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sintoma`
--

DROP TABLE IF EXISTS `sintoma`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sintoma` (
  `ID_Sintoma` int NOT NULL AUTO_INCREMENT,
  `Descripcion` varchar(100) NOT NULL,
  PRIMARY KEY (`ID_Sintoma`)
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sintoma`
--

LOCK TABLES `sintoma` WRITE;
/*!40000 ALTER TABLE `sintoma` DISABLE KEYS */;
INSERT INTO `sintoma` VALUES (1,'Llanto excesivo'),(2,'Irritabilidad'),(3,'Fiebre'),(5,'Pérdida de apetito'),(6,'Diarrea'),(7,'Tos'),(8,'Congestión nasal'),(9,'Dolor de oído'),(10,'Vómitos'),(11,'Dolor abdominal'),(12,'Dolor de cabeza'),(13,'Erupción cutánea'),(14,'Malestar general'),(15,'Dolor muscular'),(16,'Dificultad para respirar'),(17,'Dolor en el pecho'),(18,'Náuseas'),(19,'Dolor de garganta'),(20,'Ojos enrojecidos'),(21,'Hinchazón de las glándulas'),(22,'Secreción nasal'),(24,'Cansancio extremo'),(25,'Perdida de peso');
/*!40000 ALTER TABLE `sintoma` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `ID_Usuario` int NOT NULL AUTO_INCREMENT,
  `Nombre` varchar(45) NOT NULL,
  `Apellidos` varchar(50) NOT NULL,
  `Correo` varchar(45) NOT NULL,
  `Contrasena` varchar(255) DEFAULT NULL,
  `Rol` int NOT NULL,
  PRIMARY KEY (`ID_Usuario`),
  UNIQUE KEY `Correo` (`Correo`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (1,'Admin','Sistema','admin@hospital.com','$2b$12$/Pvgo.xQ0c3KN5.jeJiKc.Kjv8IyDiOITTTEEvUNnaamK1BbL3YBG',1),(2,'Dr. Juan','García López','juan.pediatra@hospital.com','$2b$12$ztWAxs1b9kJnaBNDggAMUe2Te97r2NxabHHu4Y2B1lKcm2RXji9na',2),(3,'María','Rodríguez','maria.secretaria@hospital.com','$2b$12$oZtkr60R6PTJOvk8AMTE2uCF2mtfbUvaZaosn8OuFzoGCYRttX.WS',3),(5,'Pedro Porro','Porro','dr@dr.com','$2b$12$yjOzzLrYYT2tDBZXxk8.ge1QW4oNYeZxwn7BQdfFw6fmIpHWlauoO',2),(6,'Luis','Dominguez','Luis.secretaria@hospital.com','$2b$12$LBFg/iibKfiAkD3WEjaxIeist75FIi8QF1BqXdgr3s.xV7fmhKsGG',3),(7,'jose','dominguez','jose@email.com','$2b$12$zZF.ZImOXJJCmDplm1076.7P0OscSmZfVdc1KD6uY9BvwMDH.z39i',3);
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2024-11-16 15:57:27

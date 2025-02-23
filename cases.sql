-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Feb 13, 2025 at 08:46 AM
-- Server version: 10.4.28-MariaDB
-- PHP Version: 8.2.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `scotus`
--

-- --------------------------------------------------------

--
-- Table structure for table `cases`
--

CREATE TABLE `cases` (
  `case_id` int(11) NOT NULL,
  `name` varchar(100) NOT NULL,
  `case_href` varchar(100) DEFAULT NULL,
  `view_count` int(11) DEFAULT NULL,
  `docket_number` varchar(10) DEFAULT NULL,
  `question` mediumtext DEFAULT NULL,
  `term` varchar(15) DEFAULT NULL,
  `description` varchar(255) DEFAULT NULL,
  `justia_url` varchar(100) DEFAULT NULL,
  `case_duration` int(11) DEFAULT NULL,
  `argued_duration` int(11) DEFAULT NULL,
  `delib_duration` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cases`
--

INSERT INTO `cases` (`case_id`, `name`, `case_href`, `view_count`, `docket_number`, `question`, `term`, `description`, `justia_url`, `case_duration`, `argued_duration`, `delib_duration`) VALUES
(62327, 'Chisholm v. Georgia', 'https://api.oyez.org/cases/1789-1850/2us419', 0, 'None', '<p>Can state citizens sue state governments in federal court? </p>\n', '1789-1850', 'A case in which the Court ruled that the states were under the jurisdiction of the Supreme Court and the federal government. ', 'https://supreme.justia.com/cases/federal/us/2/419/', 14, 1, 14),
(62328, 'Hylton v. United States', 'https://api.oyez.org/cases/1789-1850/3us171', 0, 'None', '<p>Was the carriage tax a direct tax, which would require apportionment among the states? </p>\n', '1789-1850', 'A case in which the Court held that the carriage tax was not a direct tax and thus was not subject to apportionment among the states.', 'https://supreme.justia.com/cases/federal/us/3/171/', 14, 3, 12),
(62329, 'Ware v. Hylton', 'https://api.oyez.org/cases/1789-1850/3us199', 0, 'None', '<p>Does the Treaty of Paris override an otherwise valid state law?</p>\n', '1789-1850', 'A case in which the Court held that federal courts have the power to determine the constitutionality of state laws, and a federal treaty supersedes any conflicting state law under the Supremacy Clause.', 'https://supreme.justia.com/cases/federal/us/3/199/', 30, 6, 24),
(62330, 'Calder v. Bull', 'https://api.oyez.org/cases/1789-1850/3us386', 0, 'None', '<p>Was the Connecticut legislation a violation of Article 1, Section 10, of the Constitution, which prohibits ex post facto laws?</p>\n', '1789-1850', NULL, 'https://supreme.justia.com/cases/federal/us/3/386/', 30, 2, 25),
(62331, 'Marbury v. Madison', 'https://api.oyez.org/cases/1789-1850/5us137', 0, '5us137', '<ol><li>Do the plaintiffs have a right to receive their commissions?</li>\n<li>Can they sue for their commissions in court?</li>\n<li>Does the Supreme Court have the authority to order the delivery of their commissions?</li>\n</ol>', '1789-1850', 'A case in which the Court established a precedent for judicial review in the United States, declaring that acts of Congress that conflict with the Constitution are null and void, as the Constitution is the supreme law of the land.', 'https://supreme.justia.com/cases/federal/us/5/137/', 13, 1, 13),
(62332, 'Little v. Barreme', 'https://api.oyez.org/cases/1789-1850/6us170', 0, 'None', '<p>Did the President have the authority to issue the order to capture ships travelling from French ports?</p>\n', '1789-1850', NULL, 'https://supreme.justia.com/cases/federal/us/6/170/', 13, 2, 10),
(62333, 'Fletcher v. Peck', 'https://api.oyez.org/cases/1789-1850/10us87', 0, 'None', '<p>Could the contract between Fletcher and Peck be invalidated by an act of the Georgia legislature?</p>\n', '1789-1850', 'A case in which the Court held that a contract is still binding and enforceable, even if secured illegally.', 'https://supreme.justia.com/cases/federal/us/10/87/', 29, 5, 12),
(62334, 'New Jersey v. Wilson', 'https://api.oyez.org/cases/1789-1850/11us164', 0, 'None', '<p>Did the repeal of the tax exemption impair the obligation of a contract between the state and the new owner of the land?</p>\n', '1789-1850', NULL, 'https://supreme.justia.com/cases/federal/us/11/164/', 2, 0, 2),
(62335, 'Martin v. Hunter\'s Lessee', 'https://api.oyez.org/cases/1789-1850/14us304', 0, 'None', '<p>Is Section 25 of the Judiciary Act, which grants the U.S. Supreme Court appellate review over state court cases involving federal law, unconstitutional?</p>\n<p> </p>\n', '1789-1850', 'A case in which the Court ruled that the Supreme Court of the United States overruled the courts of the states. ', 'https://supreme.justia.com/cases/federal/us/14/304/', 8, 3, 6),
(62336, 'McCulloch v. Maryland', 'https://api.oyez.org/cases/1789-1850/17us316', 0, '17us316', '<ol><li>Did Congress have the authority to establish the bank?</li>\n<li>Did the Maryland law unconstitutionally interfere with congressional powers?</li>\n</ol>', '1789-1850', 'A case in which the Court decided that the Second Bank of the United States could not be taxed by the state of Maryland, declaring that the government of individual states cannot impose laws on the functioning of the federal government.', 'https://supreme.justia.com/cases/federal/us/17/316/', 12, 9, 3);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `cases`
--
ALTER TABLE `cases`
  ADD PRIMARY KEY (`case_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

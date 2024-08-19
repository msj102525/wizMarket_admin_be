DROP TABLE movepopdata;

CREATE TABLE `movepopdata` (
  `keyword` varchar(255) NOT NULL,
  `yearmonth` varchar(6) NOT NULL,
  `location` varchar(255) DEFAULT NULL,
  `business` varchar(255) DEFAULT NULL,
  `person` varchar(255) DEFAULT NULL,
  `price` varchar(255) DEFAULT NULL,
  `wrcppl` varchar(255) DEFAULT NULL,
  `earn` varchar(255) DEFAULT NULL,
  `cnsmp` varchar(255) DEFAULT NULL,
  `hhCnt` varchar(255) DEFAULT NULL,
  `rsdppl` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`keyword`,`yearmonth`)
);

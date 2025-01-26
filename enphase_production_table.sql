use homepowerdb;
DROP TABLE IF EXISTS `enphase_production`;
CREATE TABLE `enphase_production` (
  `year` DECIMAL(4,0) NOT NULL,
  `month` DECIMAL(2,0) NOT NULL,
  `day` DECIMAL(2,0) NOT NULL,
  `hour` DECIMAL(2,0) NOT NULL,
  `minute` DECIMAL(2,0) NOT NULL,
  `wattHoursToday` DECIMAL(10,5) NOT NULL,
  `wattHoursSevenDays` DECIMAL(10,5) NOT NULL,
  `wattHoursLifetime` DECIMAL(15,5) NOT NULL,
  `wattsNow` DECIMAL(10,5) NOT NULL,
  `created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`year`,`month`,`day`,`hour`,`minute`)
);

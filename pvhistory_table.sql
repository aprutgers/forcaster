use homepowerdb;

#DROP TABLE IF EXISTS `pvhistory`;

CREATE TABLE `pvhistory` (
  `year` DECIMAL(4,0) NOT NULL,
  `month` DECIMAL(2,0) NOT NULL,
  `day` DECIMAL(2,0) NOT NULL,
  `hour` DECIMAL(2,0) NOT NULL,
  `gr_w` DECIMAL(10,5) NOT NULL,
  `tc` DECIMAL(10,5) NOT NULL,
  `kwh_pv` DECIMAL(10,5) NOT NULL,
  `kwh_s3p` DECIMAL(10,5) NOT NULL,
  `kwh_return` DECIMAL(10,5) NOT NULL,
  `created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (	`year`,`month`,`day`,`hour`)
);

# alters

ALTER TABLE pvhistory CHANGE kwh_pv  wh_pv DECIMAL(10,3) NOT NULL;
ALTER TABLE pvhistory CHANGE kwh_s3p wh_s3p DECIMAL(10,3) NOT NULL;
ALTER TABLE pvhistory CHANGE kwh_return wh_return DECIMAL(10,3) NOT NULL;

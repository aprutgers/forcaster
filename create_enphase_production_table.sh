#!/bin/sh
echo "create table enphase_production_table..." 
mysql -uroot < enphase_production_table.sql
echo "create table done." 

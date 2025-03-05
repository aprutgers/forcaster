import os
import sys
import mysql.connector
#import datetime
from datetime import datetime, timedelta
import json
import log
import math
import solar3p

#
# columns of pvhistory table:
#
#`day` date NOT NULL,
#`hour` DECIMAL(2,0) NOT NULL,
#`gr_w` DECIMAL(10,5) NOT NULL,
#`tc` DECIMAL(10,5) NOT NULL,
#`wh_pv` DECIMAL(10,5) NOT NULL,
#`wh_s3p` DECIMAL(10,5) NOT NULL,
#`wh_return` DECIMAL(10,5) NOT NULL, (power returned to the network)
#

# update_hour_pvhistory 
def update_hour_pvhistory(conn,now,wh_pv):
   curr_year  = now.year
   curr_month = now.month
   curr_day   = now.day
   curr_hour  = now.hour
   mycursor = conn.cursor()
   sql = 'update pvhistory set wh_pv=%s where year=%s and month=%s and day=%s and hour=%s'%(wh_pv,curr_year,curr_month,curr_day,curr_hour)
   log.logdebug(sql)
   mycursor.execute(sql)
   conn.commit();
   log.loginfo(str(mycursor.rowcount) + " record updated.")
   return mycursor.rowcount

def get_pv_production(conn,now):
   log.logdebug("get_pv_production")
   curr_year  = now.year
   curr_month = now.month
   curr_day   = now.day
   curr_hour  = now.hour

   cursor = conn.cursor()
   sql = 'select wattHoursToday from enphase_production where '
   sql = sql + 'year="%s" and month="%s" and day="%s" and hour="%s"'%(curr_year,curr_month,curr_day,curr_hour)
   log.logdebug('get_pv_production query='+sql)
   cursor.execute(sql)
   records = cursor.fetchall()
   log.loginfo('get_pv_production records:')
   log.loginfo(records)
   log.logdebug(str(cursor.rowcount) + " record found.")
   if (cursor.rowcount>0):
      return records[cursor.rowcount-1][0] # get last record for the hour
   else:
      log.logerror("no records found for specified year:%s/month:%s/day:%s/hour:%s"%(curr_year,curr_month,curr_day,curr_hour))
      return 0;

def update_hour(conn,location,rhour):

   # 1. get the past day/hour (need to run this just over the whole hour to process last hour)
   date_string = "2025-03-05 %02d:00"%(int(rhour))
   sdate = datetime.strptime(date_string, "%Y-%m-%d %H:%M")

   past_0hour = sdate
   past_1hour = sdate - timedelta(hours=1)
   past_2hour = sdate - timedelta(hours=2)
   log.loginfo("past_0hour"+str(past_0hour))
   log.loginfo("past_1hour"+str(past_1hour))
   log.loginfo("past_2hour"+str(past_2hour))

   # 3. get actual pv generated power in watt for day/hour
   past_0hour_wattHoursToday=get_pv_production(conn,past_0hour)
   log.loginfo("past 0hour wattHoursToday: " + str(past_0hour_wattHoursToday))
   past_1hour_wattHoursToday=get_pv_production(conn,past_1hour)
   log.loginfo("past 1hour wattHoursToday: " + str(past_1hour_wattHoursToday))
   delta_wattHoursToday = past_0hour_wattHoursToday - past_1hour_wattHoursToday
   # day wrapping protection, enphase will reset wattHoursToday to 0 for next day
   if (delta_wattHoursToday<0): delta_wattHoursToday=0

   # 5. get the power returned to the grid which should be a % of the delta_wattHoursToday
   #wattRetunedInHour = get_pv_watt_returned(conn,past_0hour)
   #log.logdebug("wattRetunedInHour="+str(wattRetunedInHour))
   log.logdebug("delta_wattHoursToday="+str(delta_wattHoursToday))

   # 6. insert record in pvhistory
   update_hour_pvhistory(conn,past_0hour,str(delta_wattHoursToday))

def main():
   # database connection
   conn = mysql.connector.connect(user='root', database='homepowerdb')
   # location: rotterdam as this is closest
   location='rotterdam'
   for rhour in (0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23):
      update_hour(conn,location,rhour)
   
main()

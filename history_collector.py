import os
import sys
import mysql.connector
import datetime
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

# insert_hour_pvhistory 
def insert_hour_pvhistory(conn,now,gr_w,tc,wh_pv,wh_s3p,wh_return):
   curr_year  = now.year
   curr_month = now.month
   curr_day   = now.day
   curr_hour  = now.hour
   mycursor = conn.cursor()
   sql = 'insert into pvhistory(year,month,day,hour,gr_w,tc,wh_pv,wh_s3p,wh_return) ' +\
         'values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
   mycursor.execute(sql,(curr_year,curr_month,curr_day,curr_hour,gr_w,tc,wh_pv,wh_s3p,wh_return))
   conn.commit();
   log.loginfo(str(mycursor.rowcount) + " record inserted.")
   return mycursor.rowcount

# load meteo gr_w and tc forcast data
def load_meteo_forcast_data(g_file):
   log.logdebug("open file=/home/ec2-user/solar3p/data/data."+g_file)
   with open("/home/ec2-user/solar3p/data/data."+g_file, 'r') as f:
      data = json.load(f)
   forcast = data['forecast']
   return forcast # dict

def get_day_hour_forcast(location,now):
   log.logdebug("get_day_hour_forcast")
   curr_year  = now.year
   curr_month = now.month
   curr_day   = now.day
   curr_hour  = now.hour
   # cet format: DD-MM-YYYY HH:MM
   curr_cet   = '%02d-%02d-%4d %02d:00'%(curr_day,curr_month,curr_year,curr_hour)
   
   forcast=load_meteo_forcast_data(location)
   # get the forcast for the day and hour - linear search
   for f in forcast:
      cet=f['cet'] 
      if (cet == curr_cet):
         return(f)

   log.logerror("could not find a forcast for curr_cet: " + curr_cet)
   log.logerror("return zeros")
   return { "tc": "0", "gr_w": "0" }

def get_pv_production(conn,now):
   log.logdebug("get_pv_production")
   curr_year  = now.year
   curr_month = now.month
   curr_day   = now.day
   curr_hour  = now.hour

   cursor = conn.cursor()
   sql = 'select wattHoursToday from enphase_production where '
   sql = sql + 'year="%s" and month="%s" and day="%s" and hour="%s"'%(curr_year,curr_month,curr_day,curr_hour)
   #log.logdebug('get_pv_production query='+sql)
   cursor.execute(sql)
   records = cursor.fetchall()
   #log.loginfo('get_pv_production records:')
   #log.loginfo(records)
   #log.debug(str(cursor.rowcount) + " record found.")
   if (cursor.rowcount>0):
      return records[cursor.rowcount-1][0] # get last record for the hour
   else:
      log.logerror("no records found for specified year:%s/month:%s/day:%s/hour:%s"%(curr_year,curr_month,curr_day,curr_hour))
      return 0;

def get_solar3p_forcast(now):
   log.logdebug("get_solar3p_forcast")
   curr_year  = now.year
   curr_month = now.month
   curr_day   = now.day
   curr_hour  = now.hour
   d_period="day" # default prediction period meteo (current + 4 days)
   d_pans=12       # default number of panels
   d_wp=405        # default watt power of each panel
   d_lay="SE"      # default orientation in geo direction N,NE,O,SE,S,SW,W,NW
   d_gran="hour"    # granulairity per hour
   d_file="rotterdam" # default name of data file
   try:
      # key example: 26-01-2025 09:00
      key='%02d-%02d-%4d %02d:00'%(curr_day,curr_month,curr_year,curr_hour)
      solar3p_forcast = solar3p.asdict(d_period,d_wp,d_pans,d_lay,d_gran,d_file)
      solar3p_forcast_kwh=solar3p_forcast[key]
      log.logdebug('solar3p_forcast_key='+key)
      log.logdebug('solar3p_forcast_kw='+solar3p_forcast_kwh)
      return float(solar3p_forcast_kwh)
   except:
      log.logdebug('solar3p_forcast_key='+key+" is not available - return 0.0")
      return float("0.0")

def get_pv_watt_returned(conn,now):
   log.logdebug("get_pv_watt_returned")
   curr_year  = now.year
   curr_month = now.month
   curr_day   = now.day
   curr_hour  = now.hour
   cursor = conn.cursor()
   # str_to_date(%s,"%Y-%m-%d")
   sql_date="%4d-%02d-%02d"%(curr_year,curr_month,curr_day)
   sql = 'select kwh_prod from hour_usage_prices where '
   sql = sql + 'day=str_to_date("%s"'%sql_date+',"%Y-%m-%d")'+' and hour="%s"'%curr_hour
   log.logdebug('get_pv_watt_returned query='+sql)
   cursor.execute(sql)
   records = cursor.fetchall()
   log.loginfo('get_pv_watt_returned records:')
   log.loginfo(records)
   log.logdebug(str(cursor.rowcount) + " record found.")
   if (cursor.rowcount>0):
      return 1000*records[0][0] # should be one record, convert kw to watt
   else:
      log.logerror("no records found for specified year:%s/month:%s/day:%s/hour:%s"%(curr_year,curr_month,curr_day,curr_hour))
      return 0;

def main():

   # database connection
   conn = mysql.connector.connect(user='root', database='homepowerdb')

   # location: rotterdam as this is closest
   location='rotterdam'

   # 1. get the past day/hour (need to run this just over the whole hour to process last hour)
   past_0hour = datetime.datetime.now()
   past_1hour = datetime.datetime.now() - datetime.timedelta(hours=1)
   past_2hour = datetime.datetime.now() - datetime.timedelta(hours=2)
   log.loginfo("past_0hour"+str(past_0hour))
   log.loginfo("past_1hour"+str(past_1hour))
   log.loginfo("past_2hour"+str(past_2hour))

   # 2. get the meteo prediciton data for that date and hour
   meteo_prediction = get_day_hour_forcast(location,past_0hour)
   gr_w=0
   tc=0
   cet=""
   try:
      cet=meteo_prediction['cet']
      gr_w=meteo_prediction['gr_w']
      tc=meteo_prediction['tc']
      log.loginfo("meteo cet: " + cet + " gr_w: " + gr_w + " tc: " + tc)
   except:
      log.logerror("key error for cet="+cet)
      log.logerror("using gr_w=0 and tc=0")


   # 3. get actual pv generated power in watt for day/hour
   past_0hour_wattHoursToday=get_pv_production(conn,past_0hour)
   log.loginfo("past 0hour wattHoursToday: " + str(past_0hour_wattHoursToday))
   past_1hour_wattHoursToday=get_pv_production(conn,past_1hour)
   log.loginfo("past 1hour wattHoursToday: " + str(past_1hour_wattHoursToday))
   delta_wattHoursToday = past_0hour_wattHoursToday - past_1hour_wattHoursToday
   # day wrapping protection, enphase will reset wattHoursToday to 0 for next day
   if (delta_wattHoursToday<0):
      delta_wattHoursToday=0

   # 4. get solar3p forcast in watt for past hour
   solar3p_forcast_in_watt=int(get_solar3p_forcast(past_0hour)*1000)
   log.logdebug("solar3p_forcast_in_watt="+str(solar3p_forcast_in_watt))

   # 5. get the power returned to the grid which should be a % of the delta_wattHoursToday
   wattRetunedInHour = get_pv_watt_returned(conn,past_0hour)
   log.logdebug("wattRetunedInHour="+str(wattRetunedInHour))

   # 6. insert record in pvhistory
   insert_hour_pvhistory(conn,past_0hour,gr_w,tc,str(delta_wattHoursToday),str(solar3p_forcast_in_watt),str(wattRetunedInHour))

main()

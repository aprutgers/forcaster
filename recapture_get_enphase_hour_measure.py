import os
import sys
import mysql.connector
from datetime import datetime
import requests
import json
import log
import math
from dotenv import load_dotenv

# recapture - fetch data from an error recovery .json and insert
def get_enphase_data():

   # 1. get valid web token
   enphase_token = get_enphase_web_token()
   #log.logdebug("enphase_token: " + enphase_token)

   # 2. get measurement
   #curl -f -k -H 'Accept: application/json' -H 'Authorization: Bearer <token code>’ -X <API command>
   bearer   = 'Bearer ' + enphase_token
   headers  = {"Authorization": bearer}
   url      = 'https://192.168.2.1/ivp/pdm/energy'
   requests.packages.urllib3.disable_warnings() 
   response = requests.get(url, headers=headers,verify=False)
   RD = json.loads(response.text)
   log.logdebug(RD)
   #{
    #"production": {
        #"pcu": {
            #"wattHoursToday": 9808,
            #"wattHoursSevenDays": 12836,
            #"wattHoursLifetime": 11701510,
            #"wattsNow": 97
        #},
    #}
   #}
   wattHoursToday=RD["production"]["pcu"]["wattHoursToday"]
   wattHoursSevenDays=RD["production"]["pcu"]["wattHoursSevenDays"]
   wattHoursLifetime=RD["production"]["pcu"]["wattHoursLifetime"]
   wattsNow=RD["production"]["pcu"]["wattsNow"]
   return (wattHoursToday,wattHoursSevenDays,wattHoursLifetime,wattsNow)

#
# columns of enphase_production table
#
#`year` DECIMAL(4,0) NOT NULL,
#`month` DECIMAL(2,0) NOT NULL,
#`day` DECIMAL(2,0) NOT NULL,
#`hour` DECIMAL(2,0) NOT NULL,
#`minute` DECIMAL(2,0) NOT NULL,
#`wattHoursToday` DECIMAL(10,5) NOT NULL,
#`wattHoursSevenDays` DECIMAL(10,5) NOT NULL,
#`wattHoursLifetime` DECIMAL(12,5) NOT NULL,
#`wattsNow` DECIMAL(10,5) NOT NULL,
#`created` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#
def insert_enphase_production(year,month,day,hour,minute,wattHoursToday,wattHoursSevenDays,wattHoursLifetime,wattsNow):
   log.logdebug("insert_enphase_production")
   conn = mysql.connector.connect(user='root', database='homepowerdb')
   mycursor = conn.cursor()
   sql = 'insert into enphase_production(year,month,day,hour,minute,wattHoursToday,wattHoursSevenDays,wattHoursLifetime,wattsNow) ' +\
         'values (%s,%s,%s,%s,%s,%s,%s,%s,%s)'
   mycursor.execute(sql,(year,month,day,hour,minute,wattHoursToday,wattHoursSevenDays,wattHoursLifetime,wattsNow))
   log.loginfo(str(mycursor.rowcount) + " record inserted.")
   conn.commit()
   return mycursor.rowcount
   
def main():

   log.logdebug("main")

   # recovery period
   # start date = 2025-03-05 00:00
   # end date   = 2025-03-05 20:00

   date_string = "2025-03-05 00:00"
   sdate = datetime.strptime(date_string, "%Y-%m-%d %H:%M")
   curr_year  = sdate.year
   curr_month = sdate.month
   curr_day   = sdate.day
   curr_hour  = sdate.hour
   curr_min   = sdate.minute
   print(curr_year);

   # 0. retrieve error data recovery file
   recover_data={}
   with open('/tmp/reload_enphase.json') as f:
      recover_data = json.load(f)
   for RD in recover_data['data']:
      #print(RD)
      wattHoursToday=RD["production"]["pcu"]["wattHoursToday"]
      wattHoursSevenDays=RD["production"]["pcu"]["wattHoursSevenDays"]
      wattHoursLifetime=RD["production"]["pcu"]["wattHoursLifetime"]
      wattsNow=RD["production"]["pcu"]["wattsNow"]
      print("curr_year:%s  curr_month;%s  curr_day: %s curr_hour: %s curr_min: %s wattHoursToday %s"%(curr_year,curr_month,curr_day,curr_hour,curr_min,wattHoursToday))
      insert_enphase_production(curr_year,curr_month,curr_day,curr_hour,curr_min,wattHoursToday,wattHoursSevenDays,wattHoursLifetime,wattsNow)
      curr_hour=curr_hour+1
   return;


main()

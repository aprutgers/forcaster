import os
import sys
import mysql.connector
import datetime
import requests
import json
import log
import math
from dotenv import load_dotenv

def get_enphase_web_token():

   cache_file="/home/ec2-user/forcaster/.cached_enphase_web_token"
   if os.path.exists(cache_file):
      log.logdebug("cached token exists - reusing")
      f=open(cache_file,"r")
      token=f.read()
      f.close()
      return token.rstrip('\n')

   # get credentials from .env
   load_dotenv()
   user = os.environ.get('ENVOY_USER')
   password = os.environ.get('ENVOY_PASSWORD')
   envoy_serial = os.environ.get('ENVOY_SERIAL')
   log.logdebug('user='+user)
   log.logdebug('envoy_serial='+envoy_serial)

   data = {'user[email]': user, 'user[password]': password}   
   response = requests.post('https://enlighten.enphaseenergy.com/login/login.json?', data=data) 
   response_data = json.loads(response.text)   
   log.logdebug(response_data)
   data = {'session_id': response_data['session_id'], 'serial_num': envoy_serial, 'username': user}   
   response = requests.post('https://entrez.enphaseenergy.com/tokens', json=data)   
   token = response.text

   f=open(cache_file,"w")
   f.write(token)
   f.close()
   
   return token

def get_enphase_data():

   # 1. get valid web token
   enphase_token = get_enphase_web_token()
   log.logdebug("enphase_token: " + enphase_token)

   # 2. get measurement
   #curl -f -k -H 'Accept: application/json' -H 'Authorization: Bearer <token code>’ -X <API command>
   bearer   = 'Bearer ' + enphase_token
   headers  = {"Authorization": bearer}
   url      = 'https://192.168.2.1/ivp/pdm/energy'
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
#`wattHoursLifetime` DECIMAL(10,5) NOT NULL,
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

   # 0. get current day, hour, minute 
   now = datetime.datetime.now()
   curr_year  = now.year
   curr_month = now.month
   curr_day   = now.day
   curr_hour  = now.hour
   curr_min   = now.minute

   #curr_day   = '%02d-%02d-%4d'%(curr_day,curr_month,curr_year,curr_hour,curr_min)
   #curr_cet   = '%02d-%02d-%4d %2d:$2d'%(curr_day,curr_month,curr_year,curr_hour,curr_min)

   # 1. get enphase measure data for the hour from EnPhase API with valid web_token
   (wattHoursToday,wattHoursSevenDays,wattHoursLifetime,wattsNow)= get_enphase_data()
   
   
   # 2. insert into database
   insert_enphase_production(curr_year,curr_month,curr_day,curr_hour,curr_min,wattHoursToday,wattHoursSevenDays,wattHoursLifetime,wattsNow)

main()

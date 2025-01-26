import datetime

DEBUG=1
INFO=1
ERROR=1

#
# basic logging
#
def logerror(data):
   if (ERROR == 1):
      dt = str(datetime.datetime.now())
      print(dt + " ERROR: " + str(data))

def loginfo(data):
   if (INFO == 1):
      dt = str(datetime.datetime.now())
      print(dt + " INFO: " + str(data))

def logdebug(data):
   if (DEBUG == 1):
      dt = str(datetime.datetime.now())
      print(dt + " DEBUG: " + str(data))


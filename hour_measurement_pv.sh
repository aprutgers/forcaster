#!/bin/sh
# run on each whole hour

# 1. get actual value from solor panels for this last hour which is diff hour-1 -/- hour
python /home/ec2-user/forcaster/get_enphase_hour_measure.py

# 2. insert forcast data and actual pv measurement data into pvhistory
python /home/ec2-user/forcaster/history_collector.py

# 3. refresh token when its > 1/2 a year old
/home/ec2-user/forcaster/reset_token.sh

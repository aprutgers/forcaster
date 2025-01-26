#!/bin/sh

# this script is ran each full hour from cron:
# 00 * * * *  /home/ec2-user/forcaster/create_hour_forcast.sh>>/tmp/create_hour_forcast.log 2>&1

# 1. get actual power production value from solar panels for this last hour which is diff current hour -/- hour-1
python /home/ec2-user/forcaster/get_enphase_hour_measure.py

# 2. collect and insert solar3p forcast data, actual pv measurement data from above, and actual returned power into pvhistory
python /home/ec2-user/forcaster/history_collector.py

# 3. refresh enphase web access token, only when its > 1/2 a year old (its 1 year valid)
/home/ec2-user/forcaster/reset_token.sh

#!/bin/sh
file="/home/ec2-user/forcaster/.cached_enphase_web_token"
file_epoch=$(stat $file --format %Y)
curr_epoch=$(date +%s)
diff_epoch=$(($curr_epoch-$file_epoch))
#echo $diff_epoch
day_in_seconds=86400
year_in_second=31536000
half_year_in_second=15768000
if [ $diff_epoch -ge $half_year_in_second ]
then
   echo "$file is older than 1/2 a year - remove so it will be renewed"
   /bin/rm -f /home/ec2-user/forcaster/.cached_enphase_web_token
else
   echo "$file is yonger than 1/2 a year - keep"
fi

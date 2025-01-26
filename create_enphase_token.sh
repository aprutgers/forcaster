#!/bin/sh
# test script to test to create a new web token so we can make valid API calls to the local gateway envoy API
token_file="/home/ec2-user/forcaster/.cached_enphase_web_token"
user=$(cat .env |grep ENVOY_USER|cut -d '=' -f2)
password=$(cat .env |grep ENVOY_PASSWORD|cut -d '=' -f2)
envoy_serial=$(cat .env |grep ENVOY_SERIAL|cut -d '=' -f2)
session_id=$(curl -X POST https://enlighten.enphaseenergy.com/login/login.json? -F "user[email]=$user" -F "user[password]=$password" | jq -r ".session_id")
echo "session_id=$session_id"
data="{\"session_id\": \"$session_id\", \"serial_num\": \"$envoy_serial\", \"username\": \"$user\"}"
web_token=$(curl -X POST https://entrez.enphaseenergy.com/tokens -H "Content-Type: application/json" -d "$data")
echo $web_token

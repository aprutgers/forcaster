#!/bin/sh
# to create a new token see create_enphase_token.sh
token_file="/home/ec2-user/forcaster/.cached_enphase_web_token"
echo "using $token_file"
token=$(cat $token_file)
curl -f -k -H 'Accept: application/json' -H "Authorization: Bearer $token" https://192.168.2.1/ivp/livedata/status
curl -f -k -H 'Accept: application/json' -H "Authorization: Bearer $token" https://192.168.2.1/api/v1/production
curl -f -k -H 'Accept: application/json' -H "Authorization: Bearer $token" https://192.168.2.1/ivp/pdm/energy 

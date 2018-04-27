#!/bin/sh
#
# Title: get_diff_report.sh
# Description: This script is used to check if the index.html
#              webpage has been modified and if so copy to the
#              htdocs directory on the the dashboard web server.
#              Should be run in cron as user mwadmin.
# Author: Insight Global
# Date: 04-18-2018
#
# Date & Input file
DATE=`date +"%m-%d-%Y"`
FILE=/export/app_repo/ansible_logs/backup/index.html
# How many seconds before file is deemed "older"
OLDTIME=540
# Get current and file times
CURTIME=$(date +%s)
FILETIME=$(stat $FILE -c %Y)
TIMEDIFF=$(expr $CURTIME - $FILETIME)
#echo "TIMEDIFF: " $TIMEDIFF
#echo "OLDTIME: " $OLDTIME

# Check if file is is older
if [ $TIMEDIFF -lt $OLDTIME ]; then

  echo "Updating Apache htdocs validation/index.html file."
  if [ -e "/export/app_repo/ansible_logs/backup/validations/index.html" ]; then
    # make a backup copy of the existing webpage first
    cp /export/app_repo/ansible_logs/backup/validations/index.html \
       /export/app_repo/ansible_logs/backup/validations/index.$DATE.html
  fi

  if [ -e "/export/app_repo/ansible_logs/backup/index.html" ]; then
    # copy the new webpage to the apache htdocs directory
    cp /export/app_repo/ansible_logs/backup/index.html \
       /export/app_repo/ansible_logs/backup/validations
  fi

fi

#! /bin/sh
#
# Title: webpage.sh
# Description: This script is used to create the index.html
#              webpage for the Middleware Weblogic Patch Validations Report
#              Does the following:
#              1. copies ansible temp logs to backup folder
#              2. copies current python scripts to backup folder
#              3. runs difference on pre and post temp files
#              4. creates the webpage html page
# Author: Insight Global
# Date: 04-18-2018
#
DATE=`date +"%m-%d-%Y.%H.%M"`
cd /export/app_repo/ansible_logs/backup
tar cvf /export/app_repo/ansible_logs/archive/$DATE.tar *.fnl.log
gzip /export/app_repo/ansible_logs/archive/$DATE.tar
cp /export/app_repo/ansible_logs/backup/*.diff.log /export/app_repo/ansible_logs/diffvals
rm /export/app_repo/ansible_logs/backup/*.fnl.log
rm /export/app_repo/ansible_logs/backup/*.diff.log
cp /export/app_repo/ansible_logs/postvalidations/*.fnl.log /export/app_repo/ansible_logs/backup
cp /export/app_repo/ansible_logs/scripts/*.py /export/app_repo/ansible_logs/backup
python diff_weblogic_logs.py
cp index.html index.$DATE.html
python create_webpage_report.py > ./index.html
exit

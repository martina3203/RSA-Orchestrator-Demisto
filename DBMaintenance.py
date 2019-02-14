#!/usr/bin/python
#Orchestrator Database retention script
#Version 0.1
#This script is designed with the goal of taking Database files in the Orchestrator and either remove them or sftp them somewhere else.
#This was written for python 2.7 and tested on a CentOS 7 device.
#This script should be ran by somebody who has the authority to move/copy files and stop the rsa-orchestrator service and is designed to be ran as a cron job.
#Feel free to message me


import os
import datetime
import argparse
import logging

#Options explained
#TargetHost - the device we will scp our files to
#DoNotRemove - This will NOT remove the files from their base directory. Only copies.
#User - The user to SCP files with. I would recommend an exchange of SSH keys to authenticate that way but you are welcome to use the password field to do the same.
#Password - Password for the user to SCP files over.
#Criteria - The acceptable options are "date" or "spaceusage". What this means is that for date, we will deal with the files that are older than a certain date OR we can do it as we see the partition fill up to a certain value.
#CriteriaValue - This will be an integer value but the result will be the same. If our Criteria is Date we will interpret it as "Days Old". If the Criteria is "spaceusage", we will evaluate that as a percentage usage of the file system. If you pass in 90, we will run the operation if 90% is reached
#DebugMode - This will print debug logs

parser = argparse.ArgumentParser(description="This script allows for the automatic maitenance of databases when configured as a cron job.")
parser.add_argument("--host",help='This will be the host that you will be SCP files to for long term storage.')
parser.add_argument('-u',"--username",help='This will be the user who carries out the SCP transfer.')
parser.add_argument('-p','--password',help='This will be the password of the user who is commencing the SCP transfer.')
parser.add_argument('-d','-D','--debug',help='This allows for the viewing of debug logs.',default=False,action="store_true")
parser.add_argument('--RetentionPolicy',help='This will determine the criteria we evaluate whether to move files or not. \
The options are: "date" or "spaceusage"')
parser.add_argument('--DaysOfRetention',help='If the RetentionPolicy is set to "date", \
    then we shall use this value to determine how long back our database should be. \
    If it exceeds this value, it will be archived/deleted.')
parser.add_argument('--MaxFSpercentage',help='If the Retention Policy is set to "spaceusage", \
    then we shall use this value to determine what the maximum file usage percentage should be. \
    If it exceeds this value, it will be archived/deleted.')

args = parser.parse_args()
DEBUG = args.debug
#Configure logging
if DEBUG == False:
    logging.basicConfig(format='%(asctime)s DatabaseMaintenance.py %(levelname)s: %(message)s',level=logging.INFO)
else:
    logging.basicConfig(format='%(asctime)s DatabaseMaintenance.py %(levelname)s: %(message)s ',level=logging.DEBUG)
    logging.debug("Arguments: " + str(args))


#This function starts the service back up
def startService():
    #You can modify the command here if you can't use systemctl on your device
    command = "sudo systemctl start rsa-orchestrator"
    logging.info("Starting the Service with command: " + command)
    result = os.system(command)
    logging.debug("Result code: " + str(result))
    if (result == 0):
        logging.info("Service started.")
    else:
        logging.info("Failed to start service! Retrying!")
        #Will put some retry logic in here.
        exit()
    return result

#This function starts the
def stopService():
    #You can modify the command here if you can't use systemctl on your device.
    command = "sudo systemctl stop rsa-orchestrator"
    logging.info("Stopping the service with command: " + command)
    result = os.system(command)
    logging.debug("Result code: " + str(result))
    if (result == 0):
        logging.info("Service stopped.")
    else:
        logging.info("Failed to stop service! Aborting!")
        exit()
    return result

#We will use this function to determine if the criteria is met for the files.
def checkCriteria():
    return True

#Files at the time of this code write had a format of base-filename_MMYYYY.db or simply folder_MMYYYY
def locateFiles():
    return

def copyFiles():
    return

def removeFiles():
    return

#MAIN
logging.info("Starting script.")
if (checkCriteria()):
    stopService()
    startService()
    logging.info("Script Finished.")
else:
    logging.info("Criteria is not met for Database Rotation. Exitting.")
    exit()

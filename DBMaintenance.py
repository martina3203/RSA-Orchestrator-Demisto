#!/usr/bin/python
#Orchestrator Database retention script
#Version 0.1
#This script is designed with the goal of taking Database files in the Orchestrator and either remove them or sftp them somewhere else.
#This was written for python 2.7 and tested on a CentOS 7 device.
#This script should be ran by somebody who has the authority to move/copy files and stop the rsa-orchestrator service and is designed to be ran as a cron job.
#Feel free to message me


import os
import glob
from datetime import date
from datetime import datetime
from datetime import timedelta
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
parser.add_argument('--MonthsOfRetention',help='If the RetentionPolicy is set to "date", \
    then we shall use this value to determine how long back our database should be. \
    If it exceeds this value, it will be archived/deleted.',type=int,default=100)
parser.add_argument('--MaxFSpercentage',help='If the Retention Policy is set to "spaceusage", \
    then we shall use this value to determine what the maximum file usage percentage should be. \
    If it exceeds this value, it will be archived/deleted.')
parser.add_argument('--DatabaseDirectory',help='This is the directory where your database files are being used for RSA Orchestrator. \
The default is /var/lib/rsa-orchestrator/data',default='/var/lib/rsa-orchestrator/data')

args = parser.parse_args()
DEBUG = args.debug
RetentionPolicy = args.RetentionPolicy
RetentionMonths = args.MonthsOfRetention
DatabaseDirectory = args.DatabaseDirectory

#Configure logging
if DEBUG == False:
    logging.basicConfig(format='%(asctime)s DBMaintenance.py %(levelname)s: %(message)s',level=logging.INFO)
else:
    logging.basicConfig(format='%(asctime)s DBMaintenance.py %(levelname)s: %(message)s ',level=logging.DEBUG)
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
def checkDate():
    filesMarked = []
    logging.debug("Starting date branch of checking date")
    #Now we shall check to see if we have files older than X.

    #Take today's date and get the oldest date we want to get with retention period
    today = datetime.today()
    #Convert months to days to create a time delta. We are simply going with a month is 30 days
    daysRetention = RetentionMonths * 30
    delta = timedelta(days=daysRetention)
    retentionDate = today - delta

    logging.debug("Today's date in MMYYYY format is " + today.strftime('%m%Y'))
    logging.info("Target Retention Date is " + retentionDate.strftime('%m-%d-%Y') + ". Files older than this will be moved/deleted.")

    #Checking file system for files that contain that date.
    partitionsDirectory = DatabaseDirectory + "/rsa-orchestratoridx/"

    #This is the list of index files we will search for for backup
    indexCategories = {"evidences","newInsights","incidents","entries","investigations"}
    for indexCategory in indexCategories:
        globpath = partitionsDirectory + indexCategory + "_*"
        indexDirOutput = glob.glob(globpath)
        for file in indexDirOutput:
            logging.debug("Found " + file)
            baseFilename = file.replace(partitionsDirectory,'')
            fileDateSuffix = file.replace(partitionsDirectory + indexCategory + "_",'')
            logging.debug("Base Filename: " + baseFilename + " with date suffix of " + fileDateSuffix)

            #We will now compare the dates to see if they need to be rolled overself.
            try:
                folderDate = datetime.strptime(fileDateSuffix,"%m%Y")
                logging.debug("Converted time is " + folderDate.strftime('%m%Y'))
            except ValueError:
                logging.error("Unable to convert suffix of filename to valid name. Aborting! File:" + file)
                exit()
            except:
                logging.error("Unknown error occurred while parsing for date suffix of file. Aborting! File:" + file)
                exit()

            if (folderDate < retentionDate):
                logging.info("Marking " + file + " for archival/deletion")
                filesMarked.append(file)
            else:
                logging.debug("File is NOT marked for archival/deletion: " + file)
    return filesMarked

def copyFiles():
    return

def removeFiles():
    return

#MAIN
logging.info("Starting Database Maintenance script for RSA Orchestrator.")
#If there are no elements marked for deletion
if (RetentionPolicy == "date"):
    #If the list is larger than 0
    filesMarkedForArchival = checkDate()
    if filesMarkedForArchival:
        stopService()
        startService()
    else:
        logging.info("No files marked for archival/deletion.")
    logging.info("Script Finished.")
elif (RetentionPolicy == "spaceusage"):
    logging.info("This operation is not supported yet. Exitting.")
    exit()
else:
    logging.info("Criteria is not met for Database Rotation. Exitting.")
    exit()

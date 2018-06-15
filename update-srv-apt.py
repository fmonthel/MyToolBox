#!/usr/bin/env python
#
# update-srv-apt.py
#
# Basic Python Script to apt update on servers define in srv_inventory_file
#
# Author: Florent MONTHEL (fmonthel@flox-arts.net)
#

import os
import sys
import subprocess
import ConfigParser
import logging
import datetime

# Variables
APPLICATION=os.path.basename(__file__)


# Function to apt-get update and upgrade on srv
def update_upgrade_apt(host):
    # We will connect on server with SSH and list certificate files signed on Puppet
    ssh = subprocess.Popen(["ssh", "%s" % "root@"+host, "apt-get update && apt-get upgrade -y && apt-get autoremove && apt-get autoclean"],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == []:
        error = ssh.stderr.readlines()
        raise RuntimeError('SSH error raised : "' + error + '"')


# Function to return the list of SRV from srv_inventory_file
def get_list_srv_from_file(srv_inventory_file):
    # Open file in RO mode and return list
    mysrv = open(srv_inventory_file, "r")
    tmp = list()
    for host in mysrv:
        host.replace("\n","")
        tmp.append(host)
        logging.getLogger(APPLICATION).debug('Add SRV "' + str(host) + '" in SRV list')
    # Return list
    return tmp

def main():
    # Config setupm(time,conf,logger)
    time_start = datetime.datetime.now()
    file_config = os.path.join(os.path.dirname(__file__), 'conf/config.ini')
    Config = ConfigParser.ConfigParser()
    Config.read(file_config)
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(APPLICATION)
    handler = logging.FileHandler(os.path.join(os.path.dirname(__file__), 'log/'+APPLICATION+'.log'))
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    try :
        # Get list of SRV
        logger.info('Get list of SRV from file "' + str(Config.get('GLOBAL','srv_inventory_file')) + '"')
        srvs = get_list_srv_from_file(Config.get('GLOBAL','srv_inventory_file'))
        logger.info('"' + str(len(srvs)) + '" SRV(s) found')
        # Update each servers
        for srv in srvs:
            logger.info('Update and upgrade apt on SRV "' + str(srv) + '"')
            update_upgrade_apt(srv)
        # End script
        time_stop = datetime.datetime.now()
        time_delta = time_stop - time_start
        # Output data
        print "######### DATE : %s - APP : %s #########" % (time_start.strftime("%Y-%m-%d"),APPLICATION)
        print "- Start time : %s" % (time_start.strftime("%Y-%m-%d %H:%M:%S"))
        print "- Finish time : %s" % (time_stop.strftime("%Y-%m-%d %H:%M:%S"))
        print "- Delta time : %d second(s)" % (time_delta.total_seconds())
        print "- Log file : %s" % (os.path.join(os.path.dirname(__file__), 'log/'+APPLICATION+'.log'))
    except Exception as e :
        logger.error('RunTimeError during instance creation : %s', str(e))
         
if __name__ == "__main__":
    main()
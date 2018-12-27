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
    ssh = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "%s" % "root@"+host, "apt-get update && apt-get upgrade -y && apt-get dist-upgrade -y && apt-get autoremove -y && apt-get autoclean && apt-get clean"],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == []:
        error = ssh.stderr.readlines()
        logging.getLogger(APPLICATION).warning('SSH error raised on "' + str(host) + '" : "' + str(error) + '"')
        return -1
    # Return
    return 0

# Function to return the list of SRV from srv_inventory_file
def get_list_srv_from_file(srv_inventory_file):
    # Open file in RO mode and return list
    mysrv = open(srv_inventory_file, "r")
    tmp = list()
    for v in mysrv:
        host = v.replace("\n","")
        tmp.append(host)
        logging.getLogger(APPLICATION).debug('Add SRV "' + str(host) + '" in SRV list')
    # Return list
    return tmp

def main():
    
    # Config setup (time,conf)
    time_start = datetime.datetime.now()
    file_config = os.path.join(os.path.dirname(__file__), 'conf/config.ini')
    Config = ConfigParser.ConfigParser()
    Config.read(file_config)
    
    # Create logger APPLICATION
    logger = logging.getLogger(APPLICATION)
    logger.setLevel(logging.DEBUG)
    # Create file handler which logs even debug messages
    fh = logging.FileHandler(filename=os.path.join(os.path.dirname(__file__), 'log/'+APPLICATION+'.log'))
    fh.setLevel(logging.DEBUG)
    # Create console stderr handler with a higher log level
    eh = logging.StreamHandler(sys.stderr)
    eh.setLevel(logging.ERROR)
    # Create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    eh.setFormatter(formatter)
    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(eh)
    
    try :
        # Get list of SRV
        logger.info('Get list of SRV from golden source "' + str(Config.get('GLOBAL','srv_inventory_file')) + '"')
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
        sys.exit(0)
    except Exception as e :
        logger.error('RunTimeError during instance creation : %s', str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        sys.exit(-1)
         
if __name__ == "__main__":
    main()

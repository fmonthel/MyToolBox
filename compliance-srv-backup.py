#!/usr/bin/env python
#
# compliance-srv-backup.py
#
# Basic Python Script to declare in backup servers define in srv_inventory_file
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


# Function to get all config files
def get_list_srv_from_backup_node(user,node,confdir):
    # We will connect on server with SSH and list backup conf files
    ssh = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "%s" % str(user)+"@"+str(node), "ls "+str(confdir)+"/srv.*"],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == []:
        error = ssh.stderr.readlines()
        raise RuntimeError('SSH error raised : "' + str(error) + '"')

    # Now work on result array
    tmp = list()
    for v in result :
        host = v.replace(".conf","").replace("srv.","").replace("\n","").replace(str(confdir)+"/","") # Remove some values
        tmp.append(host)
        logging.getLogger(APPLICATION).debug('Add SRV "' + str(host) + '" in SRV list from backup node')
    # Return list
    return tmp

def add_srv_on_backup_node(user,node,confdir,host):
    # We will connect on server with SSH and copy backup file
    ssh = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "%s" % str(user)+"@"+str(node), "cp "+str(confdir)+"/srv.TEMPLATE.conf.tpl "+str(confdir)+"/srv."+str(host)+".conf"],
                      shell=False,
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result != []:
        error = ssh.stderr.readlines()
        raise RuntimeError('SSH error raised : "' + error + '"')
    # We will now replace value HOST and FQDN inside the file
    ssh = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "%s" % str(user)+"@"+str(node), "sed -i -e \'s/HOST/"+str(host)+"/g\' "+str(confdir)+"/srv."+str(host)+".conf"],
                      shell=False,
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result != []:
        error = ssh.stderr.readlines()
        raise RuntimeError('SSH error raised : "' + error + '"')


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
        # Get list of SRV from Golden source
        logger.info('Get list of SRV from golden source "' + str(Config.get('GLOBAL','srv_inventory_file')) + '"')
        srvs = get_list_srv_from_file(Config.get('GLOBAL','srv_inventory_file'))
        logger.info('"' + str(len(srvs)) + '" SRV(s) found')
        # Get list of SRV from Backup
        logger.info('Get list of SRV from backup node "' + str(Config.get('BACKUP','host')) + '"')
        srvs_backup = get_list_srv_from_backup_node(Config.get('BACKUP','user'),Config.get('BACKUP','host'),Config.get('BACKUP','confdir'))
        logger.info('"' + str(len(srvs_backup)) + '" SRV(s) found')
        # For each server in Golden source be sure to have Backup file
        for srv in srvs:
            if srv in srvs_backup:
                logger.info('Compliance backup check on SRV "' + str(srv) + '" is OK')
            else :
                logger.info('Compliance backup check on SRV "' + str(srv) + '" is KO')
                add_srv_on_backup_node(Config.get('BACKUP','user'),Config.get('BACKUP','host'),Config.get('BACKUP','confdir'),srv)
                logger.info('Backup conf file for server "' + str(srv) + '" is created on backup node "' + str(Config.get('BACKUP','host')) + '"')
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

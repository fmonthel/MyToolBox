#!/usr/bin/env python
#
# generate-srv-list.py
#
# Basic Python Script to generate ref file of SRV (validated in Puppet)
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

# Function to return the list of SRV from Puppet master
def get_list_srv_from_puppet(user,host,certdir):
    # We will connect on server with SSH and list certificate files signed on Puppet
    ssh = subprocess.Popen(["ssh", "-o", "StrictHostKeyChecking=no", "%s" % user+"@"+host, "ls "+certdir],
                       shell=False,
                       stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == []:
        error = ssh.stderr.readlines()
        raise RuntimeError('SSH error raised : "' + error + '"')

    # Now work on result array
    tmp = list()
    for v in result :
        host = v.replace(".pem","").replace("\n","") # Remove some values
        tmp.append(host)
        logging.getLogger(APPLICATION).debug('Add SRV "' + str(host) + '" in SRV list from Puppet')
    # Return list
    return tmp

# Function to write the list of validate os in a file
def write_srv_in_file(list_srv,file) :
    if not isinstance(list_srv, list) :
        raise RuntimeError('LIST_SRV type is not good for variable (list expected)"' + list_srv + '"')
    # Open file in RW mode
    mysrv = open(file, "w+")
    for srv in list_srv :
        mysrv.write("%s\n" % str(srv))
    # Close file
    mysrv.close()
        

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
        logger.info('Get list of SRV from Puppet "' + str(Config.get('PUPPET','host')) + '"')
        srv = get_list_srv_from_puppet(Config.get('PUPPET','user'),Config.get('PUPPET','host'),Config.get('PUPPET','certdir'))
        logger.info('"' + str(len(srv)) + '" SRV(s) found')
        # Write this list in a file
        logger.info('Write SRV list in file "' + str(Config.get('GLOBAL','srv_inventory_file')) + '"')
        write_srv_in_file(srv,Config.get('GLOBAL','srv_inventory_file'))
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
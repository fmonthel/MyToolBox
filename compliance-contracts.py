#!/usr/bin/env python
#
# compliance-contracts.py
#
# Basic Python Script to check status of Flox-arts.net contracts (API)
#
# Author: Florent MONTHEL (fmonthel@flox-arts.net)
#

import os
import sys
import ConfigParser
import requests
import json
import logging
import datetime

# Variables
APPLICATION=os.path.basename(__file__)

# Function to get all Flox-arts.net contracts
# Return a list
def get_list_contracts(endpoint):
    
    # Set headers
    headers = { 'Content-Type': 'application/json' }
    r = requests.get(endpoint, headers=headers)
    if r.status_code != 200:
        raise RuntimeError('HTTP API error raised on endpoint : "' + str(endpoint) + '"')
    return json.loads(r.text)

# Function to parse contracts and raise anomalies
# End of contract in less than 1 month
# Contract not paid after 1 month of the start date
def parse_list_contracts(contracts):
    
    # Return value
    return_value = 0
    # We will parse dic
    for contract in contracts:
        today = datetime.datetime.now()
        startdate = datetime.datetime.strptime(contract["startdate"], '%Y-%m-%d')
        enddate = datetime.datetime.strptime(contract["enddate"], '%Y-%m-%d')
        alert_not_paid = startdate + datetime.timedelta(30)
        alert_enddate_soon = today + datetime.timedelta(30)
        # Start date + 1 month and status = waiting
        if contract["flag"] == 'waiting' and today > alert_not_paid :
            logging.getLogger(APPLICATION).error('[PAYEMENT_LATE] Contract ' + str(contract["id"]) + ' is not paid - Unix customer : ' + str(contract["customer_unix"]) + ' - Start date : ' + str(contract["startdate"]))
            return_value = -1
        # End of contract soon
        if contract["sid"] == None and contract["flag"] != 'end' and enddate < alert_enddate_soon:
            logging.getLogger(APPLICATION).error('[ENDCONTRACT_SOON] Contract ' + str(contract["id"]) + ' will end soon - Unix customer : ' + str(contract["customer_unix"]) + ' - End date : ' + str(contract["enddate"]))
            return_value = -1
    # Return
    return return_value
        
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
        # Get list of contracts from API
        logger.info('Get list of contracts from API "' + str(Config.get('FLA_API','api_ep_contract')) + '"')
        contracts = get_list_contracts(Config.get('FLA_API','api_ep_contract'))
        logger.debug('"' + str(len(contracts)) + '" contract(s) found')
        # Now we will parse contract and raise anomalies
        result = parse_list_contracts(contracts)
        # End script
        time_stop = datetime.datetime.now()
        time_delta = time_stop - time_start
        # Output data
        print "######### DATE : %s - APP : %s #########" % (time_start.strftime("%Y-%m-%d"),APPLICATION)
        print "- Start time : %s" % (time_start.strftime("%Y-%m-%d %H:%M:%S"))
        print "- Finish time : %s" % (time_stop.strftime("%Y-%m-%d %H:%M:%S"))
        print "- Delta time : %d second(s)" % (time_delta.total_seconds())
        print "- Log file : %s" % (os.path.join(os.path.dirname(__file__), 'log/'+APPLICATION+'.log'))
        sys.exit(result)
    except Exception as e :
        logger.error('RunTimeError during instance creation : %s', str(e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        sys.exit(-1)
         
if __name__ == "__main__":
    main()

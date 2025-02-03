import csv
import importlib.util           # For v2
import json                     # For handling input and output via JSON format
import logging
import re                       # For regular expression operations
import datetime                 # For handling date and time
import sys                      # For V2
# import pandas as pd             # For efficient handling of tabular content
import os
import psycopg2                 # For PostgreSQL database interactions
import GenericDB_Connection     # For generic database connection functions


def CP_Jun_Router_systemUptime(input_json):  # NOTE: Function name and file name have to be EXACTLY the same!
    """
    Description:
    Checking if Huawei Router uptime, where the uptime should be 1 days(24 hours) or more.(deviation of <minDevOk> hours is accepted)

    Parameters:
        input_json (str): A JSON-formatted string containing health check parameters, such as command outputs,
                          customer details, and any other relevant data.

    Returns:
        output_json (str): A JSON-formatted string representing the output of the health check, including any error information
             if processing fails.

    Change log:
        30 Jan 2025 Amaan Ansari     First Version, using template v6
    """

    try:
        # STEP 1: UNPACKING INPUT PARAMETERS
        commandOutput = input_json.get('inputParameter', {}).get('commandOutput')
        autoTT = input_json.get('inputParameter', {}).get('autoTT')
        details = input_json.get('inputParameter', {}).get('details')
        status = input_json.get('inputParameter', {}).get('status')
        remarks = input_json.get('inputParameter', {}).get('remarks')
        nodeName = input_json.get('inputParameter', {}).get('info', {}).get('nodeName')
        customer = input_json.get('inputParameter', {}).get('info', {}).get('customer')
        hc_set = input_json.get('inputParameter', {}).get('info', {}).get('set')
        healthCheckName = input_json.get('inputParameter', {}).get('info', {}).get('healthCheckName')
        requestId = input_json.get('inputParameter', {}).get('info', {}).get('requestId')
        processId = input_json.get('inputParameter', {}).get('info', {}).get('processId')
        region = input_json.get('inputParameter', {}).get('info', {}).get('region')
        triggerApplication = input_json.get('inputParameter', {}).get('info', {}).get('triggerApplication')
        customNodeName = input_json.get('inputParameter', {}).get('info', {}).get('customNodeName')
        # Placeholder for adding any other parameter(s) referring to reference values
        minUptime = input_json.get('inputParameter', {}).get('minUptime')

        # STEP 2: HARDCODED CONFIGURATION FOR THIS SPECIFIC CP
        vendor = 'Juniper'  # Fill with vendor name, eg 'Huawei'
        nodeType = 'Router'  # Fill with nodeType, eg 'Router'
        checkpointName = 'System Uptime'  # Give a descriptive but short name, eg 'Processor load', 'Linkset status' etc
        checkpointType = 'check'  # Select either 'check' or 'info'
        command = 'show system uptime'  # Command used to get the commandOutput, eg 'df -h'
        logicNOK = f'The uptime, if less than {minUptime} is considered as Not OK'  # Explain in words what is considered as Not OK - short and concise. Include any reference values passed into the function. Eg f'NOK if any directory has more than {maxAllowed}% used disk space'. Leave empty if checkpointType='info'
        logicWarning = f'The uptime, if less than {minUptime} is considered as Not OK'  # Same as above but for what is considered a Warning. Leave empty if not used or if checkpointType='info'

        # STEP 3: CORE LOGIC FOR THE CP TO CALCULATE REQUIRED VALUES WHEN EXECUTING
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        incID = ''  # Leave this as is - incID will not be allocated at this stage

        # Placeholder for code to extract the result value (should be ONE value which can be used below to decide checkResult)
        resultValue = ''
        # Regular Expressions
        _fullRegex = r"up (?P<uptime>[\d\w\s,]+),"
        _fullPattern = re.compile(pattern=_fullRegex)
        _match = _fullPattern.search(string=commandOutput)

        if _match:
            _upTimeString = _match[1].strip()
            # Extract the time components from the uptime string
            _weeks = re.search(r'(\d+)\s*weeks?', _upTimeString)
            _days = re.search(r'(\d+)\s*days?', _upTimeString)
            _hours = re.search(r'(\d+)\s*hours?', _upTimeString)
            _minutes = re.search(r'(\d+)\s*minutes?', _upTimeString)
            _seconds = re.search(r'(\d+)\s*seconds?', _upTimeString)


            # Convert the time components to integers, defaulting to 0 if not present
            weeks = int(_weeks.group(1)) if _weeks is not None else 0
            days = int(_days.group(1)) if _days else 0
            hours = int(_hours.group(1)) if _hours else 0
            minutes = int(_minutes.group(1)) if _minutes else 0
            seconds = int(_seconds.group(1)) if _seconds else 0

            # Convert all to hours
            resultValue = str((weeks * 7 * 24) + (days * 24) + hours + (minutes / 60) + + (seconds / 3600))

        else:
            raise Exception("Pattern Match FAILED")

        # Placeholder for code to decide checkResult
        if float(resultValue)<float(minUptime):
            checkResult = 'NOK'
        else:
            checkResult = 'OK'

        # Placeholder for code to assign shortText (one-liner to give some context to the resultValue)
        shortText = f'Uptime is {_upTimeString}' # Eg_ f'There are {resultValue} dirs with > {maxAllowed}% used disk space.'
        
        # Assigns "No" to autoTT if resultValue >= 1, otherwise assigns "Yes"
        autoTT = "No" if not resultValue else "Yes"
        
        # Determine details based on autoTT
        details = "Yes" if autoTT == "Yes" else "No"

        # Placeholder for code to assign longText.
        # NOTE: this feature is currently not in use - no need to add anything here
        # First, if fuller information of what's wrong with a CP is needed, this info needs to be written to a file (pref .txt or .csv)
        # The longText variable should contain the path to the file. (If no file is created, just leave longText empty, ie as '')
        # The path needs to be as follows: '/ssdprepo/CRs/" + processId + "/" + processId + "_" + nodeName + "_" +checkpointName + ".txt"'
        longText = ''  # Don't change - leave as empty string

        # Placeholder for code to prepare data to be written to 'details' csv-file.
        # NOTE: Only do this if it's required. If checkpoint isn't suitable for generating a details csv-file:
        #       - then comment out this section
        #       - also comment out step #5 (Write/append in csv-file)
        # 1. Prepare a variable (list) called 'headers'. The first column names must be: Region, CustomNodeName, NodeName and Timestamp.
        #    After those columns, please add the checkpoint specific columns.
        # 2. Then prepare a variable called 'data_to_write'. It should include the mandatory column values + checkpoint specific data values
        #    This should be a list of lists, so normally you need to have a for-loop to add each date-row as a list to the variable
        # For example:
        #    headers = ['Region', 'CustomNodeName', 'NodeName', 'Timestamp', 'LinkID', 'LinkName', 'LinkStatus']
        #    Assume there are 2 links. The data_to_write will then be:
        #    data_to_write = [[region, customNodeName, nodeName, timestamp, linkID1, linkName1, linkStatus1], [region, customNodeName, nodeName, timestamp, linkID2, linkName2, linkStatus2]]
        if str(details).lower()[0] == 'y':
            headers = []            # eg: ['Region', 'CustomNodeName', 'NodeName', 'Timestamp', 'Filesystem', 'Size', 'Used', 'Avail', 'Use_pct', 'Mounted_on']
            data_to_write = [[ ], [ ], ..., [ ]]      # eg region, customNodeName, nodeName, timestamp, row['Filesystem'], row['Size'], row['Used'], row['Avail'], row['Use_pct'], row['Mounted_on']] 
                                                      # for index, row in deviations.iterrows()]   --- assuming that each variable deviations is a dataFrame with all rows that need to be written.
            data_to_write = [commandOutput]
        # STEP 4: INSERT RESULTS INTO DATABASE (Don't change)
        params = GenericDB_Connection.read_db_config()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        # Fetch the latest ID and increment it
        fetch_next_id_query = "SELECT COALESCE(MAX(CAST(id AS INTEGER)), 0) + 1 AS next_id FROM hc.hc_results;"
        cursor.execute(fetch_next_id_query)
        next_id = cursor.fetchone()[0]  # Get the next available ID

        query = (
            'INSERT INTO hc.hc_results (id, customer, health_check_name, set, trigger_application, vendor, node_type, node_name, checkpoint_name, autott, command,status, remarks, checkpoint_type, result_value,check_result,short_text,long_text,request_id, process_id,timestamp,region, logic_nok, logic_warning, inc_id, custom_nodename, details) '
            'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id;')
        record_to_insert = (next_id,
                            None if not customer else customer,
                            None if not healthCheckName else healthCheckName,
                            None if not hc_set else hc_set,
                            None if not triggerApplication else triggerApplication,
                            None if not vendor else vendor,
                            None if not nodeType else nodeType,
                            None if not nodeName else nodeName,
                            None if not checkpointName else checkpointName,
                            None if not autoTT else autoTT,
                            None if not command else command,
                            None if not status else status,
                            None if not remarks else remarks,
                            None if not checkpointType else checkpointType,
                            None if not resultValue else resultValue,
                            None if not checkResult else checkResult,
                            None if not shortText else shortText,
                            None if not longText else longText,
                            None if not requestId else requestId,
                            None if not processId else processId,
                            None if not timestamp else timestamp,
                            None if not region else region,
                            None if not logicNOK else logicNOK,
                            None if not logicWarning else logicWarning,
                            None if not incID else incID,
                            None if not customNodeName else customNodeName,
                            None if not details else details
                            )
        cursor.execute(query, record_to_insert)  # NOTE: these two lines should be commented out during local testing
        conn.commit()  # NOTE: these two lines should be commented out during local testing

        # STEP 5: WRITE/APPEND IN CSV FILE   (Don't change anything here - ONLY if checkpoint is not suitable for details csv: if so comment out this part)
        if str(details).lower()[0] == 'y':
            directory = '/ssdprepo/HC/' + healthCheckName + '/' + str(requestId) + '/'
            file_name = checkpointName + '.csv'  # checkpoint name.csv
            file_path = os.path.join(directory, file_name)
            os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist
            module_name = "write_or_append_csv_v2"
            module_path = "/ssdprepo/wfmgr/texthandlers/python/write_or_append_csv_v2.py"
            spec = importlib.util.spec_from_file_location(module_name, module_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            csv_file_status = module.write_or_append_csv_v2(headers, data_to_write, file_path)
            logging.info(f'csv_file_status{csv_file_status}')

        # STEP 6: PREPARE OUTPUT AS A PYTHON DICT  (Don't touch anything here)
        outputRecord = {"customer": customer,
                        "healthCheckName": healthCheckName,
                        "set": hc_set,
                        "triggerApplication": triggerApplication,
                        "vendor": vendor,
                        "nodetype": nodeType,
                        "nodeName": nodeName,
                        "checkpointName": checkpointName,
                        "autoTT": autoTT,
                        "command": command,
                        "status": status,
                        "remarks": remarks,
                        "checkpointType": checkpointType,
                        "resultValue": resultValue,
                        "checkResult": checkResult,
                        "shortText": shortText,
                        "longText": longText,
                        "requestId": requestId,
                        "processId": processId,
                        "timestamp": timestamp,
                        "region": region,
                        "logicNOK": logicNOK,
                        "logicWarning": logicWarning,
                        "incId": "",
                        "custom_nodename": customNodeName,
                        "details": details
                        }
        output_data = {"result": str(outputRecord)}
        output_json = json.dumps(output_data, indent=2)


    # STEP 7: EXCEPTION HANDLING  (don't touch anything here)
    except Exception as e:
        error = format(e)
        output_json = {'remarks': error, 'status': 'Fail'}  # in case of error, returning python error message
        output_json = json.dumps(output_json, indent=2)

    # STEP 7: RETURN STATEMENT  (don't touch anything here)
    return output_json

# TESTING BLOCK - NOTE: ALL CODE BELOW NEEDS TO BE REMOVED OR COMMENTED AWAY BEFORE UPLOADING TO CANOPY
# You can replace the commandOutput part, maxAllowed and - if you want - also other data with text that is correct for your specific CP

# input_json = {
# "inputParameter": {
# "commandOutput": """Current time: 2025-01-04 11:25:53 WAT
# Time Source:  LOCAL CLOCK 
# System booted: 2024-10-01 01:33:35 WAT (13w4d 09:52 ago)
# Protocols started: 2024-10-01 01:37:38 WAT (13w4d 09:48 ago)
# Last configured: 2024-12-23 15:34:55 WAT (1w4d 19:50 ago) by ayvohou
# 11:25AM  up 95 days,  9:52, 1 users, load averages: 0.29, 0.30, 0.27""",
# "autoTT": "No",
# "details": "No",
# "minUptime": "95",
# "status": "SUCCESS",
# "remarks": "success",

# "info": {
# "nodeName": "AppServer1",
# "customer": "3IE",
# "set": "Daily_OSS",
# "healthCheckName": "Jun_SW_SystemUptime",
# "requestId": "12345",
# "processId": "67890",
# "region": "Ireland",
# "triggerApplication": "s",
# "customNodeName": "Andhra Pradesh"
# }
# }
# }

# a = CP_Jun_Router_systemUptime(input_json)
# print(a)

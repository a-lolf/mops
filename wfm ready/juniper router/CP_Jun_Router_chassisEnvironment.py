import csv
import importlib.util           # For v2
import json                     # For handling input and output via JSON format
import logging
import re                       # For regular expression operations
import datetime                 # For handling date and time
import sys
import traceback                      # For V2
import pandas as pd             # For efficient handling of tabular content
import os
import psycopg2                 # For PostgreSQL database interactions
import GenericDB_Connection     # For generic database connection functions


def CP_Jun_Router_chassisEnvironment(input_json):  # NOTE: Function name and file name have to be EXACTLY the same!
    """
    Description:
    Write a suitable description about what the CP is about here.

    Parameters:
        input_json (str): A JSON-formatted string containing health check parameters, such as command outputs,
                          customer details, and any other relevant data.

    Returns:
        output_json (str): A JSON-formatted string representing the output of the health check, including any error information
             if processing fails.

    Change log:
    29 Jan 2025  Amaan Ansari                    First version, using template v6
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
        maxAllowed = input_json.get('inputParameter', {}).get('maxAllowed')

        # STEP 2: HARDCODED CONFIGURATION FOR THIS SPECIFIC CP
        vendor = 'Juniper'  # Fill with vendor name, eg 'Huawei'
        nodeType = 'Router'  # Fill with nodeType, eg 'Router'
        checkpointName = 'Chassis Environment'  # Give a descriptive but short name, eg 'Processor load', 'Linkset status' etc
        checkpointType = 'check'  # Select either 'check' or 'info'
        command = 'show chassis environment'  # Command used to get the commandOutput, eg 'df -h'
        logicNOK = f"NOK if any component's temperature is > {maxAllowed} degrees C"  # Explain in words what is considered as Not OK - short and concise. Include any reference values passed into the function. Eg f'NOK if any directory has more than {maxAllowed}% used disk space'. Leave empty if checkpointType='info'
        logicWarning = f"NOK if any component's temperature is > {maxAllowed} degrees C"  # Same as above but for what is considered a Warning. Leave empty if not used or if checkpointType='info'

        # STEP 3: CORE LOGIC FOR THE CP TO CALCULATE REQUIRED VALUES WHEN EXECUTING
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        incID = ''  # Leave this as is - incID will not be allocated at this stage

        # Placeholder for code to extract the result value (should be ONE value which can be used below to decide checkResult)
        resultValue = 0
        for line in commandOutput.splitlines():
            regex = r"\s+(\d+) degrees C\s+/\s+"
            match = re.search(regex, line)
            if match:
              temperature = match.group(1)
              if temperature > maxAllowed:
                resultValue += 1 

        checkResult = "OK" if not resultValue else "NOK"
        
        # Assigns "No" to autoTT if resultValue >= 1, otherwise assigns "Yes"
        autoTT = "No" if not resultValue else "Yes"
        
        # Determine details based on autoTT
        details = "Yes" if autoTT == "Yes" else "No"

        # Placeholder for code to assign shortText (one-liner to give some context to the resultValue)
        if not resultValue:
            shortText = "All devices are reported NORMAL."
        else:
            shortText = f"There are {resultValue} components' temperature with > {maxAllowed} degrees C"                  # Eg_ f'There are {resultValue} dirs with > {maxAllowed}% used disk space.'

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
            data_to_write = [commandOutput]
            sanitized_timestamp = timestamp.replace(':', '-')
            file_path = f'{__file__}_{sanitized_timestamp}.csv'
            with open(file_path, 'w') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(data_to_write)
            
        # STEP 4: INSERT RESULTS INTO DATABASE (Don't change)
        params = GenericDB_Connection.read_db_config()
        conn = psycopg2.connect(**params)
        cursor = conn.cursor()
        # # Fetch the latest ID and increment it
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
        output_json = {'remarks': traceback.format_exc(), 'status': 'Fail'}  # in case of error, returning python error message
        output_json = json.dumps(output_json, indent=2)

    # STEP 7: RETURN STATEMENT  (don't touch anything here)
    return output_json

# TESTING BLOCK - NOTE: ALL CODE BELOW NEEDS TO BE REMOVED OR COMMENTED AWAY BEFORE UPLOADING TO CANOPY
# You can replace the commandOutput part, maxAllowed and - if you want - also other data with text that is correct for your specific CP

# input_json = {
# "inputParameter": {
# "commandOutput": """Class Item                           Status     Measurement
# Temp  PEM 0                          OK         35 degrees C / 95 degrees F
#       PEM 1                          OK         35 degrees C / 95 degrees F
#       PEM 2                          OK         35 degrees C / 95 degrees F
#       PEM 3                          OK         35 degrees C / 95 degrees F
#       Routing Engine 0               OK         30 degrees C / 86 degrees F
#       Routing Engine 0 CPU           OK         46 degrees C / 114 degrees F
#       Routing Engine 1               OK         29 degrees C / 84 degrees F
#       Routing Engine 1 CPU           OK         42 degrees C / 107 degrees F
#       CB 0 Intake                    OK         31 degrees C / 87 degrees F
#       CB 0 Exhaust A                 OK         28 degrees C / 82 degrees F
#       CB 0 Exhaust B                 OK         37 degrees C / 98 degrees F
#       CB 0 ACBC                      OK         35 degrees C / 95 degrees F
#       CB 0 XF A                      OK         48 degrees C / 118 degrees F
#       CB 0 XF B                      OK         46 degrees C / 114 degrees F
#       CB 1 Intake                    OK         30 degrees C / 86 degrees F
#       CB 1 Exhaust A                 OK         28 degrees C / 82 degrees F
#       CB 1 Exhaust B                 OK         38 degrees C / 100 degrees F
#       CB 1 ACBC                      OK         35 degrees C / 95 degrees F
#       CB 1 XF A                      OK         48 degrees C / 118 degrees F
#       CB 1 XF B                      OK         46 degrees C / 114 degrees F
#       FPC 0 Intake                   OK         37 degrees C / 98 degrees F
#       FPC 0 Exhaust A                OK         35 degrees C / 95 degrees F
# ---(more)---
                                        
#       FPC 0 Exhaust B                OK         54 degrees C / 129 degrees F
#       FPC 0 XL TSen                  OK         55 degrees C / 131 degrees F
#       FPC 0 XL Chip                  OK         49 degrees C / 120 degrees F
#       FPC 0 XL_XR0 TSen              OK         55 degrees C / 131 degrees F
#       FPC 0 XL_XR0 Chip              OK         52 degrees C / 125 degrees F
#       FPC 0 XL_XR1 TSen              OK         55 degrees C / 131 degrees F
#       FPC 0 XL_XR1 Chip              OK         54 degrees C / 129 degrees F
#       FPC 0 XQ TSen                  OK         55 degrees C / 131 degrees F
#       FPC 0 XQ Chip                  OK         46 degrees C / 114 degrees F
#       FPC 0 XQ_XR0 TSen              OK         55 degrees C / 131 degrees F
#       FPC 0 XQ_XR0 Chip              OK         49 degrees C / 120 degrees F
#       FPC 0 XM TSen                  OK         55 degrees C / 131 degrees F
#       FPC 0 XM Chip                  OK         65 degrees C / 149 degrees F
#       FPC 0 XF TSen                  OK         55 degrees C / 131 degrees F
#       FPC 0 XF Chip                  OK         72 degrees C / 161 degrees F
#       FPC 0 PLX PCIe Switch TSen     OK         40 degrees C / 104 degrees F
#       FPC 0 PLX PCIe Switch Chip     OK         41 degrees C / 105 degrees F
#       FPC 0 Aloha FPGA 0 TSen        OK         40 degrees C / 104 degrees F
#       FPC 0 Aloha FPGA 0 Chip        OK         57 degrees C / 134 degrees F
#       FPC 0 Aloha FPGA 1 TSen        OK         40 degrees C / 104 degrees F
#       FPC 0 Aloha FPGA 1 Chip        OK         67 degrees C / 152 degrees F
#       FPC 1 Intake                   OK         38 degrees C / 100 degrees F
#       FPC 1 Exhaust A                OK         38 degrees C / 100 degrees F
# ---(more 63%)---
                                        
#       FPC 1 Exhaust B                OK         60 degrees C / 140 degrees F
# ---(more 64%)---
                                        
#       FPC 1 XL TSen                  OK         62 degrees C / 143 degrees F
#       FPC 1 XL Chip                  OK         53 degrees C / 127 degrees F
#       FPC 1 XL_XR0 TSen              OK         62 degrees C / 143 degrees F
#       FPC 1 XL_XR0 Chip              OK         55 degrees C / 131 degrees F
#       FPC 1 XL_XR1 TSen              OK         62 degrees C / 143 degrees F
#       FPC 1 XL_XR1 Chip              OK         58 degrees C / 136 degrees F
#       FPC 1 XQ TSen                  OK         62 degrees C / 143 degrees F
#       FPC 1 XQ Chip                  OK         49 degrees C / 120 degrees F
#       FPC 1 XQ_XR0 TSen              OK         62 degrees C / 143 degrees F
#       FPC 1 XQ_XR0 Chip              OK         52 degrees C / 125 degrees F
#       FPC 1 XM TSen                  OK         62 degrees C / 143 degrees F
#       FPC 1 XM Chip                  OK         71 degrees C / 159 degrees F
#       FPC 1 XF TSen                  OK         62 degrees C / 143 degrees F
#       FPC 1 XF Chip                  OK         77 degrees C / 170 degrees F
#       FPC 1 PLX PCIe Switch TSen     OK         41 degrees C / 105 degrees F
#       FPC 1 PLX PCIe Switch Chip     OK         42 degrees C / 107 degrees F
#       FPC 1 Aloha FPGA 0 TSen        OK         41 degrees C / 105 degrees F
#       FPC 1 Aloha FPGA 0 Chip        OK         62 degrees C / 143 degrees F
#       FPC 1 Aloha FPGA 1 TSen        OK         41 degrees C / 105 degrees F
#       FPC 1 Aloha FPGA 1 Chip        OK         73 degrees C / 163 degrees F
# Fans  Top Rear Fan                   OK         Spinning at intermediate-speed
#       Bottom Rear Fan                OK         Spinning at intermediate-speed
#       Top Middle Fan                 OK         Spinning at intermediate-speed
# ---(more 95%)---
                                        
#       Bottom Middle Fan              OK         Spinning at intermediate-speed
# ---(more 97%)---
                                        
#       Top Front Fan                  OK         Spinning at intermediate-speed
#       Bottom Front Fan               OK         Spinning at intermediate-speed""",
# "autoTT" : "No",
# "details":"Yes",
# "maxAllowed" : "55",
# "status" : "SUCCESS",
# "remarks" : "success",
# "info" : {"nodeName" : "AppServer1",
#           "customer" : "3IE",
#           "set" : "Daily_OSS",
#           "healthCheckName" : "Nokia_NetAct_Filesystem_check",
#           "requestId" : "12345",
#           "processId" : "67890",
#           "region" : "Ireland",
#           "triggerApplication" : "s",
#           "customNodeName":"Andhra Pradesh"}
# }
# }

# a = CP_Jun_Router_chassisEnvironment(input_json)
# print(a)

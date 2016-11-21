# Script to get recent crash data from AppDynamics
import requests
import json

# Variable, update to match your environment
username = 'demouser'
password = ''
customerName = 'customer1'
controller = 'http://demo1.appdynamics.com/'

# Mobile app details, can be found in the URL when looking at mobile data
appId = '66'
mobileAppId = '30'
platform = 'iOS'

# Login to controller and setup session
session = requests.Session()
session.auth=(username + '@' + customerName, password)
session.headers['Accept-Language'] = 'en-US,en;q=0.8'
session.headers['Content-Type'] = 'application/json;charset=UTF-8'
session.headers['Accept'] = 'application/json, text/plain, */*'
login = session.get(controller + 'controller/auth?action=login')

# Get a list of crashes for the past 15 minutes
reqJSON = '{"applicationId":' + appId + ',"platform":"' + platform + '","mobileAppId":' + mobileAppId + ',"timeRangeString":"last_15_minutes|BEFORE_NOW|-1|-1|15","filters":{"@type":"CrashFilters","mobileAppNames":null,"mobileAppVersion":{"type":"TREE_LIST","name":"Mobile App Version","values":null},"carriers":{"type":"TREE_LIST","name":"Carrier","values":null},"connectionTypes":{"type":"TREE_LIST","name":"Connection Type","values":null},"deviceNames":{"type":"TREE_LIST","name":"Model","values":null},"osVersions":{"type":"TREE_LIST","name":"OS Version","values":null},"geoCountries":{"type":"TREE_LIST","name":"Country","values":null},"crashId":{"type":"TEXT","name":"Crash Id","value":null,"values":null},"crashedFile":{"type":"TEXT","name":"Crashed File","value":null,"values":null},"crashedFunction":{"type":"TEXT","name":"Crashed Function","value":null,"values":null},"exceptionName":{"type":"TEXT","name":"Exception Name","value":null,"values":null},"crashGroupId":{"type":"TEXT","name":"Group Id","value":null,"values":null}}}'
list = session.post(controller + 'controller/restui/crash/list',data=reqJSON)
crashes = json.loads(list.text)

# Loop over list and get crash details for each
for crash in crashes:
    crashId = crash['crashId']
    reqJSON = '{"applicationId":66,"platform":"iOS","mobileAppId":30,"timeRangeString":"last_15_minutes|BEFORE_NOW|-1|-1|15","crashId":"' + crashId + '"}'
    crashResp = session.post(controller + 'controller/restui/crashDetails/detailsAndSummaryData', data=reqJSON)
    crashDetails = json.loads(crashResp.text)
    # Print out the crash data
    for line in crashDetails['detailsData']['crashReportText'].split('\n'):
        print(line)

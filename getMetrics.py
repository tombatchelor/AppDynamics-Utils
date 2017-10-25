# Script to get recent crash data from AppDynamics
import requests
import json

# Variable, update to match your environment
username = ''
password = ''
customerName = ''
controller = ''

# Mobile app details, can be found in the URL when looking at mobile data
appName = ''
g

# Login to controller and setup session
response = requests.get(controller + 'controller/auth?action=login', auth=(username + '@' + customerName, password))
jsessionID = response.cookies.get('JSESSIONID')
csrf = response.cookies.get('X-CSRF-TOKEN')
cookies = {'JSESSIONID' : jsessionID}
headers = {'X-CSRF-TOKEN' : csrf}

# Get a list of metrics
response = requests.get(controller + 'controller/rest/applications/' + appName + '/metrics',  cookies=cookies, headers=headers)

print response.text

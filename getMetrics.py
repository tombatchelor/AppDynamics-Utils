# Script to get recent crash data from AppDynamics
import requests
import json

# Variable, update to match your environment
username = ''
password = ''
customerName = ''
controller = ''

# App details, can be found in the URL when looking at mobile data
appName = ''


# Login to controller and get session and CSRF tokens
response = requests.get(controller + 'controller/auth?action=login', auth=(username + '@' + customerName, password))
jsessionID = response.cookies.get('JSESSIONID')
csrf = response.cookies.get('X-CSRF-TOKEN')

# Add JSESSION ID to cookies and CSRF token to headers
cookies = {'JSESSIONID' : jsessionID}
headers = {'X-CSRF-TOKEN' : csrf}

# Get a list of metrics
response = requests.get(controller + 'controller/rest/applications/' + appName + '/metrics',  cookies=cookies, headers=headers)

print response.text

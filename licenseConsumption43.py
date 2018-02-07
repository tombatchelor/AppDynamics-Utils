# Script to get recent crash data from AppDynamics
import requests
from requests.auth import HTTPBasicAuth
import json
import time
import sys

def getNodeIdList(nodes):
    nodeList = []
    for node in nodes:
        # Only get APP_AGENT Nodes right now
        if node['agentType'] == 'APP_AGENT':
            nodeList.append(node['id'])
    return nodeList

def getListOfAvailableNodes(nodeStatus):
    nodeList = []
    for node in nodeStatus:
        if node['appServerAgentAvailability']['percentage'] > 0.0:
            nodeList.append(node['appServerAgentAvailability']['entityId'])
    return nodeList

def currentTimeMillis():
    return int(time.time()) * 1000

def lastDayMillis():
    currTime = currentTimeMillis()
    lastDay = currTime - (1000 * 60 * 60 * 24)
    return currTime - lastDay

def isPCF(node):
    if 'buildpack' in node['metaData']['appAgent']['installDir']:
        return True
    return False

def isTibcoCE(node):
    if 'vcap' in node['metaData']['appAgent']['installDir']:
        return True
    return False

# Variables, update to match your environment
username = ''
password = ''
customerName = ''
controller = ''

# Login to controller and get session and CSRF tokens, used for undocumented API
response = requests.get(controller + 'controller/auth?action=login', auth=(username + '@' + customerName, password))
jsessionID = response.cookies.get('JSESSIONID')
csrf = response.cookies.get('X-CSRF-TOKEN')

# Basic auth used for public API
basicAuth = HTTPBasicAuth(username + '@' + customerName, password)

# Add JSESSION ID to cookies and CSRF token to headers
cookies = {'JSESSIONID' : jsessionID}
headers = {'X-CSRF-TOKEN' : csrf, 'Content-Type': 'application/json;charset=UTF-8'}

# Get all app IDs
response = requests.get(controller + 'controller/rest/applications?output=JSON', auth=basicAuth)
apps = json.loads(response.text)

#Get nodes for each app and meta data
appCounter = 0
for app in apps:
    if appCounter > 5:
        break
    appCounter += 1
    response = requests.get(controller + 'controller/rest/applications/' + str(app['id']) + '/nodes?output=JSON', auth=basicAuth)
    nodes = json.loads(response.text)
    nodeList = getNodeIdList(nodes)
    if len(nodeList) > 0:
        nodeListQuery = str(nodeList).replace(' ','')
        response = requests.post(controller + 'controller/restui/appInfra/healthStatsForNodes?time-range=last_15_minutes.BEFORE_NOW.-1.-1.15', data=nodeListQuery, cookies=cookies, headers=headers)
        nodeList = getListOfAvailableNodes(json.loads(response.text))
        # Create new nodes list of just avialable nodes
        newNodeList = []
        for node in nodes:
            if node['id'] in nodeList:
                newNodeList.append(node)
        nodes = newNodeList
        app['nodes'] = nodes
        # Get node meta-data
        nodeCounter = 0
        for node in nodes:
            if nodeCounter % 10 == 0:
                # Pause each 10 nodes
                time.sleep(2)
            response = requests.get(controller + 'controller/restui/nodeUiService/node/' + str(node['id']),  cookies=cookies, headers=headers)
            if response.ok and len(response.text) > 0:
                metaData = json.loads(response.text)
                node['metaData'] = metaData
            nodeCounter += 1
    # Pause between apps
    time.sleep(5)

# Remove apps with no available nodes
newAppList = []
for app in apps:
    if 'nodes' in app:
        newAppList.append(app)

apps = newAppList
# apps is now a list of apps with Java agent and the agent meta data

# Get the split of differnt types of Java agent
for app in apps:
    app['fullJava'] = 0
    app['pcfNode'] = 0
    app['tibcoCE'] = 0
    for node in app['nodes']:
        if isPCF(node):
            app['pcfNode'] += 1
        elif isTibcoCE(node):
            app['tibcoCE'] += 1
        else:
            app['fullJava'] += 1

# Output Json
jsonRecord = open('json-dump.json','w')
jsonRecord.write(json.dumps(apps))

#Output CSV
csvOutput = open('java-license.csv','w')
csvOutput.write('App Name, Full Java, PCF Java, Tibco Java\n')
for app in apps:
    csvOutput.write(
        app['name'] + ',' +
        str(app['fullJava']) + ',' +
        str(app['pcfNode']) + ',' +
        str(app['tibcoCE']) + '\n'
    )


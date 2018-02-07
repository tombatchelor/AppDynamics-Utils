# Script to get recent crash data from AppDynamics
import requests
from requests.auth import HTTPBasicAuth
import json
import time

def getNodeIdList(nodes):
    nodeList = []
    for node in nodes:
         nodeList.append(node['id'])
    return nodeList

def getListOfAvailableNodes(nodeStatus):
    nodeList = []
    for node in nodeStatus['data']:
        if node['healthMetricStats']['appServerAgentAvailability']['percentage'] > 0.0:
            nodeList.append(node['nodeId'])
    return nodeList

def currentTimeMillis():
    return int(time.time()) * 1000

def lastDayMillis():
    currTime = currentTimeMillis()
    lastDay = currTime - (1000 * 60 * 60 * 24)
    return currTime - lastDay

nodeListQuery = {"requestFilter":[1647,1650,1658,1659,1648,1649,1657,1660,1646,1644],
    "resultColumns":["HEALTH","APP_AGENT_STATUS","APP_AGENT_VERSION","LAST_APP_SERVER_RESTART_TIME","MACHINE_AGENT_STATUS","VM_RUNTIME_VERSION"],
    "offset":0,
    "limit":-1,
    "searchFilters":[],
    "columnSorts":
        [{"column":"TIER",
         "direction":"ASC"}],
    "timeRangeStart":151797441638,
    "timeRangeEnd":1517961041638}


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
for app in apps:
    response = requests.get(controller + 'controller/rest/applications/' + str(app['id']) + '/nodes?output=JSON', auth=basicAuth)
    nodes = json.loads(response.text)
    nodeList = getNodeIdList(nodes)
    if len(nodeList) > 0:
        nodeListQuery['requestFilter'] = nodeList
        nodeListQuery['timeRangeStart'] = lastDayMillis()
        nodeListQuery['timeRangeEnd'] = currentTimeMillis()
        postData = json.dumps(nodeListQuery).replace(' ','')
        response = requests.post(controller + 'controller/restui/nodes/list/health/ids', data=postData, cookies=cookies, headers=headers)
        nodeList = getListOfAvailableNodes(json.loads(response.text))
        # Create new nodes list of just avialable nodes
        newNodeList = []
        for node in nodes:
            if node['id'] in nodeList:
                newNodeList.append(node)
        nodes = newNodeList
        app['nodes'] = nodes
        # Get node meta-data
        for node in nodes:
            response = requests.get(controller + 'controller/restui/nodeUiService/appAgentByNodeId/' + str(node['id']),  cookies=cookies, headers=headers)
            if response.ok and len(response.text) > 0:
                metaData = json.loads(response.text)
                node['metaData'] = metaData

# Remove apps with no available nodes
newAppList = []
for app in apps:
    if 'nodes' in app:
        newAppList.append(app)

apps = newAppList
print(json.dumps(apps))

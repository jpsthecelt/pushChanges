import requests
import pprint
import sys
import json
import argparse

#loginHash = {
#    'client_id': 'D4MP726BR4JEZLWRQX7RMI7IAU',
#    'client_secret': 'FKBNBWPZ4YXUPHZNGN5XV7TSSM',
#    'grant_type': 'password',
#    'username': 'john.singer@plutora.com',
#    'password': 'jps.jps'
#}

# Function to filter out the names
def names(name):
    return name['value']

if __name__ == '__main__':
    pp = pprint.PrettyPrinter(indent=4)

    # parse commandline and get appropriate passwords/configuration-items
    #
    parser = argparse.ArgumentParser(description='Get configuration-filename and item to dump')
    parser.add_argument('-f', action='store', dest='config_filename',
                        help='Config filename ')
    parser.add_argument('-c', action='store', dest='change_item',
                        help='Plutora Changefile (in JSON)")')
    results = parser.parse_args()
    change_entity = results.change_item

    config_filename = results.config_filename
    if config_filename == None:
        config_filename = 'credentials.cfg'

    try:
       # If we don't specify a configfile on the commandline, assume one & try accessing
       # using the specified/assumed configfilename, grabbing ClientId & Secret from the JSON (manual setup of Plutora Oauth authorization.
       with open(config_filename) as data_file:
              data = json.load(data_file)
       client_id = data["credentials"]["client_id"]
       client_secret = data["credentials"]["client_secret"]
       plutora_username = data["credentials"]["username"].replace('@','%40')
       plutora_password = data["credentials"]["password"]

       payload = "client_id=" + client_id + "&client_secret=" + client_secret + "&grant_type=password&username="
       payload = payload + plutora_username.replace('%40', '@') + "&password=" + plutora_password + "&="

       res = requests.post('https://usoauth.plutora.com/oauth/token', data=payload, headers = { 'Content-Type': 'application/x-www-form-urlencoded'})
       auth_token = None
       if res.status_code == 200:
           auth_token = str(res.json()['access_token'])
       else:
           print ("Error logging in , pls check credentials")
           pp.pprint(res.json())
           sys.exit(-1)

       if not auth_token:
           print ("Error authenticating.. Exiting....")
           pp.pprint(res.json())
           sys.exit(-1)

       auth_header = { 'Authorization': 'bearer %s' %(auth_token,) }

       # Verify that all is okay by printing the email associated with user
       res = requests.get('https://usapi.plutora.com/me', headers=auth_header)
       print (res.text)

       # get new changes-entity values from the indicated JSON file.
       fileName = change_entity
       with open(fileName) as data_file:
           changes_array = data_file.read().splitlines()
       changes = ''.join(map(str, changes_array))
       doc = json.loads(changes)

       name = doc['changes']['name']
       changePriority = doc['changes']['ChangePriority']
       changeStatus = doc['changes']['ChangeStatus']
       changeType = doc['changes']['ChangeType']
       changeDeliveryRisk = doc['changes']['ChangeDeliveryRisk']
       changeTheme = doc['changes']['ChangeTheme']
       raisedByUser = doc['changes']['RaisedByUser']
       organization = doc['changes']['Organization']

       # Get the Keys for "Changes" POST request
       changePriorityResponse = requests.get('https://usapi.plutora.com/lookupfields/ChangePriority', headers=auth_header)
       if changePriorityResponse.status_code != 200:
           print ("Error getting Change priorities")
           pp.pprint(changePriorityResponse.json())
           sys.exit(-1)

       changePriorities = changePriorityResponse.json()

       changePriorityVal = [changePriorityVal for changePriorityVal in changePriorities if changePriorityVal['value'] == changePriority]
       if len(changePriorityVal) == 0:
           print ("Cannot find Change Priority with %s. Has to be one of %s") %(changePriority, ','.join(map(names, changePriorities)))
           sys.exit(-1)
       else:
           changePriorityId = changePriorityVal[0]['id']

       changeStatusResponse = requests.get('https://usapi.plutora.com/lookupfields/ChangeStatus', headers=auth_header)
       if changeStatusResponse.status_code != 200:
           print ("Error getting Change status")
           pp.pprint(changeStatusResponse.json())
           sys.exit(-1)

       changeStatuses = changeStatusResponse.json()

       changeStatusVal = [changeStatusVal for changeStatusVal in changeStatuses if changeStatusVal['value'] == changeStatus]
       if len(changeStatusVal) == 0:
           print ("Cannot find Change Status with %s. Has to be one of %s") %(changeStatus, ','.join(map(names, changeStatuses)))
           sys.exit(-1)
       else:
           changeStatusId = changeStatusVal[0]['id']

       changeTypeResponse = requests.get('https://usapi.plutora.com/lookupfields/ChangeType', headers=auth_header)
       if changeStatusResponse.status_code != 200:
           print ("Error getting Change Type")
           pp.pprint(changeTypeResponse.json())
           sys.exit(-1)

       changeTypes = changeTypeResponse.json()

       changeTypeVal = [changeTypeVal for changeTypeVal in changeTypes if changeTypeVal['value'] == changeType]
       if len(changeTypeVal) == 0:
           print ("Cannot find Change Type with %s. Has to be one of %s") %(changeType, ','.join(map(names, changeTypes)))
           sys.exit(-1)
       else:
           changeTypeId = changeTypeVal[0]['id']

       changeDeliveryRiskResponse = requests.get('https://usapi.plutora.com/lookupfields/ChangeDeliveryRisk', headers=auth_header)
       if changeDeliveryRiskResponse.status_code != 200:
           print ("Error getting Change Delivery Risk %i" % changeDeliveryRiskResponse.status_code)
           pp.pprint(changeDeliveryRiskResponse.json())
           sys.exit(-1)

       changeDeliveryRisks  = changeDeliveryRiskResponse.json()

       changeDeliveryRiskVal = [changeDeliveryRiskVal for changeDeliveryRiskVal in changeDeliveryRisks if changeDeliveryRiskVal['value'] == changeDeliveryRisk]
       if len(changeDeliveryRiskVal) == 0:
           print ("Cannot find Change Delivery Risk with %s. Has to be one of %s") %(changeType, ','.join(map(names, changeDeliveryRisks)))
           sys.exit(-1)
       else:
           changeDeliveryRiskId = changeDeliveryRiskVal[0]['id']

       changeThemesResponse = requests.get('https://usapi.plutora.com/lookupfields/ChangeTheme', headers=auth_header)
       if changeThemesResponse.status_code != 200:
           print ("Error getting Change Themes")
           pp.pprint(changeThemesResponse.json())
           sys.exit(-1)

       changeThemes = changeThemesResponse.json()

       changeThemesVal = [changeThemesVal for changeThemesVal in changeThemes if changeThemesVal['value'] == changeTheme]
       if len(changeThemesVal) == 0:
           print ("Cannot find Change Theme with %s. Has to be one of %s") %(changeType, ','.join(map(names, changeThemes)))
           sys.exit(-1)
       else:
           changeThemeId = changeThemesVal[0]['id']

       usersResponse = requests.get('https://usapi.plutora.com/users', headers=auth_header)
       if usersResponse.status_code != 200:
           print ("Error getting Users %i" % usersResponse.status_code)
           pp.pprint(usersResponse.json())
           sys.exit(-1)

       users = usersResponse.json()
       usersVal = [usersVal for usersVal in users if usersVal['userName'] == raisedByUser]
       if len(usersVal) == 0:
           print ("Cannot find User with %s. ") %(raisedByUser,)
           sys.exit(-1)
       else:
           userId = usersVal[0]['id']

       orgResponse = requests.get('https://usapi.plutora.com/organizations', headers=auth_header)
       if orgResponse.status_code != 200:
           print ("Error getting Organizations")
           pp.pprint(orgResponse.json())
           sys.exit(-1)

       organizations = orgResponse.json()
       orgVal = [orgVal for orgVal in organizations if orgVal['name'] == organization]
       if len(orgVal) == 0:
           print ("Cannot find Organization with %s. ") %(organization,)
           sys.exit(-1)
       else:
           orgId = orgVal[0]['id']

       changeDict = {
           "Name": str(name),
           "ChangePriorityId": str(changePriorityId),
           "ChangeStatusId": str(changeStatusId),
           "RaisedById": str(userId),
           "OrganizationId": str(orgId),
           "ChangeTypeId": str(changeTypeId),
           "ChangeDeliveryRiskId": str(changeDeliveryRiskId),
           "ChangeThemeId": str(changeThemeId)
       }

       changeHeaders = {
           'Authorization': 'bearer %s' %(auth_token,)
       }
       res = requests.post('https://usapi.plutora.com/changes', data=changeDict, headers=changeHeaders)
       if res.status_code == 201:
           print ("Change created")
       else:
           print ("Error in posting changes: %i" % res.status_code)

       pp.pprint(res.json())


    except Exception, ex:
        # ex.msg is a string that looks like a dictionary
        print "EXCEPTION: %s " % ex.msg
        exit('couldnt open file {0}'.format(config_filename))


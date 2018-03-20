from botocore.vendored import requests
import json
import os

def lambda_handler(event, context):
    key = os.environ['oauthkey']
    baseurl = 'https://console.cloud.vmware.com/csp/gateway'
    uri = '/am/api/auth/api-tokens/authorize'
    headers = {'Content-Type':'application/json'}
    payload = {'refresh_token': key}
    r = requests.post(f'{baseurl}{uri}', headers = headers, params = payload)
    if r.status_code != 200:
        print(f'Unsuccessful Login Attmept. Error code {r.status_code}')
    else:
        print('Login successful. ') 
        auth_header = r.json()['access_token']
        finalHeader = {'Content-Type':'application/json','csp-auth-token':auth_header}
        req = requests.get('https://vmc.vmware.com/vmc/api/orgs', headers = finalHeader)
        orgID = req.json()[0]['id']
        sddcReq = requests.get('https://vmc.vmware.com/vmc/api/orgs/'+orgID+'/sddcs', headers=finalHeader)
        sddcCreator = sddcReq.json()[0]['user_name']
        sddcName = sddcReq.json()[0]['name']
        sddcURL = sddcReq.json()[0]['resource_config']['vc_url']
        sddcAdmin = sddcReq.json()[0]['resource_config']['cloud_username']
        sddcPass = sddcReq.json()[0]['resource_config']['cloud_password']
        sddcRegion = sddcReq.json()[0]['resource_config']['region']
        sddcID = sddcReq.json()[0]['id']
        sddc = requests.get('https://vmc.vmware.com/vmc/api/orgs/'+orgID+'/sddcs/'+sddcID+'/', headers=finalHeader)
        response = {
            "dialogAction":
                {
                 "fulfillmentState":"Fulfilled",
                 "type":"Close","message":
                    {
                      "contentType":"PlainText",
                      "content": "*SDDC Name:* "+sddcName+" \n*SDDC Region:* "+sddcRegion+" \n*SDDC vCenter URL:* "+sddcURL+" \n*SDDC vCenter Username:* "+sddcAdmin+" \n*SDDC vCenter Password:* "+sddcPass+" \n*Created By:* "+sddcCreator
                    }
                }
            }
        return response
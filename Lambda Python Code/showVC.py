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
        sddcURL = sddcReq.json()[0]['resource_config']['vc_url']
        response = {
            "dialogAction":
                {
                 "fulfillmentState":"Fulfilled",
                 "type":"Close","message":
                    {
                      "contentType":"PlainText",
                      "content": "*SDDC vCenter URL:* "+sddcURL
                    }
                }
            }
        return response

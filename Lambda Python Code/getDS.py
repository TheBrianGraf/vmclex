from botocore.vendored import requests
import os 
import json

def lambda_handler(event, context):
    url = os.environ['vcurl']
    user = os.environ['user']
    password = os.environ['pass']

    vmurl = f'{url}/rest/vcenter/datastore'

    
    def authvcenter(url, user, password):
        print('Authenticating to vCenter, user: {}'.format(user))
        resp = requests.post(f'{url}/rest/com/vmware/cis/session',
                             auth=(user, password), verify=False)
        if resp.status_code != 200:
            print('Error! API responded with: {}'.format(resp.status_code))
            return
        auth_header = {'vmware-api-session-id': resp.json()['value']}
        return auth_header
    
    authheader = authvcenter(url,user,password)

    vms = requests.get(vmurl, headers=authheader)

    vmdata = vms.json()

    # Add new list of VMs to DynamoDB
            
    arr = [] 
    for i in vmdata['value']:
        arr.append("*Name:* "+i['name']+" || *Free Space:* "+str(int(i['free_space']/1024/1024/1024/1024))+'\n')
    strlist = ''.join(arr)
        
    lexresponse = {
            "dialogAction":
                {
                 "fulfillmentState":"Fulfilled",
                 "type":"Close","message":
                    {
                      "contentType":"PlainText",
                      "content": "*"+str(len(vmdata['value']))+" Datastores are currently present*"+"\n\n"+"*Current Datastore statistics are as follows (rounded down): *"+"\n"+strlist
                    }
                }
            }

    return lexresponse
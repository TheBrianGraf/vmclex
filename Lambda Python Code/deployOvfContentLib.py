from botocore.vendored import requests
import os 
import json
import uuid
import boto3

def lambda_handler(event, context):
    template = event["currentIntent"]["slots"]["template"]
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('templates')
    resp = table.get_item(Key={'id': template})
    ovf = resp['Item']['uuid']
    print(ovf)
    url = os.environ['vcurl']
    user = os.environ['user']
    password = os.environ['pass']
    def authvcenter(url, user, password):
        print('Authenticating to vCenter, user: {}'.format(user))
        resp = requests.post(f'{url}/rest/com/vmware/cis/session',
                             auth=(user, password), verify=False)
        if resp.status_code != 200:
            print('Error! API responded with: {}'.format(resp.status_code))
            return
        auth_header = {'vmware-api-session-id': resp.json()['value']}
        return auth_header
        
    authhead = authvcenter(url,user,password)

    vmname = "BG-"+str(uuid.uuid4())
    depurl = f'{url}/rest/com/vmware/vcenter/ovf/library-item/id:{ovf}?~action=deploy'
    # Thanks Matt Dreyer for this! 
    deploymentspec = {
        "target": {
            "resource_pool_id": "resgroup-464",
            "host_id": "host-37",
            "folder_id": "group-v49"
        },
        "deployment_spec": {
            "name": vmname,
            "accept_all_EULA": "true",
            "storage_mappings": [
                {
                    "key": "dont-delete-this-key",
                    "value": {
                        "type": "DATASTORE",
                                "datastore_id": "datastore-61",
                                "provisioning": "thin"
                    }
                }
            ],
            "storage_provisioning": "thin",
            "storage_profile_id": "aa6d5a82-1c88-45da-85d3-3d74b91a5bad",
        }
    }
    # some of the sickest hackery i've ever done in python right here 
    try:
        requests.post(depurl, headers=authhead, json=deploymentspec, timeout=1.5)
    except requests.exceptions.ReadTimeout:
        pass

    lexresponse = {
            "dialogAction":
                {
                 "fulfillmentState":"Fulfilled",
                 "type":"Close","message":
                    {
                      "contentType":"PlainText",
                      "content": template+" VM deployment has started. Please wait 45 seconds to 1 minute for deployment to complete."
                    }
                }
            }

    return lexresponse
from botocore.vendored import requests
import os 
import json
import boto3

def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    client = boto3.client('dynamodb')
    table = dynamodb.Table('LexVMs')
    table_name = 'LexVMs'
    # Clear items from Database
    response = client.describe_table(TableName='LexVMs')
    keys = [k['AttributeName'] for k in response['Table']['KeySchema']]
    response = table.scan()
    items = response['Items']

    with table.batch_writer() as batch:
        for item in items:
            key_dict = {k: item[k] for k in keys}
            print("Deleting " + str(item) + "...")
            batch.delete_item(Key=key_dict)
            
    # Finished Clearing Items
    
    url = os.environ['vcurl']
    user = os.environ['user']
    password = os.environ['pass']

    vmurl = f'{url}/rest/vcenter/vm?filter.resource_pools=resgroup-464'

    deploymentspec = {
        "target": {
            "resource_pool_id": "resgroup-464",
            "host_id": "host-37",
            "folder_id": "group-v49"
        }
    }
    
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
    for i in vmdata['value']:
            table.put_item(Item={'VMName': i['name'] ,'id': i['vm'], 'power_state':i['power_state']})
            
    arr = [] 
    for i in vmdata['value']:
        arr.append("*Name:* "+i['name']+'\n')
    strlist = ''.join(arr)
        
    lexresponse = {
            "dialogAction":
                {
                 "fulfillmentState":"Fulfilled",
                 "type":"Close","message":
                    {
                      "contentType":"PlainText",
                      "content": "*"+str(len(vmdata['value']))+" VM's have been added to DynamoDB*"+"\n\n"+"*The following VMs are active in this Resource Pool:*"+"\n"+strlist
                    }
                }
            }

    return lexresponse
import os
import json
import re
import boto3
import urllib3

S3_BUCKET = os.environ['S3_BUCKET']
APPLICATION_ID = os.environ['APPLICATION_ID']

def lambda_handler(event, context):
    client = boto3.client("s3")
    slash_objects = client.list_objects_v2(Bucket=f"{S3_BUCKET}", Prefix="Resources/").get('Contents')
    print(slash_objects)

    http = urllib3.PoolManager()
    slash_url = f"https://discord.com/api/v8/applications/{APPLICATION_ID}/commands"

    for slash_object in slash_objects:
        slasher = re.search('Resources/(.+?).PNG', slash_object.get('Key'))
        if slasher:
            slash_command = json.dumps({
                "name": f"{slasher.group(1)}",
                "description": f"display the {slasher.group(1)} chart"
                }).encode('utf-8')
            #print(slash_command)
            r = http.request('POST', slash_url, headers={'Content-Type': 'application/json'}, body=slash_command)
    
    
    return {
        'statusCode': 200,
        'body': json.dumps('All commands registered!')
    }
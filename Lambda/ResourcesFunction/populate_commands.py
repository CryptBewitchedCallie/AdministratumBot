import os
import json
import re
import boto3
import urllib3
import time

# import environment variables
S3_BUCKET = os.environ['S3_BUCKET']
APPLICATION_ID = os.environ['APP_ID']
BOT_TOKEN = os.environ['BOT_TOKEN']
# initialise global variables/resources
http = urllib3.PoolManager()
slash_url = f"https://discord.com/api/v8/applications/{APPLICATION_ID}/commands"
slash_headers = {'Content-Type': 'application/json', 'Authorization': f'Bot {BOT_TOKEN}'}
slash_responses = [200, 201]  # acceptable HTTP responses


def create_slash_command(slash_object):
    slasher = re.search('Resources/(.+?).PNG', slash_object.get('Key'))
    if slasher:
        slash_command = json.dumps({
            "name": f"{slasher.group(1)}",
            "description": f"display the {slasher.group(1)} chart"
            }).encode('utf-8')
        r = http.request('POST', slash_url, headers=slash_headers, body=slash_command)
        if r.status == 429:  # rate limited, initiate a wait:
            print("rate limited, waiting 15 seconds")
            time.sleep(15)
            r = http.request('POST', slash_url, headers=slash_headers, body=slash_command)
        if r.status not in slash_responses:  # any response but "created" or "ok"
            print(slash_command)
            print(r.status)
            print(r.data)
            raise urllib3.exceptions.HTTPError
        print(f"{slasher.group(1)} created")
        time.sleep(3)  # found we were hitting it too hard, slow down!


def lambda_handler(event, context):
    client = boto3.client("s3")
    slash_objects = client.list_objects_v2(Bucket=f"{S3_BUCKET}", Prefix="Resources/").get('Contents')

    for slash_object in slash_objects:
        create_slash_command(slash_object)
    
    return {
        'statusCode': 200,
        'body': json.dumps('All commands registered!')
    }

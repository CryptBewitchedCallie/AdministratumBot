import os
import json
import re
import boto3
import urllib3
import time
import base64
from botocore.exceptions import ClientError

# import environment variables
SECRET_ARN = os.environ['SECRET_ARN']
REGION = os.environ['REGION']
# initialise global variables/resources
http = urllib3.PoolManager()
slash_responses = [200, 201]  # acceptable HTTP responses


def create_slash_command(slash_url, slash_headers, slash_object):
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

    secret = get_secret()
    app_id = secret['APP_ID']
    bot_token = secret['BOT_TOKEN']
    s3_bucket = secret['S3_BUCKET']

    slash_url = f"https://discord.com/api/v8/applications/{app_id}/commands"
    slash_headers = {'Content-Type': 'application/json', 'Authorization': f'Bot {bot_token}'}
    slash_objects = client.list_objects_v2(Bucket=f"{s3_bucket}", Prefix="Resources/").get('Contents')

    for slash_object in slash_objects:
        create_slash_command(slash_url, slash_headers, slash_object)
    
    return {
        'statusCode': 200,
        'body': json.dumps('All commands registered!')
    }


def get_secret():
    # # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=REGION
    )
    try:
        get_secret_value_response=client.get_secret_value(
            SecretId=SECRET_ARN
        )
    except ClientError as e:
        raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
        else:
            secret = base64.b64decode(get_secret_value_response['SecretBinary'])
    secret = json.loads(secret)
    return secret

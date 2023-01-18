import os
import json
import urllib3
import boto3
import base64
from botocore.exceptions import ClientError

SECRET_ARN = os.environ['SECRET_ARN']
REGION = os.environ['REGION']
# global variables
http = urllib3.PoolManager()
APP_ID = ''
S3_BUCKET = ''


def lambda_handler(event, context):
    print(f"event {event}")  # debug print

    body = json.loads(event.get('body'))

    # get the secret manager bits
    secret = get_secret()
    global APP_ID
    APP_ID = secret['APP_ID']
    global S3_BUCKET
    S3_BUCKET = secret['S3_BUCKET']

    # find the file to pick up
    command = body['data']['name']
    # send the webhook
    webhook_url = event.get('webhook_url')
    webhook_object = json.dumps({
        "username": secret['WEBHOOK_NAME'],
        "avatar_url": secret['WEBHOOK_AVATAR'],
        "embeds": [{"image": {"url": f"https://{S3_BUCKET}.s3-eu-west-1.amazonaws.com/Resources/{command}.PNG"}}]
    }).encode('utf-8')

    try:
        r = http.request('POST', webhook_url, headers={'Content-Type': 'application/json'}, body=webhook_object)
    except:
        return {
            "isBase64Encoded": False,
            "statusCode": 500,
            "body": "Something bad happened",
            "headers": {
                "content-type": "application/json"
            }
        }

    # API call complete
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": "Action completed",
        "headers": {
            "content-type": "application/json"
        }
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

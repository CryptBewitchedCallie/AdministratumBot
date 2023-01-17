import os
import boto3
import json
import urllib3
import base64
from botocore.exceptions import ClientError

# environment variables
NEXT_LAMBDA = os.environ['NEXT_LAMBDA']
SECRET_ARN = os.environ['SECRET_ARN']
REGION = os.environ['REGION']
# global variables
http = urllib3.PoolManager()
PUBLIC_KEY = ''
APP_ID = ''
BOT_TOKEN = ''
WEBHOOK_NAME = ''
WEBHOOK_AVATAR = ''


def create_webhook(channel_id):
    # prepare webhook components
    webhook_url = f"https://discord.com/api/v8/channels/{channel_id}/webhooks"
    webhook_headers = {'Content-Type': 'application/json', 'Authorization': f'Bot {BOT_TOKEN}'}
    webhook_content = json.dumps({
        "name": f"{WEBHOOK_NAME}",
        "avatar": f"{WEBHOOK_AVATAR}"
    }).encode('utf-8')

    # register the webhook
    return http.request('POST', webhook_url, headers=webhook_headers, body=webhook_content)


def find_webhook(all_webhooks, channel_id):
    webhook_token = ''
    webhook_id = ''
    webhook_found = False
    for webhook_object in json.loads(all_webhooks):
        print(f"webhook_object {webhook_object}")  # debug
        if webhook_object.get('application_id') == APP_ID and webhook_object.get('channel_id') == channel_id:
            webhook_token = webhook_object.get('token')
            webhook_id = webhook_object.get('id')
            webhook_found = True
    return webhook_found, webhook_id, webhook_token


def call_next_lambda(event):
    client = boto3.client("lambda")
    client.invoke(
        FunctionName=NEXT_LAMBDA,
        InvocationType="Event",
        Payload=json.dumps(event).encode('utf8')
    )


def ack_interaction(body, ack_type):
    # acknowledge the interaction
    # print(f"body {body}")
    interaction_id = body.get('id')
    interaction_token = body.get('token')
    response_url = f"https://discord.com/api/v8/interactions/{interaction_id}/{interaction_token}/callback"
    ack_object = json.dumps({"type": ack_type, "data": {"content": "instruction received!"}}) .encode('utf-8')
    r = http.request('POST', response_url, headers={'Content-Type': 'application/json'}, body=ack_object)
    print(f"ack response data {r.data}")


def lambda_handler(event, context):
    print(f"event {event}")  # debug print

    body = json.loads(event.get('body'))
    channel_id = body.get('channel_id')

    # Acknowledge the interaction to say we're working on things
    # except commented out, the auth function does an initial stage of this and now I'm not sure which part is achieving what
    # ack_interaction(body, 1)

    # fetch the required secrets and other configuration data
    secret = get_secret()
    global BOT_TOKEN
    BOT_TOKEN = secret['BOT_TOKEN']
    global PUBLIC_KEY
    PUBLIC_KEY = secret['PUBLIC_KEY']
    global APP_ID
    APP_ID = secret['APP_ID']
    global WEBHOOK_NAME
    WEBHOOK_NAME = secret['WEBHOOK_NAME']
    global WEBHOOK_AVATAR
    WEBHOOK_AVATAR = secret['WEBHOOK_AVATAR']

    # Ask if there are existing webhooks
    webhook_url = f"https://discord.com/api/v8/channels/{channel_id}/webhooks"
    webhook_headers = {'Authorization': f'Bot {BOT_TOKEN}'}
    r = http.request('GET', webhook_url, headers=webhook_headers)
    # print(f"r.data {r.data}")  # debug print

    # If no existing webhooks create one
    if r.data == b'[]':
        r = create_webhook(channel_id)

    # get the right token for this app/channel combo
    all_webhooks = r.data.decode('utf-8')
    # print(f"r.data.decode {r.data.decode('utf-8')}")  # debug
    webhook_found, webhook_id, webhook_token = find_webhook(all_webhooks, channel_id)
    # if there wasn't a matching webhook then create one and get the IDs and all
    if not webhook_found:
        r = create_webhook(channel_id)
        all_webhooks = r.data.decode('utf-8')
        webhook_found, webhook_id, webhook_token = find_webhook(all_webhooks, channel_id)

    # create webhook URL from the response
    webhook_url = f"https://discord.com/api/webhooks/{webhook_id}/{webhook_token}"

    # Now that it's registered, send the webhook message
    event["webhook_url"] = webhook_url
    call_next_lambda(event)

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
    # Create a Secrets Manager client
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

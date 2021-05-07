import os
import boto3
import json
import urllib3

# environment variables
PUBLIC_KEY = os.environ['PUBLIC_KEY']
APP_ID = os.environ['APP_ID']
WEBHOOK_NAME = os.environ['WEBHOOK_NAME']
WEBHOOK_AVATAR = os.environ['WEBHOOK_AVATAR']
BOT_TOKEN = os.environ['BOT_TOKEN']
NEXT_LAMBDA = os.environ['NEXT_LAMBDA']
# global variables
http = urllib3.PoolManager()


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


def call_next_lambda(event):
    client = boto3.client("lambda")
    client.invoke(
        FunctionName=NEXT_LAMBDA,
        InvocationType="Event",
        Payload=json.dumps(event).encode('utf8')
    )


def lambda_handler(event, context):
    print(f"event {event}")  # debug print

    body = json.loads(event.get('body'))
    channel_id = body.get('channel_id')

    # Ask if there are existing webhooks
    webhook_url = f"https://discord.com/api/v8/channels/{channel_id}/webhooks"
    webhook_headers = {'Authorization': f'Bot {BOT_TOKEN}'}
    r = http.request('GET', webhook_url, headers=webhook_headers)

    # If no existing webhooks create one
    if r.data == b'[]':
        r = create_webhook(channel_id)

    # get the right token for this app/channel combo
    webhook_token = ''
    webhook_id = ''
    for webhook in json.loads(r.data.decode('utf-8')):
        if (webhook.get('application_id') == APP_ID and webhook.get('channel_id') == channel_id):
            webhook_token = webhook.get('token')
            webhook_id = webhook.get('id')

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

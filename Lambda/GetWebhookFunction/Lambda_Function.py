import os
import boto3
import json
import urllib3

# environment variables
PUBLIC_KEY = os.environ['PUBLIC_KEY']
APP_ID = os.environ['APP_ID']
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


def find_webhook(all_webhooks, channel_id):
    webhook_token = ''
    webhook_id = ''
    webhook_found = False
    for webhook_object in json.loads(all_webhooks):
        # print(f"webhook_object {webhook_object}")  # debug
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


def ack_interaction(body):
    # acknowledge the interaction
    # print(f"body {body}")
    interaction_id = body.get('id')
    interaction_token = body.get('token')
    response_url = f"https://discord.com/api/v8/interactions/{interaction_id}/{interaction_token}/callback"
    ack_object = json.dumps({"type": 4, "data": {"content": "instruction received!"}}) .encode('utf-8')
    r = http.request('POST', response_url, headers={'Content-Type': 'application/json'}, body=ack_object)
    # print(f"response data {r.data}")


def lambda_handler(event, context):
    # print(f"event {event}")  # debug print
    body = json.loads(event.get('body'))
    channel_id = body.get('channel_id')

    # Acknowledge the interaction to say we're working on things
    ack_interaction(body)

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

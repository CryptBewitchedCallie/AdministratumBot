import os
import json
import urllib3

PUBLIC_KEY = os.environ['PUBLIC_KEY']
APP_ID = os.environ['APP_ID']
WEBHOOK_NAME = os.environ['WEBHOOK_NAME']
WEBHOOK_AVATAR = os.environ['WEBHOOK_AVATAR']
BOT_TOKEN = os.environ['BOT_TOKEN']


def lambda_handler(event, context):
    print(f"event {event}")  # debug print

    body = json.loads(event.get('body'))
    channel_id = body['webhook']['channel_id']
    http = urllib3.PoolManager()

    # prepare webhook components
    webhook_url = f"https://discord.com/api/v8/channels/{channel_id}/webhooks"
    webhook_headers = json.dumps({
        'Content-Type': 'application/json',
        'Authorization': f'Bot {BOT_TOKEN}'
    }).encode('utf-8')
    webhook_content = json.dumps({
    "name": f"{WEBHOOK_NAME}",
    "avatar": f"{WEBHOOK_AVATAR}"
    }).encode('utf-8')

    # register the webhook
    r = http.request('POST', webhook_url, headers=webhook_headers, body=webhook_content)
    print(r)

    channel_id = r.data.get('channel_id')
    token = r.data.get('token')

    # create webhook URL from the response
    webhook_url = f"https://discord.com/api/webhooks/{channel_id}/{token}"

    # send webhook to say hello
    webhook_content = json.dumps({
        "username": f"{WEBHOOK_NAME}",
        "avatar_url": f"{WEBHOOK_AVATAR}",
        "embeds": [{"image": {"url": f"https://{S3_BUCKET}.s3-eu-west-1.amazonaws.com/Resources/blep.PNG"}}]
        }).encode('utf-8')
    r = http.request('POST', webhook_url, headers=webhook_headers, body=webhook_content)
    print(r)

    # API call complete
    return {
              "isBase64Encoded": False,
              "statusCode": 200,
              "body": "Action completed",
              "headers": {
                "content-type": "application/json"
              }
            }

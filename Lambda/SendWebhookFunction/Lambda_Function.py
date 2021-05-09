import os
import json
import urllib3

APP_ID = os.environ['APP_ID']
S3_BUCKET = os.environ['S3_BUCKET']


def lambda_handler(event, context):
    print(f"event {event}")  # debug print

    http = urllib3.PoolManager()
    body = json.loads(event.get('body'))

    # find the file to pick up
    command = body['data']['name']

    # send the webhook
    webhook_url = event.get('webhook_url')
    webhook_object = json.dumps({
        "username": "administratum_test",
        "avatar_url": "https://logos-download.com/wp-content/uploads/2016/02/warhammer-40000-and_bird_logo.png",
        "embeds": [{"image": {"url": f"https://{S3_BUCKET}.s3-eu-west-1.amazonaws.com/Resources/{command}.PNG"}}]
    }).encode('utf-8')
    r = http.request('POST', webhook_url, headers={'Content-Type': 'application/json'}, body=webhook_object)

    # API call complete
    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": "Action completed",
        "headers": {
            "content-type": "application/json"
        }
    }

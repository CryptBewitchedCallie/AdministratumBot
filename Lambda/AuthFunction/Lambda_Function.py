import os
import json
import boto3
import urllib3
from nacl.signing import VerifyKey

# environment variables
PUBLIC_KEY = os.environ['PUBLIC_KEY']
NEXT_LAMBDA = os.environ['NEXT_LAMBDA']
# global variables
http = urllib3.PoolManager()
PING_PONG = {"type": 1}
RESPONSE_TYPES = {
                    "PONG": 1,
                    "ACK_NO_SOURCE": 2,
                    "MESSAGE_NO_SOURCE": 3,
                    "MESSAGE_WITH_SOURCE": 4,
                    "ACK_WITH_SOURCE": 5
                  }


def verify_signature(event):
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
    signature = event['headers'].get('x-signature-ed25519')
    timestamp = event['headers'].get('x-signature-timestamp')
    body = event.get('body')

    message = timestamp.encode()+body.encode()
    sigbytes = bytes.fromhex(signature)
    verify_key.verify(message, sigbytes)  # raises an error if unequal


def ping_pong(body):
    if body.get("type") == 1:
        return True
    return False


def ack_interaction(body):
    # acknowledge the interaction
    print(body)
    interaction_id = body.get('id')
    interaction_token = body.get('token')
    response_url = f"https://discord.com/api/v8/interactions/{interaction_id}/{interaction_token}/callback"
    ack_object = json.dumps({"type": 5, "data": {"content": "instruction received, processing request"}}) .encode('utf-8')
    r = http.request('POST', response_url, headers={'Content-Type': 'application/json'}, body=ack_object)


def call_next_lambda(event):
    client = boto3.client("lambda")
    client.invoke(
        FunctionName=NEXT_LAMBDA,
        InvocationType="Event",
        Payload=json.dumps(event).encode('utf8')
    )


def lambda_handler(event, context):
    print(f"event {event}")  # debug print
    # verify the signature
    try:
        verify_signature(event)
    except Exception as e:
        print("not authorized")
        return {
              "isBase64Encoded": False,
              "statusCode": 401,
              "body": "[UNAUTHORIZED] Invalid request signature!"
            }

    # check if message is a ping
    body = json.loads(event.get('body'))
    if ping_pong(body):
        return {
              "isBase64Encoded": False,
              "statusCode": 200,
              "headers": {
                "content-type": "application/json"
              },
              "body": "{\"type\": 1}"
            }

    # for anything else acknowledge the interaction and tell it we're working on the request...
    ack_interaction(body)
    # ... call the next function...
    call_next_lambda(event)
    # ... and while that's running respond that all's ok
    # API call complete
    return {
              "isBase64Encoded": False,
              "statusCode": 200,
              "headers": {
                "content-type": "application/json"
              },
              "body": "{\"type\": 2}"
            }

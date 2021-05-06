import os
import json
import boto3
from nacl.signing import VerifyKey
from nacl.signing import BadSignatureError

PUBLIC_KEY = os.environ['PUBLIC_KEY']
NEXT_LAMBDA = os.environ['NEXT_LAMBDA']
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


def call_next_lambda(event):
    client = boto3.client("lambda")
    client.invoke(
        FunctionName=NEXT_LAMBDA,
        InvocationType="Event",
        Payload=event
    )


def lambda_handler(event, context):
    print(f"event {event}")  # debug print
    # verify the signature
    try:
        verify_signature(event)
    except BadSignatureError as e:
        print("not authorized")
        return {
              "isBase64Encoded": False,
              "statusCode": 401,
              "body": "[UNAUTHORIZED] Invalid request signature!",
              "headers": {
                "content-type": "application/json"
              }
            }

    # check if message is a ping
    body = json.loads(event.get('body'))
    if ping_pong(body):
        return PING_PONG

    # for anything else call the next function, and while that's running respond that all's ok
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

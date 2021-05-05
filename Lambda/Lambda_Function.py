import os
import json
import urllib3
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

PUBLIC_KEY = os.environ['PUBLIC_KEY']
WEBHOOK = os.environ['WEBHOOK']
APP_ID = os.environ['APP_ID']
PING_PONG = {"type": 1}
RESPONSE_TYPES =  { 
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
    verify_key.verify(message, sigbytes) # raises an error if unequal

def ping_pong(body):
    if body.get("type") == 1:
        return True
    return False
    
def lambda_handler(event, context):
    print(f"event {event}") # debug print
    # verify the signature
    try:
        verify_signature(event)
    except Exception as e:
        print("not authorized")
        #raise Exception(f"[UNAUTHORIZED] Invalid request signature: {e}")
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
    
    
    http = urllib3.PoolManager()
    
    #acknowledge the interaction
    interaction_id = body.get('id')
    interaction_token = body.get('token')
    response_url = f"https://discord.com/api/v8/interactions/{interaction_id}/{interaction_token}/callback"
    ack_object = json.dumps({"type": 4, "data":{"content":"instruction received!"}}) .encode('utf-8')
    r = http.request('POST', response_url, headers={'Content-Type': 'application/json'}, body=ack_object)
    
    #send the webhook
    blep_object = json.dumps({
        "username": "administratum_test",
        "avatar_url": "https://logos-download.com/wp-content/uploads/2016/02/warhammer-40000-and_bird_logo.png",
        "embeds":[
        {"image":{"url":"https://dtrpg-public-files.s3.us-east-2.amazonaws.com/images/54/65872.jpg"}}
        ]
        }).encode('utf-8')
    r = http.request('POST', WEBHOOK, headers={'Content-Type': 'application/json'}, body=blep_object)
   
   
    #API call complete
    return {
              "isBase64Encoded": False,
              "statusCode": 200,
              "body": "Action completed",
              "headers": {
                "content-type": "application/json"
              }
            }

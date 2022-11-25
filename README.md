# AdministratumBot
Serverless AWS Discord bot (with Dark Heresy in mind)

# Status
A chain of 3 Lambdas. An initial Auth function verifies the request. If authorised the details are passed to the GetWebhook function which tries to identify if a webhook URL already exists for the given Channel and Application, and if not creates one. Once the appropriate webhook details are identified these (along with the original request) are passed to the SendWebhook function which passes the requested message to the channel.

# Local Debug
Requirements: PyCharm (I guess), Docker, AWS SAM CLI

Config files (for some at least) are already created in the /Lambda/RunConfigurations/ directory, edit these as appropriate for your own settings (ex. altering S3 bucket names, app IDs, keys, etc)

**NOTE:** the Auth function can't be run locally until I figure out WTF to do with the PyNaCl layer

# Deploying to Discord

* In the Discord developer portal navigate to Applications then Create New Application
* On the General screen take a not of the App ID and Public Key
* On the Bot screen take a note of the Token 
* Deploy to AWS (see the section below) with the IDs/tokens/etc you noted above
* Upload your image files to a "Resources/" directory on the S3 created during AWS deployment... but make sure the file names are in lower case, the file types are in uppre case, and they're all .PNG files (I'm sorry! I promise I'll fix this!)
* Open the AWS Console, go to Lambdas, and find the RegisterResourceFunction Lambda
* In that function run (can use "Test" and a blank event)
* in the AWS Console go to API Gateway, find the deployed API, go to Stages, open the "test", navigate down to "/Administratum POST" and copy the Invoke URL
* Return to the Discord developer portal, go to your Application on the General Information screen and paste the URL into the "Interactions Endpoint URL"
* Go to Oauth2 then General and put the same URL in as the redirect URL
* Under OAuth2 go to URL Generator. Select "applications.commands"and "bot" in the top set, then "send messages" and "manage webhooks" in the bottom set
* Visit the generated link and authorise the application to connect to your server

# Deploying to AWS
Requirements: AWS SAM CLI, Application and Bot registered in Discord

This application is deployed via the template.yaml file in the root folder. 

Before deploying update the Parameters section with the required values for your deployment. This will require having already registered the application and bot with Discord via the Developer portal in order to generate the appropriate IDs, keys, etc.

Ensure all is up-to-date and use the AWS SAM CLI to build and run locally within the AdministratumBot top directory:
* sam build
* sam deploy --guided --profile YourSavedAWSCredentialsProfile --no-fail-on-empty-changeset
* roll back auth function to 3.8 in the AWS console (temp fix for my laziness)

After that note the POST endpoint from API Gateway and update the Interactions Endpoint URL under the Applications section of the Discord Developer Portal. If set up correctly this will accept the URL.

Still in the Developer Portal go to the OAuth2 section. Paste the POST endpoint under the Redirect URL. Enable the "application.commands" and "bot" scopes, then "Manage Webhooks" and "Send Messages" bot permissions. Open the generated URL and follow the prompts to add the application to your channel.

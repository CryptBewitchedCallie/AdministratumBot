# AdministratumBot
Serverless AWS Discord bot (with Dark Heresy in mind)

# Status
A chain of 3 Lambdas. An initial Auth function verifies the request. If authorised the details are passed to the GetWebhook function which tries to identify if a webhook URL already exists for the given Channel and Application, and if not creates one. Once the appropriate webhook details are identified these (along with the original request) are passed to the SendWebhook function which passes the requested message to the channel.

# Local Debug
Requirements: PyCharm (I guess), Docker, AWS SAM CLI

Config files (for some at least) are already created in the /Lambda/RunConfigurations/ directory, edit these as appropriate for your own settings (ex. altering S3 bucket names, app IDs, keys, etc)

**NOTE:** the Auth function can't be run locally until I figure out WTF to do with the PyNaCl layer

# Deploying to AWS
Requirements: AWS SAM CLI, Application and Bot registered in Discord

This application is deployed via the template.yaml file in the root folder. 

Before deploying update the Parameters section with the required values for your deployment. This will require having already registered the application and bot with Discord via the Developer portal in order to generate the appropriate IDs, keys, etc.

Ensure all is up-to-date and run the build and deploy Github action, or use the AWS SAM CLI to build and run loclly.

After that note the POST endpoint from API Gateway and update the Interactions Endpoint URL under the Applications section of the Discord Developer Portal. If set up correctly this will accept the URL.

Still in the Developer Portal go to the OAuth2 section. Paste the POST endpoint under the Redirect URL. Enable the "application.commands" and "bot" scopes, then "Manage Webhooks" and "Send Messages" bot permissions. Open the generated URL and follow the prompts to add the application to your channel.
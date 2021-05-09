# AdministratumBot
Serverless AWS Discord bot (with Dark Heresy in mind)

# Status
A chain of 3 Lambdas. An initial Auth function verifies the request. If authorised the details are passed to the GetWebhook function which tries to identify if a webhook URL already exists for the given Channel and Application, and if not creates one. Once the appropriate webhook details are identified these (along with the original request) are passed to the SendWebhook function which passes the requested message to the channel.

# Local Debug
Requirements: PyCharm (I guess), Docker, AWS CLI

Config files (for some at lest) are already created in the /Lambda/RunConfigurations/ directory, edit these as appropriate for your own settings (ex. altering S3 bucket names, app IDs, keys, etc)

**NOTE:** the Auth function can't be run locally until I figure out WTF to do with the PyNaCl layer
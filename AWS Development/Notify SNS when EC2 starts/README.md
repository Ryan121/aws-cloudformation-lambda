# Requirement
There is a requirement to know when instances are started to build AMIs. Thus, when an instance is spun up to build an AMI, send a
SNS notification to the subscribed users.

# Solution
A CloudFormationo template was created to deploy an S3 bucket, CloudTrail trail, SQS queue, , EventBridge rule, SNS topic and Lambda function to detect packer builds, notify subsribers to the SNS topic of when an EC2 instance is spun up to build a new image, when the image is being created and when the build EC2 instance is terminated. When terminating the instance, the id of AMI due to be created is checked to ensure it exists and the user is notified if the build was
successful/unsuccessful.

An S3 bucket was created to store CloudTrail logs. Logs are retained for 7 days.
A CloudTrail trail was created to log AWS API calls
An EventBridge rule was created to invoke a Lambda function when certain API calls are made
The lambda function pushes messages to SNS to notify the status of the AMI creation process
An SQS queue was utilised to persist the AMI id of the image being created and published within the Lambda function
Finally, the SQS message is deleted by the Lambda when the TerminateInstances API call is made by a packer build when 
it matches an exisiting (just built) AMI within the account.


# Requirement
There is a need to notify users when new images are released into production. 
This solution requires the pool of users to be members of the same teams channel to receive notifications pushed to that channel via emails 
or a webhook. Both methods have been configured within the Lambda solution, select the best based on the security constraints.
Prior to use, also change the subscription email address in the CloudFormation template to match that of the selected teams channel and/or edit the 
webook url within the Lambda function to match the webhook generated within the selected teams channel.
Also edit either the email or webhook response email to contain the triggering event information (e.g. Image info). They both currently contain placeholder
text for testing.

# Solution
A lambda function has been created in Python that send teams notifications via a webhook or SNS notifications
The function logs message state in Cloudwatch and returns a successful or unsuccssful status code.
The lambda function was integrated into a Cloudformation template for deployment.
The SNS Topic is deployed within CloudFormation.

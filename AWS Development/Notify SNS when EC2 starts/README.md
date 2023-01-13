# Requirement
There is a requirement to know when instances are started to build AMIs. Thus, when an instance is spun up to build an AMI, send a
SNS notification to the subscribed users.

# Solution
A lambda function has been created in Python that deletes all stale instance or volume based snapshots
The function takes a single payload object, 'age', which refers to the  minimum age (in days) of snapshots that require deletion.
The payload format is {"age": "7"}. This example deletes all snapshots that are not associated with any AMIs that are 7 days old or older
The function logs all deleted snapshots in Cloudwatch and returns a successful or unsuccssful status code.
The lambda function was integrated into a Cloudformation template for deployment.

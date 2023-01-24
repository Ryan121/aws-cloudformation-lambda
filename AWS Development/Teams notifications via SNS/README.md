# Requirement
There is a need to delete any snapshots that don't have an associated AMI or that are older than X days old

# Solution
A lambda function has been created in Python that deletes all stale instance or volume based snapshots
The function takes a single payload object, 'age', which refers to the  minimum age (in days) of snapshots that require deletion.
The payload format is {"age": "7"}. This example deletes all snapshots that are not associated with any AMIs that are 7 days old or older
The function logs all deleted snapshots in Cloudwatch and returns a successful or unsuccssful status code.
The lambda function was integrated into a Cloudformation template for deployment.

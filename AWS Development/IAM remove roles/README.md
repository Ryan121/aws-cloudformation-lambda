# Requirement
Each time packer creates a new instance, it's also creates a IAM role. These roles sometimes get left if the AMI build process fails.
A Lambda function is required to clean up left over packer roles and their inline policies.
Role and name format: packer-6182950d-0f0f-1300-4508-205e0346beca.
The lambda function must be written in Python using the Boto3 library for API calls and should be able to be triggered by an Eventbridge rule but should be source agnostic.
The Lambda function needs to be installable from a CloudFormation template with the code in-line (not as a zip file).

# Solution
A lambda function has been created in Python that deletes all stale IAM roles specific to the packer AMI build process.
The function identifies the stale roles by looking for the "packer-" string within IAM roles.
Once a role is identified, the policies attached to the role are removed, the instance profile is removed and deleted, and the role is deleted. The function repeats this for all identifed roles that meet the required condition.
The function logs all deleted roles in Cloudwatch and returns a successful or unsuccssful status code.
The lambda function was integrated into a Cloudformation template for deployment.

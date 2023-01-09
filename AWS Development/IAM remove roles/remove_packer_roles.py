import logging
import boto3
from datetime import datetime, timezone

# Packer role naming convention
# packer-6182950d-0f0f-1300-4508-205e0346beca
name_conv = "packer-"

# IAM  boto3 client
client = boto3.client('iam')

# A list of all IAM roles
roles = client.list_roles()
Role_list = roles['Roles']

# Current date and time
current_datetime = datetime.now(timezone.utc)


def lambda_handler(event, context):

    # A variable to count the number of roles removed
    del_role_count = 0

    try:
        # Iterate through the list of roles
        for role_key in Role_list:

            # Get role name as a string
            role_name = role_key['RoleName']
            # role_arn = role_key['Arn']

            # Get role name object
            role = client.get_role(RoleName=role_name)['Role']

            # Check if the packer- naming convention is in the role name
            if name_conv in role_name:
                # Check the last time the role was used
                last_used = role.get('RoleLastUsed', {}).get('LastUsedDate')

                # Get all attached policies in account
                policy_paginator = client.get_paginator('list_attached_role_policies')

                # Initialise list for the attached policies specific the role of interest
                role_policy_arn = []

                # Iterate through attached policies and append to list
                for response in policy_paginator.paginate(RoleName=role_name):

                    # Get attached policies
                    att_policies = response.get('AttachedPolicies')
                    for i in range(0, len(response.get('AttachedPolicies'))):
                        role_policy_arn.append(att_policies[i]['PolicyArn'])

                    # Check if an instance profile exists for the role
                    response = client.list_instance_profiles_for_role(
                        RoleName=role_name,
                    )
                    att_instance_profiles = response.get('InstanceProfiles')

                    # Detach all policies from role
                    for idx, policy_no in enumerate(role_policy_arn):
                        client.detach_role_policy(
                            PolicyArn=role_policy_arn[idx],
                            RoleName=role_name
                        )

                    # Remove role from instance profile and delete Instance Profile
                    # If an instance profile exists
                    if len(att_instance_profiles) > 0:
                        client.remove_role_from_instance_profile(
                            InstanceProfileName=role_name,
                            RoleName=role_name
                        )

                        response = client.delete_instance_profile(
                            InstanceProfileName=role_name
                        )

                    # Delete role
                    response = client.delete_role(
                        RoleName=role_name,
                    )
                    # Delete Instance Profile

                    logging.info(f'The role: {role_name}, last used: {last_used}, has been deleted.')
                    print(f'The role: {role_name}, last used: {last_used}, has been deleted.')

                del_role_count += 1

        log = f'A total of {del_role_count} packer roles were removed at {current_datetime}.'
        logging.info(log)
        print(log)
        return {
            'statusCode': 201,
            'body': 'Function run successfully. Please see logs for more details.'
        }

    except Exception as e:
        logging.error(e)
        return {
            'statusCode': 501,
            'body': '{"status":"Function error!"}'
        }


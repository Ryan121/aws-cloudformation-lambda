import boto3

# Key variables
ec2_instance_name = "my-ec2-instance-rs"
table_name = "LambdaTable"

# Region
region = 'eu-west-2'

# Resources
ec2 = boto3.client('ec2', region_name=region)
dynamodb = boto3.resource('dynamodb', region_name=region)


def lambda_handler(event, context):

    reservations = ec2.describe_instances(Filters=[
    {
        "Name": "instance-state-name",
        "Values": ["running", "stopped"],
    }
    ]).get("Reservations")
    print('reservations', reservations)

    table = dynamodb.Table(table_name)
    table_response = table.scan()
    data = table_response['Items']
    print('table data', data)

    for reservation in reservations:
        for instance in reservation["Instances"]:
            print('The EC2 name: ', instance["Tags"][0]['Value'])
            print('The EC2 state: ', instance["State"]['Name'])

            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]

            if instance["State"]['Name'] == "running":

                # Only get IP's if the instance is running
                public_ip = instance["PublicIpAddress"]
                private_ip = instance["PrivateIpAddress"]
                print(f"Instance running with: {instance_id}, {instance_type}, {public_ip}, {private_ip}")
                
                db_response = table.put_item(
                Item={
                    'Event': 'EC2 status - Lambda',
                    'LogMessage': f'The Lambda function was ran & the instance: {str(instance_id)}, is still running!',
                })

            elif instance["State"]['Name'] == "stopped":

                print(f"Instance with: {instance_id}, {instance_type}")

                if instance["Tags"] is not None:
                    if instance["Tags"][0]['Value'] == ec2_instance_name:
                        ec2.start_instances(InstanceIds=[instance_id])
                        status_string = f'Started EC2 instance, ID: {str(instance_id)}, Name: {ec2_instance_name}'
                        print(status_string)
                        # print('Lambda function created and ran!')
                        db_response = table.put_item(
                            Item={
                                'Event': 'EC2 status',
                                'LogMessage': status_string,
                            })
                        print('Dynamo DB response:', db_response)


    return 'Lambda Ran Successfully!'

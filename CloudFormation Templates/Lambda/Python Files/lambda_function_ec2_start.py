import boto3

# Region
region = 'eu-west-2'
# instances = ['i-06c71e6cfafe1cf54']

# Resources
ec2 = boto3.client('ec2', region_name=region)

reservations = ec2.describe_instances(Filters=[
    {
        "Name": "instance-state-name",
        "Values": ["running", "stopped"],
    }
]).get("Reservations")
print('reservations', reservations)

dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table('LambdaTable_prod')


def lambda_handler(event, context):
    
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            public_ip = instance["PublicIpAddress"]
            private_ip = instance["PrivateIpAddress"]
            print(f"{instance_id}, {instance_type}, {public_ip}, {private_ip}")
            
            print(instance["Values"])
            
            if instance["Values"] != "started":
                
                if instance["Tags"] is not None:
                    for tags in instance["Tags"]:
                        if tags["Key"] == 'Name':
                            instancename = tags["Value"]
                            print('Instance Name:', instancename)
                            if instancename == "my-ec2-instance-rs":
                                # if INPUT == 'start':
                                # Start by tag name
                                ec2.start_instances(InstanceIds=instance_id)
                                print('Started instance: ' + str(instance_id))
                                print('Lambda function created and ran!')
                                # elif INPUT == 'stop':
                                    # Start by tag name
                                # ec2.stop_instances(InstanceIds=instance_id)
                                # print('Started instance: ' + str(instance_id))
                                # print('Lambda function created and ran!')
                            
                                # out_reservations = ec2.describe_instances(Filters=[{"Name": "example_ec2"}]).get("Reservations")
                                
                                db_response = table.put_item(
                                Item={
                                    'id': 1,
                                    'title': 'EC2 status',
                                    'content': f'{out_reservations}',
                                })
                                print('Dynamo DB response:', db_response)
                                return 'Lambda Ran Successfully!'
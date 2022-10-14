import boto3

ec2_client = boto3.client("ec2", region_name="us-west-2")
reservations = ec2_client.describe_instances(Filters=[
    {
        "Name": "instance-state-name",
        "Values": ["running"],
    }
]).get("Reservations")

for reservation in reservations:
    for instance in reservation["Instances"]:
        instance_id = instance["InstanceId"]
        instance_type = instance["InstanceType"]
        public_ip = instance["PublicIpAddress"]
        private_ip = instance["PrivateIpAddress"]
        print(f"{instance_id}, {instance_type}, {public_ip}, {private_ip}")

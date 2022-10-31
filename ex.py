import boto3
from datetime import datetime, timedelta
import time

# Key variables
ec2_instance_name = "my-ec2-instance-rs"
table_name = "LambdaTable"

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

# if int(len(reservations)) == 0:
#     reservations = ec2.describe_instances(Filters=[
#         {
#             "Name": "instance-state-name",
#             "Values": ["stopped"],
#         }
#     ])
#     print('reservations', reservations)
#
dynamodb = boto3.resource('dynamodb', region_name=region)
table = dynamodb.Table(table_name)
table_response = table.scan()
data = table_response['Items']
print('table data', data)
#
#
# client = boto3.client('logs')
# log_group = '/aws/lambda/RSEC2Lambda'
#
# ## For the latest
# stream_response = client.describe_log_streams(
#     logGroupName=log_group,  # Can be dynamic
#     orderBy='LastEventTime',  # For the latest events
#     limit=1  # the last latest event, if you just want one
# )
# print('stream response', stream_response)
#
# latestlogStreamName = stream_response["logStreams"][0]["logStreamName"]
# print('latestlogStreamName', latestlogStreamName)
#
# response = client.get_log_events(
#     logGroupName=log_group,
#     logStreamName=latestlogStreamName,
#     startTime=12345678,
#     endTime=12345678,
# )
# print('response', response)
#
# ## For more than one Streams, e.g. latest 5
# stream_response = client.describe_log_streams(
#     logGroupName=log_group,  # Can be dynamic
#     orderBy='LastEventTime',  # For the latest events
#     limit=5
# )
# print('Next Stream Response', stream_response["logStreams"])
# for log_stream in stream_response["logStreams"]:
#     latestlogStreamName = log_stream["logStreamName"]
#     print('Log stream list', latestlogStreamName)
#
#     response = client.get_log_events(
#         logGroupName=log_group,
#         logStreamName=latestlogStreamName,
#         startTime=int((datetime.today() - timedelta(weeks=5)).timestamp()),
#         endTime=int(datetime.now().timestamp()),
#     )
#     print('log list response', response)
#     ## For example, you want to search "ClinicID=7667", can be dynamic
#
#     for event in response["events"]:
#         print('the big event', event)
#         if event["message"] == "Lambda function created and ran!":
#             print(event["message"])
# elif event["message"]["username"] == "simran+test@example.com":
#     print(event["message"])


# start_query_response = client.start_query(
#     logGroupName=log_group,
#     startTime=int((datetime.today() - timedelta(weeks=5)).timestamp()),
#     endTime=int(datetime.now().timestamp()),
#     queryString=query,
# )
#
# print('client', client)

# for reservation in reservations:
#     for instance in reservation["Instances"]:
#         print('The EC2 name: ', instance["Tags"][0]['Value'])
#         print('The EC2 state: ', instance["State"]['Name'])
#
#         instance_id = instance["InstanceId"]
#         instance_type = instance["InstanceType"]
#
#         if instance["State"]['Name'] == "running":
#
#             # Only get IP's if the instance is running
#             public_ip = instance["PublicIpAddress"]
#             private_ip = instance["PrivateIpAddress"]
#             print(f"Instance running with: {instance_id}, {instance_type}, {public_ip}, {private_ip}")
#
#         elif instance["State"]['Name'] == "stopped":
#
#             print(f"Instance with: {instance_id}, {instance_type}")
#
#             if instance["Tags"] is not None:
#                 if instance["Tags"][0]['Value'] == ec2_instance_name:
#                     ec2.start_instances(InstanceIds=[instance_id])
#                     status_string = f'Started EC2 instance, ID: {str(instance_id)}, Name: {ec2_instance_name}'
#                     print(status_string)
#                     # print('Lambda function created and ran!')
#                     db_response = table.put_item(
#                         Item={
#                             'Event': 'EC2 status',
#                             'LogMessage': status_string,
#                         })
#                     print('Dynamo DB response:', db_response)

        # if instance["State"]['Name'] == "stopped":
        #
        #
        #         for tags in instance["Tags"]:
        #             if tags["Key"] == 'Name':
        #                 instancename = tags["Value"]
        #                 print('Instance Name:', instancename)
        # if instancename == "example_ec2":
        #
        #     if INPUT == 'start':
        #         # Start by tag name
        #         ec2.start_instances(InstanceIds=instance_id)
        #         print('Started instance: ' + str(instance_id))
        #         print('Lambda function created and ran!')
        #     elif INPUT == 'stop':
        #         # Start by tag name
        #         ec2.stop_instances(InstanceIds=instance_id)
        #         print('Started instance: ' + str(instance_id))
        #         print('Lambda function created and ran!')
        #
        #     out_reservations = ec2.describe_instances(Filters=[{"Name": "example_ec2"}]).get(
        #         "Reservations")
        #
        #     return 'Lambda Ran Successfully!'

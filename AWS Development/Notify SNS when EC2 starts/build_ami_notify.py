import boto3
import logging
import json
from datetime import datetime, timezone


def lambda_handler(event, context):
    # Initialise logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Current date and time
    datetime_now = datetime.now(timezone.utc)

    try:
        # Extract Cloudwatch event details
        # trigger_name = event['detail']['eventName']
        # trigger_user = event['detail']['userIdentity']['userName']
        # trigger_time = event['detail']['eventTime']
        # trigger_region = event['detail']['awsRegion']
        # trigger_eventID = event['detail']['eventID']
        # logger.info(f"User: { trigger_user }, Event name: { trigger_name }, Event ID: { trigger_eventID }, "
        #             f"AWS Region: { trigger_region }, Event time: { trigger_time }")
        # print(trigger_eventID)

        # Initialise Cloudtrail client
        trail_client = boto3.client('cloudtrail')

        # Extract trail events
        paginator = trail_client.get_paginator('lookup_events')

        # Initialise SNS client
        sns_client = boto3.client('sns')

        # Get the existing topic name created by CloudFormation using the create_topic method
        topic = sns_client.create_topic(Name='packer-image-build-topic')
        topic_arn = topic['TopicArn']

        # Initialise EC2 client
        ec2_client = boto3.client('ec2')

        # Initialise AMI variable
        image_ami = ""

        flag = False
        while not flag:
            # Extract all trail events that match the cloudwatch trigger event
            page_iterator = paginator.paginate(
                LookupAttributes=[
                    {'AttributeKey': 'EventId', 'AttributeValue': '0bf0d52d-ccb8-4e1f-a8ad-5eb3a13445e8'}])

            for page in page_iterator:
                for ind_ev in page['Events']:
                    print(ind_ev['EventId'])
                    if ind_ev['EventId'] == trigger_eventID:
                        flag = True

        for page in page_iterator:
            for ind_event in page['Events']:

                if ind_event["EventId"] == trigger_eventID:
                    for res_name in ind_event["Resources"][:]:
                        if trigger_name == "RunInstances" and res_name['ResourceType'] == 'AWS::EC2::Instance':
                            sns_message = f"An EC2 instance ({res_name['ResourceName']}) was started by {trigger_user} " \
                                          f"at {trigger_time} in {trigger_region}. Installing new image requirements... "
                            print(sns_message)
                            logger.info(sns_message)
                            message = {"Packer Build Update": sns_message}
                            response = sns_client.publish(
                                TargetArn=topic_arn,
                                Message=sns_message
                            )
                            break

                        elif trigger_name == "StopInstances" and res_name['ResourceType'] == 'AWS::EC2::Instance':
                            sns_message = f"Shutting down  {res_name['ResourceName']}."
                            print(sns_message)
                            logger.info(sns_message)
                            message = {"Packer Build Update": sns_message}
                            response = sns_client.publish(
                                TargetArn=topic_arn,
                                Message=sns_message
                            )
                            break

                        elif trigger_name == "CreateImage" and res_name['ResourceType'] == 'AWS::EC2::Ami':
                            image_ami = res_name['ResourceName']
                            sns_message = f"Creating new image ({res_name['ResourceName']})."
                            print(sns_message)
                            logger.info(sns_message)
                            message = {"Packer Build Update": sns_message}
                            response = sns_client.publish(
                                TargetArn=topic_arn,
                                Message=sns_message
                            )
                            break

                        elif trigger_name == "TerminateInstances" and res_name['ResourceType'] == 'AWS::EC2::Instance':
                            response = ec2_client.describe_images()
                            for image in response['Images']:
                                if image_ami == image['ImageId']:
                                    sns_message = f"New AMI with id: {image_ami} was successfully built." \
                                                  f"Terminating build instance:  {res_name['ResourceName']}."
                                    print(sns_message)
                                    logger.info(sns_message)
                                    message = {"Packer Build Update": sns_message}
                                    response = sns_client.publish(
                                        TargetArn=topic_arn,
                                        Message=sns_message
                                    )
                                    break
                                else:
                                    sns_message = f"Image creation for {image_ami} failed." \
                                                  f"Terminating build instance:  {res_name['ResourceName']}."
                                    print(sns_message)
                                    logger.info(sns_message)
                                    message = {"Packer Build Update": sns_message}
                                    response = sns_client.publish(
                                        TargetArn=topic_arn,
                                        Message=sns_message
                                    )
                                    break
                            break

        logger.info(f"The function ran successfully at {datetime_now.now()}.")
        return {
            'statusCode': 201,
            'body': 'Function run successfully. Please see logs for more details.'
        }

    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 501,
            'body': '{"status":"Function error!"}'
        }

lambda_handler([],[])

import boto3
import logging
from datetime import datetime, timezone
import json


def lambda_handler(event, context):

    # Initialise logging
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Current date and time
    datetime_now = datetime.now(timezone.utc)

    # Packer build string
    userAgent_string = "packer-"

    try:
        # Get the source IP of the user and build agent
        sourceIP = event['detail']['sourceIPAddress']
        userAgent = event['detail']['userAgent']

        # Run when Cloudwatch triggers a packer initiated image build
        # With the RunIstnaces, CreateImage and TerminateInstances API Calls via CloudTrail
        if userAgent_string in userAgent:
            # Extract Cloudwatch event details
            trigger_name = event['detail']['eventName'] # Name of the API Call
            trigger_user = event['detail']['userIdentity']['userName'] # User who initiated the packer build
            trigger_time = event['detail']['eventTime'] # Build start time
            trigger_region = event['detail']['awsRegion'] # AWS Region of API call
            # trigger_eventID = event['detail']['eventID'] # Event ID
            logger.info(f"User: {trigger_user}, Event name: {trigger_name}, Event ID: , "
                        f"AWS Region: {trigger_region}, Event time: {trigger_time}") # Log key details

            # Initialise SNS client
            sns_client = boto3.client('sns')

            # Get the existing topic name created by CloudFormation using the create_topic method
            topic = sns_client.create_topic(Name='packer-image-build-topic')
            topic_arn = topic['TopicArn']

            # Initialise EC2 client
            ec2_client = boto3.client('ec2')

            # Initialise SQS client
            sqs_client = boto3.client('sqs')
            sqs_queue = sqs_client.get_queue_url(
                QueueName="packer-image-build-queue",
            )

            # Get SQS url
            sqs_queue_url = sqs_queue["QueueUrl"]

            # Initialise build instance ID
            instance_id = ""

            # Initialise AMI variable
            image_ami = ""

            # Check API call
            if trigger_name == "RunInstances":

                # Extract EC2 instance building image
                instance_id = event['detail']['responseElements']['instancesSet']['items'][0]['instanceId']

                # Notify subscribers of EC2 start
                sns_message = f"An packer build instance ({instance_id}) was started by {trigger_user} " \
                              f"at {trigger_time} in the {trigger_region} region. Installing new image requirements..."

                # Log message
                logger.info(sns_message)
                
                # Publish message to topic
                response = sns_client.publish(
                    TargetArn=topic_arn,
                    Message=sns_message
                )

            # # StopInstances API call removed 
            # elif trigger_name == "StopInstances":
            #     instance_id = event['detail']['responseElements']['instancesSet']['items'][0]['instanceId']

            #     sns_message = f"The packer build EC2 instance ({instance_id}) was stopped " \
            #                   f" {trigger_user}. "
            #     print(sns_message)
            #     logger.info(sns_message)
            #     response = sns_client.publish(
            #         TargetArn=topic_arn,
            #         Message=sns_message
            #     )

            elif trigger_name == "CreateImage":
                
                # Extract EC2 instance building image
                instance_id = event['detail']['requestParameters']['instanceId']
                
                # Extract image AMI
                image_ami = event['detail']['responseElements']['imageId']

                # Notify subscribers of image build
                message = f"Image build requirements installed. EC2 instance {instance_id} was stopped." \
                          f"Creating new image for {trigger_user} with ID: {image_ami}."

                logger.info(message)

                sns_client.publish(
                    TargetArn=topic_arn,
                    Message=message
                )

                # Push message to SQS containing user IP, name and the image AMI for future reference
                sqs_message = {f"{sourceIP} - {trigger_user}": f"{image_ami}"}
                sqs_client.send_message(
                    QueueUrl=sqs_queue_url,
                    MessageBody=json.dumps(sqs_message)
                )

            elif trigger_name == "TerminateInstances":

                # Extract EC2 instance building image
                instance_id = event['detail']['responseElements']['instancesSet']['items'][0]['instanceId']

                # Get messages from SQS
                response = sqs_client.receive_message(
                    QueueUrl=sqs_queue_url,
                    MaxNumberOfMessages=10,
                    WaitTimeSeconds=3,
                )

                # print(f"Number of messages received: {len(response.get('Messages', []))}")

                # Access messages if they exist
                if len(response.get('Messages', [])) > 0:

                    for message in response.get("Messages", []):

                        message_dict = json.loads(message["Body"])
                        
                        # Get message handle
                        receipt_handle = message['ReceiptHandle']
                        # print(message["Body"])
                        # print(f"Message body: {json.loads(message_body)}")
                        # print(f"Receipt Handle: {message['ReceiptHandle']}")
                        
                        # Put keys into listfor iteration
                        keys = list(message_dict.keys())

                        for key in keys:
                            # If the user IP and username matches a key stored in SQS
                            if key == f"{sourceIP} - {trigger_user}":
                                
                                try:
                                    # Validate that the AMI string stored in SQS actually exists
                                    response = ec2_client.describe_images(ImageIds=[message_dict[key]])

                                    sns_message = f"New AMI with id: {message_dict[key]} was successfully built by {trigger_user}. " \
                                                  f"Terminating build instance:  {instance_id}."

                                    logger.info(sns_message)

                                    response = sns_client.publish(
                                        TargetArn=topic_arn,
                                        Message=sns_message
                                    )
                                # Log error if AMI does not exist
                                except Exception as e:
                                    logger.error(f"The AMI: {message_dict[key]}, does not exist")
                                    sns_message = f"Build failed for {trigger_user}." \
                                                  f"Terminating build instance: {instance_id}. Better luck next time :)"
                                    response = sns_client.publish(
                                        TargetArn=topic_arn,
                                        Message=sns_message
                                    )

                                # Delete the SQS message as the corresponding AMI has been built or failed
                                response = sqs_client.delete_message(
                                    QueueUrl=sqs_queue_url,
                                    ReceiptHandle=receipt_handle,
                                )
                                break

                            else:
                                sns_message = f"Build failed for {trigger_user}." \
                                              f"Terminating build instance: {instance_id}. Better luck next time :)"
                                logger.info(sns_message)
                                response = sns_client.publish(
                                    TargetArn=topic_arn,
                                    Message=sns_message
                                )
                else:
                    sns_message = f"Build failed for {trigger_user}." \
                                  f"Terminating build instance: {instance_id}. Better luck next time :)"
                    logger.info(sns_message)
                    response = sns_client.publish(
                        TargetArn=topic_arn,
                        Message=sns_message
                    )

            logger.info(f"The function ran by {trigger_user}, ran successfully at {datetime_now.now()}.")
        else:
            logger.info(f"The function ran at {datetime_now.now()}, however, a packer build was not detected.")
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

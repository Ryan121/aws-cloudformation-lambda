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

        

    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 501,
            'body': '{"status":"Function error!"}'
        }

import boto3
import logging
from datetime import datetime, timezone

# define the DynamoDB table that Lambda will connect to
# tableName = "lambda-apigateway"

# create the DynamoDB resource 
# dynamo = boto3.resource('dynamodb').Table(tableName)
# dynamo = boto3.client('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

print('Loading function')

def lambda_handler(event, context):


    # Current date and time
    datetime_now = datetime.now(timezone.utc)

    

    try:


        logger.info(f"An image build was started by packer () snapshots were deleted at { datetime_now.now() }.")
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


import boto3
import json
import logging

# define the DynamoDB table that Lambda will connect to
# tableName = "lambda-apigateway"

# create the DynamoDB resource 
# dynamo = boto3.resource('dynamodb').Table(tableName)
# dynamo = boto3.client('dynamodb')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

print('Loading function')

def lambda_handler(event, context):
    '''Provide an event that contains the following keys:

      - operation: one of the operations in the operations dict below
      - payload: a JSON object containing parameters to pass to the 
                 operation being performed
    '''

    tableName = "Movies"

    dynamo = boto3.resource('dynamodb').Table(tableName)
    x = 0
    # define the functions used to perform the CRUD operations
    def ddb_create(x):
        dynamo.put_item(**x)

    def ddb_read(x):
        dynamo.get_item(**x)

    def ddb_update(x):
        dynamo.update_item(**x)
        
    def ddb_delete(x):
        dynamo.delete_item(**x)

    def echo(x):
        return x

    logger.info(f"Initiating lambda...")

    try:

        operation = event['operation']
        logger.info(f"The operation of the request api call is: { operation }")

        operations = {
            'create': ddb_create,
            'read': ddb_read,
            'update': ddb_update,
            'delete': ddb_delete,
            'echo': echo,
        }

        if operation in operations:
            output = operations[operation](event.get('payload'))
            logger.info(f" { event['operation'] } operation successfully ran" )
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json"
                },
                "body": json.dumps({"message": output})
            }
        else:
            raise ValueError('Unrecognized operation "{}"'.format(operation))

    except Exception as e:
        logger.error(e)
        return {
            'statusCode': 501,
            'body': '{"status":"Function error!"}'
        }

lambda_handler({"operation": "create", "year":2011, "title":"Ironman"}, [])

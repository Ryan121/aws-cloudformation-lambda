import boto3

region = 'eu-west-2'
instances = ['i-06c71e6cfafe1cf54']
ec2 = boto3.client('ec2', region_name=region)

def lambda_handler(event, context):
    ec2.stop_instances(InstanceIds=instances)
    print('Stopped instance: ' + str(instances))
    print('Lambda function created and ran!')
    return 'success'
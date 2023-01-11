import boto3
import logging
from datetime import datetime, timezone


def lambda_handler(event, context):

    try:
        # Set the age in days of snapshots to remove
        delete_age = 0

        # The total number of deleted snapshots
        deleted_count = 0

        # Current date and time
        datetime_now = datetime.now(timezone.utc)

        # Initialise logging
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        logger.info("Event: %s" % (event,))
        logger.info("Context: %s" % (context,))

        # Set region to identify snapshots
        region = "us-east-1"

        # Initialise ec2 client in the specified region
        client = boto3.client('ec2', region_name=region)

        # Get snapshots created by the account owner
        snapshots = client.describe_snapshots(OwnerIds=['self'])

        # Describe the relevant snapshots
        for snapshot in snapshots['Snapshots']:
            # print('ID: ' + str(snapshot['SnapshotId']))
            # print('Volume: ' + str(snapshot['VolumeId']))
            # print('Size: ' + str(snapshot['VolumeSize']) + ' GiB')
            # print('Created: ' + str(snapshot['StartTime']))

            snapshot_age = (datetime_now - snapshot['StartTime']).days
            # print('Snapshot Age: ' + str(snapshot_age) + ' Days')
            # print('---------------------')

            # Check if the snapshot has associated AMI's
            image = client.describe_images(
                Filters=[
                    {'Name': 'block-device-mapping.snapshot-id', 'Values': [snapshot['SnapshotId']]}
                ]
            )

            # Get the number of associated AMI's
            no_of_associated_images = len(image['Images'])

            # Delete snapshots that are older than X days old & are not associated with any AMI's
            if snapshot_age >= delete_age and no_of_associated_images == 0:
                response = client.delete_snapshot(
                    SnapshotId=snapshot['SnapshotId'],
                    DryRun=False
                )

                # print(f"Deleted snapshot: {str(snapshot['SnapshotId'])}, of size: {str(snapshot['VolumeSize']) + ' GiB'},"
                #       f"associated with the volume: {str(snapshot['VolumeId'])}, that was {str(snapshot_age)} "
                #       f"days old.")
                logger.info(f"Deleted snapshot: {str(snapshot['SnapshotId'])}, of size: "
                            f"{str(snapshot['VolumeSize']) + ' GiB'},"
                            f"associated with the volume: {str(snapshot['VolumeId'])}, that was {str(snapshot_age)} "
                            f"days old.")
                deleted_count += 1

        # print(f"A total of {deleted_count} snapshots were deleted at { datetime_now }.")
        logger.info(f"A total of {deleted_count} snapshots were deleted at { datetime_now.now() }.")
        return {
            'statusCode': 201,
            'body': 'Function run successfully. Please see logs for more details.'
        }

    except Exception as e:
        logging.error(e)
        return {
            'statusCode': 501,
            'body': '{"status":"Function error!"}'
        }

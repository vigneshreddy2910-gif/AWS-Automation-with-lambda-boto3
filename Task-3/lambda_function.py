import boto3
import logging
from datetime import datetime, timezone

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ec2 = boto3.client("ec2")


def lambda_handler(event, context):
    try:
        logger.info("Lambda execution started")
        logger.info(event)

        instance_id = event["detail"]["instance-id"]
        logger.info(f"Instance ID: {instance_id}")

        response = ec2.describe_instances(
            InstanceIds=[instance_id]
        )
        logger.info("Instance does exist.")

        launch_datetime = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        ec2.create_tags(
            Resources=[instance_id],
            Tags=[
                {
                    "Key": "LaunchDate",
                    "Value": launch_datetime
                },
                {
                    "Key": "Environment",
                    "Value": "Development"
                }
            ]
        )

        logger.info(f"Tags added successfully to {instance_id}")

        return {
            "statusCode": 200,
            "body": f"Successfully tagged {instance_id}"
        }

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")

        return {
            "statusCode": 500,
            "body": str(e)
        }
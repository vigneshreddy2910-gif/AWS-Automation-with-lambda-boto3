import os
import boto3
import logging
from datetime import datetime, timezone, timedelta

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event, context):
    bucket_name = os.environ.get("BUCKET_NAME")

    if not bucket_name:
        raise ValueError("Missing BUCKET_NAME environment variable.")

    time_value = int(os.environ.get("TIME_VALUE"))
    time_unit = os.environ.get("TIME_UNIT")

    if time_unit == "minutes":
        cutoff_date = datetime.now(timezone.utc) - timedelta(minutes=time_value)
    elif time_unit == "hours":
        cutoff_date = datetime.now(timezone.utc) - timedelta(hours=time_value)
    elif time_unit == "days":
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=time_value)
    else:
        raise ValueError("TIME_UNIT must be one of: minutes, hours, days")

    s3 = boto3.client("s3")

    logger.info(f"Bucket: {bucket_name}")
    logger.info(f"Deleting objects older than {time_value} {time_unit}")

    paginator = s3.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name)

    delete_keys = []

    for page in pages:
        for obj in page.get("Contents", []):
            if obj["LastModified"] < cutoff_date:
                delete_keys.append({"Key": obj["Key"]})

    deleted_objects_count = 0

    for i in range(0, len(delete_keys), 1000):
        response = s3.delete_objects(
            Bucket=bucket_name,
            Delete={"Objects": delete_keys[i:i + 1000]}
        )

        deleted_objects_count += len(response.get("Deleted", []))

    logger.info(f"Deleted {deleted_objects_count} object(s).")

    return {
        "statusCode": 200,
        "body": {
            "message": "S3 bucket cleanup completed.",
            "bucket": bucket_name,
            "deleted_objects_count": deleted_objects_count,
        },
    }
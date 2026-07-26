import boto3
import os
from datetime import datetime, timezone, timedelta

ec2 = boto3.client("ec2")

VOLUME_ID = os.environ["VOLUME_ID"]

RETENTION_DAYS = 30

def lambda_handler(event, context):

    snapshot = ec2.create_snapshot(
        VolumeId=VOLUME_ID,
        Description="Created by Lambda"
    )

    snapshot_id = snapshot["SnapshotId"]

    ec2.create_tags(
        Resources=[snapshot_id],
        Tags=[
            {
                "Key": "CreatedBy",
                "Value": "Lambda-Backup"
            }
        ]
    )

    print(f"Created Snapshot: {snapshot_id}")

    snapshots = ec2.describe_snapshots(
        OwnerIds=["self"],
        Filters=[
            {
                "Name": "tag:CreatedBy",
                "Values": ["Lambda-Backup"]
            }
        ]
    )["Snapshots"]

    cutoff = datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)

    for snap in snapshots:

        if snap["StartTime"] < cutoff:

            ec2.delete_snapshot(
                SnapshotId=snap["SnapshotId"]
            )

            print(f"Deleted Snapshot: {snap['SnapshotId']}")

    return {
        "statusCode": 200,
        "body": "Snapshot completed"
    }
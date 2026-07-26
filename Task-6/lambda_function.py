import boto3
import os
from botocore.exceptions import ClientError

s3 = boto3.client("s3")
sns = boto3.client("sns")

TOPIC_ARN = os.environ["TOPIC_ARN"]


def lambda_handler(event, context):

    buckets = s3.list_buckets()["Buckets"]

    public_found = False

    for bucket in buckets:

        bucket_name = bucket["Name"]

        print(f"Checking: {bucket_name}")

        is_public = False

        # Check Public Access Block
        try:
            pab = s3.get_public_access_block(Bucket=bucket_name)

            config = pab["PublicAccessBlockConfiguration"]

            if not all(config.values()):
                is_public = True

        except ClientError:
            pass

        # Check Bucket Policy
        try:
            policy = s3.get_bucket_policy_status(Bucket=bucket_name)

            if policy["PolicyStatus"]["IsPublic"]:
                is_public = True

        except ClientError:
            pass

        # Check ACL
        try:
            acl = s3.get_bucket_acl(Bucket=bucket_name)

            for grant in acl["Grants"]:

                grantee = grant.get("Grantee", {})

                if grantee.get("URI") == "http://acs.amazonaws.com/groups/global/AllUsers":

                    is_public = True

        except ClientError:
            pass

        if is_public:

            public_found = True

            print(f"PUBLIC: {bucket_name}")

            sns.publish(
                TopicArn=TOPIC_ARN,
                Subject="Public S3 Bucket Detected",
                Message=f"The bucket '{bucket_name}' appears to be publicly accessible."
            )

    if not public_found:

        print("No public buckets found.")

    return {
        "statusCode": 200,
        "body": "Audit completed."
    }
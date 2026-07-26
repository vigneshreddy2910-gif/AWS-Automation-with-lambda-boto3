# Task 6 – Audit S3 Buckets for Public Access and Notify

## Task Description

Amazon Simple Storage Service (Amazon S3) is widely used to store application data, backups, logs, and static website content. Since S3 buckets may contain sensitive information, accidental public exposure can lead to serious security risks.

This task automates the process of auditing all S3 buckets within an AWS account to identify buckets that are publicly accessible. The solution uses AWS Lambda together with the Boto3 SDK to inspect each bucket's Block Public Access configuration, Bucket Policy status, and Access Control List (ACL). Whenever a publicly accessible bucket is detected, an email notification is automatically sent using Amazon Simple Notification Service (Amazon SNS).

The Lambda function can also be scheduled using Amazon EventBridge to perform periodic security audits without requiring manual intervention.

---

# Objectives

- Audit every Amazon S3 bucket within the AWS account.
- Detect publicly accessible buckets.
- Verify the Block Public Access configuration.
- Verify the Bucket Policy status.
- Verify Bucket ACL permissions.
- Send an email notification through Amazon SNS whenever an insecure bucket is detected.
- Follow AWS security best practices by implementing a Least Privilege IAM Role and Policy.
- Demonstrate automated security auditing using AWS Lambda.

---

# Architecture

```text
                 Amazon EventBridge
                   (Scheduled Trigger)
                          │
                          ▼
                  AWS Lambda Function
                          │
                          ▼
                List All Amazon S3 Buckets
                          │
      ┌───────────────────┼───────────────────┐
      │                   │                   │
      ▼                   ▼                   ▼
Check Public       Check Bucket       Check Bucket
Access Block          Policy               ACL
      │                   │                   │
      └───────────────────┼───────────────────┘
                          ▼
            Is Bucket Publicly Accessible?
                    │              │
                  Yes              No
                    │              │
                    ▼              ▼
            Amazon SNS Topic    End Execution
                    │
                    ▼
          Email Notification Sent
```

---

# Prerequisites

Before implementing this task, ensure the following AWS resources are available.

- AWS Account
- Amazon S3
- Amazon SNS
- AWS Lambda
- IAM Role
- IAM Policy
- Amazon EventBridge
- Python 3.14 Runtime

---

# Step 1 – Create an Amazon SNS Topic

Navigate to

```
AWS Console
→ Amazon SNS
→ Topics
→ Create Topic
```

Configuration

| Property | Value |
|-----------|-------|
| Type | Standard |
| Name | S3PublicAudit |

Click **Create Topic**.

The SNS Topic will be responsible for delivering email notifications whenever the Lambda function detects a publicly accessible S3 bucket.

> **Screenshot**

<img width="1627" height="882" alt="Screenshot 2026-07-26 124647" src="https://github.com/user-attachments/assets/60cd4cfd-662d-4341-815f-efe4e92d6e47" />

---

# Step 2 – Subscribe an Email Endpoint

Open the SNS Topic created previously.

Navigate to

```
Create Subscription
```

Configuration

| Property | Value |
|-----------|-------|
| Protocol | Email |
| Endpoint | Your Email Address |

Click **Create Subscription**.

AWS sends a confirmation email to the specified email address.

Open the email and click **Confirm Subscription**.

Once confirmed, the subscription status changes from **Pending Confirmation** to **Confirmed**.

This email subscription will receive security alerts whenever the Lambda function detects a public S3 bucket.

> **Screenshot**

<img width="1571" height="668" alt="Screenshot 2026-07-26 124831" src="https://github.com/user-attachments/assets/6cb3de54-f3cf-4485-bade-9f64bd397f8a" />

<img width="1040" height="462" alt="Screenshot 2026-07-26 125107" src="https://github.com/user-attachments/assets/125b5ec0-810d-4c52-969f-9c4bc17e1c30" />

<img width="1450" height="467" alt="Screenshot 2026-07-26 125143" src="https://github.com/user-attachments/assets/906cf867-6f8a-4805-8389-12ff533f2518" />


---

# Step 3 – Create a Test Amazon S3 Bucket

Navigate to

```
AWS Console
→ Amazon S3
→ Create Bucket
```

Example Configuration

| Property | Value |
|-----------|-------|
| Bucket Name | public-audit-demo |
| Region | us-east-1 |

During bucket creation, disable **Block Public Access** so that the bucket can be configured for public access.

This intentionally insecure configuration is created only for testing purposes, allowing the Lambda function to successfully identify the bucket as publicly accessible.

After the bucket has been created, navigate to

```
Amazon S3
→ Your Bucket
→ Permissions
→ Bucket Policy
→ Edit
```

Copy and paste the bucket policy provided in this repository.

```
Task-6/bucketpolicy.json
```

Replace the placeholder bucket name in the policy with the name of your own bucket before saving the changes.

The bucket policy grants public read access to the bucket, allowing the Lambda function to verify that the bucket policy permits public access.

By combining a disabled Block Public Access configuration with a public bucket policy, the bucket satisfies the conditions required for testing the security audit performed by the Lambda function.

> **Note**

This configuration is intended only for demonstration and testing purposes. Once testing has been completed, the bucket should be secured by re-enabling Block Public Access and removing the public bucket policy.

> **Screenshot**

<img width="1012" height="892" alt="Screenshot 2026-07-26 131416" src="https://github.com/user-attachments/assets/31e38317-db53-47eb-84ee-22cd91a70259" />

<img width="1482" height="883" alt="Screenshot 2026-07-26 131519" src="https://github.com/user-attachments/assets/297a4f4e-3d3e-4b09-b191-464fd408516d" />

---

# Step 4 – Create the IAM Role

Navigate to

```
AWS Console
→ IAM
→ Roles
→ Create Role
```

Configuration

Trusted Entity

```
AWS Service
```

Service

```
Lambda
```

Provide an appropriate role name.

Example

```
S3PublicAuditRole
```

Click **Create Role**.

This IAM Role allows the Lambda function to securely communicate with Amazon S3, Amazon SNS, and CloudWatch Logs.

> **Screenshot**

<img width="1867" height="697" alt="Screenshot 2026-07-26 125250" src="https://github.com/user-attachments/assets/90f3bf81-42a4-4634-8207-e81b3b120d6f" />

<img width="1875" height="887" alt="Screenshot 2026-07-26 130040" src="https://github.com/user-attachments/assets/a778e65a-4282-4829-bfd2-8770630c88b0" />

---

# Step 5 – Create the IAM Policy

Attach a custom inline policy to the IAM Role created in the previous step.

The complete policy used in this implementation is available in this repository.

```
Task-6/s3auditrolepolicy.json
```

---

## Permissions Included

| Permission | Purpose |
|------------|----------|
| s3:ListAllMyBuckets | Lists every S3 bucket available in the AWS account. |
| s3:GetBucketPublicAccessBlock | Retrieves the Block Public Access configuration. |
| s3:GetBucketPolicyStatus | Determines whether a bucket policy allows public access. |
| s3:GetBucketAcl | Retrieves the bucket Access Control List (ACL). |
| sns:Publish | Publishes email notifications to the SNS Topic. |
| logs:CreateLogGroup | Creates a CloudWatch Log Group during the first execution. |
| logs:CreateLogStream | Creates a new execution log stream. |
| logs:PutLogEvents | Stores Lambda execution logs. |

---

## Why These Permissions Are Required

### s3:ListAllMyBuckets

Allows Lambda to retrieve every S3 bucket within the AWS account before beginning the audit.

---

### s3:GetBucketPublicAccessBlock

Retrieves the Block Public Access configuration for every bucket.

This allows Lambda to determine whether AWS protection against public access is enabled.

---

### s3:GetBucketPolicyStatus

Checks whether a bucket policy allows anonymous users to access bucket contents.

---

### s3:GetBucketAcl

Retrieves the Access Control List associated with each bucket.

The Lambda function uses this information to detect public read or write permissions.

---

### sns:Publish

Allows the Lambda function to send an email notification whenever a public bucket is detected.

---

### CloudWatch Permissions

These permissions allow AWS Lambda to automatically create execution logs that assist in monitoring and troubleshooting.

---

## Role of the IAM Policy

The IAM Policy grants only the permissions required to audit S3 bucket security and publish notifications through Amazon SNS.

Rather than granting administrative permissions, the policy follows the Principle of Least Privilege, ensuring that the Lambda function can perform only the operations necessary for the assignment.

> **Screenshot**

<img width="1867" height="877" alt="Screenshot 2026-07-26 125945" src="https://github.com/user-attachments/assets/a25813a5-f273-4d81-90b4-2d068376895c" />


---

# Step 6 – Create the Lambda Function

Navigate to

```
AWS Console
→ Lambda
→ Create Function
```

Configuration

| Property | Value |
|-----------|-------|
| Function Name | S3PublicAudit |
| Runtime | Python 3.14 |
| Architecture | x86_64 |
| Execution Role | Use Existing Role |

Select the IAM Role created previously.

Click **Create Function**.

> **Screenshot**

<img width="1640" height="857" alt="Screenshot 2026-07-26 130208" src="https://github.com/user-attachments/assets/87b3b91b-a469-4c05-835b-c33da08bd33a" />


---

# Step 7 – Configure Environment Variables

Navigate to

```
Configuration
→ Environment Variables
```

Create the following environment variable.

| Key | Value |
|------|-------|
| SNS_TOPIC_ARN | ARN of the SNS Topic |

Example

```
arn:aws:sns:us-east-1:123456789012:S3PublicAudit
```

The Lambda function reads the SNS Topic ARN dynamically and publishes notifications to the configured topic whenever a public bucket is detected.

Using environment variables instead of hardcoding resource identifiers improves portability and allows the same Lambda function to be deployed across multiple AWS environments.

> **Screenshot**

<img width="1562" height="402" alt="Screenshot 2026-07-26 130503" src="https://github.com/user-attachments/assets/fe20ce09-0b1a-45e7-b7d9-6eeebf3aa7fb" />


---

# Step 8 – Deploy the Lambda Code

Replace the default Lambda source code with the implementation provided in this repository.

```
Task-6/lambda_function.py
```

After replacing the code, click

```
Deploy
```

The deployed Lambda function performs the following operations:

- Retrieves all Amazon S3 buckets within the AWS account.
- Checks the Block Public Access configuration.
- Verifies the Bucket Policy status.
- Inspects the Bucket Access Control List (ACL).
- Identifies publicly accessible buckets.
- Publishes an email notification through Amazon SNS whenever an insecure bucket is detected.
- Displays the audit results in the Lambda execution report.

> **Screenshot**

<img width="1411" height="702" alt="Screenshot 2026-07-26 130618" src="https://github.com/user-attachments/assets/17098874-013f-4aab-ba88-661068dd72bb" />


---

# Step 9 – Verify the Lambda Function

Once the Lambda function has been deployed successfully, create a new Test Event to verify its execution.

Navigate to

```
Lambda
→ Test
→ Create New Test Event
```

Use the following sample event.

```json
{}
```

Since this Lambda function retrieves all Amazon S3 buckets directly from the AWS account, no custom event payload is required.

Save the event and click **Test**.

During execution, the Lambda function performs the following operations:

- Retrieves every Amazon S3 bucket within the AWS account.
- Checks the Block Public Access configuration of each bucket.
- Examines the Bucket Policy status.
- Inspects the Bucket Access Control List (ACL).
- Determines whether the bucket is publicly accessible.
- Publishes an email notification through Amazon SNS whenever a public bucket is detected.
- Displays the audit summary in the Lambda execution report.

A successful execution returns a response similar to:

```json
{
    "statusCode": 200,
    "body": "S3 bucket audit completed successfully."
}
```

> **Screenshot**

<img width="1452" height="825" alt="Screenshot 2026-07-26 131725" src="https://github.com/user-attachments/assets/4b91908c-6a2a-4790-b70e-280d11a2abc7" />


---

# Lambda Execution Report

The Lambda execution report provides detailed information regarding the execution of the function.

The report includes:

- Function Status
- Request ID
- Execution Duration
- Billed Duration
- Memory Allocation
- Memory Utilized
- Initialization Duration
- Names of audited S3 buckets
- Public bucket detection results
- Amazon SNS notification status

> **Screenshot**

<img width="1452" height="825" alt="Screenshot 2026-07-26 131725" src="https://github.com/user-attachments/assets/8abd6bc8-772e-4f12-92fe-a1dd96f57c0d" />

---

# Step 10 – Verify Email Notification

If the Lambda function detects one or more publicly accessible S3 buckets, an email notification is automatically sent to the subscribed email address through Amazon SNS.

Open the subscribed email account and verify that the notification has been received.

The notification contains information about the bucket that requires immediate attention.

Example Notification

```
Subject

Public S3 Bucket Detected

Message

The following S3 bucket is publicly accessible:

public-audit-demo

Please review the bucket permissions immediately.
```

Successful receipt of this email confirms that Amazon SNS has correctly delivered the notification generated by the Lambda function.

> **Screenshot**

<img width="1525" height="592" alt="Screenshot 2026-07-26 131745" src="https://github.com/user-attachments/assets/79ba8537-75ce-4914-9493-892c042b3488" />


---

# Step 11 – Configure Amazon EventBridge

To automate periodic security audits, configure an Amazon EventBridge rule to invoke the Lambda function on a scheduled basis.

Navigate to

```
AWS Console
→ Amazon EventBridge
→ Rules
→ Create Rule
```

Configuration

| Property | Value |
|-----------|-------|
| Rule Name | DailyS3Audit |
| Rule Type | Schedule |
| Schedule Pattern | Rate Expression |
| Rate | 1 Day |
| Target | AWS Lambda |
| Function | S3PublicAudit |

Click **Create Rule**.

Once configured, Amazon EventBridge automatically invokes the Lambda function according to the defined schedule.

This removes the need for manual execution and ensures that S3 bucket permissions are continuously monitored.

> **Screenshot**

<img width="1532" height="567" alt="Screenshot 2026-07-26 131908" src="https://github.com/user-attachments/assets/aebe4e6d-4310-435a-870c-cd09c7faa305" />

<img width="1538" height="368" alt="Screenshot 2026-07-26 131934" src="https://github.com/user-attachments/assets/40fea3fc-d7a3-40f2-80eb-95ff9da4e168" />

<img width="1455" height="832" alt="Screenshot 2026-07-26 131952" src="https://github.com/user-attachments/assets/dc004c1e-2d47-4399-8a91-3ae7a3d55824" />

---

# Step 12 – Verify EventBridge Configuration

After creating the EventBridge rule, verify the following:

- Rule Status is **Enabled**
- Target Lambda Function is correctly configured
- Schedule Expression is correctly displayed
- Rule is associated with the intended Lambda function

Once the scheduled execution time is reached, Amazon EventBridge automatically triggers the Lambda function.

The execution details can then be viewed in the Lambda execution report.

> **Screenshot**

<img width="1483" height="821" alt="Screenshot 2026-07-26 132030" src="https://github.com/user-attachments/assets/daf85fe8-1ee8-4bc8-ae60-2201650b0d95" />


---

# Expected Output

After successful implementation:

- Every Amazon S3 bucket within the AWS account is audited.
- Block Public Access configuration is verified.
- Bucket Policy status is verified.
- Bucket ACL permissions are verified.
- Publicly accessible buckets are successfully detected.
- Email notifications are delivered through Amazon SNS whenever an insecure bucket is identified.
- Security audits execute automatically through Amazon EventBridge.

---

# Discussion

Amazon S3 enables organizations to securely store large volumes of data. However, accidental permission changes may expose sensitive information to the public internet.

Automating security audits using AWS Lambda provides several advantages:

- Continuous monitoring of bucket security.
- Immediate notification whenever a bucket becomes publicly accessible.
- Reduced manual effort required for periodic security reviews.
- Early detection of security misconfigurations.
- Improved compliance with organizational security policies.

Although AWS provides services such as AWS Config and Amazon GuardDuty for broader security monitoring, this Lambda-based implementation demonstrates how custom security automation can be developed using AWS native services while maintaining complete control over the audit logic.

---

# Conclusion

This implementation demonstrates how AWS Lambda, Boto3, Amazon SNS, and Amazon EventBridge can be integrated to automate Amazon S3 security auditing.

The solution continuously examines every S3 bucket for insecure configurations, including disabled Block Public Access settings, public bucket policies, and permissive ACLs. Whenever a security risk is detected, an email notification is immediately delivered through Amazon SNS.

By implementing a dedicated IAM Role with a Least Privilege Policy and automating execution through Amazon EventBridge, the solution provides a secure, scalable, and efficient approach for continuously monitoring Amazon S3 bucket security within an AWS environment.

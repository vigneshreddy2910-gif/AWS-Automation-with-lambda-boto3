# AWS Automation with Lambda & Boto3

This repository contains my implementation of AWS Automation assignments using **AWS Lambda**, **Python (Boto3)**, **IAM**, **EventBridge**, **CloudWatch**, and other AWS services.

Each task demonstrates a real-world automation scenario commonly used in DevOps and Cloud Engineering.

---

## Technologies Used

- AWS Lambda
- Python 3.14
- Boto3
- IAM
- EventBridge
- Amazon EC2
- Amazon EBS
- Amazon S3
- Amazon SNS

---

# Completed Assignments

## Task 1 – Automated S3 Bucket Cleanup

### Objective

Automate deletion of stale objects from an Amazon S3 bucket.

**Requirements**

- Delete objects older than 30 days
- Print deleted object names
- Use least privilege IAM
- Support pagination
- Test using Lambda

📄 **Documentation**

➡️ [Task 1 – S3 Bucket Cleanup](./Task-1-S3-Bucket-Cleanup/readme.md)

---

## Task 2 – Automated EBS Snapshot Creation and Cleanup

### Objective

Automatically create snapshots for an EBS volume and remove snapshots older than the retention period.

**Requirements**

- Create EBS Snapshot
- Tag Snapshot
- Delete old snapshots
- Weekly EventBridge schedule

📄 **Documentation**

➡️ [Task 2 – EBS Snapshot Automation](./Task-2-EBS-Snapshot/readme.md)

---

## Task 3 – Auto Tagging EC2 Instances on Launch

### Objective

Automatically tag newly launched EC2 instances for ownership and cost allocation.

**Requirements**

- EventBridge Trigger
- Lambda
- EC2 Tagging

📄 **Documentation**

➡️ [Task 3 – Auto Tag EC2](./Task-3-AutoTag-EC2/readme.md)

---

## Task 6 – Audit S3 Buckets for Public Access

### Objective

Audit all S3 buckets for public accessibility and notify administrators using SNS.

**Requirements**

- Check Public Access Block
- Check Bucket Policy
- Check ACL
- Send SNS Email
- Scheduled EventBridge Rule

📄 **Documentation**

➡️ [Task 6 – S3 Public Audit](./Task-6-S3-Public-Audit/readme.md)

---

# Repository Highlights

- Least Privilege IAM Policies
- AWS Lambda (Python 3.14)
- Boto3 SDK
- EventBridge Scheduling
---

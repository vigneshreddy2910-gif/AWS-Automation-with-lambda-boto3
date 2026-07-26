# Task 2 – Automated EBS Snapshot Creation and Cleanup

## Task Description

Amazon Elastic Block Store (EBS) provides persistent block storage for Amazon EC2 instances. Regular snapshots are essential for backup and disaster recovery, allowing volumes to be restored in the event of accidental deletion, corruption, or system failure.

This task automates the process of creating snapshots of an EBS volume using AWS Lambda and Boto3. Each newly created snapshot is tagged for easy identification, while snapshots exceeding the configured retention period are automatically deleted.

For demonstration purposes, the retention period was temporarily configured to **1 minute** during testing. In a production environment, the retention period should be configured to **30 days** as specified in the assignment requirements.

---

# Objectives

- Automate EBS snapshot creation using AWS Lambda.
- Automatically tag every newly created snapshot.
- Delete snapshots older than the configured retention period.
- Follow AWS security best practices by implementing a Least Privilege IAM Policy.
- Verify successful execution using the Lambda execution report.
- Automate weekly execution using Amazon EventBridge.

---

# Architecture

```text
                     Amazon EC2 Instance
                              │
                              │
                       Attached EBS Volume
                              │
                              ▼
                    AWS Lambda Function
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
         ▼                    ▼                    ▼
 Create Snapshot       Apply Tags        Find Old Snapshots
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                    Delete Expired Snapshots
                              │
                              ▼
                   Lambda Execution Report
                              │
                              ▼
                     Amazon EventBridge
                      (Weekly Schedule)
```

---

# Prerequisites

Before implementing this task, ensure the following AWS resources are available.

- AWS Account
- Amazon EC2 Instance
- Amazon EBS Volume
- AWS Lambda
- IAM Role
- IAM Policy
- Amazon EventBridge
- Python 3.14 Runtime

---

# Step 1 – Create an Amazon EC2 Instance

Navigate to

```
AWS Console
→ EC2
→ Launch Instance
```

Example Configuration

| Property | Value |
|-----------|-------|
| Name | Snapshot-Test |
| AMI | Ubuntu Server |
| Instance Type | t2.micro |
| Storage | 8 GB gp3 |
| Key Pair | Existing or New |
| Security Group | Default |

Launch the instance.

Once the instance has been launched, AWS automatically creates and attaches an EBS Volume that will be used during this assignment.

> **Screenshot**

<img width="1490" height="765" alt="Screenshot 2026-07-26 115507" src="https://github.com/user-attachments/assets/0ec7a0cc-6ef3-4f2e-a2a1-714e36249204" />


---

# Step 2 – Locate the EBS Volume

Navigate to

```
AWS Console
→ EC2
→ Elastic Block Store
→ Volumes
```

Locate the volume attached to the EC2 instance.

Copy the **Volume ID**, as it will be required later when configuring the Lambda function.

Example

```
vol-0123456789abcdef0
```

> **Screenshot**

<img width="1742" height="781" alt="Screenshot 2026-07-26 115604" src="https://github.com/user-attachments/assets/1b3350f9-9030-4a56-b419-3abf5f35c9c7" />


---

# Step 3 – Create the IAM Role

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
LambdaSnapshotRole
```

Create the role.

> **Screenshot**

<img width="1702" height="616" alt="Screenshot 2026-07-26 115704" src="https://github.com/user-attachments/assets/0244d34b-8e80-4e06-b245-3957772fa5a4" />

<img width="1678" height="801" alt="Screenshot 2026-07-26 120136" src="https://github.com/user-attachments/assets/0ad037fc-fcfc-4e03-9ef6-4b79a0eecc62" />

---

# Step 4 – Create the IAM Policy

Attach a custom inline policy to the IAM Role created in the previous step.

The complete policy used in this implementation is available in this repository.

```
Task-2/EBSSnapshotpolicy.json
```

## Permissions Included

| Permission | Purpose |
|------------|----------|
| ec2:CreateSnapshot | Creates snapshots of the specified EBS volume. |
| ec2:DescribeSnapshots | Retrieves existing snapshots for retention verification. |
| ec2:DeleteSnapshot | Deletes snapshots older than the configured retention period. |
| ec2:CreateTags | Adds custom tags to newly created snapshots. |
| logs:CreateLogGroup | Creates a CloudWatch Log Group during the first execution. |
| logs:CreateLogStream | Creates a new log stream for each execution. |
| logs:PutLogEvents | Stores Lambda execution logs. |

## Role of the IAM Policy

The IAM Policy grants the Lambda function only the permissions required to perform snapshot management operations. Restricting permissions to only the required EC2 and CloudWatch actions follows the Principle of Least Privilege, reducing the overall security risk of the solution.

> **Screenshot**

<img width="1707" height="810" alt="Screenshot 2026-07-26 120119" src="https://github.com/user-attachments/assets/adb8d5c7-bf18-4b73-a01a-75384ce7549f" />


---

# Step 5 – Create the Lambda Function

Navigate to

```
AWS Console
→ Lambda
→ Create Function
```

Configuration

| Property | Value |
|-----------|-------|
| Function Name | EBSBackup |
| Runtime | Python 3.14 |
| Architecture | x86_64 |
| Execution Role | Use Existing Role |

Select the IAM Role created in the previous step.

Click **Create Function**.

> **Screenshot**

<img width="1446" height="766" alt="Screenshot 2026-07-26 120240" src="https://github.com/user-attachments/assets/469a0894-e054-4888-b685-6f00821da67b" />

<img width="1477" height="847" alt="Screenshot 2026-07-26 120508" src="https://github.com/user-attachments/assets/d8ee2a2a-c40b-492c-8170-e3e485de309b" />

---

# Step 6 – Configure Environment Variables

After the Lambda function has been created, navigate to

```
Configuration
→ Environment Variables
```

Create the following variable.

| Key | Value |
|------|-------|
| VOLUME_ID | Your EBS Volume ID |

Example

```
Key

VOLUME_ID

Value

vol-0123456789abcdef0
```

Save the configuration.

The Lambda function retrieves the Volume ID from the environment variable instead of hardcoding it inside the source code. This approach improves maintainability and follows AWS development best practices.

> **Screenshot**

<img width="1497" height="422" alt="Screenshot 2026-07-26 120550" src="https://github.com/user-attachments/assets/739734a5-779d-4baa-bd29-2ae90879b3c9" />

<img width="1451" height="286" alt="Screenshot 2026-07-26 120706" src="https://github.com/user-attachments/assets/bfe4928f-3b5c-42b1-83ff-807c39379884" />

---

# Step 7 – Deploy the Lambda Code

Replace the default Lambda source code with the implementation provided in this repository.

```
Task-2/lambda_function.py
```

After replacing the code, click

```
Deploy
```

The deployed Lambda function performs the following operations:

- Reads the EBS Volume ID from the environment variables.
- Creates a new snapshot of the specified volume.
- Tags the snapshot with a custom identifier.
- Retrieves previously created snapshots.
- Deletes snapshots older than the configured retention period.
- Prints the created and deleted Snapshot IDs in the execution logs.

> **Screenshot**

<img width="1477" height="847" alt="Screenshot 2026-07-26 120508" src="https://github.com/user-attachments/assets/60fd5181-633d-4984-9f0d-e4a43e9bfee4" />


---
# Step 8 – Verify the Lambda Function

Once the Lambda function has been deployed successfully, create a new Test Event to verify its execution.

Navigate to

```
Lambda
→ Test
→ Create New Test Event
```

Configuration

| Property | Value |
|-----------|-------|
| Event Name | SnapshotTest |
| Event JSON | `{}` |

Save the event and click **Test**.

During execution, the Lambda function performs the following operations sequentially:

- Reads the configured EBS Volume ID.
- Creates a new snapshot of the specified EBS volume.
- Applies the predefined tag to the newly created snapshot.
- Retrieves all snapshots previously created by the Lambda function.
- Compares their creation time with the configured retention period.
- Deletes snapshots that exceed the retention threshold.
- Displays the Snapshot IDs of both created and deleted snapshots.

A successful execution returns a response similar to:

```json
{
    "statusCode": 200,
    "body": "Snapshot completed successfully."
}
```

> **Screenshot**

<img width="1406" height="622" alt="Screenshot 2026-07-26 120913" src="https://github.com/user-attachments/assets/61de24b7-a2a4-4654-b8c9-57f13cfb6816" />


---

# Step 9 – Verify Snapshot Creation

Navigate to

```
AWS Console
→ EC2
→ Elastic Block Store
→ Snapshots
```

A new snapshot should now be visible.

Open the snapshot and verify that the custom tag has been successfully applied.

Example

| Tag Key | Tag Value |
|----------|-----------|
| CreatedBy | Lambda-Backup |

The presence of this tag confirms that the Lambda function successfully completed both the snapshot creation and tagging operations.

> **Screenshot**

<img width="1441" height="647" alt="Screenshot 2026-07-26 120930" src="https://github.com/user-attachments/assets/ff29bd07-7df6-478d-8b97-4e31e49aff9c" />


---

# Step 10 – Verify Snapshot Cleanup

For testing purposes, the snapshot retention period was temporarily configured to **1 minute**.

After waiting approximately two minutes, execute the Lambda function once again.

During the second execution:

- A new snapshot will be created.
- The previously created snapshot will now exceed the configured retention period.
- The older snapshot will automatically be deleted.

This confirms that the cleanup logic is functioning correctly.

> **Screenshot**

<img width="1720" height="237" alt="Screenshot 2026-07-26 121202" src="https://github.com/user-attachments/assets/dec4f24e-ede5-4ec7-8563-0fb39efa2cf0" />
The previous Snapshot was deleted and new Snapshot is created 

---

# Lambda Execution Report

The Lambda execution report provides a detailed summary of each execution, including:

- Function Status
- Execution Duration
- Billed Duration
- Memory Allocation
- Memory Utilized
- Initialization Duration
- Snapshot IDs created during execution
- Snapshot IDs deleted during execution

---

# Step 11 – Automate Using Amazon EventBridge

To eliminate the need for manual execution, the Lambda function can be scheduled using Amazon EventBridge.

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
| Rule Name | WeeklySnapshot |
| Rule Type | Schedule |
| Schedule Pattern | Rate Expression |
| Rate | 1 Week |
| Target | AWS Lambda |
| Function | EBSBackup |

Create the rule.

Once configured, EventBridge automatically invokes the Lambda function every week without requiring any manual intervention.

This ensures that snapshots are created on a regular schedule while expired snapshots continue to be removed automatically.

> **Screenshot**

<img width="1565" height="647" alt="Screenshot 2026-07-26 123113" src="https://github.com/user-attachments/assets/5b4393ea-8150-4cd2-8dd1-a38c20777467" />

<img width="1462" height="355" alt="Screenshot 2026-07-26 123126" src="https://github.com/user-attachments/assets/db8f9fc5-9d3c-417b-b1ae-6f1aa95f5a80" />

<img width="1480" height="782" alt="Screenshot 2026-07-26 123139" src="https://github.com/user-attachments/assets/1443bf69-b2f1-43a1-8061-8a7ac734ce87" />

---

# EventBridge Verification

After the EventBridge rule has been created, verify that:

- The rule status is **Enabled**.
- The target Lambda function is correctly associated.
- The schedule expression is configured as intended.

When the scheduled time is reached, Amazon EventBridge automatically invokes the Lambda function.

The execution can then be verified through the Lambda execution report.

> **Screenshot**

<img width="1218" height="847" alt="Screenshot 2026-07-26 123157" src="https://github.com/user-attachments/assets/2088171b-0db7-4be2-84cf-af25a646aff6" />


---

# Expected Output

After successful implementation:

- A snapshot is automatically created for the specified EBS volume.
- Every newly created snapshot receives the predefined tag.
- Older snapshots exceeding the configured retention period are automatically deleted.
- Snapshot creation and deletion details are displayed in the Lambda execution report.
- Weekly execution is fully automated through Amazon EventBridge.

---

# Discussion

Amazon Data Lifecycle Manager (DLM) is AWS's managed service for automating EBS snapshot creation and retention without requiring custom code.

However, AWS Lambda provides significantly greater flexibility when custom automation logic is required. Examples include:

- Applying custom tags during snapshot creation.
- Using dynamic retention periods based on business requirements.
- Sending notifications after snapshot creation.
- Copying snapshots across AWS Regions or accounts.
- Integrating backup workflows with additional AWS services.

Because of this flexibility, Lambda is often preferred when organizations require customized backup workflows beyond the capabilities provided by Data Lifecycle Manager.

---

# Conclusion

This implementation demonstrates how AWS Lambda and Boto3 can automate EBS backup management with minimal manual effort.

The solution creates snapshots, applies custom tags, removes outdated snapshots, and integrates with Amazon EventBridge for scheduled execution. By following the Principle of Least Privilege through a dedicated IAM Role and Policy, the implementation remains secure while significantly reducing the operational effort involved in maintaining EBS backups.

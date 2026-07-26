# Task 3 – Auto Tagging EC2 Instances on Launch

## Task Description

Managing Amazon EC2 instances across multiple projects and environments can become challenging as the number of resources increases. Resource tagging is an AWS best practice that helps identify resources based on ownership, environment, project, cost allocation, and lifecycle management.

This task automates the process of tagging EC2 instances immediately after they enter the **Running** state. AWS Lambda, together with Amazon EventBridge and the Boto3 SDK, is used to detect newly launched EC2 instances and automatically apply predefined tags.

The implementation adds the launch date and a custom environment tag to every newly launched EC2 instance without requiring manual intervention.

---

# Objectives

- Automatically detect newly launched EC2 instances.
- Apply predefined tags using AWS Lambda and Boto3.
- Follow the Principle of Least Privilege by creating a custom IAM Role and Policy.
- Verify successful execution using the Lambda execution report.
- Demonstrate event-driven automation using Amazon EventBridge.

---

# Architecture

```text
                  Launch EC2 Instance
                           │
                           ▼
                EC2 Changes State
                    Pending → Running
                           │
                           ▼
                Amazon EventBridge Rule
                           │
                           ▼
                 AWS Lambda Function
                           │
              Extract EC2 Instance ID
                           │
                           ▼
              Apply Custom EC2 Tags
                           │
                           ▼
                  Updated EC2 Instance
                           │
                           ▼
               Lambda Execution Report
```

---

# Prerequisites

Before implementing this task, ensure the following AWS resources are available.

- AWS Account
- Amazon EC2
- AWS Lambda
- Amazon EventBridge
- IAM Role
- IAM Policy
- Python 3.14 Runtime

---

# Step 1 – Launch an Amazon EC2 Instance

Navigate to

```
AWS Console
→ EC2
→ Launch Instance
```

Example Configuration

| Property | Value |
|-----------|-------|
| Name | AutoTag-Test |
| AMI | Ubuntu Server |
| Instance Type | t2.micro |
| Key Pair | Existing or New |
| Security Group | Default |

Launch the instance.

This EC2 instance will later be used to verify that the Lambda function automatically applies tags when the instance enters the **Running** state.

> **Screenshot**

<img width="1430" height="742" alt="Screenshot 2026-07-25 180703" src="https://github.com/user-attachments/assets/2bf29314-5d13-4672-b222-0a2011b22165" />

<img width="1412" height="702" alt="Screenshot 2026-07-25 180755" src="https://github.com/user-attachments/assets/f385106c-9056-4ceb-98d0-fa5d3bc132c6" />

---

# Step 2 – Create the IAM Role

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
LambdaAutoTagRole
```

Create the role.

> **Screenshot**

<img width="1665" height="141" alt="Screenshot 2026-07-25 181133" src="https://github.com/user-attachments/assets/5007b812-06c0-451b-aada-ed4b22a50708" />

<img width="1177" height="532" alt="Screenshot 2026-07-25 181148" src="https://github.com/user-attachments/assets/98a2f223-c71b-4733-9182-0c8c73ebbff6" />

<img width="1640" height="836" alt="Screenshot 2026-07-25 181812" src="https://github.com/user-attachments/assets/624a9d86-fb12-46e2-a621-a2234bbb51e1" />

---

# Step 3 – Create the IAM Policy

Attach a custom inline policy to the IAM Role created in the previous step.

The complete policy used in this implementation is available in this repository.

Also attach AWSLambdaBasicExecutionRole policy which is directly provided by AWS.

```
Task-3/lambdaautotagpolicy.json
```

---

## Permissions Included

| Permission | Purpose |
|------------|----------|
| ec2:CreateTags | Allows the Lambda function to add custom tags to EC2 instances. |
| ec2:DescribeInstances | Retrieves instance information before applying tags. |
| logs:CreateLogGroup | Creates the CloudWatch Log Group during the first execution. |
| logs:CreateLogStream | Creates a new log stream for each Lambda execution. |
| logs:PutLogEvents | Stores Lambda execution logs. |

---

## Why These Permissions Are Required

### ec2:CreateTags

This permission allows the Lambda function to write tags to an EC2 instance.

Without this permission, the function would successfully execute but would fail when attempting to apply tags.

---

### ec2:DescribeInstances

Although the EventBridge event already contains the EC2 Instance ID, this permission allows the Lambda function to retrieve additional metadata about the instance before applying tags.

Examples include:

- Current Instance State
- Existing Tags
- Availability Zone
- Instance Type
- VPC Information

Including this permission follows industry best practices and enables future enhancements without requiring changes to the IAM Policy.

---

## Role of the IAM Policy

The IAM Policy grants only the permissions required to perform EC2 tagging operations.

Rather than granting administrative access, the policy follows the Principle of Least Privilege by allowing only the specific EC2 and CloudWatch actions required by the Lambda function.

This minimizes the security risk while ensuring successful execution.

> **Screenshot**

<img width="1596" height="740" alt="Screenshot 2026-07-25 181518" src="https://github.com/user-attachments/assets/65e092b4-8654-44dc-b23b-b1860a8f7803" />

<img width="1442" height="271" alt="Screenshot 2026-07-25 181945" src="https://github.com/user-attachments/assets/c529df78-726b-40f8-8842-408b0b150d51" />

<img width="750" height="610" alt="Screenshot 2026-07-25 182025" src="https://github.com/user-attachments/assets/f63e4caa-7a33-4d0b-a25e-9a854448e204" />

<img width="1050" height="260" alt="Screenshot 2026-07-25 182050" src="https://github.com/user-attachments/assets/4d60c89c-07c1-4ea9-9ef1-62daa9dae100" />

---

# Step 4 – Create the Lambda Function

Navigate to

```
AWS Console
→ Lambda
→ Create Function
```

Configuration

| Property | Value |
|-----------|-------|
| Function Name | AutoTagEC2 |
| Runtime | Python 3.14 |
| Architecture | x86_64 |
| Execution Role | Use Existing Role |

Select the IAM Role created previously.

Click **Create Function**.

> **Screenshot**

<img width="1432" height="761" alt="Screenshot 2026-07-25 182214" src="https://github.com/user-attachments/assets/9df8746f-9e29-4f81-9156-5890e4dbfc77" />


---

# Step 5 – Deploy the Lambda Code

Replace the default Lambda source code with the implementation available in this repository.

```
Task-3/lambda_function.py
```

After replacing the code, click

```
Deploy
```

The deployed Lambda function performs the following operations:

- Receives the EventBridge event.
- Extracts the EC2 Instance ID.
- Retrieves instance metadata.
- Generates the current launch date.
- Reads the configured environment from the environment variables.
- Applies the predefined tags to the EC2 instance.
- Displays a confirmation message in the Lambda execution report.

> **Screenshot**
<img width="1401" height="842" alt="Screenshot 2026-07-25 182341" src="https://github.com/user-attachments/assets/9ca78fae-be14-4919-8f14-3f698654616d" />


<img width="1390" height="610" alt="Screenshot 2026-07-25 182433" src="https://github.com/user-attachments/assets/faf2ebec-5abf-4a8b-882d-8e2acfd37c44" />


---

# Step 6 – Verify the Lambda Function

Once the Lambda function has been deployed successfully, create a new Test Event to verify its execution.

Navigate to

```
Lambda
→ Test
→ Create New Test Event
```

Use the following sample event.

```json
{
  "detail": {
    "instance-id": "i-0123456789abcdef0",
    "state": "running"
  }
}
```

Replace the sample instance ID with the ID of your own EC2 instance.

Save the event and click **Test**.

During execution, the Lambda function performs the following operations:

- Receives the EventBridge event.
- Extracts the EC2 Instance ID.
- Retrieves the current date.
- Reads the configured environment variable.
- Applies the predefined tags to the EC2 instance.
- Displays a confirmation message in the Lambda execution report.

A successful execution returns a response similar to:

```json
{
    "statusCode": 200,
    "body": "Tags applied successfully."
}
```

> **Screenshot**

<img width="1402" height="777" alt="Screenshot 2026-07-25 182621" src="https://github.com/user-attachments/assets/efa283a3-5e59-411c-bfd1-3fb707088d24" />


---

# Lambda Execution Report

The Lambda execution report provides detailed information regarding the execution of the function.

The report includes:

- Function Status
- Request ID
- Execution Duration
- Billed Duration
- Memory Allocated
- Memory Utilized
- Initialization Duration
- Confirmation message after successful tagging

> **Screenshot**

<img width="1412" height="747" alt="Screenshot 2026-07-25 182701" src="https://github.com/user-attachments/assets/115fcbb2-550a-4fc1-afb3-e114fe88edc5" />


---

# Step 8 – Verify EC2 Tags

Navigate to

```
AWS Console
→ EC2
→ Instances
```

Select the EC2 instance that was used for testing.

Open the **Tags** tab.

The following tags should now be visible.

| Tag Key | Example Value |
|----------|---------------|
| LaunchDate | 2026-07-21 11.47.25 UTC|
| Environment | Development |

The successful appearance of these tags confirms that the Lambda function has correctly processed the event and updated the EC2 instance.

> **Screenshot**

<img width="1433" height="327" alt="Screenshot 2026-07-25 182724" src="https://github.com/user-attachments/assets/f93e2347-eb8a-430a-91d4-858759664c91" />


---

# EventBridge Automation

In a production environment, this solution is designed to operate automatically using **Amazon EventBridge**.

An EventBridge Rule monitors EC2 state-change events. Whenever an EC2 instance transitions to the **Running** state, EventBridge automatically invokes the Lambda function.

The Lambda function then performs the following actions automatically:

- Receives the EC2 State Change Notification.
- Extracts the EC2 Instance ID.
- Retrieves the configured environment value.
- Applies the predefined tags.
- Records the execution details in the Lambda execution report.

This event-driven architecture eliminates the need for manual execution and ensures that every newly launched EC2 instance is tagged consistently across the AWS environment.

> **Note**

No EventBridge screenshots are included for this task, as the Lambda function was manually verified using a test event. In production, the same Lambda function can be triggered automatically through Amazon EventBridge without any changes to the implementation.

---

# Expected Output

After successful implementation:

- Newly launched EC2 instances are automatically detected.
- The LaunchDate tag is added using the current date.
- The Environment tag is applied using the configured environment variable.
- The Lambda execution report confirms successful tagging.
- Resource tagging becomes fully automated without requiring manual intervention.

---

# Discussion

Although EC2 instances can be manually tagged during creation, automating the process using AWS Lambda provides several advantages.

Some common use cases include:

- Automatically tagging resources for cost allocation.
- Identifying the deployment environment (Development, Testing, Production).
- Recording ownership information.
- Applying compliance-related tags.
- Enforcing organizational tagging standards across AWS accounts.

Because the Lambda function is event-driven, it reacts immediately whenever a new EC2 instance enters the **Running** state, ensuring that every resource follows the organization's tagging policy.

This automation reduces manual effort, minimizes human error, and improves overall cloud resource management.

---

# Conclusion

This implementation demonstrates how AWS Lambda, Boto3, and Amazon EventBridge can be combined to automate EC2 resource tagging.

The solution automatically detects newly launched EC2 instances, applies predefined tags, and records execution details through the Lambda execution report.

By implementing a dedicated IAM Role with a Least Privilege Policy, the solution remains secure while automating an important operational task that is widely used for governance, cost management, and resource organization in production AWS environments.

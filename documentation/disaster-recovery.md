# Disaster recovery

## Table of contents

- [Disaster recovery](#disaster-recovery)
  - [Table of contents](#table-of-contents)
  - [What is disaster recovery?](#what-is-disaster-recovery)
  - [What may have happened?](#what-may-have-happened)
  - [Disaster recovery plan](#disaster-recovery-plan)
    - [Full application recovery](#full-application-recovery)
      - [Prerequisites for full application recovery](#prerequisites-for-full-application-recovery)
      - [Steps for full application recovery](#steps-for-full-application-recovery)
    - [Partial application recovery](#partial-application-recovery)
      - [Prerequisites for partial application recovery](#prerequisites-for-partial-application-recovery)
      - [Steps for partial application recovery](#steps-for-partial-application-recovery)
    - [Data recovery](#data-recovery)
  - [Notes](#notes)

## What is disaster recovery?

Disaster recovery is the process of resuming normal operations after a disaster by regaining access to data, hardware, software, networking equipment, power, and connectivity. Disaster recovery is a subset of business continuity.

## What may have happened?

A major disaster may have occurred. This may include:

- AWS Region being down
- AWS account being compromised and resources deleted

## Disaster recovery plan

### Full application recovery

This is the process of recovering the application in a different AWS account and/or region to the one currently deployed.

#### Prerequisites for full application recovery

1. Texas sets up a new AWS account/region to the one currently used.
2. Terraform prerequisites are set up in the new AWS account/region. This includes:
   - S3 bucket for Terraform state
   - DynamoDB table for Terraform state locking
3. Manually set up ECR repositories in the new AWS management account/region. This is because ECR repositories haven't been set up in Terraform yet.

#### Steps for full application recovery

1. Run Terraform in the new AWS account/region. This will create all the resources needed to run the application.
   1. Run the Terraform deploying the shared resources first.
   2. Deploy the first blue/green environment.
   3. (Optional) Deploy the second blue/green environment.
   4. Deploy the blue/green link Terraform stack.
2. Give new API Key to Profile Manager/NHS.UK team.

### Partial application recovery

This is the process of recovering the application within the same AWS account and region as currently deployed.

#### Prerequisites for partial application recovery

1. (if needed) Terraform prerequisites are set up in the AWS account/region. This includes:
   - S3 bucket for Terraform state
   - DynamoDB table for Terraform state locking
2. (if needed) Manually set up ECR repositories in the AWS management account/region. This is because ECR repositories haven't been set up in Terraform yet.

#### Steps for partial application recovery

1. Run Terraform in the current. Terraform will create any non-existent resources needed to run the application.
   1. Run the Terraform deploying the shared resources first.
   2. Deploy the first blue/green environment.
   3. (Optional) Deploy the second blue/green environment.
   4. Deploy the blue/green link Terraform stack.
2. (if needed) Give new API Key to Profile Manager/NHS.UK team.

### Data recovery

DynamoDB data is backed up using point in time recovery. The data can be restored to any point in time within the last 35 days.
This is documented in confluence [here](https://nhsd-confluence.digital.nhs.uk/display/DI/How+to+restore+a+DynamoDB+table).

## Notes

This is a suggestion for a disaster recovery plan. It's not a complete plan and should be used as a starting point for a full disaster recovery plan. As well this plan hasn't been tested yet.

It's likely that problems will be discovered when applying this plan.

# Service matcher lambda issue

## Table of contents

- [Service matcher lambda issue](#service-matcher-lambda-issue)
  - [Table of contents](#table-of-contents)
  - [Description](#description)
  - [How did the development team discover the issue?](#how-did-the-development-team-discover-the-issue)
  - [Steps to gain more information about the issue](#steps-to-gain-more-information-about-the-issue)
  - [Application features to ensure data integrity](#application-features-to-ensure-data-integrity)
  - [How to fix the issue](#how-to-fix-the-issue)

## Description

This is a breaking issue within the service matcher lambda.

Examples of an issue could be:

- Incorrect environment variables
- Incorrect lambda permissions
- Secrets manager secrets are incorrect or missing (Managed by DoS Integration DevOps Team and Core DoS Team)
- The lambda isn't able to connect to the AWS Aurora Postgres database (DoS)
- The lambda isn't able to save/receive change events to the AWS SQS queue

## How did the development team discover the issue?

A slack alert arrived in the development team slack channel with the following message:
`Service Matcher Error Rate`

![Service Matcher Lambda Error Rate Alert](./service_matcher_lambda_error_rate_alert.png)

## Steps to gain more information about the issue

- Check the CloudWatch Dashboard for the service matcher error rate
- Check the CloudWatch Logs for the service matcher lambda
- Check the CloudWatch Log Insights Errors query, then look for the service matcher lambda errors

## Application features to ensure data integrity

- The service matcher lambda is idempotent, so change events can be retried without any issues
- Failed change events automatically are retried 4 times (5 times including original run), before being sent to the dead letter queue. This queue is subscribed by the change event DLQ handler lambda, which saves the change events to the AWS DynamoDB database.
  - Once the issue is fixed, the change events can be reprocessed by the development team using the event replay lambda.
- Database connections use default timeouts to remove connections that are no longer in use

## How to fix the issue

1. Diagnose the issue using the steps preceding under the "Steps to gain more information about the issue" section
2. Fix the issue
3. Reprocess the failed change events using the event replay lambda
4. Monitor the service matcher lambda error rate to ensure the issue has been resolved

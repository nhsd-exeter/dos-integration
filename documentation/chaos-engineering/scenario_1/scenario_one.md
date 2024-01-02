# Ingest change event lambda issue

## Table of contents

- [Ingest change event lambda issue](#ingest-change-event-lambda-issue)
  - [Table of contents](#table-of-contents)
  - [Description](#description)
  - [How did the development team discover the issue?](#how-did-the-development-team-discover-the-issue)
  - [Steps to gain more information about the issue](#steps-to-gain-more-information-about-the-issue)
  - [Application features to ensure data integrity](#application-features-to-ensure-data-integrity)
  - [How to fix the issue](#how-to-fix-the-issue)

## Description

This is a breaking issue within the ingest change event lambda.

Examples of an issue could be:

- Incorrect environment variables
- Incorrect lambda permissions
- The lambda isn't able to save change events to the AWS DynamoDB database
- The lambda isn't able to send change events to the AWS SQS queue

## How did the development team discover the issue?

A slack alert arrived in the development team slack channel with the following message:
`Ingest Change Event Error Rate`

![Ingest Change Event Lambda Error Rate Alert](./ingest_change_event_lambda_error_rate_alert.png)

## Steps to gain more information about the issue

## Application features to ensure data integrity

## How to fix the issue

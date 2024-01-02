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
- The lambda isn't able to connect to the AWS Aurora Postgres database (DoS)
- The lambda isn't able to save/receive change events to the AWS SQS queue

## How did the development team discover the issue?

A slack alert arrived in the development team slack channel with the following message:
`Service Matcher Error Rate`

![Service Matcher Lambda Error Rate Alert](./service_matcher_lambda_error_rate_alert.png)

## Steps to gain more information about the issue

## Application features to ensure data integrity

## How to fix the issue

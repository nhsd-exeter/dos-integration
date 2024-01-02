# Slack messenger lambda issue

## Table of contents

- [Slack messenger lambda issue](#slack-messenger-lambda-issue)
  - [Table of contents](#table-of-contents)
  - [Description](#description)
  - [How did the development team discover the issue?](#how-did-the-development-team-discover-the-issue)
  - [Steps to gain more information about the issue](#steps-to-gain-more-information-about-the-issue)
  - [How to fix the issue](#how-to-fix-the-issue)

## Description

This is a breaking issue within the slack message lambda.

Examples of an issue could be:

- Incorrect environment variables
- Incorrect lambda permissions
- The lambda isn't able to save/receive slack messages to the AWS SNS topic

## How did the development team discover the issue?

- Check AWS CloudWatch Dashboard for the slack messenger lambda errors rate
- Inconsistencies between expected alarms and actual alarms. Using Splunk dashboard to compare the two.

## Steps to gain more information about the issue

- Check AWS CloudWatch logs for the slack messenger lambda for any errors

There may be hidden errors that aren't being reported to Slack:

- Run CloudWatch Log Insights Errors query to find any errors that aren't being reported to Slack

## How to fix the issue

1. Diagnose the issue using the steps preceding under the "Steps to gain more information about the issue" section
2. Fix the issue
3. Reprocess the failed change events using the event replay lambda
4. Monitor the service sync lambda error rate to ensure the issue has been resolved

Note: the fixing process need to be run multiple times if the Slack messenger error was hiding another error elsewhere in the application.

# API Gateway 5XX issue

## Table of contents

- [API Gateway 5XX issue](#api-gateway-5xx-issue)
  - [Table of contents](#table-of-contents)
  - [Description](#description)
  - [How did the development team discover the issue?](#how-did-the-development-team-discover-the-issue)
  - [Steps to gain more information about the issue](#steps-to-gain-more-information-about-the-issue)
  - [Application features to ensure data integrity](#application-features-to-ensure-data-integrity)
  - [How to fix the issue](#how-to-fix-the-issue)

## Description

This is a breaking issue with the API Gateway.

Examples of an issue could be:

- API Gateway incorrectly configured
- Incorrect API Gateway permissions
- The API Gateway isn't able to send change events to the AWS SQS queue

## How did the development team discover the issue?

A slack alert arrived in the development team slack channel with the following message:
`DI 5XX Endpoint Errors`

![DI 5XX Endpoint Errors Alert](./api_gateway_5xx_error_alert.png)

## Steps to gain more information about the issue

## Application features to ensure data integrity

## How to fix the issue

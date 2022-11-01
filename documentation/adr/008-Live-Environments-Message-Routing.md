# ADR-008: Live Environments Message Routing

## Overview

Live Environments Message Routing - How to select which environment a message is routed to?

* Date: 2022/10/18
* Status: Decided
* Deciders: Adi & Jack

## Context

How to select which environment a message is routed to? So that messages can be routed to the correct environment and withheld from the live environment during deployment.

High level requirements:

* Messages must be routed to the correct environment
* Messages must be withheld from the live environment during deployment
* Message routing must be configurable by Infrastructure as Code (IaC)

### Detailed analysis of the options

#### Option 1 - SQS Lambda Subscription

This option is to have a Lambda function that is subscribed to the SQS queue. The lambda from the environment is live will be subscribed.

This allows the subscription to be controlled by the IaC and the lambda function can be used to route the message to the correct environment or withhold it from the live environment during deployment. To withhold the message from the live environment there won't be a lambda function subscribed to the queue so the message will be held in the queue.

## Decision

We debated multiple minor options but each was unable to pause messages during deployment so **The decision was to go with option 1**. This allows us to have a lambda function that can be used to route the message to the correct environment or withhold it from the live environment during deployment. Therefore the shared resources can all be handled by Terraform with no manual intervention to pause messages during deployment or to route messages to the correct environment.

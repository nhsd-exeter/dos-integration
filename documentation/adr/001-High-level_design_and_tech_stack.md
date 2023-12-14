# ADR-001: High-level design and tech stack

## Overview

Option selection report - Technology for centralized messaging broker

* Date: **16/01/2022**
* Status: **Decided**
* Deciders: **The DoS Integration team, the DoS Tech Strategy team, Edward Sparkes**

## Context

DI is a greenfield integration project enabling the changes made by service owners such as Pharmacies to their contact information and opening times on NHS.uk to be reflected in DoS to ensure consumers of DoS have up to date and accurate information about UEC services.

It replaces Profile updater which provided a separate UI for service providers to update data for DoS. The new solution ensures service providers only need to make the changes in 1 place. As an interim solution Profile updater was updated to take a CSV feed from NSH Uk once a day and passed this information to DoS. This solution has its own limitations like data won't reflect to the end user immediately. The proposed solution is based on Messaging Queue technology (publish/subscribe). This paper provides the available options and our recommendations. we are evaluating the options available as "Cloud native solutions/services"  which are  as follows

1. Use serverless AWS native event services.
2. Use MSK (Amazon Managed Streaming for Apache Kafka)

Our decision is use AWS native event services.

The rest of this paper discusses the requirements and provides further analysis of the options (pros and cons of the available options).

High level requirements:

* The solution must support the receiving of data in  real-time
* The solution must provide a configurable short to mid term data storage to handle exceptions
* The solution must be able throttle requests to DoS due to current technical restrictions and to negate or minimise any impact to critical care consumers of DoS
* The solution must have the ability to replay messages in chronological or other orders - this is to recover from any failures during downstream data processing
* The solution must provide management information about the number of messages processed, failures, retries, latency and other management information

### Detailed analysis of the options

#### Option 1 - Use AWS Managed Services

This solution utilises SQS and EventBridge to handle the asynchronous orchestration of change events from NHS UK through to delivery of change requests to DoS.

Pros:

* A fully managed service in AWS
* Easy to configure
* Good experience of Terraform in the team for provisioning the services
* Faster time to value - we can start using this with very little effort
* Slightly cheaper infrastructure costs compared to MSK (to be confirmed based on volumes of messages)
* Better fit for non functional requirements especially around throttling requests into DoS API Gateway

Cons:

* Short duration for messages on the queue (less than 14 days)
* Restricted capabilities to reprocess failed messages
* Restricted ability to manage capacity and throughput

However, there is a limitation on the "time to live" for messages

### Option 2 - Use AWS MSK Managed Service

In this solution, there is a managed Kafka cluster which takes care of the message queuing part of the solution. The Kafka cluster has features to configure the "time to live" and it comes with a host of management features that enables rich reporting and message replay functionality.

Pros:

* A fully managed service in AWS
* Fine grained control to configure the service
* Meets requirements for message replay, Management Information and configurable time to live for the messages

Cons:

* More complex to configure compared to the other option
* Potentially higher costs (TBV)
* More code required to manage throttling requirements
* Limited experience in the team

## Decision

* Design: Use of AWS managed services, serverless design, AWS native event services
* Tech Stack: API Gateway, Lambda, SQS, DynamoDB, EventBridge

Based on the non-functional requirements, the AWS native solution is a better fit to the overall solution.

The diagram below shows the physical architecture of the solution.

![DoS Infrastructure](../diagrams/DoS%20Integration-Infrastructure.drawio.png "Dos Infrastructure")

### The Happy Path

1. Service owners make changes to their service through the NHS UK website. They can make the changes through a Web user interface or through an API. The API will likely be used by large pharmacy groups such as LLoyds and Boots that manage thousands of pharmacies. Address and organisation name changes cannot be made via the NHS UK website or API and will come via NHS UK from a weekly BSA file uploaded into NHS UK.

2. NHS UK updates their record and sends a full service record including updated and non updated fields onto two queues. One queue is used internally to update search indexes the other is for DoS integration, there are two separate queues to allow the two consumers to diverge in the messages they need to receive.

3. An Azure function is triggered when new messages appear on DoS integration queue.

4. The function sends the message to an endpoint in the DoS Integration solution. An API key is required. The message needs to include the full message and a sequence number to ensure DoS receives and processed messages for a given service in order to avoid any changes being accidentally undone. Optionally a correlation id can be provided in `x-correlation-id` header to enable event tracing from the source system.

5. The API gateway endpoint is configured as proxy to an SQS queue to store the messages for processing. The queue is configured as a FIFO queue with ODS code being used as MessageID to ensure the solution can both scale horizontally for different ODS services whilst ensuring all messages for a given ODS service are processed sequentially to avoid any race conditions.

6. Lambda function triggered by messages appearing on the SQS queue. This Lambda validates the message.

7. The Lambda function will save the incoming message to DynamoDB, this enables us to store the message for replay and audit purposes for longer than the maximum 2 weeks SQS supports, although suggest we configure a TTL on the items in DynamoDB to prevent the database scaling indefinitely and to ensure we don't persist data longer than required.

8. The Lambda function will check DynamoDB for the latest sequence number processed for the message ODS code, if there have been no previous messages or the sequence number is greater than the last processed then the Lambda continues execution, if not the message is discarded and logged.

9. The Lambda then retrieves services from the DoS database and compares them to the message to see what changes are required. The Lambda connects to a dedicated read replica of the DoS Database, connections are cleared up after use.

10. If changes have been identified they are sent to a separate queue for forwarding to DoS.

11. An orchestrator function is triggered by EventBridge to run every minute with concurrency of 1. It reads messages from the queue and sends them to the event sender lambda via asynchronous invocation at a rate of 3 / second. This rate is configurable in the lambda environment variables.

12. The event sender forwards the change request to the DoS change request API, and remove the message from the queue.

### Known issues

There are a number of scenarios that could occur that will not result in a change in DoS and that identify a discrepancy between the two systems. In order to rectify or at the least understand these discrepancies they must be captured. The following known scenarios include.

* ODS code not in DoS
* Postcode not in DoS or in DoS without lat/lon and easting/northing
* Invalid opening times, including overlaps
* Service marked as Hidden or Closed from NHS UK

In each of these scenarios a specific log record will be written. All logs are shipped to Splunk via Kinesis Firehose. Reports will be written in Splunk to look for these specific scenarios and notifications sent to relevant teams for investigation. All reports are saved under the `Texas UEC Profile Updater` App in Splunk and all logs are in the `cw_logs_uec_dos_int_prod` and `cw_logs_uec_dos_int_nonprod` indexes

For these known scenarios the message is removed from the queue as it will not pass until the underlying issue has been rectified. Once the issue is resolved the message can be replayed at a later date as it has been saved to DynamoDB.

### Exception routes

1. Processing lambda fails or cant meet demand from the SQS queue.
If the lambda fails to process the message for some unknown or intermittent reason, perhaps including a database connection issue, the message will be re-queued and retried. The number of times it is retried and the time between each retry can be configured. This retry mechanism will make resilient to intermittent issues. If it still fails after retry attempts have been exhausted it will be moved to a dead letter queue. This will allow other messages for the same ODS code to come through and hopefully succeed.

    1.1. New messages on the DLQ will trigger a Lambda function

    1.2. The Lambda function will attempt to write the message to Dynamo so we will keep a record of it.

    1.3. And fire a notification to inform someone that the message couldn't be processed.

2. DoS API Gateway returns a potentially intermittent error (429 or 5xx).
If the DoS API Gateway returns a 429 or a 5xx error the message, the event sender will update a record in the Dynamo DB to say there is an issue with the downstream system, it will also not remove the message from the queue so it can be retried when the downstream system is back up. The orchestrator checks this status before processing next batch of messages and if it finds there is an error, it pauses execution for a configured time and then sends a health check message to the event sender which is forwarded to the DoS API. If the healthcheck returns good then the Event Sender updates the Dynamo DB to say all is well and the orchestrator resumes sending change requests. If it is still down the orchestrator will repeat pausing and sending health checks until the service resumes. This solution ensures the system is resilient to temporary downstream outages. Messages will remain on the queue for up to 14 days or until the queue is full, which provides ample buffer for issues with the DoS Change request API to be resolved and processing continue without any intervention on the DI side.

![DoS Infrastructure](../diagrams/DoS%20Integration-Circuit%20Breaker.drawio.png "Dos Infrastructure")

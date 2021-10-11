# ADR-001: High-level design and tech stack

## Title

Option selection report - Technology for centralized messaging broker

* Date: 2021/09/30
* Status: Proposed
* Deciders: The DoS Integration team, the DoS Tech Strategy team, Daniel Stefaniuk

## Context

DI is a greenfiled project to share the service information between NHS.UK and UEC DoS...

Currently, the Profile updater receives data from NHS UK (once a day in CSV format) , validates this data and passes it to various downstream services (mainly DOS Services). The current solution has its own limitations like data won't reflect to the end user immediately. The proposed solution is based on Messaging Queue technology (publish/subscribe). This paper provides the available options and our recommendations. we are evaluating the options available as "Cloud native solutions/services"  which are  as follows

1. Use a combination of SNS (Simple Notification Service) and SQS (Simple Queue Service)
2. Use MSK (Amazon Managed Streaming for Apache Kafka)

Our decision is to move to MSK.

The rest of this paper discusses the requirements and provides further analysis of the options (pros and cons of the available options).

High level requirements:

* The solution must support the receiving of data in  real-time (JSON messages over APIs)
* The solution must provide a configurable short to mid term data storage to handle exceptions
* The solution must have the ability to replay messages in chronological or other orders - this is to recover from any failures during downstream data processing
* The solution must provide management information about the number of messages processed, failures, retries, latency and other management information

### Detailed analysis of the options

#### Option 1 - Use AWS SNS & SQS  Managed Service

In this solution, as the figure suggests, there are two components: SNS and SQS. The first service notifies that a new message is available for processing and the second component stores the message and makes it available for downstream processing systems. Once a message is processed by the downstream process, housekeeping is automatically performed to clear up the queue.

Pros:

* Both the solution components are managed services in AWS
* Easy to configure
* Faster time to value - we can start using this with very little effort
* Slightly cheaper infrastructure costs compared to MSK (to be confirmed based on volumes of messages)

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

## Decision

* Design: Use of AWS managed services, serverless design, data stream processing
* Tech Stack: Use of AWS MSK (Kafka), AWS CodePipeline, AWS CloudWatch & X-Ray

Based on the non-functional requirements, the MSK solution is a better fit to the overall solution. We decided to use the AWS MSK managed service to receive  messages from NHS.UK

![AWS MSK  Managed Service](../diagrams/DoS%20Integration%20-%20Infrastructure.png "AWS MSK Managed Service")

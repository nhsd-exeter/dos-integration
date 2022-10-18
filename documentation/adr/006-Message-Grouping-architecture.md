# ADR-006: Message Grouping Architecture

## Overview

Message Grouping Architecture - How can DI group change events into a single change event? So that only a single Change Event is sent to the DoS application.

* Date: 2022/10/17
* Status: Decided
* Deciders: Adi & Jack

## Context

NHS UK give DI multiple change events for each user session. This means DI receive multiple change events with the data changing incrementally between events. When a new cohort is introduced the first message received is the data is mostly incorrect with it being updated to the correct data in the following messages as the user progresses through the journey.

High level requirements:

* Change events are grouped into a single (latest) change event
* Most messages are grouped into a single change event within a reasonable time frame
*

### Detailed analysis of the options

#### Option 1 - SQS Message Deduplication for Grouping

This option is to use SQS Message Deduplication to group messages into a single change event by deduplicating SQS messages within a delay queue.  However this option is not possible as the deduplication only works for exactly 5 minutes. If we wanted to increase or decrease delay times messages would be lost or not grouped correctly.

#### Option 2 - DynamoDB Lock for Grouping

This option is to use DynamoDB Lock to group messages into a single change event by locking the odscode in DynamoDB. This lock would tell the message grouping lambda whether to send through the odscode to the delay queue. As the lock is released after the message is processed by the service matcher lambda the lock would be released and the next message for the odscode would be able to be processed.

Steps:

1. Change Event is received by the message grouping lambda
2. Change Event is added to message grouping dynamodb table
3. Check if odscode is locked in dynamodb (Message Grouping Lock table)
    1. If not locked:
        1. Add odscode is lock into DynamoDB (Message Grouping Lock table)
        2. Odscode is added to delay queue
    2. If locked:
        1. Odscode is not added to delay queue
4. Message is processed by service matcher lambda
5. Lock is released in DynamoDB (Message Grouping Lock table)
6. Latest change event for odscode is processed by service matcher lambda

Pros:

* Locking mechanism is reliable
* Locking time can be increased or decreased to suit the needs of the application
* Locking mechanism is scalable

Cons:

* Locking mechanism is complex
* Locking mechanism is not free (small cost for additional DynamoDB tables)

## Decision

**The decision was to go with option 2** as it is more flexible and scalable than option 1. This allows us to increase or decrease the locking time to suit the needs of the application such as if we wanted to increase the locking time to allow for more messages to be grouped into a single change event when a new cohort is introduced. Or decrease the locking time to allow for messages to be processed quicker such as in nonprod.

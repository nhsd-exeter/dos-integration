# ADR-010: Improve Application Performance

## Overview

How to improve DoS Integration's application performance to allow for multi-cohorts

* Date: 2023/04/12
* Status: Decided
* Deciders: DI Development Team

## Context

How can DI's application throughput be increased to support multi-cohorts. While keeping services processed in FIFO order (per cohort).

High level requirements:

* Cohort data is in FIFO order
* Application can handle large spikes of traffic such as around bank holidays
* Costs don't radically increase
* Architecture can be easily changed when new cohorts are ready to be on-boarded

### Constraints

If DI's performance is improved it is likely that Profile Manager's (PM) side will be the bottleneck for DoS Integration. Which will have to be rectified by PM's development team.

### Detailed analysis of the options

#### Option 1 - Remove orchestrator

This option is to remove the orchestrator and have the service matcher place the right queue for the service type which would then be pulled off by a service sync lambda for that specific cohort. The rate limiting for these service sync lambdas would be to use lambda max concurrency

Pros:

* DI's Performance can scale dramatically (1X - 1000X)
* Reduced code means less maintenance. Orchestrator is difficult to read and understand the message processing.
* No Additional Cost
* Easy to add new cohorts or add specific routes for DoS types

Cons:

* Slightly longer development time from option 1

#### Option 2 - Multiple orchestrators

Option two is to scale the Orchestrators so that there would be multiple orchestrators per cohort. This means that to work out performance the orchestrators would have to be 6X to for a rate per second. 6 Per second is the current maximum performance for the Orchestrator lambda.

Pros:

* Easy to implement, fast to market time

Cons:

* Continue to use an anti pattern
* Rate per second isn't crucial as DB usage is now the limiting factor
* A cost increase to improve performance (Each orchestrator costs about $65 per year)
* More difficult to add new routes for different DoS service types.

## Decision

**The decision was to go with option 1** as it can radically improve performance while taking away technical debt, it's the best of both worlds.

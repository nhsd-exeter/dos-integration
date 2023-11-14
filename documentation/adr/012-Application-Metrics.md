# ADR-012: Review of Application Metrics and how metrics are generated

## Overview

How to generate metrics? - What is the best process?, Costs least and is easiest to maintain.

* Date: 2023/11/14
* Status:
* Deciders: The DoS Integration development team


## Context

The DoS Integration project currently uses a Python library called aws-embedded-metrics to create metrics using AWS's system for generating metrics by embedding them into logs. However, an alternative cloud native option is to use AWS CloudWatch Metric Filters. Is our current approach the best for creating AWS CloudWatch metrics?

As well any decision can be used to inform any new applications that may be developed by this team in future.

High level requirements

* Generating Metrics should be cheap to create and store
* Generating Metrics should be maintainable
* CloudWatch Metrics work with Splunk

### Detailed analysis of the options

#### Option 1 - Maintain Metrics as Embedded Metrics

This option is to remain with aws-embedded-metrics as the way for generating metrics.

Pros:

* Metrics are co-located next to logs

Cons:

* Embedded metrics use an untyped library requiring the any type to be used
* Difficult to understand metrics class due to no types
* Requires an additional Python library which must be install and imported
* Library doesn't currently have 3.12 wheels which breaks the docker build when set to run in Python 3.12
* Library isn't well supported in comparison to aws-lambda-powertools which also have metric generating features.

#### Option 2 - Migrate Metrics to CloudWatch Metric Filters

This option is to replace the current Metric generation system with CloudWatch Metric Filters to generate the logs

Pros:

* CloudWatch Metric Filters are free
  * Note: Metrics themselves still cost money
* Allows earlier migration to Python 3.12
* Reducing application code increases performance of lambdas and application throughput
  * Reduces Python code complexity including unit test complexity
* Less logs created
  * Easier to analyse logs due to less clutter
* Doesn't require an additional Python library

Note: Reducing logs and lambda duration cost from estimates appears to reduces cost negligibly

Cons:

* Metrics code isn't co-located with logs
* Metrics are defined by JSON matching, if the matching criteria no longer matches the log then no metric will be created

## Decision

**The decision was made to go with option 2** as it provides many benefits such as reducing code complexity with few downsides. On of the downsides mentioned in this discussion is the chance for the metrics to be incorrectly set after a future change is made to ensure this doesn't happen the mitigation will be to add a new key on each log which suggests that the log is being used by a CloudWatch Metric Filter to reduce the likelihood of a breaking change.

As such we will now transition all generation of metrics to AWS CloudWatch Metric Filters and remove any related code to aws-embedded-metrics.

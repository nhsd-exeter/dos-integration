# ADR-012: Review of Application Metrics and how metrics are generated

## Overview


## Context


### Detailed analysis of the options

#### Option 1 - Maintain Metrics as Embedded Metrics



#### Option 2 - Migrate Metrics to CloudWatch Metric Filters

This option is to replace the current Metric generation system with CloudWatch Metric Filters to generate the logs

Pros:

* CloudWatch Metric Filters are free
  * Note: Metrics which are already a known for still cost money
* Allows earlier migration to Python 3.12
* Reducing Application code should increase performance of lambdas
  * Faster lambdas cost less
* Less logs created
  * Reduced Log Cost
  * Easier to analyse logs due to less clutter

Cons:

* Metrics code isn't co-located with logs

## Decision

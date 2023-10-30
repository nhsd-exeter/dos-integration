# ADR-011: Quality Checking

## Overview

How to ensure that DoS data is checked for quality

* Date: 2023/10/01
* Status: Decided
* Deciders: DI Development Team

## Context

How can DoS Integration check the data integrity and quality of the DoS Database.

High level requirements:

* Minimize database usage
* Minimize message latency

### Detailed analysis of the options

#### Option 1 - Improve current adhoc checking

This option is to improve the searching in the Service Matcher.

Pros:

* Quick to implement

Cons:

* Slows down message latency with each additional check

#### Option 2 - Create new all at once database checking solution

This option is to replace the DoS profiling checks in the Service Matcher with a new lambda that runs weekly to check the database.

Pros:

* Improves message latency by removing current checks
* New checks can be added without adding additional latency
* Easier to maintain as reporting is separate to other processes in the Service Matcher

Cons:

* Slows down deployment as an additional lambda must be built

## Decision

**The decision was to go with option 2** as it reduces the load of the DoS database and improves message latency.

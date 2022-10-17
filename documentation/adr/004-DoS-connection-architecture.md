# ADR-004: DoS Connection Architecture

## Overview

DoS Connection Architecture - How to improve throughput of the application? / How to remove the DoS Changes queue (events in changes table in a pending state)?

* Date: 2022/07/22
* Status: Decided
* Deciders: The DI development team / DoS team

## Context

A large of number of changes events caused an issue where changes were backed up with the DoS DB and then were not processed in a timely manner. This solution is to remove the DoS Changes queue (events in changes table in a pending state) so that it can never happen again.

High level requirements:

* To process a high number of changes events in a timely manner
* Changes events are process efficiently to reduce load/requests on the DoS DB

### Detailed analysis of the options

#### Option 1 - Tactical Solution - Improve DoS API Gateway

This option is to automatically approve the changes when they are received in the DoS Change Endpoint. Therefore the change queue is not required and won't be limiting the number of changes that can be processed.

Pros:

* No need to maintain a change queue
* Modification of a current system is easier and faster than building a new system

Cons:

* Maintaining a legacy system that will be replaced by a new system at some point to remove PHP from tech stack
* DI Team doesn't have knowledge of the DoS API Gateway, Changes Endpoint and the Save Endpoint.
* Lack of skills within the DI team to improve/fix the DoS API Gateway

### Option 2 - Strategic Solution - Connect directly to the DoS database

This option is to connect directly to the DoS database and process the changes directly.

Pros:

* No need to maintain a change queue
* New system will be able to process changes faster and more efficiently than the legacy Change Endpoint
* Understanding built when creating the new system will be helpful to the DI team
* Easier to upgrade the new system to include new data items

Cons:

* DI Team doesn't have much knowledge of the DoS database
* DI Team doesn't have knowledge of the DoS API Gateway, Changes Endpoint and the Save Endpoint so a bit of work is required to get the new system to connect to the DoS database and understand the data structures
* DI is tighter coupled to the DoS database.

## Decision

**The decision was to go with option 2 using the strategic solution** as it was the most compatible with the project and team. The benefits of option 1 were the development time would be shorter and easier to develop but after an experiment it uncovered some issues with the way the change endpoint behaved. So it was decided that it was more beneficial to build option 2 rather than fix option 1.

The team were happy with this decision as more of the DI process is now under DI Team's control and they will be more confident in the new system.

## Glossary

DoS API Gateway - The DoS API Gateway is the main entry point for the DoS integration project. Nginx is used to proxy the requests to the DoS API.

Changes Endpoint - The Changes Endpoint is the API that the DoS API Gateway proxies to.

Note: DoS API Gateway and Changes Endpoint may be used inter-changeably in some cases. As the process is colloquially known as the "DoS API Gateway" despite being a multilayered endpoints.

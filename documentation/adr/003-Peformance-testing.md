# ADR-003: Performance Testing

## Overview

Performance Testing - What tool to use to performance test?

* Date: 2021/12/25
* Status: Decided
* Deciders: The DI development team

## Context

The dos integration project needs a reporting solution to inform DoS Leads and other stakeholders about the comparison of data between DoS and NHS UK.

High level requirements:

* Can it test the performance of the following?
  * DoS Integration Endpoint (Max connection, response times)
  * Throughput (Change Event to Change Request delay)
  * Database (Connection on the database, are we overloading the database?)

### Detailed analysis of the options

#### Option 1 - Locust Performance Testing Tool

This option is to use the python tool Locust to run performance tests.

Pros:

* Python based tool which is the main programming language for this project
* DoS Team know python and use it in their projects
* Locust is hackable allowing to tracking of any python command or external process
* Plugins to monitor Kafka, etc

Cons:

* Have to use external projects to create improved graphs
* Runs on a single thread so may have to use multiple worker instances to get high requests per second

### Option 2 - JMeter and Gatling Performance Testing Tools

This option is to use either JMeter or Gatling to run performance tests. These tools are both similar in they use a form of Java for their performance tests and has been grouped together for that reason.

Pros:

* Nice looking graphs and reports
* Gatling has been used on other projects

Cons:

* Adds another programming language to the tech stack
* DI team have limited skills and knowledge of Java
* DoS team would have to maintain another performance testing tool
* Request based performance testing, difficult to track change event to change request throughput time

## Decision

**The decision was to go with option 1 using locust** as it is the most compatible with the project and team. Being the tool is Python and open source it can be exploited to be the most suitable to performance test tool for testing throughput of the DI application.

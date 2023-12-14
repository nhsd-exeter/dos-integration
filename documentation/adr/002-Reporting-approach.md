# ADR-002: Reporting approach

## Overview

Reporting Approach - How to report, send reports and alert to slack

* Date: 2021/11/12
* Status: Decided
* Deciders: The full DoS Integration team

## Context

The dos integration project needs a reporting solution to inform DoS Leads and other stakeholders about the comparison of data between DoS and NHS UK.

High level requirements:

* The ability to create reports
* Reports can be sent via email to pre-decided list of email addresses
* When reports are generated a notification is sent and received in Slack
* Multiple people in the team can create/edit reports (Not limited to point of failure)

### Detailed analysis of the options

#### Option 1 - Splunk Reporting, Emailing and Alerting

This option uses Cloud Splunk as a platform for reporting. Using all their features such as generating reports, emailing reports and alerting from Splunk.

Pros:

* Splunk is a well used product/platform so no platform validation is required to confirm it works.
* Anyone with permissions can create reports (devs, tests, BAs, ect)
* An all in one platform does all what we want
* Simple to write new reports
* Already have a similar solution from the DoS Team. So there is experience in the DoS Products if we require some help.
* A corporate solution which is paid for by NHS Digital. No money taken out of DoS Integration team's budget.
* New reports can be created quickly and adhoc

Cons:

* Difficult to get access to Splunk. Slow and very restrictive permissions.
* Splunk’s limited job search rate
* To generate a report the user must understand how to write Splunk queries
* Control of our reporting is in Splunk's hands
* Logs may not reach Splunk (very low possibility)
* Splunk holds log data for only two years (another storage method is needed for longer than two years)

### Option 2 - Use AWS Services for Reporting, Emailing and Alerting

This option is to use a range of AWS services to store logs, report, email and alert. Such as S3, Athena, EventBridge, Lambda and SES. This isn't a definitive list but some possible services that can be used to create the solution.

Pros:

* Control over infrastructure and reporting (we create and control what we require)
* We can use Python to create whatever kinds of reports we want CSV, PDF and graphs. All report data/format is within DoS Integration team's control.
* 100% of logs in storage mechanism. (Less chance of log not reaching log storage)
* Keep logs for longer than two years

Cons:

* Need a pipeline to deploy reporting infrastructure (This pipeline would increase development time)
* Additional Texas permissions required to trigger reports (Texas may not give us such permission)
* A lengthy process to create a report. A developer is required to create each report and must be tested.
* Requires multiple AWS Services that must be put into infrastructure as code. Which must be maintained.
* Reporting solution must be paid for by our team. Money taken out of our budget

## Decision

**The decision was made to go with option 1** using Splunk as our reporting platform with all its features. As it would effect delivery time least, allow most people to get permissions to create and share adhoc reports.

However we are going for a fast fail approach where if Splunk as our reporting platform can't do what we required or we can't get permissions we will switch to using option 2.

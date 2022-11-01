# ADR-005: Email Sending Architecture

## Overview

Email Sending Architecture - How can DI send emails to users in a timely, asynchronous and reliable manner?

* Date: 2022/09/01
* Status: Decided
* Deciders: Adi & Jack

## Context

Under certain circumstances DI needs to be able to email users to notify them of events. In this case it is when a DoS user had pending changes which DI has rejected.

High level requirements:

* To process send emails in a timely manner
* Emails are sent asynchronously to rest of the application
* Emails aren't sent in non-production environments

### Detailed analysis of the options

#### Option 1 - Use NHS Mail (SMTP connection)

This option is to use NHS Mail to send emails. This is the current method used by the DoS application.

Pros:

* We need a NHS Email address anyway so why not use it to send emails
* No cost to DI to use NHS Mail

Cons:

* Requires a NHS Email address to be created with SMTP access which can often be a slow process
* Relies on NHS Mail working which is a Microsoft 365 service therefore Microsoft Azure is required to be available and working
* Need to change password for NHS Email address when it expires every year meaning so there will be temporary interruption in emails being sent between the password change and the new password being set in secrets manager

### Option 2  - Use AWS SES (Boto3 Connection)

This option is to use AWS SES to send emails. SES is a service provided by AWS which allows you to send emails which pretends to be from your own domain meaning that it doesn't rely on NHS Mail after it has been set up.

Pros:

* Reliable as built on AWS
* Password change won't cause downtime as it doesn't rely on NHS Mail
* Simulator mailbox can be used to test emails are being sent

Cons:

* A slight cost to DI to use AWS SES
* Difficult to set up to have the emails appear to be from the NHS domain

## Decision

**The decision was to go with option 2** as it is more reliable and doesn't rely on NHS Mail. Also the cost of using AWS SES is minimal but provides us with a better interface to send emails using boto3. The simulator mailbox is also a nice feature to have to test emails are being sent.

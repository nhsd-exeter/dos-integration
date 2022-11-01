# ADR-009: Live Environments Shared Resources

## Overview

Live Environments Shared Resources - How to share resources between live environments?

* Date: 2022/10/18
* Status: Decided
* Deciders: Adi & Jack

## Context

How to share resources between live environments? So that we can swap between environments without losing data.

High level requirements:

* Persistent data must be shared between environments
* Shared resources must be configurable by Infrastructure as Code (IaC)
* Shared resources must be accessible by all live environments

### Detailed analysis of the options

#### Option 1 - Shared Resources between environments

This option is to have shared resources between environments. This means that the resources are created once and then used by all environments. So any resources that are already created will have to be migrated to a new terraform stack and state to allow it to be remove from blue/green environments. Shared resources that use KMS encryption will need to be migrated to a new shared KMS key and using Terraform outputs to allow the new KMS key to be used by the blue/green environments.


## Decision

**The decision was to go with option 1** as it was the only feasible plan to ensure persistent data was retained between environments. This allows us to have shared resources between environments so we can swap between environments without losing data.

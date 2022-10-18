# ADR-007: Live Environments Versioning

## Overview

Live Environments Versioning - How to version the live environment of the DI application?

* Date: 2022/10/18
* Status: Decided
* Deciders: Adi & Jack

## Context

How to version the live environment of the DI application? So that we can deploy changes to the live environment without affecting the current live version.

High level requirements:

* DI team must know which version of the application is live and in use at any given time
* Reports must be able to be run on any version of the application

### Detailed analysis of the options

#### Option 1 - Static Environments (Blue/Green)

This option is to have two static environments (Blue/Green) that are used for the live environment. When a new version of the application is ready to be deployed to the live environment the current live environment is swapped with the new environment. This means that the current live environment is now the new environment and the new environment is now the live environment. This means either the blue or green environment is in use and would have to be tracked somewhere so new deployments are made to the other environment.

With this way of working to upgrade an environment the IaC (Infrastructure as Code) must be run on an already deployed environment.

#### Option 2 - Dynamic Environments (1.0, 2.0, 4.0)

This option is to have multiple environments that can be used and swapped to if required. Such as the current Live version, rollback version and a version ready for the next release. The live version will also be documented but as version is a number it will be easier to remember which version is live.

With this way of working to upgrade an environment the IaC (Infrastructure as Code) won't be run on existing environments meaning the code doesn't need to be backwards compatible. This reduces the complexity of the IaC and testing required.

## Decision

**The decision was to go with option 2** as it is more flexible and scalable than option 1. This allows us to have multiple environments that can be used and swapped to if required so we could scale to as many environments as required. By not having to run the IaC on existing environments it reduces deployment time and complexity of the IaC.

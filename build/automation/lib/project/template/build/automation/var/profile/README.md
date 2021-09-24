# Profile

## Overview

Profile is a list of configuration options specific to an environment expressed as `make`/`shell` variables. The expectation is that there is a one to one mapping between a profile and an environment with an exception to the `dev` profile that is used as well to derive settings for environments created from the task branches.

## Defaults

* `local` - local development profile
* `dev` - shared development profile that runs on every commit in the CI pipeline or used for the cleanup
* `test` - test profile that runs nightly in the CI pipeline
* `demo` - production, UX
* `live` - production, service
* `tools,tools-nonprod,tools-prod` - CI/CD execution environment

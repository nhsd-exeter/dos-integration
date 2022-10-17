# Profile

## Overview

Profile is a set of configuration options specific to an environment expressed as `make` variables. The expectation is that there is a one to one mapping between a profile and an environment with an exception to the `dev` profile that is used as well to derive settings for environments created from the other branches, e.g. `task/*`.

## Defaults

* `local` - local development profile (Not attached to an AWS Account)
* `task` - a specific environment for branches. This should be default for creating non-prod infrastructure (AWS Non-prod Account)
* `dev` - shared development profile that supports automation on every commit to the remote main branch in the CI pipeline or it is used for a clean up jobs (AWS Non-prod Account)
* `test` - test profile that runs nightly in the CI pipeline (AWS Non-prod Account)
* `demo` - production, UX (AWS Prod Account)
* `live` - production, service (AWS Prod Account)
* `tools,tools-nonprod,tools-prod` - CI/CD execution environment
* `perf` - a profile for performance testing which uses the DoS Perf DB (AWS Non-prod Account)

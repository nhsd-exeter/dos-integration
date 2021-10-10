# Profile

## Overview

Profile is a set of configuration options specific to an environment expressed as `make` variables. The expectation is that there is a one to one mapping between a profile and an environment with an exception to the `dev` profile that is used as well to derive settings for environments created from the other branches, e.g. `task/*`.

## Defaults

* `local` - local development profile
* `dev` - shared development profile that supports automation on every commit to the remote master branch in the CI pipeline or it is used for a cleanup
* `test` - test profile that runs nightly in the CI pipeline
* `demo` - production, UX
* `live` - production, service
* `tools,tools-nonprod,tools-prod` - CI/CD execution environment

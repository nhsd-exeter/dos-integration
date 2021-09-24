# Jenkins

## Setup

### Prerequisites

For the Make DevOps automation scripts to function properly the following environment variables have to be set.

- Manage Jenkins - Configure System - Global properties
  - `AWS_ACCOUNT_ID_MGMT`
  - `AWS_ACCOUNT_ID_NONPROD`
  - `AWS_ACCOUNT_ID_PROD`
  - `AWS_ACCOUNT_ID_LIVE_PARENT`

### Pipelines

Here are the items to consider and a pattern for setting up a Jenkins pipeline.

- Item name: `$(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)-development|test|tag|production|cleanup`
- Display name: `Project Name (Development|Test|Tag|Cleanup)` or just `Project Name` for the production deployment
- Branch Sources - Git - Project Repository
- Branch Sources - Git - Credentials
- Branch Sources - Git - Behaviours:
  - `Discover branches`
  - `Check out to matching local branch`
  - `Filter by name (with wildcards)`, e.g. `master`, `task/*`
- Build Configuration - Script Path: `build/jenkins/Jenkinsfile.development|test|tag|production|cleanup`

For production

- Branch Sources - Git - Behaviours:
  - `Discover tags` only
- Branch Sources - Git - Build strategies:
  - `Tags`, `Ignore tags older than` set to 1
- Scan Multibranch Pipeline Triggers - Periodically if not otherwise run
  - Interval set to `1 minute`

## GitHub Integration

For an integration with a GitHub repository make use of the GitHub Apps, i.e. the `Texas Jenkins (read-only)`.

- Branch Sources - GitHub - Credentials - GHApp
- Branch Sources - GitHub - Repository HTTPS URL

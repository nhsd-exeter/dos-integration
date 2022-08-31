# DoS Integration

## Table of Contents

- [DoS Integration](#dos-integration)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
    - [DI Confluence Page](#di-confluence-page)
    - [Architecture](#architecture)
    - [Technology Stack](#technology-stack)
  - [Quick Start](#quick-start)
    - [Development Requirements](#development-requirements)
    - [Clone Repository](#clone-repository)
    - [AWS Authentication](#aws-authentication)
    - [Mac setup](#mac-setup)
  - [Contributing](#contributing)
  - [Development](#development)
    - [Add IP Address to IP Allow List](#add-ip-address-to-ip-allow-list)
    - [DoS Database Connection](#dos-database-connection)
    - [Code Formatting](#code-formatting)
    - [Code Quality](#code-quality)
  - [Testing](#testing)
    - [Unit Testing](#unit-testing)
    - [Integration Testing](#integration-testing)
    - [Performance Testing](#performance-testing)
    - [Test data and mock services](#test-data-and-mock-services)
    - [Manual check](#manual-check)
  - [General Deployment](#general-deployment)
    - [API Key](#api-key)
    - [Artefacts Versioning](#artefacts-versioning)
    - [CI/CD Pipelines](#cicd-pipelines)
    - [Deployment From the Command-line](#deployment-from-the-command-line)
    - [Branching Strategy](#branching-strategy)
    - [Branch Naming for Automatic Deployments](#branch-naming-for-automatic-deployments)
    - [Branch Naming to not automatically deploy](#branch-naming-to-not-automatically-deploy)
      - [Quick Deployment](#quick-deployment)
    - [Remove Deployment From the Command-line](#remove-deployment-from-the-command-line)
    - [Remove deployment with commit tag](#remove-deployment-with-commit-tag)
    - [Remove deployment on Pull Request merge](#remove-deployment-on-pull-request-merge)
    - [Secrets](#secrets)
    - [AWS Access](#aws-access)
  - [Production Deployment](#production-deployment)
    - [Prerequisites](#prerequisites)
    - [How to deploy](#how-to-deploy)
      - [Example](#example)
  - [Creating Batch Comparison Reports](#creating-batch-comparison-reports)
      - [Dentists](#dentists)
  - [Architecture](#architecture-1)
    - [Data](#data)
    - [Authentication and Authorisation](#authentication-and-authorisation)
    - [Guiding Principles](#guiding-principles)
  - [Operation](#operation)
    - [Observability](#observability)
      - [Tracing Change events and requests Correlation Id](#tracing-change-events-and-requests-correlation-id)
    - [Cloud Environments](#cloud-environments)
    - [Runbooks](#runbooks)
  - [Product](#product)
    - [Communications](#communications)
    - [Documentation](#documentation)

## Overview

The NHS.uk website, and the DoS (Directory of Services) service are separate entities which both store a lot of the same important data about Pharmacies/Dentists and other health organisations around the UK. The management of these individual services therefore needs to update information in multiple places online to keep their data fully up to date for their users.

The DoS Integration project aims to keep any updates made on NHS.uk consistent with DoS by comparing any updates and creating any change requests needed to keep the information up to date.

### DI Confluence Page
https://nhsd-confluence.digital.nhs.uk/display/DI/DoS+Integration+Home

### Architecture

<img src="./documentation/diagrams/DoS Integration-Components.drawio.png" width="1024" /><br /><br />

### Technology Stack

The current technology stack is:

- Python - Main programming language
- AWS: Lambda, DynamoDB, API Gateway, Codepipeline, KMS, SQS
- Serverless Framework - (Where supported)
- Terraform - Infrastructure as code tool (Where serverless not supported)

## Quick Start

### Development Requirements

It is recommended to use either a macOS or Linux. If using a Windows machine it is highly recommended to run a VM using WSL2 to create a Linux environment to work with. Try not to use the Windows command line.

A mac is no longer required for basic development since task branches are automatically built on the push of a new commit. However the build/deploy commands currently are only designed to work with macOS.

This project contains a macOS environment which can be installed and setup that gives the user a wide range of tools useful for development. More info on this is in the mac setup section.

The main components you will need for *basic* development work, are your OS version of the below.

- A VPN Client (OpenVPN or Tunnelblick are 2 NHS Digital suggested options)
- Git
- Python (The project currenly runs on 3.9.7)
- AWS CLI
- Docker

### Clone Repository

Clone the repository

    git clone git@github.com:nhsd-exeter/dos-integration.git
    cd ./dos-integration

### AWS Authentication

Please, ask one of your colleagues for the AWS account numbers used by the project. You will use these as roles which you will assume from your account.

Instructions and tips for basic authentication for AWS can be found online. Any method that lets you authenticate and assume roles will work with this project.
https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html

There is also an automated method to setup AWS access within the mac setup. Once the mac stup scripts have been run, the following command can be used to choose and switch between AWS roles automatically.

    tx-mfa

### Mac setup

The following is equivalent to the `curl -L bit.ly/make-devops-macos-setup | bash` command.

    make macos-setup

There are configuration options that should be set before proceeding. The following command will ensure that tooling like `docker` and `git` are going to operate as expected, including local secret scanning and code formatting are enabled. Make sure you authenticated in the AWS non-prod account first before running `make setup`

    make setup

Please, ask one of your colleagues for the AWS account numbers used by the project. The next command will prompt you to provide them. This information can be sourced from a properly set up project by running `make show-configuration | grep ^AWS_ACCOUNT_ID_`

    make devops-setup-aws-accounts


## Contributing

Here is the list of the development practices that have to be followed by the team and the individual members:

- Only use single canonical branch **develop**. Any intermediate branch significantly increases the maintenance overhead of the repository.
- Apply the git rebase workflow and never merge from develop to a task branch. Follow the **squash-rebase-merge** pattern to keep the history linear and clean.
- Cryptographically sign your commits using **gpg** to ensure its content have not been tampered with.
- Format the summary message of your pull request (merge request) using the following pattern **"JIRA-XXX Summary of the change being made"** for complies and clarity as well as to enable tooling to produce release notes automatically.
- Announce your PR/MR on the development Slack channel to allow any team member to review it and to share the knowledge. A change can be merged only if all comments have been addressed and it has been **approved by at least one peer**. Make good use of paring/mobbing/swarming practices for collaborative coding.

Before starting any work, please read [CONTRIBUTING.md](documentation/CONTRIBUTING.md) for more detailed instructions.

## Development

### Add IP Address to IP Allow List

To find your public IP you can visit https://www.google.com/search?q=whats+my+ip

An IP Allowlist is kept in secrets manager for each environment (task, dev, live etc). The task environment list is used for each task environment deployed. The Secret Name for each is of the format

    uec-dos-int-XXXX-ip-addresses-allowlist

where XXXX is the name of the environment in lowercase. For most development work you only need to add your IP to the task and dev environments list.

You can also add your IP to the lists with a script.

Prerequisites (first setup only)

    make tester-build

To add an IP address to the IP allow lists, Ensure you're authenticated for access to AWS and run the following command.

    make update-all-ip-allowlists

To add an IP address to the IP allow lists and deploy the allow list to environment run the following command.The `PROFILE` delineates which environment to update with the latest IP allow list. Set `ENVIRONMENT` if you are changing an environment not linked to your branch

    make update-ip-allowlists-and-deploy-allowlist PROFILE=task

### DoS Database Connection

The following env vars are required for the project to establish a connection to the DoS database (or a replica).

DB_SECRET_NAME
DB_SERVER
DB_PORT
DB_NAME
DB_SCHEMA
DB_USER_NAME
DB_SECRET_KEY

To connect to the local postgres database use these connection

    Host = localhost
    Port = 5432
    Database = postgres
    Username = postgres
    Password = postgres
    Schema = postgres

### Code Formatting

Code quality checks can be done with the pip installed 'black' module and run with the command.
    python -m black --line-length 120

This is also wrapped in a function
To format the code run:
    make python-code-format FILES=./application
    make python-code-format FILES=./test

### Code Quality

Code quality checks can be done with the pip installed 'flake8' module and run with the command.
    python3 -m flake8 --max-line-length=120

This is also wrapped in a function:

    make python-linting

## Testing

List all the type of test suites included and provide instructions how to execute them

- Unit
- Integration
- Contract
- End-to-end
- Performance
- Security
- Smoke

How to run test suite in the pipeline

### Unit Testing

Unit testing is to test the functions within each lambda. This testing is done on the local system to where the commands are run e.g CLI, CI/CD Pipelines

This includes:This testing includes:

- Function calls
- Correct data types and data returned from function
- All paths tested of the application

This testing is generally done by a developer

To run unit tests run the following commands

    make tester-build
    make unit-test

For coverage run

    make coverage-report

The unit tests are run using pytest and coverage (both available to download via pip). If you want to run the unit tests without the setup, or want to target only certain files/folders you can run the tests in your own enviornment directly by going to the /application directory and running.

    python3 -m pytest --cov=. -vv

It is always a good idea to run the unit tests in the IMAGE enviornment for a final run-through to ensure they pass in the correct enviormental conditions.


### Integration Testing

Integration Testing is to test the functional capabilities of the individual component work together with mocks and partner services. Asserting that individual components can work in harmony together achieving the overall business goals. This testing is done on AWS to test the connection between components.

This testing includes:

- Limited use of Mocks
- Check data when passed between components
- Meets business needs of the application

This testing is generally done by a tester

Prerequisites

    tx-mfa
    Sign into Non-Prod VPN
    make tester-build

To run unit tests run the following commands

    make integration-test PROFILE=task TAGS=dev PARALLEL_TEST_COUNT=10

### Performance Testing

Performance testing is the practice of evaluating how a system performs in terms of responsiveness and stability under a particular workload. Performance tests are typically executed to examine speed, robustness, reliability of the application.

This testing includes:

- Checking non functional requirements (performance/reliability)

This testing is generally done by a tester

To run the performance tests run the following commands after you have run `tx-mfa` to sign into Non-Prod

To run a stress test

    make tester-build
    make stress-test PROFILE=perf ENVIRONMENT=perf START_TIME=$(date +%Y-%m-%d_%H-%M-%S)
    Wait for the test to complete
    make performance-test-data-collection PROFILE=perf ENVIRONMENT=perf START_TIME=[Start Time from above command] END_TIME=$(date +%Y-%m-%d_%H-%M-%S)

Note: if you have any errors consider reducing number of users or increasing the docker resources

To run a load test

    make tester-build
    make load-test PROFILE=perf ENVIRONMENT=perf START_TIME=$(date +%Y-%m-%d_%H-%M-%S)
    Wait for the test to complete
    make performance-test-data-collection PROFILE=perf ENVIRONMENT=perf START_TIME=[Start Time from above command] END_TIME=$(date +%Y-%m-%d_%H-%M-%S)

### Test data and mock services

- How the test data set is produced
- Are there any mock services in place

### Manual check

Here are the steps to perform meaningful local system check:

- Log in to the system using a well known username role

## General Deployment

### API Key

API Key(s) must be generated prior to external API-Gateways being set up. It is automatically created when deploying with `make deploy PROFILE=task`. However the dev, demo and live profiles' key must be manually generated prior to deployment.

### Artefacts Versioning

E.g. semantic versioning vs. timestamp-based

### CI/CD Pipelines

<img src="./documentation/diagrams/DevOps-Pipelines and Automations.drawio.png" width="1024" /><br /><br />

All `test`  Codebuild automations can be found in the AWS CodePipeline app in `Texas` `mgmt` account and included the following:

- uec-dos-int-tools-stress-test-stage
- uec-dos-int-tools-load-test-stage

More infromation can be on the DI confluence https://nhsd-confluence.digital.nhs.uk/display/DI/Code+Development+and+Deployment


### Deployment From the Command-line

    make build-and-deploy PROFILE=task # Builds docker images, pushes them and deploys to lambda

### Branching Strategy

More infromation can be on the DI confluence https://nhsd-confluence.digital.nhs.uk/display/DI/Code+Development+and+Deployment

<img src="./documentation/diagrams/DoS Integration-GitHub.drawio.png" width="1024" /><br /><br />



### Branch Naming for Automatic Deployments

For a branch to be automatically deployed on every push the branch must be prefixed with `task`. This will then be run on an AWS Codebuild stage to deploy the code to a task environment. e.g `task/DI-123_My_feature_branch`

Once a branch which meets this criteria has been pushed the it will run a build and deployment for the environment and notify the dos-integration-dev-status channel with the status of your deployment.

### Branch Naming to not automatically deploy

For a branch that is meant for testing or another purpose and you don't want it to deploy on every push to the branch. It must be prefixed with one of these `spike|automation|test|bugfix|hotfix|fix|release|migration`. e.g. `fix/DI-123_My_fix_branch`

#### Quick Deployment

To quick update the lambdas run the following command. Note this only updates the lambdas and api-gateway

    make sls-only-deploy PROFILE=task VERSION=latest

### Remove Deployment From the Command-line

    make undeploy PROFILE=task # Builds docker images, pushes them and deploys to lambda

### Remove deployment with commit tag

You can remove a task deployment using a single command to create a tag which then runs an AWS codebuild stage that will undeploy that environment

    make tag-commit-to-destroy-environment ENVIRONMENT=[environment to destroy] COMMIT=[short commit hash]
    e.g. make tag-commit-to-destroy-environment ENVIRONMENT=di-363 COMMIT=2bc43dd // This destroys the di-363 task environment

### Remove deployment on Pull Request merge

When a pull request is merged it will run an AWS Codebuild project that will destroy the environment if it exists.
The codebuild stage can be found within the development-pipeline terraform stack.

### Secrets

Where are the secrets located, i.e. AWS Secrets Manager, under the `$(PROJECT_ID)-$(PROFILE)/deployment` secret name and variable `$(DEPLOYMENT_SECRETS)` should be set accordingly.

### AWS Access

To be able to interact with a remote environment, please make sure you have set up your AWS CLI credentials and
MFA to the right AWS account using the following command

    tx-mfa

## Production Deployment

### Prerequisites

The production pipeline terraform stack must be deployed

    make deploy-deployment-pipelines PROFILE=tools ENVIRONMENT=dev

### How to deploy

To deploy an update/new version to a production environment the commit must be tagged using the command below. This will automatically run a Github web hook that will trigger an AWS Codebuild project that will deploy the environment based on the git tag.

Note: This should only be run against a commit on the main branch as the code has been built into an image and pushed to ECR. Also short commit hash is the first 7 characters of the commit hash.

To Deploy Demo

    make tag-commit-for-deployment PROFILE=demo ENVIRONMENT=demo COMMIT=[short commit hash]

To Deploy Live

    make tag-commit-for-deployment PROFILE=live ENVIRONMENT=live COMMIT=[short commit hash]

#### Example

    make tag-commit-for-deployment PROFILE=demo ENVIRONMENT=demo COMMIT=1b4ef5a

## Creating Batch Comparison Reports

Batch comparison reports can be generated for whole datasets at once. Pulling a complete dataset from NHS.uk and a DoS DB of choice.

#### Dentists

To run and generate the comparison reports for dentists. Ensure you are Authenticated to the correct AWS account and logged into the correct VPN for whichever DoS DB you are trying to use.

You can use a make command. Either specifying PROFILE, or a full set of DoS DB details.

    make create-dentist-reports PROFILE=dev

or

    make create-dentist-reports \
      DB_SERVER_NAME= server_name \
      DB_PORT=5432 \
      DB_NAME=name_of_the_db \
      DB_USER_NAME_SECRET_NAME=some_db_name \
      DB_USER_NAME_SECRET_KEY=some_key \
      DB_SECRET_NAME=secret_name_for_secret_manager \
      DB_SECRET_KEY=DB_USER_PASSWORD \
      DB_SCHEMA=pathwaysdos


These can also be run directly with Python if the required packages are installed. Ensure you have the needed enviornmental variables (DB_SERVER, DB_PORT, DB_NAME, DB_USER_NAME, DB_SECRET_NAME, DB_SECRET_KEY, DB_SCHEMA). From the application/ directory run the following python command.

    python3 comparison_reporting/run_dentist_reports.py

## Architecture

### Data

What sort of data system operates on and processes

- Data set
- Consistency and integrity
- Persistence

### Authentication and Authorisation

- Default user login for testing
- Different user roles
- Authorisation type
- Authentication method

It is recommended that any other documentation related to the aspect of security should be stored in a private workspace.



### Guiding Principles

List of the high level principles that a product /development team must adhere to:

- The solution has to be coded in the open - e.g. NHSD GitHub org
- Be based on the open standards, frameworks and libraries
- API-first design
- Test-first approach
- Apply the automate everything pattern
- AWS-based cloud solution deployable to the NHSD CPaaS Texas platform
- Use of the Make DevOps automation scripts (macOS and Linux)

## Operation

### Observability

- Logging
  - Indexes
  - Format
- Tracing
  - AWS X-Ray Trace Ids (These are included in logs)
  - `correlation-id` and `reference` (dos) provide a common key to track change events across systems: NHS UK Profile Editor, DoS Integrations, and DoS (Api Gateway)
- Monitoring
  - Dashboards
- Alerting
  - Triggers
  - Service status
- Fitness functions
  - What do we measure?

What are the links of the supporting systems?

#### Tracing Change events and requests Correlation Id

  To be able to track a change event and the change requests it can become across systems a common id field is present on logs related to each event. The id is generated in `Profile Editor` (NHS UK) which is then assigned to the `correlation-id` header of the request send to our (DoS Integration) endpoint, for a given change event. The `correlation-id` header is then used throughout the handling of the change event in `DoS Integration`.

  If a change event does result in change requests being created for `DoS` then the change requests have a `reference` key with the value being the correlation id.

  The events can be further investigated in DoS Integration process by using the X-Ray trace id that is associated with the log that has the correlation id.


### Cloud Environments

List all the environments and their relation to profiles

- Task
  - Profile: 'task'
- Dev
  - Profile: `dev`
- Demo
  - Profile: `demo`
- Live
  - Profile: `live`

### Runbooks

The runbooks for this project can be found on the DI confluence.
https://nhsd-confluence.digital.nhs.uk/display/DI/Runbooks

## Product

### Communications

- Slack channels
  - Getting Started (Private: Ask for invite) `di-get-started`
    - Handy tips on how to get started as part of the DoS Integration team
  - Full Development Team (Private: Ask for invite) `dos-integration-devs`
    - For team conversations and team notifications
  - Devs/Tests Only (Private: Ask for invite) `di-coders`
    - For technical conversation without distracting the non technical team members
  - Swarming Channel (Public) `dos-integration-swarming`
    - For team meetings and swarming sessions. Generally used for huddles.
- TO DO SLACK CHANNELS
  - CI/CD and data pipelines, processes, e.g. `[service-name]-automation`
  - Service status, e.g. `[service-name]-status`
- Email addresses in use, e.g. `[service.name]@nhs.net`

All of the above can be service, product, application or even team specific.

### Documentation

- Sprint board link

  <https://nhsd-jira.digital.nhs.uk/secure/RapidBoard.jspa?rapidView=3875>

  Note this sprint board requires permissions for both APU (PU project) and DI project

- Backlog link

  <https://nhsd-jira.digital.nhs.uk/secure/RapidBoard.jspa?rapidView=3875&view=planning&issueLimit=100>

- Roadmap

  <https://nhsd-confluence.digital.nhs.uk/display/DI/Roadmap>

- Risks register

  We have a risk register but not accessible/viewable by the development team. So if a new risk needs to be added the Delivery Manager is the best to talk to.

- Documentation workspace link

  Documentation is stored in the [documentation](documentation) folder

- Confluence

  A separate confluence space has been set up for the DoS Integration Project

  <https://nhsd-confluence.digital.nhs.uk/display/DI/DoS+Integration+Home>

- Definition of Ready/Done

  <https://nhsd-confluence.digital.nhs.uk/pages/viewpage.action?pageId=293247477>

- Ways of working

  <https://nhsd-confluence.digital.nhs.uk/display/DI/DI+Ways+of+Working>

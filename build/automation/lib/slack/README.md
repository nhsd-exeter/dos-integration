# Slack

## Channel Naming Convention

This is a list of default Slack channels to support development and service maintenance activities by automated notifications and daily activities. The intention is to introduce a consistent approach to ensure exceptional operational circumstances are handled well by the teams across the products family.

- `[project-name/project-id]-status-live` for any live component issue or notification that requires an immediate reaction by the team responsible for it
- `[project-name/project-id]-scheduled-jobs-[profile]` for automated scheduled jobs that execution is expected at a specific time for business or technical operations
- `[project-name/project-id]-pipeline-notifications-[profile]` for notifications of environment creations, pipeline failures and successfully deployments
- `[project-name/project-id]-release-notes` for automatically issuing release notes from git history and commit messages
- `[team-name]-dev` for day to day development discussions, e.g. pull request announcements and related technical conversations
- `[team-name]-swarming` for mob programming and swarming sessions

where

- `profile` is provides a set of environment configuration variables and its usage is described [here](https://github.com/nhsd-exeter/make-devops/blob/master/build/automation/lib/project/template/build/automation/var/profile/README.md).
- `project-name` should match the `$(PROJECT_NAME)` make variable defined in the `build/automation/var/project.mk` file, e.g. `integration` or `service-fuzzy-search-api`
- `project-id` should be used if more hierarchical naming convention needs to be in place, it is defined as `PROJECT_ID = $(PROJECT_GROUP_SHORT)-$(PROJECT_NAME_SHORT)` in the `build/automation/var/project.mk` file, e.g. `uec-dos-int`, `uec-dos-api-sfsa`
- `team-name` should match the the name of the team currently responsible for the project, e.g. `service-finder` or `dos-integration`

## Template message

Template messages are defined as `build/automation/lib/slack/*.json` files and can be used by

## Script Usage

    make slack-it \
      BUILD_STATUS=success \
      SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXXXXXXXX/YYYYYYYYYYY/ZZZZZZZZZZZZZZZZZZZZZZZZ

## Links

- [Your Apps](https://api.slack.com/apps/)
- [Sending your first Slack message using Webhook](https://api.slack.com/tutorials/slack-apps-hello-world)
- [Creating rich message layouts](https://api.slack.com/messaging/composing/layouts)

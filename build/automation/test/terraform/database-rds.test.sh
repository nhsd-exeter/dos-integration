#!/bin/bash

# Arrange
make project-create-infrastructure MODULE_TEMPLATE=rds STACK_TEMPLATE=rds STACK=database
make project-create-profile NAME=dev
cat << HEREDOC >> build/automation/var/profile/dev.mk
DB_INSTANCE = \$(PROJECT_GROUP_SHORT)-\$(PROJECT_NAME_SHORT)-\$(DB_NAME)-\$(PROFILE)
DB_PORT = 5432
DB_NAME = test
DB_USERNAME = test
HEREDOC

# Act
make terraform-apply-auto-approve STACK=database PROFILE=dev

# Assert
make terraform-output STACK=database PROFILE=dev TERRAFORM_REINIT=false OPTS="-json"
make terraform-show STACK=database PROFILE=dev TERRAFORM_REINIT=false OPTS="-json"

# Clean up
make terraform-destroy-auto-approve STACK=database PROFILE=dev

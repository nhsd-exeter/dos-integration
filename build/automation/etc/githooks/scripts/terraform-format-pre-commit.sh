#!/bin/bash

[ $(make project-check-if-tech-is-included-in-stack NAME=terraform) == false ] && exit 0

if [ "$PROJECT_NAME" == "$DEVOPS_PROJECT_NAME" ]; then
  if [ $(make git-check-if-commit-changed-directory DIR=build/automation/lib/terraform/template PRECOMMIT=true) == true ]; then
    if ! make -s terraform-fmt DIR=build/automation/lib/terraform/template OPTS="-check -list=false" 2> /dev/null; then
      tput setaf 202
      printf "\n\n  $(echo $0 | sed "s;$PWD/;;"): Please, format the Terraform files in 'build/automation/lib/terraform/template'\n"
      tput sgr0
      exit 1
    fi
  fi
fi
if [ $(make git-check-if-commit-changed-directory DIR=infrastructure PRECOMMIT=true) == true ]; then
  if ! make -s terraform-fmt DIR=infrastructure OPTS="-check -list=false" 2> /dev/null; then
    tput setaf 202
    printf "\n\n  $(echo $0 | sed "s;$PWD/;;"): Please, format the Terraform files in 'infrastructure'\n"
    tput sgr0
    exit 1
  fi
fi

# TODO: Add `make docker-run-terraform-tfsec`
# TODO: Add `make docker-run-terraform-checkov`
# TODO: Add `make docker-run-terraform-compliance`
# TODO: Add `make docker-run-config-lint`

exit 0

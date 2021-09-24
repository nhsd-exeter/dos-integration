# Terraform Stack: `rds`

## Description

This stack provisions RDS PostgreSQL.

## Dependencies

- `terraform-state` stack
- `networking` stack

## Usage

### Create an operational stack from the template

    make project-create-infrastructure MODULE_TEMPLATE=rds STACK_TEMPLATE=rds STACK=database PROFILE=dev

### Provision the stack

    make terraform-plan STACK=database PROFILE=dev
    make terraform-apply-auto-approve STACK=database PROFILE=dev

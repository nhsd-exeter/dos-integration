#!/bin/bash
set -e

[ $(make project-check-if-tech-is-included-in-stack NAME=python) == false ] && exit 0

make python-run-ruff-checks

exit 0

#!/bin/bash
set -e

[ $(make project-check-if-tech-is-included-in-stack NAME=python) == false ] && exit 0

if [ $(make git-check-if-commit-changed-directory DIR=application PRECOMMIT=true) == true ]; then
  make -s python-code-format python-code-check \
    FILES=application
fi

if [ $(make git-check-if-commit-changed-directory DIR=test PRECOMMIT=true) == true ]; then
  make -s python-code-format python-code-check \
    FILES=test
fi

exit 0

#!/bin/bash
set -e

git secrets --pre_commit_hook -- "$@"

exit 0

#!/bin/bash
set -e
# Remove all local tags
git tag -l | xargs git tag -d
# Get remote tags
git fetch

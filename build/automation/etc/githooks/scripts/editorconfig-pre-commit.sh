#!/bin/bash
set -e

make -s docker-run-editorconfig \
  DIR="$PWD"

exit 0

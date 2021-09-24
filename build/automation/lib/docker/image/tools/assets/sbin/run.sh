#!/bin/bash
set -e

if [ $# -gt 0 ]; then
  exec $trace $gosu "$@"
fi

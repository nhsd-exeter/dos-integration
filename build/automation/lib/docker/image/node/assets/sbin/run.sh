#!/bin/bash
set -e

if [ $# -eq 0 ]; then
  exec $trace $gosu node app.js
else
  exec $trace $gosu "$@"
fi

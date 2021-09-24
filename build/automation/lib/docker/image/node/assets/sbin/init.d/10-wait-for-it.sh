#!/bin/bash
set -e

if [ -n "$WAIT_FOR" ]; then
  echo "Waiting for '$WAIT_FOR' to be avialable"
  /sbin/wait-for-it.sh $WAIT_FOR -- echo "'$WAIT_FOR' is up"
fi

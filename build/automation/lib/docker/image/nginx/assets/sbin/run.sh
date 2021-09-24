#!/bin/bash
set -e

if [ $# -gt 0 ]; then
  exec $trace $gosu "$@"
else
  exec $trace $gosu nginx -c /etc/nginx/nginx.conf -g "daemon off;"
fi

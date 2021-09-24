#!/bin/bash
set -e

if [ "gunicorn" == "$1" ]; then
  exec $trace $gosu gunicorn \
    -w 8 \
    --bind 0.0.0.0:8443 \
    --certfile /certificate/certificate.crt \
    --keyfile /certificate/certificate.key \
    --ssl-version 5 \
    $APP.wsgi
elif [ $# -gt 0 ]; then
  exec $trace $gosu "$@"
fi

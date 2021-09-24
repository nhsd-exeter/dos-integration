#!/bin/bash
set -e

if [ "elasticsearch" == "$1" ] || [ $# -eq 0 ]; then
  export ELASTICSEARCH_DAEMON_USER=$SYSTEM_USER
  export ELASTICSEARCH_DAEMON_GROUP=$SYSTEM_USER
  exec /opt/bitnami/scripts/elasticsearch/entrypoint.sh /opt/bitnami/scripts/elasticsearch/run.sh
elif [ $# -gt 0 ]; then
  exec $trace $gosu "$@"
fi

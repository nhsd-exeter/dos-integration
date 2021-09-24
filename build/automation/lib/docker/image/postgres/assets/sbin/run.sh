#!/bin/bash
set -e

function run_psql() {
  [[ "$ON_ERROR_STOP" =~ ^(false|no|off|0|FALSE|NO|OFF)$ ]] && ON_ERROR_STOP=0 || ON_ERROR_STOP=1
  $trace $gosu psql \
    --set ON_ERROR_STOP=$ON_ERROR_STOP \
    postgres://${DB_USERNAME}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}?sslmode=require \
    "$@"
}

if [ "sql" == "$1" ]; then
  sql="$2"
  echo "Running SQL: $sql"
  run_psql -c "$sql"
elif [ "script" == "$1" ] || [ "scripts" == "$1" ]; then
  # Process arguments
  ([ -n "$2" ] && [[ $2 != --run-as* ]]) && dir=$2 || dir=/data
  for arg in "$@"; do
      if [[ $arg = --run-as-connection-details-prefix=* ]]; then
        connection_details_prefix=$(echo $arg | sed "s;--run-as-connection-details-prefix=;;g")
      fi
      if [[ $arg = --run-as-script-name-pattern=* ]]; then
        script_name_pattern=$(echo $arg | sed "s;--run-as-script-name-pattern=;;g")
      fi
  done
  i=0
  # Run scripts
  for file in $dir/*; do
    (
      # Check for alternative connection details
      for item in $(echo $script_name_pattern | sed "s;,; ;g"); do
          if [[ $file = *$item* ]]; then
            DB_NAME=$(eval echo "\$${connection_details_prefix}_NAME")
            DB_USERNAME=$(eval echo "\$${connection_details_prefix}_USERNAME")
            DB_PASSWORD=$(eval echo "\$${connection_details_prefix}_PASSWORD")
          fi
      done
      echo "Running script: '$file'"
      [[ $file == *.sql ]] && run_psql -f $file
      [[ $file == *.sql.gz ]] && gunzip -c $file | run_psql
      echo
    )
    i=$((i+1))
  done
  if [ $i -eq 0 ]; then
    echo "ERROR: No script found"
    exit 1
  fi
elif [ "postgres" == "$1" ] || [ $# -eq 0 ]; then
  export POSTGRES_DB=$DB_NAME
  export POSTGRES_USER=$DB_USERNAME
  export POSTGRES_PASSWORD=$DB_PASSWORD
  exec /usr/local/bin/docker-entrypoint.sh postgres -c config_file=/etc/postgresql/postgresql.conf
elif [ $# -gt 0 ]; then
  exec $trace $gosu "$@"
fi

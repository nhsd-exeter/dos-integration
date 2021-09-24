#!/bin/bash
set -e

export DB_HOST=${DB_HOST:-postgres}
export DB_PORT=${DB_PORT:-5432}
export DB_NAME=${DB_NAME:-postgres}
export DB_USERNAME=${DB_USERNAME:-postgres}
export DB_PASSWORD=${DB_PASSWORD:-postgres}

# Configure
[[ "$DEBUG" =~ ^(true|yes|on|1|TRUE|YES|ON)$ ]] && set -x
[[ "$TRACE" =~ ^(true|yes|on|1|TRUE|YES|ON)$ ]] && export trace="strace -tt -T -v -s 65536 -f"
([[ "$GOSU" =~ ^(false|no|off|0|FALSE|NO|OFF)$ ]] || [ $(id -u) -ne 0 ]) && export gosu="" || export gosu="gosu $SYSTEM_USER"
# Run init scripts
for file in /sbin/init.d/*; do
  case "$file" in
    *.sh)
      source $file "$@"
      ;;
  esac
done
# Run main process
source /sbin/run.sh

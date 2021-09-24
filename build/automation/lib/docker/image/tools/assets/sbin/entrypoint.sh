#!/bin/bash
set -e

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

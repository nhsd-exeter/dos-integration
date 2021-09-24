#!/bin/bash
set -e

function main() {
  if [ "scripts" == "$1" ]; then
    replace_variables_in_scripts "$@"
  elif [ "postgres" == "$1" ] || [ $# -eq 0 ]; then
    replace_variables_in_postgres
  fi
  set_file_permissions
}

function replace_variables_in_scripts() {
  dir=${2:-/data}
  for file in $dir/*; do
    [ -f $file ] && _replace_variables $file ||:
  done
}

function replace_variables_in_postgres() {
  for file in /docker-entrypoint-initdb.d/*; do
    [ -f $file ] && _replace_variables $file ||:
  done
}

function set_file_permissions() {
  am_i_root && chmod 0600 /etc/postgresql/certificate.* ||:
  am_i_root && chown -R $SYSTEM_USER_UID:$SYSTEM_USER_GID /etc/postgresql ||:
}

function _replace_variables() {
  file=$1
  echo "Replace variables in '$file'"
  for str in $(cat $file | grep -Eo "[A-Za-z0-9_]*_TO_REPLACE" | sort | uniq); do
    key=$(cut -d "=" -f1 <<<"$str" | sed "s/_TO_REPLACE//g")
    value=$(echo $(eval echo "\$$key"))
    [ -z "$value" ] && echo "WARNING: Variable $key has no value in '$file'" || sed -i \
      "s;${key}_TO_REPLACE;${value//&/\\&};g" \
      $file ||:
  done
}

function am_i_root() {
  if [ $(id -u) -eq 0 ]; then
      true
  else
    false
  fi
}

main "$@"

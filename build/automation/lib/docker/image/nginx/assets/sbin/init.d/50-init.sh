#!/bin/bash
set -e

DOMAIN=${DOMAIN:-localhost}

function main() {
  prepare_configuration_files
  set_file_permissions
}

function prepare_configuration_files() {
  if [ -n "$REVERS_PROXY_UI_HOST" ] && [ -n "$REVERS_PROXY_API_HOST" ]; then
    config="reverse-proxy"
  else
    config="default"
  fi
  for template in $(ls -1 /etc/nginx/*.conf.template /etc/nginx/conf.d/$config.conf.template 2> /dev/null); do
    file=$(echo $template | sed "s;.template;;g")
    cp -fv $template $file
    _replace_variables $file
  done
}

function set_file_permissions() {
  chown $SYSTEM_USER_UID:$SYSTEM_USER_GID \
    "$(readlink /dev/stderr)" \
    "$(readlink /dev/stdout)"
  chown $SYSTEM_USER_UID /var/run
  chown -R $SYSTEM_USER_UID:$SYSTEM_USER_GID \
    /certificate/* \
    /var/cache/nginx
  chmod 400 /certificate/*
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

main "$@"

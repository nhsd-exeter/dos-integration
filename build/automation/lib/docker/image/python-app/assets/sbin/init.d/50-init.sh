#!/bin/bash
set -e

function main() {
  set_file_permissions
  set_application_directory
}

function set_file_permissions() {
  chown -R $SYSTEM_USER_UID:$SYSTEM_USER_GID /certificate/*
  chmod 400 /certificate/*
}

function set_application_directory() {
  if [ -z "$APP" ]; then
      dir=$(ls -1 -d */ | head -n 1)
      export APP=${dir%?}
  fi
}

main "$@"

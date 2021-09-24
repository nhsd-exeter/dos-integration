#!/bin/bash
set -e

function main() {
  set_file_permissions
}

function set_file_permissions() {
  chown -R $SYSTEM_USER_UID:$SYSTEM_USER_GID /certificate/*
  chmod 400 /certificate/*
}

main "$@"

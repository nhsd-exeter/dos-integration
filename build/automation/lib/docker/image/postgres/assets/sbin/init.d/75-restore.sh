#!/bin/bash
set -e

if [ -f /var/lib/postgresql/backup.tar.gz ]; then
  rm -rf /var/lib/postgresql/data/*
  tar -zxvf /var/lib/postgresql/backup.tar.gz -C /var/lib/postgresql/data
fi

#!/bin/sh

name="unknown"
version="unknown"

# Debian family
if [ -f /etc/debian_version ]; then
  id=$(cat /etc/os-release | grep "^ID=" | awk -F= '{ print $2 }')
  if [ "$id" = "debian" ] || [ "$id" = "raspbian" ]; then
    name=$id
    version=$(cat /etc/debian_version)
  else
    name=$(cat /etc/lsb-release | grep "^DISTRIB_ID" | awk -F= '{ print $2 }')
    version=$(cat /etc/lsb-release | grep "^DISTRIB_RELEASE" | awk -F= '{ print $2 }')
  fi

# RedHat family
elif [ -f /etc/redhat-release ]; then
  name=$(cat /etc/redhat-release | sed s/\ release.*// | tr "[A-Z]" "[a-z]")
  echo "$name" | grep -q red && name="redhat"
  echo "$name" | grep -q centos && name="centos"
  echo "$name" | grep -q scientific && name="scientific"
  version=$(cat /etc/redhat-release | sed s/.*release\ // | sed s/\ .*//)

# Alpine
elif which apk > /dev/null 2>&1; then
  name=alpine
  version=$(cat /etc/alpine-release)

# BusyBox
elif which busybox > /dev/null 2>&1; then
  name=busybox
  version=$(busybox | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
fi

printf "\"filesystem\":{\"name\":\"$(printf $name | tr [A-Z] [a-z])\",\"version\":\"$(printf $version | tr [A-Z] [a-z])\"}"

#!/bin/bash

function system_detect() {

  # Set defalut values
  SYSTEM_NAME=$(uname)
  SYSTEM_DIST="unknown"
  SYSTEM_DIST_BASED_ON="unknown"
  SYSTEM_PSEUDO_NAME="unknown"
  SYSTEM_VERSION="unknown"
  SYSTEM_ARCH=$(uname -m)
  SYSTEM_ARCH_NAME="unknown" # Can be "i386" or "amd64" or "arm64"
  SYSTEM_KERNEL=$(uname -r)
  SYSTEM_CONTAINER=""

  # Detect if MacOS is in use
  if [[ "$OSTYPE" == "darwin"* ]]; then

    SYSTEM_NAME="unix"
    SYSTEM_DIST="macos"
    SYSTEM_DIST_BASED_ON="bsd"
    [[ $(sw_vers -productVersion | \grep 10.10 | wc -l) -gt 0 ]] && SYSTEM_PSEUDO_NAME="Yosemite"
    [[ $(sw_vers -productVersion | \grep 10.11 | wc -l) -gt 0 ]] && SYSTEM_PSEUDO_NAME="El Capitan"
    [[ $(sw_vers -productVersion | \grep 10.12 | wc -l) -gt 0 ]] && SYSTEM_PSEUDO_NAME="Sierra"
    [[ $(sw_vers -productVersion | \grep 10.13 | wc -l) -gt 0 ]] && SYSTEM_PSEUDO_NAME="High Sierra"
    [[ $(sw_vers -productVersion | \grep 10.14 | wc -l) -gt 0 ]] && SYSTEM_PSEUDO_NAME="Mojave"
    [[ $(sw_vers -productVersion | \grep 10.15 | wc -l) -gt 0 ]] && SYSTEM_PSEUDO_NAME="Catalina"
    [[ $(sw_vers -productVersion | \grep 11. | wc -l) -gt 0 ]] && SYSTEM_PSEUDO_NAME="Big Sur"
    [[ $(sw_vers -productVersion | \grep 12. | wc -l) -gt 0 ]] && SYSTEM_PSEUDO_NAME="Monterey"
    SYSTEM_VERSION=$(sw_vers -productVersion)
    SYSTEM_ARCH_NAME="i386"
    [[ $(uname -m | \grep x86_64 | wc -l) -gt 0 ]] && SYSTEM_ARCH_NAME="amd64"
    [[ $(uname -m | \grep arm | wc -l) -gt 0 ]] && SYSTEM_ARCH_NAME="arm64"

  # Detect if Debian family is in use
  elif [[ -f /etc/debian_version ]]; then

    local id=$(cat /etc/os-release | \grep "^ID=" | awk -F= '{ print $2 }')
    if [[ "$id" == "debian" ]] || [[ "$id" == "raspbian" ]]; then
      SYSTEM_DIST=$id
      SYSTEM_PSEUDO_NAME=$(cat /etc/os-release | \grep "^VERSION=" | awk -F= '{ print $2 }' | \grep -oEi '[a-z]+')
      SYSTEM_VERSION=$(cat /etc/debian_version)
    else
      SYSTEM_DIST=$(cat /etc/lsb-release | \grep '^DISTRIB_ID' | awk -F= '{ print $2 }')
      SYSTEM_PSEUDO_NAME=$(cat /etc/lsb-release | \grep '^DISTRIB_CODENAME' | awk -F= '{ print $2 }')
      SYSTEM_VERSION=$(cat /etc/lsb-release | \grep '^DISTRIB_RELEASE' | awk -F= '{ print $2 }')
    fi
    SYSTEM_DIST_BASED_ON="debian"
    SYSTEM_ARCH_NAME="i386"
    [[ $(uname -m | \grep 64 | wc -l) -gt 0 ]] && SYSTEM_ARCH_NAME="amd64"

  # Detect if RedHat family is in use
  elif [[ -f /etc/redhat-release ]]; then

    SYSTEM_DIST=$(cat /etc/redhat-release | sed s/\ release.*// | tr "[A-Z]" "[a-z]")
    [[ "$SYSTEM_DIST" == *"red"* ]] && SYSTEM_DIST="redhat"
    [[ "$SYSTEM_DIST" == *"centos"* ]] && SYSTEM_DIST="centos"
    [[ "$SYSTEM_DIST" == *"scientific"* ]] && SYSTEM_DIST="scientific"
    SYSTEM_DIST_BASED_ON="redhat"
    SYSTEM_PSEUDO_NAME=$(cat /etc/redhat-release | sed s/.*\(// | sed s/\)//)
    SYSTEM_VERSION=$(cat /etc/redhat-release | sed s/.*release\ // | sed s/\ .*//)
    SYSTEM_ARCH_NAME="i386"
    [[ $(uname -m | \grep 64 | wc -l) -gt 0 ]] && SYSTEM_ARCH_NAME="amd64"

  # Detect if Windows/Cygwin is in use
  elif [[ "$OSTYPE" == "cygwin"* ]]; then

    SYSTEM_NAME="windows"
    SYSTEM_DIST="cygwin"
    SYSTEM_DIST_BASED_ON="linux"
    SYSTEM_PSEUDO_NAME="Windows"
    SYSTEM_VERSION=$(cmd /c ver | \grep -oEi '[0-9]+\.[0-9]+\.[0-9]+')
    SYSTEM_ARCH_NAME="i386"
    [ $(uname -m | \grep 64 | wc -l) -gt 0 ] && SYSTEM_ARCH_NAME="amd64"
    SYSTEM_KERNEL=$(uname -r | \grep -oEi '[0-9]+\.[0-9]+\.[0-9]+')

  fi

  # Detect if containerisation is in use
  if cat /proc/1/cgroup 2> /dev/null | grep -i docker > /dev/null 2>&1; then
    SYSTEM_CONTAINER="docker"
  fi

  # Format information
  export SYSTEM_NAME=$(echo $SYSTEM_NAME | tr "[A-Z]" "[a-z]")
  export SYSTEM_DIST=$(echo $SYSTEM_DIST | tr "[A-Z]" "[a-z]")
  export SYSTEM_DIST_BASED_ON=$(echo $SYSTEM_DIST_BASED_ON | tr "[A-Z]" "[a-z]")
  export SYSTEM_PSEUDO_NAME=$(echo $SYSTEM_PSEUDO_NAME | tr "[A-Z]" "[a-z]" | tr " " "_")
  export SYSTEM_VERSION=$(echo $SYSTEM_VERSION | tr "[A-Z]" "[a-z]")
  export SYSTEM_ARCH=$(echo $SYSTEM_ARCH | tr "[A-Z]" "[a-z]")
  export SYSTEM_ARCH_NAME=$(echo $SYSTEM_ARCH_NAME | tr "[A-Z]" "[a-z]")
  export SYSTEM_KERNEL=$(echo $SYSTEM_KERNEL | tr "[A-Z]" "[a-z]")
  [ -n "$SYSTEM_CONTAINER" ] && export SYSTEM_CONTAINER=$(echo $SYSTEM_CONTAINER | tr "[A-Z]" "[a-z]")

  return 0
}

function system_export() {

  echo "SYSTEM_NAME=$SYSTEM_NAME"
  echo "SYSTEM_DIST=$SYSTEM_DIST"
  echo "SYSTEM_DIST_BASED_ON=$SYSTEM_DIST_BASED_ON"
  echo "SYSTEM_PSEUDO_NAME=$SYSTEM_PSEUDO_NAME"
  echo "SYSTEM_VERSION=$SYSTEM_VERSION"
  echo "SYSTEM_ARCH=$SYSTEM_ARCH"
  echo "SYSTEM_ARCH_NAME=$SYSTEM_ARCH_NAME"
  echo "SYSTEM_KERNEL=$SYSTEM_KERNEL"
  [ -n "$SYSTEM_CONTAINER" ] && echo "SYSTEM_CONTAINER=$SYSTEM_CONTAINER"

  return 0
}

function main() {

  system_detect
  system_export
}

main

#!/bin/bash
set -e

function main() {
  download
  cd "$HOME/.make-devops"
  make macos-install-essential
  finish
}

function download() {
  curl -L \
    "https://github.com/nhsd-exeter/make-devops/tarball/${BRANCH_NAME:-master}?$(date +%s)" \
    -o /tmp/make-devops.tar.gz
  tar -zxf /tmp/make-devops.tar.gz -C /tmp
  rm -rf \
    /tmp/make-devops.tar.gz \
    /tmp/make-devops* \
    "$HOME/.make-devops"
  mv /tmp/nhsd-exeter-make-devops-* "$HOME/.make-devops"
}

function finish() {
  tput setaf 2
  printf "\nDone: Install essential development dependencies\n\n"
  tput sgr0
}

main

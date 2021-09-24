#!/bin/bash

message="$(cat $1)"

if [ $(make git-check-if-commit-msg-is-correct BUILD_COMMIT_MESSAGE="$message") == false ]; then
  tput setaf 202
  printf "\n\n  $(echo $0 | sed "s;$PWD/;;"): Commit message '$message' does not meet the accepted convention\n\n"
  make show-configuration | grep GIT_COMMIT_MESSAGE_ && printf "\nPlease, for more details see the 'build/automation/test/git.test.mk' file.\n"
  tput sgr0
  exit 1
fi

exit 0

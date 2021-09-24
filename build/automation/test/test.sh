#!/bin/bash

export TEST_PASS_COUNT=0
export TEST_FAIL_COUNT=0

function mk_test_initialise() {
  TEST_PASS_COUNT=0
  TEST_FAIL_COUNT=0
  (
    if [[ "$DEBUG" =~ ^(true|yes|y|on|1|TRUE|YES|Y|ON)$ ]]; then
      mk_test_print_red_on_yellow "$(echo $1 | sed -e s/^test-//) >>> "
    else
      mk_test_print "$(echo $1 | sed -e s/^test-//) "
    fi
  ) >&5
}

function mk_test() {
  if [ $# -eq 2 ]; then
    description="$1"; shift
  fi
  if [ "$1" != false ] && test $1; then
    TEST_PASS_COUNT=$((TEST_PASS_COUNT+1))
    ( mk_test_print "." ) >&5
  else
    TEST_FAIL_COUNT=$((TEST_FAIL_COUNT+1))
    ( mk_test_print "x" ) >&5
  fi
  if [ -z "$description" ]; then
    mk_test_complete
  fi
}

function mk_test_complete() {
  (
    printf " $TEST_PASS_COUNT/$(((TEST_PASS_COUNT + TEST_FAIL_COUNT))) "
    if [ $TEST_FAIL_COUNT -gt 0 ]; then
      mk_test_print_red "fail"
    else
      mk_test_print_green "pass"
    fi
    printf "\n"
  ) >&5
}

# ==============================================================================

function mk_test_skip_if_not_macos() {
  if [ "$(uname)" != "Darwin" ]; then
    mk_test_skip
  else
    return 1
  fi
}

function mk_test_skip() {
  (
    mk_test_print_blue "skip"
    printf "\n"
  ) >&5
}

function mk_test_proceed_if_macos() {
  if [ "$(uname)" = "Darwin" ]; then
    return 0
  else
    return 1
  fi
}

# ==============================================================================

function mk_test_print_green() {
  mk_test_print "$*" 64
}

function mk_test_print_red() {
  mk_test_print "$*" 196
}

function mk_test_print_blue() {
  mk_test_print "$*" 21
}

function mk_test_print_red_on_yellow() {
  mk_test_print "$*" 196 190
}

function mk_test_print() {
  (
    set +x
    if test -t 1 && [ -n "$TERM" ] && [ "$TERM" != "dumb" ]; then
      [ -n "$3" ] && tput setab $3
      [ -n "$2" ] && tput setaf $2
    fi
    printf "$1"
    if test -t 1 && [ -n "$TERM" ] && [ "$TERM" != "dumb" ]; then
      tput sgr 0
    fi
  )
}

# ==============================================================================

export -f mk_test_initialise
export -f mk_test
export -f mk_test_complete
export -f mk_test_skip_if_not_macos
export -f mk_test_skip
export -f mk_test_proceed_if_macos
export -f mk_test_print_green
export -f mk_test_print_red
export -f mk_test_print_blue
export -f mk_test_print_red_on_yellow
export -f mk_test_print

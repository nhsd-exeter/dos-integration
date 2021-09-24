#!/bin/sh

if ! which python > /dev/null 2>&1; then
  exit 0
fi

version="$(python --version 2>&1 | awk '{ print $2 }')"
dependencies=$(
  pip list 2> /dev/null | while read -r line; do
    echo $line | grep -qi ^package && continue
    echo $line | grep -q ^- && continue
    package=$(echo $line | awk '{ print $1 }')
    version=$(echo $line | awk '{ print $2 }')
    printf "{\"name\":\"${package}\",\"version\":\"${version}\"},"
  done
)

printf "\"python\":{\"version\":\"${version}\",\"dependencies\":[$(printf "$dependencies" | head -c -1)]}"

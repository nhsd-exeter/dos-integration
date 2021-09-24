#!/bin/sh

if ! which php > /dev/null 2>&1; then
  exit 0
fi

( curl -sS https://getcomposer.org/installer | php -n -- --install-dir=/usr/local/bin --filename=composer ) > /dev/null 2>&1
[ ! -f composer.json ] && [ -f composer.lock ] && cp composer.lock composer.json
version="$(php --version 2>&1 | head -n 1 | grep -o '[0-9]*\.[0-9]*\.[0-9]*')"
dependencies=$(
  composer show -i 2> /dev/null | while read -r line; do
    package=$(echo $line | awk '{ print $1 }')
    version=$(echo $line | awk '{ print $2 }')
    printf "{\"name\":\"${package}\",\"version\":\"${version}\"},"
  done
)

printf "\"php\":{\"version\":\"${version}\",\"dependencies\":[$(printf "$dependencies" | head -c -1)]}"

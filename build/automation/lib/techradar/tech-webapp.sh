#!/bin/sh

if [ ! -f yarn.lock ]; then
  exit 0
fi

version=""
dependencies=$(
  awk '/^["@a-z0-9-_\.]*@/{n=NR+1} n>=NR' yarn.lock | sed '$!N;s/\n/ /' | sed 's/"//g' | sed 's/@/ @/g' | awk '{ print $1 " " $NF }' | while read -r line; do
    package=$(echo $line | awk '{ print $1 }')
    version=$(echo $line | awk '{ print $2 }')
    printf "{\"name\":\"${package}\",\"version\":\"${version}\"},"
  done
)

printf "\"webapp\":{\"version\":\"${version}\",\"dependencies\":[$(printf "$dependencies" | head -c -1)]}"

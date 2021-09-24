#!/bin/sh

if ! which java > /dev/null 2>&1; then
  exit 0
fi

version="$(java -version 2>&1 | awk -F '"' '/version/ { print $2 }')"
dependencies=$(
  for jar in $(find / -name '*.jar' -not -path /usr/share -not -path /usr/lib); do
    for dependency in $(jar -tf $jar 2> /dev/null | grep .jar$ | awk '{ print $NF }'); do
      str=$(basename $dependency | sed "s/.jar//" | sed "s/[\.A-Za-z-]*$//")
      version=$(echo $str | rev | cut -d- -f1 | rev)
      library=$(echo $str | sed "s/-${version}//")
      printf "{\"name\":\"${library}\",\"version\":\"${version}\"},"
    done
  done
)

printf "\"java\":{\"version\":\"${version}\",\"dependencies\":[$(printf "$dependencies" | head -c -1)]}"

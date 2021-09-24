#!/bin/sh

tech=
for script in $(ls -1 /tech-*.sh); do
  output=$($script)
  if [ -n "$output" ]; then
    tech="${tech}${output},"
  fi
done

printf "${tech}$(/filesystem.sh)"

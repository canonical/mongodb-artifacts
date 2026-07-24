#!/bin/bash

if ! type "yq" > /dev/null; then
    echo "Missing yq, please install."
    exit 1
fi

if [ $# -ne 1 ]
  then
    echo "Invalid arguments supplied"
    echo "Usage: bash scripts/set-version.sh X.Y.Z-W"
    exit 1
fi

readarray -d '' snaps < <(find . -path '*/snap/snapcraft.yaml' -print0)
readarray -d '' rocks < <(find . -path '*/rockcraft.yaml' -print0)


all_files=("${snaps[@]}" "${rocks[@]}")


for file in "${all_files[@]}"; do
    VERSION="$1" yq -i '.version = strenv(VERSION)' $file
done


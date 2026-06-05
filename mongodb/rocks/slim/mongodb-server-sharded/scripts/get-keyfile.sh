#!/bin/bash
# Print the contents of the MongoDB internal-authentication keyfile to stdout.
#
# Use it to copy the auto-generated key from one container into the others so
# that every member of a sharded cluster shares the same key:
#
#   key="$(docker exec configsvr get-keyfile)"
#   docker exec shard1 set-keyfile "$key"
set -euo pipefail

source /bin/keyfile-common.sh

if [ ! -e "${KEYFILE}" ]; then
  echo "get-keyfile: no keyfile found at ${KEYFILE}" >&2
  exit 1
fi

cat "${KEYFILE}"

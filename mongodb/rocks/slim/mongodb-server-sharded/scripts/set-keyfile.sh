#!/bin/bash
# Set or rotate the MongoDB internal-authentication keyfile.
#
# Usage:
#   set-keyfile <key>   Store <key> as the keyfile contents.
#   set-keyfile         Rotate: generate a fresh random key and store it.
#
# The keyfile is written with mode 400, owned by the mongodb user (584788), so
# this must run as root (the default user for "docker exec").
#
# Note: mongod/mongos read the keyfile only at startup, so restart the service
# after changing it. Every member of a sharded cluster must use the same key, so
# propagate the new value with get-keyfile/set-keyfile before restarting them. A
# keyfile bind-mounted read-only cannot be modified from inside the container.
set -euo pipefail

source /bin/keyfile-common.sh

if [ "$#" -gt 0 ]; then
  printf '%s\n' "$1" | write_keyfile
else
  generate_keyfile
fi

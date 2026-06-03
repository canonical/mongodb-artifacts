#!/bin/bash
# Generate a MongoDB internal-authentication keyfile and print it to stdout.
#
# The same keyfile must be shared by every member of the sharded cluster
# (config servers, shard servers and query routers). Generate it once and pipe
# the output into the store-keyfile app on each machine.
set -eu

usage() {
    cat <<'EOF'
Usage: mongodb-server-sharded.generate-keyfile

Generate a MongoDB internal-authentication keyfile and print it to stdout.

The same keyfile must be shared by every member of the sharded cluster
(config servers, shard servers and query routers). Generate it once and use
the output as input to the store-keyfile app on each machine.

Example:
  sudo snap run mongodb-server-sharded.generate-keyfile > /path/to/keyfile
EOF
}

case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
esac

exec "${SNAP}/usr/bin/openssl" rand -base64 756

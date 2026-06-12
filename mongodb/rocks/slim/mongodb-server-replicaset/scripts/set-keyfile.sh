#!/bin/bash
# Set the MongoDB internal-authentication keyfile.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: set-keyfile KEY

Set the MongoDB internal-authentication keyfile.

Store KEY as the keyfile contents. Every member of a replica set must use the
same keyfile value; sync it with get-keyfile/set-keyfile before restarting
them.

Example:
  docker exec replicaset set-keyfile "$KEYFILE_CONTENT"
  docker restart replicaset
EOF
}

case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
esac

source /bin/keyfile-common.sh

if [ "$#" -ne 1 ]; then
    echo "set-keyfile: expected exactly one KEY argument" >&2
    usage >&2
    exit 1
fi

if [ -z "$1" ]; then
    echo "set-keyfile: KEY must not be empty" >&2
    exit 1
fi

printf '%s\n' "$1" | write_keyfile

echo "Keyfile stored at ${KEYFILE}" >&2

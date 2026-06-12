#!/bin/bash
# Set the MongoDB internal-authentication keyfile.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: set-keyfile KEY

Set the MongoDB internal-authentication keyfile.

Example:
  docker exec mongos set-keyfile "$KEYFILE_CONTENT"
  docker restart mongos
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

#!/bin/bash
# Print the contents of the MongoDB internal-authentication keyfile to stdout.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: get-keyfile

Print the contents of the stored MongoDB internal-authentication keyfile.

The same keyfile must be shared by every member of the replica set.

Example:
  KEYFILE_CONTENT="$(docker exec replicaset get-keyfile)"
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

if [ "$#" -ne 0 ]; then
    echo "get-keyfile: expected no arguments" >&2
    usage >&2
    exit 1
fi

source /bin/keyfile-common.sh

if [ ! -e "${KEYFILE}" ]; then
    echo "get-keyfile: no keyfile found at ${KEYFILE}" >&2
    exit 1
fi

cat "${KEYFILE}"

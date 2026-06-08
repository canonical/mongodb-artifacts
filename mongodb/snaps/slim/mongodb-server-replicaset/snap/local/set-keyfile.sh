#!/bin/bash
# Set or rotate the MongoDB internal-authentication keyfile.
#
# Usage:
#   mongodb-server-replicaset.set-keyfile <key>   Store <key> as the keyfile.
#   mongodb-server-replicaset.set-keyfile         Rotate to a new random key.
#
# Run with sudo; the helper writes the keyfile as the snap_daemon user that
# runs mongod and mongos. The user is responsible for syncing the same keyfile
# value across all cluster members.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: mongodb-server-replicaset.set-keyfile [KEY]

Set or rotate the MongoDB internal-authentication keyfile.

With KEY, store that exact value as the keyfile contents. Without KEY, generate
a fresh random key and store it. Every member of a replicaset must use the
same keyfile value; sync it with get-keyfile/set-keyfile before restarting them.

Examples:
  sudo snap run mongodb-server-replicaset.set-keyfile "$key"
  sudo snap run mongodb-server-replicaset.set-keyfile
EOF
}

case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
esac

. "${SNAP}/keyfile-common.sh"

if [ "$#" -gt 1 ]; then
    echo "set-keyfile: expected zero or one argument" >&2
    usage >&2
    exit 1
fi

if [ "$(id -u)" = "0" ]; then
    exec "${SNAP}/usr/bin/setpriv" \
        --clear-groups \
        --reuid snap_daemon \
        --regid snap_daemon \
        -- \
        "${SNAP}/set-keyfile.sh" "$@"
fi

if [ "$#" -eq 1 ]; then
    if [ -z "$1" ]; then
        echo "set-keyfile: KEY must not be empty" >&2
        exit 1
    fi
    printf '%s\n' "$1" | write_keyfile
else
    generate_keyfile
fi

echo "Keyfile stored at ${KEYFILE}" >&2

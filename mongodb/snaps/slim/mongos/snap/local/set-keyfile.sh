#!/bin/bash
# Set the MongoDB internal-authentication keyfile.
#
# Run with sudo; the helper writes the keyfile as the snap_daemon user that
# runs mongos.
set -euo pipefail

usage() {
    cat <<'EOF'
Usage: mongos.set-keyfile KEY

Set the MongoDB internal-authentication keyfile to KEY.

The same keyfile value must be shared by every member of the sharded cluster.
Run this with sudo; the helper writes the keyfile as the snap_daemon user that
runs mongos.

Example:
  sudo snap run mongos.set-keyfile "$key"
EOF
}

case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
esac

if [ "$#" -ne 1 ]; then
    echo "set-keyfile: expected exactly one KEY argument" >&2
    usage >&2
    exit 1
fi

if [ -z "$1" ]; then
    echo "set-keyfile: KEY must not be empty" >&2
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

KEYFILE="${SNAP_DATA}/etc/keyfile"
TMPFILE="$(mktemp "${KEYFILE}.XXXXXX")"
trap 'rm -f "${TMPFILE}"' EXIT

printf '%s\n' "$1" > "${TMPFILE}"

# MongoDB requires the keyfile to be owned by the user running the daemon
# (snap_daemon, uid/gid 584788) and readable only by that owner.
chmod 400 "${TMPFILE}"

mv "${TMPFILE}" "${KEYFILE}"
trap - EXIT

echo "Keyfile stored at ${KEYFILE}" >&2

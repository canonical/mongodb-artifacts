#!/bin/bash
# Read a MongoDB internal-authentication keyfile from stdin and store it in the
# snap's common directory with the ownership and permissions MongoDB requires.
#
# Must be run as root (e.g. with sudo) so the keyfile can be handed over to the
# snap_daemon user that runs mongod and mongos.
set -eu

umask 077

KEYFILE="${SNAP_COMMON}/mongodb-keyfile"
TMPFILE="$(mktemp "${SNAP_COMMON}/.mongodb-keyfile.XXXXXX")"
trap 'rm -f "${TMPFILE}"' EXIT

# Read the keyfile contents from stdin.
cat > "${TMPFILE}"

if [[ ! -s "${TMPFILE}" ]]; then
    echo "error: no keyfile content received on stdin" >&2
    exit 1
fi

# MongoDB requires the keyfile to be owned by the user running the daemon
# (snap_daemon, uid 584788) and readable only by that owner.
#
# Set the mode before changing ownership: while we still own the file we can
chmod 400 "${TMPFILE}"
chown 584788:root "${TMPFILE}"

# Atomically move the validated keyfile into place.
mv "${TMPFILE}" "${KEYFILE}"
trap - EXIT

echo "Keyfile stored at ${KEYFILE}" >&2

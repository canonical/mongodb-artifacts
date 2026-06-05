#!/bin/bash
# Shared helpers for managing the MongoDB internal-authentication keyfile.
#
# This file is sourced by the startup scripts and by the get-keyfile /
# set-keyfile commands. The keyfile lives next to the MongoDB config files at
# /etc/mongod/keyfile and must be readable only by the mongodb user
# (uid/gid 584788), so writing it requires root.

KEYFILE="${KEYFILE:-/etc/mongod/keyfile}"
KEYFILE_UID=584788
KEYFILE_GID=584788

# Write stdin to the keyfile with the correct ownership (584788:584788) and
# permissions (400). The write is atomic: a temporary file in the same
# directory is populated, locked down, then renamed over the keyfile so that
# readers never observe a partial key. Requires root.
write_keyfile() {
  local tmp
  tmp="$(mktemp "${KEYFILE}.XXXXXX")"
  cat > "${tmp}"
  chown "${KEYFILE_UID}:${KEYFILE_GID}" "${tmp}"
  chmod 400 "${tmp}"
  mv -f "${tmp}" "${KEYFILE}"
}

# Generate a fresh random key and store it in the keyfile.
generate_keyfile() {
  openssl rand -base64 756 | write_keyfile
}

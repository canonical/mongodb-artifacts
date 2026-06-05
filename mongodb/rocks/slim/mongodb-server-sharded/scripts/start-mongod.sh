#!/bin/bash

# Start mongod as the unprivileged mongodb user.
#
# Extra arguments can be supplied through the MONGOD_ARGS environment variable,
# for example:
#   docker run -e MONGOD_ARGS="--configsvr --replSet configrs --bind_ip_all" ...
set -euo pipefail

source /bin/keyfile-common.sh

# Auto-generate an internal-authentication keyfile on first start, unless one is
# already present (e.g. bind-mounted from the host). Restarts reuse it.
if [ ! -e "${KEYFILE}" ]; then
  generate_keyfile
fi

exec /usr/bin/setpriv --clear-groups --reuid mongodb --regid mongodb -- \
  /usr/bin/mongod --config /etc/mongod/mongod.conf ${MONGOD_ARGS:-} "$@"

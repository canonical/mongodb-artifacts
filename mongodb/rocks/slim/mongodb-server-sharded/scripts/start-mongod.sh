#!/bin/bash

# Start mongod as the unprivileged mongodb user.
#
# Extra arguments can be supplied through the MONGOD_ARGS environment variable,
# for example:
#   docker run -e MONGOD_ARGS="--configsvr --replSet configrs --bind_ip_all" ...
exec /usr/bin/setpriv --clear-groups --reuid mongodb --regid mongodb -- \
  /usr/bin/mongod --config /etc/mongod/mongod.conf ${MONGOD_ARGS} "$@"

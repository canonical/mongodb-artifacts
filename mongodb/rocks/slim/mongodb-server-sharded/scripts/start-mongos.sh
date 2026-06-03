#!/bin/bash

# Start mongos as the unprivileged mongodb user.
#
# Extra arguments can be supplied through the MONGOS_ARGS environment variable,
# for example:
#   docker run -e MONGOS_ARGS="--configdb configrs/configsvr:27019 --bind_ip_all" ...
exec /usr/bin/setpriv --clear-groups --reuid mongodb --regid mongodb -- \
  /usr/bin/mongos --config /etc/mongod/mongos.conf ${MONGOS_ARGS} "$@"

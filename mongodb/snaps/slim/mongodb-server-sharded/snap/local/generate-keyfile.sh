#!/bin/bash
# Generate a MongoDB internal-authentication keyfile and print it to stdout.
#
# The same keyfile must be shared by every member of the sharded cluster
# (config servers, shard servers and query routers). Generate it once and pipe
# the output into the store-keyfile app on each machine.
set -eu

exec "${SNAP}/usr/bin/openssl" rand -base64 756

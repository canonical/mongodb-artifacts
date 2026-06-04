#!/bin/bash
# Generate a MongoDB keyfile for internal cluster authentication.
#
# The keyfile is written to stdout. Redirect it to a file on the host,
# restrict its permissions so only the mongodb user (uid 584788) can read it,
# and bind-mount the same file into every container in the cluster:
#
#   docker run --rm <image> exec generate-keyfile > mongodb-keyfile
#   chmod 400 mongodb-keyfile
#   sudo chown 584788:584788 mongodb-keyfile
#
set -euo pipefail

openssl rand -base64 756

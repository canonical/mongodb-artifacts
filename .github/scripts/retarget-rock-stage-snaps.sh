#!/usr/bin/env bash
set -euo pipefail

# Check that rockcraft.yaml has stage snaps for this rock pointing at the
# expected channel, e.g. "mongodb-server-sharded/8/edge".
if ! yq \
    '.parts[] | select(has("stage-snaps")) | .["stage-snaps"][] | select(test("^" + strenv(ROCK_NAME) + "/8/edge$"))' \
    "${ROCKCRAFT_FILE}" | grep -q .; then
  echo "No ${ROCK_NAME}/8/edge stage snap channel found in ${ROCKCRAFT_FILE}"
  exit 1
fi

# Rewrite rockcraft.yaml to point stage snaps at the PR snap channel. For
# example, "mongodb-server-sharded/8/edge" becomes
# "mongodb-server-sharded/8/edge/pr-123".
yq -i \
  '(.parts[] | select(has("stage-snaps")) | .["stage-snaps"][]) |= sub("/8/edge$"; "/" + strenv(SNAP_CHANNEL))' \
  "${ROCKCRAFT_FILE}"

git diff -- "${ROCKCRAFT_FILE}"

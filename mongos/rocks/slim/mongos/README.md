# Mongos rock (OCI Image)

[MongoDB](https://github.com/mongodb/mongo) is a source-available, cross-platform,
document-oriented database application. Classified as a NoSQL database program,
MongoDB uses JSON-like documents with optional schemas.

The Mongos rock is an Open Container Initiative (OCI) image derived from the
[Mongos snap](https://snapcraft.io/mongos) and built from the official Percona repositories. The
tool used to create this rock is called
[Rockcraft](https://canonical-rockcraft.readthedocs-hosted.com/en/latest/index.html).

This rock is intended to run `mongos`, the MongoDB query router for sharded clusters. It connects
client requests to the config server replica set and routes operations to the appropriate shards.

This image does not run `mongod` and does not store cluster data. For config-servers and shards
use the `mongodb-server-sharded` rock. For replica set deployments, use the
`mongodb-server-replicaset` rock.

## How the rock is structured

The rock defines one service:

| Service  | Startup   | Command                        | Default port |
| -------- | --------- | ------------------------------ | ------------ |
| `mongos` | `enabled` | `/bin/bash /bin/start-mongos.sh` | `27018`      |

The `mongos` service runs as the unprivileged `mongodb` user (uid `584788`) and reads the
configuration file found in the image:

- `mongos` &rarr; `/etc/mongod/mongos.conf`

Extra MongoDB arguments are passed through the `MONGOS_ARGS` environment variable. You can read
more about the available options in the [`mongos`](https://www.mongodb.com/docs/manual/reference/program/mongos/)
documentation.

## Installing Docker

To get started with the rock, first install Docker:

```bash
sudo snap install docker
```

## Obtaining the rock

Pull the published image from the GitHub Container Registry:

```bash
docker pull ghcr.io/canonical/mongos:<version>
```

Alternatively, import a locally built rock archive into Docker using `skopeo` (bundled with
Rockcraft):

```bash
sudo rockcraft.skopeo --insecure-policy copy \
  oci-archive:mongos_*_amd64.rock \
  docker-daemon:ghcr.io/canonical/mongos:local-test
```

The rest of this guide refers to the image through the `IMAGE` shell variable, so that you can
adjust the tag in a single place:

```bash
export IMAGE=ghcr.io/canonical/mongos:local-test
```

## Using the rock as a query router

The `mongos` router must be able to reach an existing config server replica set. The config server
replica set name and member addresses are passed with `--configdb`:

```text
--configdb <config-replica-set>/<config-server-host>:<port>[,<config-server-host>:<port>...]
```

For example, if the config server replica set is named `configrs` and has a member reachable as
`configsvr:27019`, use:

```bash
--configdb configrs/configsvr:27019
```

### Configure internal authentication

MongoDB sharded cluster components use a shared keyfile for internal authentication. `mongos` must
use the same keyfile as the config servers and shard servers.

Each container automatically generates a keyfile at `/etc/mongod/mongodb-keyfile` (mode `400`,
owned by the `mongodb` user, uid `584788`) the first time it starts, unless a keyfile is already
present at that path.

In this walkthrough, the config server is assumed to be running in another container named
`configsvr` on a Docker network named `mongo-cluster`. Read the cluster key from that container:

```bash
KEYFILE_CONTENT="$(docker exec configsvr get-keyfile)"
```

If your config server is not containerized, obtain the same internal-authentication keyfile value
from your deployment process instead.

### Start mongos

Start a `mongos` container on the same Docker network as the config server. The router listens on
port `27018` by default. A `mongos` container needs a `--configdb` value at startup so it can find
the config server replica set:

```bash
docker run -d \
  --name mongos \
  --network mongo-cluster \
  -e MONGOS_ARGS="--configdb configrs/configsvr:27019 --bind_ip 0.0.0.0" \
  "$IMAGE"
```

On first start, this container generated its own keyfile. Replace it with the shared cluster key and
restart the container so `mongos` reloads it:

```bash
docker exec mongos set-keyfile "$KEYFILE_CONTENT"
docker restart mongos
```

Check that the service is active:

```bash
docker exec mongos pebble services
```

### Connect through mongos

Connect to the router using an admin user that already exists in the sharded cluster:

```bash
docker exec -it mongos mongosh "mongodb://admin:<ADMIN_PASSWORD>@127.0.0.1:27018/admin"
```

Verify the sharded cluster configuration:

```javascript
sh.status()
```

If the cluster already has shards, the output should list them. If you are building a new sharded
cluster, add shards through `mongos` after their replica sets are initialized:

```javascript
sh.addShard("shard1rs/shard1:27017")
```

## Tear down

When you are finished, stop the router container gracefully, then remove it:

```bash
docker stop mongos
docker rm mongos
```

The `mongos` container does not store cluster data. Removing it does not remove data from the config
servers or shards.

## Managing the keyfile

The image provides two commands for inspecting and changing the internal-auth keyfile of a running
container. Run them as the default `docker exec` user (root), which can read and rewrite the `400`
keyfile owned by uid `584788`:

| Command | Behaviour |
| ------- | --------- |
| `get-keyfile` | Print the current keyfile (`/etc/mongod/mongodb-keyfile`) to standard output. |
| `set-keyfile <key>` | Store `<key>` as the keyfile contents. |

For example, to copy the key from an existing config server container into `mongos`:

```bash
key="$(docker exec configsvr get-keyfile)"
docker exec mongos set-keyfile "$key"
docker restart mongos
```

Notes:

- `mongos` reads the keyfile only at startup, so restart the service (`docker restart <container>`)
  after changing the keyfile for it to take effect.
- Every config server, shard server, and router in a sharded cluster must use the same key. When
  rotating, propagate the new value to all components before restarting them.

## Available tools

The rock also packages the standard MongoDB command-line tools:

- `get-keyfile`
- `set-keyfile`
- `mongos`
- `mongosh`
- `mongodump`
- `mongoexport`
- `mongofiles`
- `mongoimport`
- `mongorestore`
- `mongostat`
- `mongotop`

Run them with `docker exec` against a running container, for example:

```bash
docker exec -it mongos mongosh --port 27018
docker exec mongos mongodump --port 27018 --out /tmp/backup
```

## Getting command help

To see more information about a service or tool, run it with `--help`. For example:

```bash
docker run --rm "$IMAGE" exec mongos --help
docker exec <container-name> mongodump --help
```

## Logs

`mongos` writes its log inside the container:

- `mongos` &rarr; `/var/log/mongodb/mongos.log`

View it with `docker exec`, or inspect Pebble's view of the service:

```bash
docker exec mongos tail -f /var/log/mongodb/mongos.log
docker exec mongos pebble services
```

## License

The Mongos rock is free software, distributed under the Apache Software License, version 2.0. See
[LICENSE](LICENSE) for more information. It installs and operates Percona Server for MongoDB, which
is licensed under the Server Side Public License (SSPL) version 1.

## Trademark Notice

MongoDB is a trademark or registered trademark of MongoDB, Inc.
Percona is a trademark or registered trademark of Percona LLC.
Other trademarks are property of their respective owners.
The Mongos rock is not sponsored, endorsed, or affiliated with MongoDB, Inc.

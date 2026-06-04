# Sharded MongoDB Server rock (OCI Image)

[![Operator Tests](https://github.com/canonical/mongodb-artifacts/actions/workflows/integration.yaml/badge.svg)](https://github.com/canonical/mongodb-artifacts/actions/workflows/integration.yaml)

[MongoDB](https://github.com/mongodb/mongo) is a source-available, cross-platform, document-oriented database application. Classified as a NoSQL database program, MongoDB uses JSON-like documents with optional schemas.

The Sharded MongoDB Server rock is an Open Container Initiative (OCI) image derived from the [Sharded MongoDB Server snap](https://snapcraft.io/mongodb-server-sharded) and built from the official Percona repositories. The tool used to create this rock is called [Rockcraft](https://canonical-rockcraft.readthedocs-hosted.com/en/latest/index.html).

This rock is intended to be run as a MongoDB sharded deployment. It delivers both the `mongod` and `mongos` components for a complete sharded cluster, plus the standard MongoDB administration tools.

For replica set deployments, see the [`mongodb-server-replicaset`](https://snapcraft.io/mongodb-server-replicaset) rock.
For standalone mongos, see [`mongos`]

## How the rock is structured

The rock defines two services:

| Service  | Startup    | Command                          | Default port |
| -------- | ---------- | -------------------------------- | ------------ |
| `mongod` | `enabled`  | `/usr/bin/mongod` (config server / shard) | `27017` |
| `mongos` | `disabled` | `/usr/bin/mongos` (query router) | `27018` |

Because a single container hosts a single role, the `mongod` service starts automatically while `mongos` is started on demand:

- A default container runs `mongod`. Use it for config servers and shard servers.
- A container started with `start mongos` runs only the query router.

Both services run as the unprivileged `mongodb` user (uid `584788`) and read the configuration files found into the image:

- `mongod` &rarr; `/etc/mongod/mongod.conf` (data in `/var/lib/mongodb`)
- `mongos` &rarr; `/etc/mongod/mongos.conf`

Extra MongoDB arguments are passed through the `MONGOD_ARGS` and `MONGOS_ARGS` environment variables. You can read more about the available options in the [`mongod`](https://www.mongodb.com/docs/manual/reference/program/mongod/) and [`mongos`](https://www.mongodb.com/docs/manual/reference/program/mongos/) documentation.

## Installing Docker

To get started with the rock, first install Docker:

```bash
sudo snap install docker
```

## Obtaining the rock

Pull the published image from the GitHub Container Registry:

```bash
docker pull ghcr.io/canonical/mongodb-server-sharded:8_edge
```

Alternatively, import a locally built rock archive into Docker using `skopeo` (bundled with Rockcraft):

```bash
sudo rockcraft.skopeo --insecure-policy copy \
  oci-archive:mongodb-server-sharded_8.0.10-4_amd64.rock \
  docker-daemon:ghcr.io/canonical/mongodb-server-sharded:8_edge
```

The rest of this guide refers to the image through the `IMAGE` shell variable, so that you can adjust the tag in a single place:

```bash
export IMAGE=ghcr.io/canonical/mongodb-server-sharded:8_edge
```

## Using the rock as a sharded cluster

The following walkthrough builds a minimal sharded cluster on a single host using one config server, one shard, and one query router, all on a dedicated Docker network. In production, run each component on a separate host and use multi-member replica sets.

### Create a Docker network

A user-defined network lets the containers reach each other by name:

```bash
docker network create mongo-cluster
```

### Configure internal authentication

MongoDB sharded clusters use a shared keyfile for internal authentication between config servers, shard servers, and query routers (`mongos`).

On the host machine, generate a keyfile using the image's `generate-keyfile` command, then restrict its permissions so that only the `mongodb` user (uid `584788`) can read it:

```bash
docker run --rm "$IMAGE" exec generate-keyfile > mongodb-keyfile
chmod 400 mongodb-keyfile
sudo chown 584788:584788 mongodb-keyfile
```

`generate-keyfile` writes a fresh random key to standard output, which is redirected into `mongodb-keyfile` on the host.

The same keyfile will be mounted read-only into every container in the cluster, at `/etc/mongod/keyfile`.

> **Note:** Run all of the `docker run` commands below from the same directory where you created `mongodb-keyfile`, otherwise `$(pwd)` won't point at the file. The keyfile is bind-mounted from the host, not copied into the containers, so it must remain on the host for the lifetime of the cluster — do not delete it, or containers will fail to start when restarted.

### Start the config server

Start a `mongod` container as a config server. It joins the `configrs` replica set, listens on port `27019`, mounts the shared keyfile and a data volume:

```bash
docker run -d \
  --name configsvr \
  --network mongo-cluster \
  -v configsvr-data:/var/lib/mongodb \
  -v "$(pwd)/mongodb-keyfile:/etc/mongod/keyfile:ro" \
  -e MONGOD_ARGS="--configsvr --replSet configrs --port 27019 --bind_ip_all --keyFile /etc/mongod/keyfile" \
  "$IMAGE"
```

#### Initialize the config server replica set

Connect to the config server:

```bash
docker exec -it configsvr mongosh --port 27019
```

Initialize the replica set:

```javascript
rs.initiate({
  _id: "configrs",
  configsvr: true,
  members: [
    { _id: 0, host: "configsvr:27019" }
  ]
})
```

Verify that the replica set has elected a primary:

```javascript
rs.status()
```

#### Create an admin user

When using a keyfile, authorization is enabled. Use the localhost exception to create an admin user before running cluster administration commands:

```javascript
use admin

db.createUser({
  user: "admin",
  pwd: "<ADMIN_PASSWORD>",
  roles: [
    { role: "root", db: "admin" }
  ]
})
```

### Start a shard server

Start another `mongod` container as a shard server, using the same keyfile. It joins the `shard1rs` replica set and listens on the default port `27017`:

```bash
docker run -d \
  --name shard1 \
  --network mongo-cluster \
  -v shard1-data:/var/lib/mongodb \
  -v "$(pwd)/mongodb-keyfile:/etc/mongod/keyfile:ro" \
  -e MONGOD_ARGS="--shardsvr --replSet shard1rs --port 27017 --bind_ip_all --keyFile /etc/mongod/keyfile" \
  "$IMAGE"
```

#### Initialize the shard replica set

Connect to the shard instance:

```bash
docker exec -it shard1 mongosh --port 27017
```

Initialize the replica set:

```javascript
rs.initiate({
  _id: "shard1rs",
  members: [
    { _id: 0, host: "shard1:27017" }
  ]
})
```

Verify that the replica set has elected a primary:

```javascript
rs.status()
```

### Start the query router

Start a container running only the `mongos` service by passing the `start mongos` subcommand to Pebble. The router points at the config server replica set and listens on port `27018`:

```bash
docker run -d \
  --name mongos \
  --network mongo-cluster \
  -v "$(pwd)/mongodb-keyfile:/etc/mongod/keyfile:ro" \
  -e MONGOS_ARGS="--configdb configrs/configsvr:27019 --bind_ip_all --keyFile /etc/mongod/keyfile" \
  "$IMAGE" start mongos
```

### Add the shard to the cluster

Connect to the query router using the admin user created earlier:

```bash
docker exec -it mongos mongosh "mongodb://admin:<ADMIN_PASSWORD>@127.0.0.1:27018/admin"
```

Add the shard replica set to the cluster:

```javascript
sh.addShard("shard1rs/shard1:27017")
```

You should see:

```javascript
{
  shardAdded: 'shard1rs',
  ok: 1,
  '$clusterTime': { /* ... */ },
  operationTime: Timestamp({ t: 1780386971, i: 18 })
}
```

Verify the cluster configuration:

```javascript
sh.status()
```

The output should show the newly added `shard1rs` shard.

### Shard a test collection

Still connected to `mongos`, create the required shard-key index:

```javascript
use testdb
db.test.createIndex({ _id: "hashed" })
```

Shard the collection:

```javascript
sh.shardCollection("testdb.test", { _id: "hashed" })
```

Add documents to the collection:

```javascript
for (let i = 0; i < 1000; i++) {
  db.test.insertOne({ value: i })
}
```

Check the number of documents:

```javascript
db.test.countDocuments()
```

Check the distribution:

```javascript
db.test.getShardDistribution()
```

The output should show that the data is stored in `shard1rs`.

### Tear down

When you are finished, stop the containers gracefully, then remove them:

```bash
docker stop configsvr shard1 mongos
docker rm configsvr shard1 mongos
docker network rm mongo-cluster
```

Removing the containers does **not** delete their data: the `configsvr-data` and `shard1-data` volumes persist, so you can start fresh containers against the same volumes and recover the data.

To delete the data permanently, remove the volumes as well:

```bash
docker volume rm configsvr-data shard1-data
```

## Available tools

The rock also packages the standard MongoDB command-line tools:

- `mongosh`
- `mongobridge`
- `mongodump`
- `mongoexport`
- `mongofiles`
- `mongoimport`
- `mongorestore`
- `mongostat`
- `mongotop`

Run them with `docker exec` against a running container, for example:

```bash
docker exec -it configsvr mongosh --port 27019
docker exec configsvr mongodump --port 27019 --out /var/lib/mongodb/backup
```

## Getting command help

To see more information about a service or tool, run it with `--help`. For example:

```bash
docker run --rm "$IMAGE" exec mongod --help
docker run --rm "$IMAGE" exec mongos --help
docker exec <container-name> mongodump --help
```

## Logs

Each component writes its log inside the container:

- `mongod` &rarr; `/var/log/mongodb/mongod.log`
- `mongos` &rarr; `/var/log/mongodb/mongos.log`

View them with `docker exec`, or inspect Pebble's view of the services:

```bash
docker exec configsvr tail -f /var/log/mongodb/mongod.log
docker exec configsvr pebble services
```

## License

The Sharded MongoDB Server rock is free software, distributed under the Apache
Software License, version 2.0. See [LICENSE](LICENSE) for more information.
It installs and operates Percona Server for MongoDB, which is licensed under the
Server Side Public License (SSPL) version 1.

## Trademark Notice

MongoDB is a trademark or registered trademark of MongoDB, Inc.
Percona is a trademark or registered trademark of Percona LLC.
Other trademarks are property of their respective owners.
The Sharded MongoDB Server rock is not sponsored, endorsed, or affiliated with MongoDB, Inc.

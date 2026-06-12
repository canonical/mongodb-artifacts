# MongoDB Server replica set rock (OCI Image)

[MongoDB](https://github.com/mongodb/mongo) is a source-available, cross-platform,
document-oriented database application. Classified as a NoSQL database program,
MongoDB uses JSON-like documents with optional schemas.

The Replica Set MongoDB Server rock is an Open Container Initiative (OCI) image derived from the
[Replica Set MongoDB Server snap](https://snapcraft.io/mongodb-server-replicaset) and built from the
official Percona repositories. The tool used to create this rock is called
[Rockcraft](https://canonical-rockcraft.readthedocs-hosted.com/en/latest/index.html).

This rock is intended to be run as a MongoDB replica set deployment. It delivers the `mongod`
component plus the standard MongoDB administration tools.

For sharded deployments, use the `mongodb-server-sharded` rock.
For standalone `mongos`, use the `mongos` rock.

## How the rock is structured

The rock defines one service:

| Service  | Startup   | Command                         | Default port |
| -------- | --------- | ------------------------------- | ------------ |
| `mongod` | `enabled` | `/bin/bash /bin/start-mongod.sh` | `27017`      |

The `mongod` service runs as the unprivileged `mongodb` user (uid `584788`) and reads the
configuration file found in the image:

- `mongod` &rarr; `/etc/mongod/mongod.conf` (data in `/var/lib/mongodb`)

Extra MongoDB arguments are passed through the `MONGOD_ARGS` environment variable. You can read
more about the available options in the [`mongod`](https://www.mongodb.com/docs/manual/reference/program/mongod/)
documentation.

## Installing Docker

To get started with the rock, first install Docker:

```bash
sudo snap install docker
```

## Obtaining the rock

Pull the published image from the GitHub Container Registry:

```bash
docker pull ghcr.io/canonical/mongodb-server-replicaset:<version>
```

Alternatively, import a locally built rock archive into Docker using `skopeo` (bundled with Rockcraft):

```bash
sudo rockcraft.skopeo --insecure-policy copy \
  oci-archive:mongodb-server-replicaset_*_amd64.rock \
  docker-daemon:ghcr.io/canonical/mongodb-server-replicaset:local-test
```

The rest of this guide refers to the image through the `IMAGE` shell variable, so that you can
adjust the tag in a single place:

```bash
export IMAGE=ghcr.io/canonical/mongodb-server-replicaset:local-test
```

## Using the rock as a replica set

The following walkthrough builds a minimal three-member replica set on a single host, using a
dedicated Docker network. In production, run each member on a separate host or failure domain and
use persistent storage sized for your workload.

### Create a Docker network

A user-defined network lets the containers reach each other by name:

```bash
docker network create mongo-replicaset
```

### Configure internal authentication

MongoDB replica set members use a shared keyfile for internal authentication. Every member must use
the same keyfile.

Each container automatically generates a keyfile at `/etc/mongod/mongodb-keyfile` (mode `400`,
owned by the `mongodb` user, uid `584788`) the first time it starts, unless a keyfile is already
present at that path.

In this walkthrough we let the first member generate the key, read it back with `get-keyfile`, and
apply it to the other members with `set-keyfile`.

### Start the replica set members

Start the first `mongod` container. It joins the `rs0` replica set, listens on the default port
`27017`, and mounts a data volume:

```bash
docker run -d \
  --name mongo1 \
  --network mongo-replicaset \
  -v mongo1-data:/var/lib/mongodb \
  -e MONGOD_ARGS="--replSet rs0 --bind_ip 0.0.0.0" \
  "$IMAGE"
```

Capture the key the first member generated into a shell variable, so you can apply it to the other
members:

```bash
KEYFILE_CONTENT="$(docker exec mongo1 get-keyfile)"
```

Start the second and third members:

```bash
docker run -d \
  --name mongo2 \
  --network mongo-replicaset \
  -v mongo2-data:/var/lib/mongodb \
  -e MONGOD_ARGS="--replSet rs0 --bind_ip 0.0.0.0" \
  "$IMAGE"

docker run -d \
  --name mongo3 \
  --network mongo-replicaset \
  -v mongo3-data:/var/lib/mongodb \
  -e MONGOD_ARGS="--replSet rs0 --bind_ip 0.0.0.0" \
  "$IMAGE"
```

On first start, these containers generated their own keyfiles. Replace them with the first member's
key and restart the containers so `mongod` reloads the shared keyfile:

```bash
docker exec mongo2 set-keyfile "$KEYFILE_CONTENT"
docker exec mongo3 set-keyfile "$KEYFILE_CONTENT"
docker restart mongo2 mongo3
```

### Initialize the replica set

Connect to the first member:

```bash
docker exec -it mongo1 mongosh --port 27017
```

Initialize the replica set:

```javascript
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo1:27017" },
    { _id: 1, host: "mongo2:27017" },
    { _id: 2, host: "mongo3:27017" }
  ]
})
```

Verify that the replica set has elected a primary:

```javascript
rs.status()
```

### Create an admin user

When using a keyfile, authorization is enabled. Use the localhost exception to create an admin user
before running authenticated administration commands:

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

### Write and read test data

Reconnect with the admin user:

```bash
docker exec -it mongo1 mongosh "mongodb://admin:<ADMIN_PASSWORD>@127.0.0.1:27017/admin"
```

Insert a test document through the primary:

```javascript
use testdb
db.test.insertOne({ _id: 1, value: "hello from rs0" })
db.test.findOne({ _id: 1 })
```

To check the replica set from another member, connect with a replica-set URI and allow reads from
secondaries:

```bash
docker exec -it mongo2 mongosh \
  "mongodb://admin:<ADMIN_PASSWORD>@mongo1:27017,mongo2:27017,mongo3:27017/admin?replicaSet=rs0&readPreference=secondaryPreferred"
```

Then read the document:

```javascript
db.getSiblingDB("testdb").test.findOne({ _id: 1 })
```

## Tear down

When you are finished, stop the containers gracefully, then remove them:

```bash
docker stop mongo1 mongo2 mongo3
docker rm mongo1 mongo2 mongo3
docker network rm mongo-replicaset
```

Removing the containers does **not** delete their data: the `mongo1-data`, `mongo2-data`, and
`mongo3-data` volumes persist, so you can start fresh containers against the same volumes and
recover the data.

To delete the data permanently, remove the volumes as well:

```bash
docker volume rm mongo1-data mongo2-data mongo3-data
```

## Managing the keyfile

The image provides two commands for inspecting and changing the internal-auth keyfile of a running
container. Run them as the default `docker exec` user (root), which can read and rewrite the `400`
keyfile owned by uid `584788`:

| Command | Behaviour |
| ------- | --------- |
| `get-keyfile` | Print the current keyfile (`/etc/mongod/mongodb-keyfile`) to standard output. |
| `set-keyfile <key>` | Store `<key>` as the keyfile contents. |

For example, to copy the auto-generated key from one container into another so they share the same
key:

```bash
key="$(docker exec mongo1 get-keyfile)"
docker exec mongo2 set-keyfile "$key"
```

Notes:

- `mongod` reads the keyfile only at startup, so restart the service (`docker restart <container>`)
  after changing the keyfile for it to take effect.
- Every member of a replica set must use the same key. When rotating, propagate the new value to all
  members before restarting them.

## Available tools

The rock also packages the standard MongoDB command-line tools:

- `get-keyfile`
- `set-keyfile`
- `mongosh`
- `mongobridge`
- `mongod-cli`
- `mongodump`
- `mongoexport`
- `mongofiles`
- `mongoimport`
- `mongorestore`
- `mongostat`
- `mongotop`

Run them with `docker exec` against a running container, for example:

```bash
docker exec -it mongo1 mongosh --port 27017
docker exec mongo1 mongodump --port 27017 --out /var/lib/mongodb/backup
```

## Getting command help

To see more information about a service or tool, run it with `--help`. For example:

```bash
docker run --rm "$IMAGE" exec mongod --help
docker exec <container-name> mongodump --help
```

## Logs

`mongod` writes its log inside the container:

- `mongod` &rarr; `/var/log/mongodb/mongod.log`

View it with `docker exec`, or inspect Pebble's view of the service:

```bash
docker exec mongo1 tail -f /var/log/mongodb/mongod.log
docker exec mongo1 pebble services
```

## License

The Replica Set MongoDB Server rock is free software, distributed under the Apache Software License,
version 2.0. See [LICENSE](LICENSE) for more information. It installs and operates Percona Server
for MongoDB, which is licensed under the Server Side Public License (SSPL) version 1.

## Trademark Notice

MongoDB is a trademark or registered trademark of MongoDB, Inc.
Percona is a trademark or registered trademark of Percona LLC.
Other trademarks are property of their respective owners.
The Replica Set MongoDB Server rock is not sponsored, endorsed, or affiliated with MongoDB, Inc.

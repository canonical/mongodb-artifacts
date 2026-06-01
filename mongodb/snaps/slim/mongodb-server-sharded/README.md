# Sharded MongoDB Server Snap
[![.github/workflows/publish.yaml](https://github.com/canonical/mongodb-artifacts/actions/workflows/publish.yaml/badge.svg)](https://github.com/canonical/mongodb-artifacts/actions/workflows/publish.yaml)

This repository contains the packaging metadata for creating a snap of Sharded MongoDB built from the official Percona Debian repositories. For more information on snaps, visit [snapcraft.io](https://snapcraft.io/).

This snap is intended to be run as a MongoDB sharded deployment. It delivers both `mongod` and `mongos` components for a complete sharded cluster. If you only need the query router, there is a smaller separate [`mongos`](https://snapcraft.io/mongos) snap available.

For replica set deployments, see the [`mongodb-server-replicaset`](https://snapcraft.io/mongodb-server-replicaset) snap.

## Installing the Snap
The snap can be installed directly from the Snap Store. Follow the link below for more information.
<br>

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/mongodb-server-sharded)

or 

```bash
sudo snap install mongodb-server-sharded --channel=8/edge
```

## Using Sharded MongoDB server

## Configure internal authentication

This snap delivers both `mongod` and `mongos` components for a sharded cluster deployment.
MongoDB sharded clusters use a shared keyfile for internal authentication between config servers,
shard servers, and query routers (`mongos`).

### Generate a keyfile

Generate a keyfile on one machine:

```bash
openssl rand -base64 756 > mongodb-keyfile
chmod 400 mongodb-keyfile
```

Copy the same keyfile to all machines participating in the cluster.

For snap deployments, place the keyfile in a location accessible to the snap, for example:

```bash
sudo cp mongodb-keyfile /var/snap/mongodb-server-sharded/common/mongodb-keyfile
sudo chmod 400 /var/snap/mongodb-server-sharded/common/mongodb-keyfile
```

### Configure the config server and query router

Configure `mongod` service to used the shared keyfile:

```bash
sudo snap set mongodb-server-sharded mongod-args="--configsvr --replSet configrs --port 27019 --bind_ip 127.0.0.1 --keyFile /var/snap/mongodb-server-sharded/common/mongodb-keyfile"
```

Configure `mongos` to use the shared keyfile:
```bash
sudo snap set mongodb-server-sharded mongos-args="--configdb configrs/127.0.0.1:27019 --bind_ip 127.0.0.1 --port 27018 --keyFile /var/snap/mongodb-server-sharded/common/mongodb-keyfile"
```

### Start the services
```bash
sudo snap start mongodb-server-sharded.mongod
sudo snap start mongodb-server-sharded.mongos
```

### Check service status
```bash
snap services mongodb-server-sharded
```

You should see both `mongodb-server-sharded.mongod` and `mongodb-server-sharded.mongos` listed.

### Configure shard servers

This snap only allows a single `mongod` service per machine. If you want to add another shard,
run it on a separate machine and make sure the machines can connect to each other over the required
MongoDB ports.

When configuring a shard server, use the same keyfile:

```bash
sudo snap set mongodb-server-sharded mongod-args="--shardsvr --replSet shard1rs --port 27020 --bind_ip 0.0.0.0 --keyFile /var/snap/mongodb-server-sharded/common/mongodb-keyfile"
```

Start the service:

``` bash
sudo snap start mongodb-server-sharded.mongod
```

### Initialize the shard replica set

Connect to the shard instance:

```bash
snap run mongodb-server-sharded.mongosh --port 27020
```

Initialize the replica set:

```javascript
rs.initiate({
  _id: "shard1rs",
  members: [
    { _id: 0, host: "<SHARD_MACHINE_IP>:27020" }
  ]
})
```

Verify that the replica set has elected a primary:

```javascript
rs.status()
```

### Add the shard to the cluster

Connect to the query router (`mongos`):

```bash
snap run mongodb-server-sharded.mongosh --port 27018
```

Add the shard replica set to the cluster:

```javascript
sh.addShard("shard1rs/<SHARD_MACHINE_IP>:27020")
```

Example:

```javascript
sh.addShard("shard1rs/10.0.0.25:27020")
```

### Verify the cluster configuration

List the registered shards:

```javascript
sh.status()
```

The output should show the newly added shard replica set.


## Available snap apps
The snap includes the following command-line tools:

- `mongodb-server-sharded.mongosh`
- `mongodb-server-sharded.mongobridge`
- `mongodb-server-sharded.mongod-cli`
- `mongodb-server-sharded.mongodump`
- `mongodb-server-sharded.mongoexport`
- `mongodb-server-sharded.mongofiles`
- `mongodb-server-sharded.mongoimport`
- `mongodb-server-sharded.mongorestore`
- `mongodb-server-sharded.mongostat`
- `mongodb-server-sharded.mongotop`

Use `snap run` with the app name, for example:
```bash
snap run mongodb-server-sharded.mongosh --port 27019
```


## Getting command help
To see more information about a service or app, run it with `--help`. For example:
```bash
sudo snap run mongodb-server-sharded.mongod --help
sudo snap run mongodb-server-sharded.mongos --help
```
You can use this pattern for any of the included apps.

## Logs
Logs are stored in:

- `/var/snap/mongodb-server-sharded/common/var/log/mongodb/mongod.log`
- `/var/snap/mongodb-server-sharded/common/var/log/mongodb/mongos.log`

## License
The Sharded MongoDB Server Snap is free software, distributed under the Apache
Software License, version 2.0. See [LICENSE](LICENSE) for more information.

## Trademark Notice
MongoDB is a trademark or registered trademark of MongoDB, Inc.
Percona is a trademark or registered trademark of Percona LLC.
Other trademarks are property of their respective owners.

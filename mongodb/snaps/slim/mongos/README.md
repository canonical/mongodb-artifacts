# Mongos Snap
[![.github/workflows/publish.yaml](https://github.com/canonical/mongodb-artifacts/actions/workflows/publish.yaml/badge.svg)](https://github.com/canonical/mongodb-artifacts/actions/workflows/publish.yaml)

This repository contains the packaging metadata for creating a snap of Mongos built from the official Percona Debian repositories. Mongos is the MongoDB sharded cluster query router.

This snap includes only the `mongos` query router for a sharded deployment. For the full sharded cluster, see the [`mongodb-server-sharded`](https://snapcraft.io/mongodb-server-sharded) snap as a complement. For a replica set deployment instead, see the [`mongodb-server-replicaset`](https://snapcraft.io/mongodb-server-replicaset) snap.

## Installing the snap
The snap can be installed directly from the Snap Store.

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/mongos)

or 

```bash
sudo snap install mongos --channel=8/edge
```

## Using mongos snap
Before starting the service, configure the query router to connect to your config server replica set.

```bash
sudo snap set mongos mongos-args="--configdb configrs/127.0.0.1:27019 --bind_ip 127.0.0.1 --port 27018"
```

Start the service:

```bash
sudo snap start mongos.mongos
```

## Check service status
```bash
snap services mongos
```

You should see:
```
Service         Startup   Current  Notes
mongos.mongos   disabled  active   -
```

## Available apps
This snap includes the following apps:

- `mongos.mongodump`
- `mongos.mongoexport`
- `mongos.mongofiles`
- `mongos.mongoimport`
- `mongos.mongorestore`
- `mongos.mongosh`
- `mongos.mongostat`
- `mongos.mongotop`

Use `snap run` with the app name. For example:

```bash
snap run mongos.mongosh --port 27018
```

## Getting command help
To see more information about a service or app, run it with `--help`. For example:
```bash
sudo snap run mongodb-server-sharded.mongos --help
```

You can use this pattern for any of the included apps.

## Logs
Logs are stored in:

- `/var/snap/mongodb/common/var/log/mongodb/mongos.log`

## License
The Mongos Snap is free software, distributed under the Apache Software License,
version 2.0. See [LICENSE](LICENSE) for more information.

## Trademark Notice
MongoDB is a trademark or registered trademark of MongoDB, Inc.
Percona is a trademark or registered trademark of Percona LLC.
Other trademarks are property of their respective owners.

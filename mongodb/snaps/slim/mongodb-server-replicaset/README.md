# MongoDB server replica set snap
[![.github/workflows/publish.yaml](https://github.com/canonical/mongodb-artifacts/actions/workflows/publish.yaml/badge.svg)](https://github.com/canonical/mongodb-artifacts/actions/workflows/publish.yaml)

This repository contains the packaging metadata for creating a snap of MongoDB built from the official Percona Debian repositories. For more information on snaps, visit [snapcraft.io](https://snapcraft.io/).

This snap is intended to be run as a MongoDB replica set deployment. For sharded deployments,
see the [`mongodb-server-sharded`](https://snapcraft.io/mongodb-server-sharded) snap and the [`mongos`](https://snapcraft.io/mongos) snaps.


## Installing the snap
The snap can be installed directly from the Snap Store.

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/mongodb-server-replicaset)


or 

```bash
sudo snap install mongodb-server-replicaset --channel=8/edge
```

## Using the MongoDB replicaset server snap

This snap delivers `mongod` components for a replica set deployment. Run the following command to start the service:

```bash
sudo snap start mongodb-server-replicaset.mongod
```

## Check MongoDB service status
```bash
snap services mongodb-server-replicaset
```

You should see:
```
Service                           Startup   Current  Notes
mongodb-server-replicaset.mongod  disabled  active   -
```

## Available apps
This snap provides the following apps:

- `mongodb-server-replicaset.mongobridge`
- `mongodb-server-replicaset.mongod-cli`
- `mongodb-server-replicaset.mongodump`
- `mongodb-server-replicaset.mongoexport`
- `mongodb-server-replicaset.mongofiles`
- `mongodb-server-replicaset.mongoimport`
- `mongodb-server-replicaset.mongorestore`
- `mongodb-server-replicaset.mongosh`
- `mongodb-server-replicaset.mongostat`
- `mongodb-server-replicaset.mongotop`

Use `snap run` with the app name. For example:
```bash
snap run mongodb-server-replicaset.mongosh
```

## Getting command help
To see more information about a service or app, run it with `--help`. For example:
```bash
sudo snap run mongodb-server-sharded.mongod --help
```
You can use this pattern for any of the included apps.

## Logs
Logs are stored in:

- `/var/snap/mongodb-server-replicaset/common/var/log/mongodb/mongod.log`

## License
The MongoDB Replicaset Server Snap is free software, distributed under the Apache Software License,
version 2.0. See [LICENSE](LICENSE) for more information.

## Trademark Notice
MongoDB is a trademark or registered trademark of MongoDB, Inc.
Percona is a trademark or registered trademark of Percona LLC.
Other trademarks are property of their respective owners.

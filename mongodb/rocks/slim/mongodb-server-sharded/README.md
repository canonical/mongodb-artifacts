## Introduction to Sharded MongoDB Server rock  (OCI Image)

[![Operator Tests](https://github.com/canonical/mongodb-artifacts/actions/workflows/integration.yaml/badge.svg)](https://github.com/canonical/mongodb-artifacts/actions/workflows/integration.yaml)

[MongoDB](https://github.com/mongodb/mongo) is a source-available, cross-platform, document-oriented database application. Classified as a NoSQL database program, MongoDB uses JSON-like documents with optional schemas.

Sharded MongoDB Server rock is an Open Container Initiative (OCI) image derived from the [Sharded MongoDB Server Snap](https://snapcraft.io/mongodb-server-sharded). The tool used to create this rock is called [Rockcraft](https://canonical-rockcraft.readthedocs-hosted.com/en/latest/index.html).

## Version

Rocks will be named as `<version>-<series>_<risk>`.

`<version>` is the software version; `<series>` is the Ubuntu LTS series that rocks supports; and the <risk> is the type of release, if it is edge, candidate or stable. Example versioning will be 5-22.04_stable which means Charmed MongoDB is a version 5 of the software, supporting the 22.04 Ubuntu release and currently a 'stable' version of the software. See  versioning details [here](https://snapcraft.io/docs/channels).

Channel can also be represented by combining `<version>_<risk>`



## Rocks Usage
### Starting mongod and accessing the database
To get started with the mongodb-server-sharded rock, first install docker:

```bash
sudo snap install docker
```

Then to use the Sharded MongoDB Server rock run the following command

```bash
sudo docker run --rm -it ghcr.io/canonical/mongodb-server-sharded:8_edge
```

By running this command you have already started the mongod service with Percona Server for MongoDB. Leave this command running and create another terminal.

*Note if you would like to start `mongod` with custom options you can append your desired options to the container run command i.e.*: `sudo docker run --rm -it ghcr.io/canonical/mongodb-server-sharded:8_edge --bind-ip-all --another-option` *you can read more about [mongod optons here](https://www.mongodb.com/docs/manual/reference/program/mongod/)*

To access your now running MongoDB instance enter the command: 

```bash
sudo docker container ls
```

This should output something like this:

```bash
CONTAINER ID   IMAGE                                COMMAND                  CREATED          STATUS          PORTS     NAMES
bf08481d18a3   ghcr.io/canonical/mongodb-server-sharded:8_edge   "/bin/pebble enter -…"   About a minute ago   Up About a minute             quizzical_sinoussi
```

The name of the container is listed under `NAME` - use this name to connect to your now running database

```bash
sudo docker exec --interactive <container-name> mongosh
```

Now enter `show dbs` this should show you all of your available databases and output something like:

```bash
admin   0.000GB
config  0.000GB
local   0.000GB
```

While using `mongo` can run a variety of [database commands](https://www.mongodb.com/docs/manual/reference/command/) such as creating databases, users, adding config options, etc. When you are ready to return to the terminal enter `exit`.


### Others tools within the rock

The MongoDB rock also packages other useful tools like `mongodump`, `mongorestore`, and many other tools. You can read more about the tools packaged in the snap by entering:

```bash
docker exec <container-name> <tool name> --help`
``` 


## License
The Sharded MongoDB Server rock is free software, distributed under the Apache
Software License, version 2.0. See [LICENSE](LICENSE) for more information.
It installs and operates Percona Server for MongoDB, which is licensed under the Server Side Public License (SSPL) version 1.

## Trademark Notice
MongoDB is a trademark or registered trademark of MongoDB, Inc.
Percona is a trademark or registered trademark of Percona LLC.
Other trademarks are property of their respective owners.
Sharded MongoDB server is not sponsored, endorsed, or affiliated with MongoDB, Inc.
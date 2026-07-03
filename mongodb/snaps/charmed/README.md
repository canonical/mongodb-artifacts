# Charmed MongoDB Snap
[![.github/workflows/publish.yaml](https://github.com/canonical/charmed-mongodb-snap/actions/workflows/publish.yaml/badge.svg)](https://github.com/canonical/charmed-mongodb-snap/actions/workflows/publish.yaml)

This repository contains the packaging metadata for creating a snap of Charmed MongoDB built from the official percona debian repositories. For more information on snaps, visit [snapcraft.io](https://snapcraft.io/). 

## Installing the Snap
The snap can be installed directly from the Snap Store. Follow the link below for more information.
<br>

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/charmed-mongodb)

## Building the Snap
### Clone Repository
```bash
git clone https://github.com/canonical/charmed-mongodb-snap.git
cd charmed-mongodb-snap
```
### Installing and Configuring Prerequisites
```bash
sudo snap install snapcraft --classic
sudo snap install lxd
sudo lxd init --auto
```
### Packing and Installing the Snap
```bash
snapcraft pack
sudo snap install ./charmed-mongodb*.snap --devmode
```

## License
The Charmed MongoDB Snap is free software, distributed under the Apache
Software License, version 2.0. See
[LICENSE](https://github.com/canonical/charmed-mongodb-snap/blob/5/edge/licenses)
for more information.

## Trademark Notice
MongoDB is a trademark or registered trademark of MongoDB, Inc.
Percona is a trademark or registered trademark of Percona LLC.
Other trademarks are property of their respective owners.


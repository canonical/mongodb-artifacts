# mongodb-artifacts

This repository contains MongoDB packaging artifacts used by Canonical, including snaps and rocks for MongoDB server deployments.


## Repository structure

The main directory structure is:

```text
mongodb-artifacts/
├── LICENSE
├── README.md
└── mongodb/
    ├── snaps/
    │   └── slim/
    │       ├── mongodb-server-replicaset/ # Snap for a MongoDB replica set deployment.
    │       ├── mongodb-server-sharded/ # Snap for a full MongoDB sharded deployment that includes both `mongod` and `mongos`.
    │       └── mongos/ # Snap for the MongoDB sharded cluster query router only (`mongos`).
    └── rocks/  # future MongoDB rocks
```

## Getting started

To work on a specific snap, change into the appropriate subdirectory and use `snapcraft` to build it:

```bash
git clone https://github.com/canonical/mongodb-artifacts.git
cd mongodb-artifacts/mongodb/snaps/slim/<snap-name>
snapcraft pack
```

For development builds, install the generated snap with `--devmode`:

```bash
sudo snap install ./<snap-name>*.snap --devmode
```

Each snap also includes its own `README.md` with installation, usage, and build instructions.

## Contributing

If you want to contribute, see the `CONTRIBUTING.md` file in the relevant snap subdirectory for clone, build, lint, and test instructions.

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

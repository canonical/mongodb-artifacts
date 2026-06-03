import base64
import yaml
import subprocess
import time
import pytest


def test_install():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)

        subprocess.run(
            f"sudo snap install ./{snapcraft['name']}_{snapcraft['version']}_amd64.snap --dangerous".split(),
            check=True,
        )


@pytest.mark.run(after="test_install")
def test_generate_and_store_keyfile():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    name = snapcraft["name"]
    keyfile = f"/var/snap/{name}/common/mongodb-keyfile"

    generated = subprocess.run(
        f"{name}.generate-keyfile".split(),
        check=True,
        capture_output=True,
    )
    assert generated.stdout, "generate-keyfile produced no output"

    # The keyfile must be 756 random bytes, base64-encoded (`rand -base64 756`).
    decoded = base64.b64decode(generated.stdout)
    assert len(decoded) == 756, f"expected 756 decoded bytes, got {len(decoded)}"

    subprocess.run(
        f"sudo snap run {name}.store-keyfile".split(),
        check=True,
        input=generated.stdout,
    )

    stat = subprocess.run(
        ["sudo", "stat", "-c", "%a %u", keyfile],
        check=True,
        capture_output=True,
        text=True,
    )
    mode, uid = stat.stdout.split()
    assert mode == "400", f"unexpected keyfile mode: {mode}"
    assert uid == "584788", f"unexpected keyfile owner uid: {uid}"

    # The stored content must match what was generated.
    stored = subprocess.run(
        ["sudo", "cat", keyfile],
        check=True,
        capture_output=True,
    )
    assert stored.stdout == generated.stdout, "stored keyfile content differs"


@pytest.mark.run(after="test_generate_and_store_keyfile")
def test_all_apps():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)

        for app, data in snapcraft["apps"].items():
            if not data.get("daemon"):
                print(f"Testing {snapcraft['name']}.{app}....")
                subprocess.run(
                    f"{snapcraft['name']}.{app} --help".split(),
                    check=True,
                )


def _current_status(name, app):
    """Return the 'Current' column from `snap services <name>.<app>`.

    The output looks like:

        Service                        Startup   Current   Notes
        mongodb-server-sharded.mongod  disabled  active    -

    so the status is the third whitespace-separated field of the data row.
    """
    result = subprocess.run(
        f"snap services {name}.{app}".split(),
        check=True,
        capture_output=True,
        text=True,
    )
    print(result.stdout)
    for line in result.stdout.strip().splitlines()[1:]:
        fields = line.split()
        if fields and fields[0] == f"{name}.{app}":
            return fields[2]
    raise AssertionError(f"{name}.{app} not found in:\n{result.stdout}")


@pytest.mark.run(after="test_all_apps")
def test_all_services():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    name = snapcraft["name"]
    keyfile = f"/var/snap/{name}/common/mongodb-keyfile"

    # Configure mongod as the config server ...
    subprocess.run(
        [
            "sudo",
            "snap",
            "set",
            name,
            f"mongod-args=--configsvr --replSet configrs --port 27019 "
            f"--bind_ip 127.0.0.1 --keyFile {keyfile}",
        ],
        check=True,
    )
    # Configure mongos as the query router pointing at it.
    subprocess.run(
        [
            "sudo",
            "snap",
            "set",
            name,
            f"mongos-args=--configdb configrs/127.0.0.1:27019 "
            f"--bind_ip 127.0.0.1 --port 27018 --keyFile {keyfile}",
        ],
        check=True,
    )

    try:
        for app in ("mongod", "mongos"):
            print(f"\nTesting {name}.{app} service....")
            subprocess.run(f"sudo snap start {name}.{app}".split(), check=True)
            time.sleep(5)
            status = _current_status(name, app)
            assert status == "active", f"{name}.{app} is {status!r}, expected 'active'"
    finally:
        for app in ("mongos", "mongod"):
            subprocess.run(f"sudo snap stop {name}.{app}".split())


@pytest.mark.run(after="test_all_services")
def test_remove():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    subprocess.run(f"sudo snap remove --purge {snapcraft['name']}".split())

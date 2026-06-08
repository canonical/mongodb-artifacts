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
def test_set_keyfile():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    name = snapcraft["name"]
    keyfile = f"/var/snap/{name}/current/etc/keyfile"

    content = "test-keyfile-value"

    subprocess.run(
        ["sudo", "snap", "run", f"{name}.set-keyfile", content],
        check=True,
    )

    stat = subprocess.run(
        ["sudo", "stat", "-c", "%a %u %g", keyfile],
        check=True,
        capture_output=True,
        text=True,
    )
    mode, uid, gid = stat.stdout.split()
    assert mode == "400", f"unexpected keyfile mode: {mode}"
    assert uid == "584788", f"unexpected keyfile owner uid: {uid}"
    assert gid == "584788", f"unexpected keyfile owner gid: {gid}"

    stored = subprocess.run(
        ["sudo", "cat", keyfile],
        check=True,
        capture_output=True,
        text=True,
    )
    assert stored.stdout == f"{content}\n", "stored keyfile content differs"


@pytest.mark.run(after="test_set_keyfile")
def test_mongos_config_keyfile():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    name = snapcraft["name"]
    keyfile = f"/var/snap/{name}/current/etc/keyfile"
    config_file = f"/var/snap/{name}/current/etc/mongod/mongos.conf"

    config_content = subprocess.run(
        ["sudo", "cat", config_file],
        check=True,
        capture_output=True,
        text=True,
    )
    loaded_config = yaml.safe_load(config_content.stdout)
    assert loaded_config["security"]["keyFile"] == keyfile


@pytest.mark.run(after="test_mongos_config_keyfile")
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
def test_mongos_service():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    name = snapcraft["name"]

    subprocess.run(
        [
            "sudo",
            "snap",
            "set",
            name,
            f"mongos-args=--configdb configrs/127.0.0.1:27019 "
            f"--bind_ip 127.0.0.1 --port 27018",
        ],
        check=True,
    )

    app = "mongos"
    try:
        print(f"\nTesting {name}.{app} service....")
        subprocess.run(f"sudo snap start {name}.{app}".split(), check=True)
        time.sleep(5)
        status = _current_status(name, app)
        assert status == "active", f"{name}.{app} is {status!r}, expected 'active'"
    finally:
        subprocess.run(f"sudo snap stop {name}.{app}".split())


@pytest.mark.run(after="test_mongos_service")
def test_remove():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    subprocess.run(f"sudo snap remove --purge {snapcraft['name']}".split())

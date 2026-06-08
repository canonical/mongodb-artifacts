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
def test_keyfile_actions():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    name = snapcraft["name"]
    keyfile = f"/var/snap/{name}/current/etc/keyfile"

    set_content = "test-set-keyfile-value"
    subprocess.run(
        ["sudo", "snap", "run", f"{name}.set-keyfile", set_content],
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

    retrieved = subprocess.run(
        f"sudo snap run {name}.get-keyfile".split(),
        check=True,
        capture_output=True,
        text=True,
    )
    assert retrieved.stdout == f"{set_content}\n", "get-keyfile content differs"


@pytest.mark.run(after="test_keyfile_actions")
def test_keyfile_path_in_config():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    name = snapcraft["name"]
    keyfile = f"/var/snap/{name}/current/etc/keyfile"

    config_file = f"/var/snap/{name}/current/etc/mongod/mongod.conf"
    config_content = subprocess.run(
        ["sudo", "cat", config_file],
        check=True,
        capture_output=True,
        text=True,
    )
    loaded_config = yaml.safe_load(config_content.stdout)
    assert loaded_config["security"]["keyFile"] == keyfile


@pytest.mark.run(after="test_keyfile_actions")
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

        for app, data in snapcraft["apps"].items():
            if data.get("daemon"):
                print(f"\nTesting {snapcraft['name']}.{app} service....")
                subprocess.run(
                    f"sudo snap start {snapcraft['name']}.{app}".split(), check=True
                )
                time.sleep(5)
                status = _current_status(snapcraft["name"], app)
                subprocess.run(f"sudo snap stop {snapcraft['name']}.{app}".split())

                assert status == "active"


@pytest.mark.run(after="test_all_services")
def test_remove():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    subprocess.run(f"sudo snap remove --purge {snapcraft['name']}".split())

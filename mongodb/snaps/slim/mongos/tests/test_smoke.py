import base64
import os
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
def test_store_keyfile():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    name = snapcraft["name"]
    keyfile = f"/var/snap/{name}/common/mongodb-keyfile"

    # Build a representative keyfile (756 random bytes, base64-encoded).
    content = base64.b64encode(os.urandom(756))

    subprocess.run(
        f"sudo snap run {name}.store-keyfile".split(),
        check=True,
        input=content,
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

    # The stored content must match what was provided on stdin.
    stored = subprocess.run(
        ["sudo", "cat", keyfile],
        check=True,
        capture_output=True,
    )
    assert stored.stdout == content, "stored keyfile content differs"


@pytest.mark.run(after="test_install")
def test_all_apps():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)

        override = {}

        skip = []

        for app, data in snapcraft["apps"].items():
            if not bool(data.get("daemon")) and app not in skip:
                print(f"Testing {snapcraft['name']}.{app}....")
                subprocess.run(
                    f"{snapcraft['name']}.{app} {override.get(app, '--help')}".split(),
                    check=True,
                )


@pytest.mark.run(after="test_install")
def test_all_services():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)

        skip = []

        for app, data in snapcraft["apps"].items():
            if bool(data.get("daemon")) and app not in skip:
                print(f"\nTesting {snapcraft['name']}.{app} service....")
                subprocess.run(
                    f"sudo snap start {snapcraft['name']}.{app}".split(), check=True
                )
                time.sleep(5)
                service = subprocess.run(
                    f"snap services {snapcraft['name']}.{app}".split(),
                    check=True,
                    capture_output=True,
                )
                subprocess.run(f"sudo snap stop {snapcraft['name']}.{app}".split())

                assert "active" in str(service.stdout)


@pytest.mark.run(after="test_all_services")
def test_remove():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)
    subprocess.run(f"sudo snap remove --purge {snapcraft['name']}".split())

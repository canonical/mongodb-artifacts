import base64
import os
import yaml
import subprocess
import time
import pytest


def test_install():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)

        version = snapcraft["parts"]["mongodb-compass"]["source-tag"][1:]

        subprocess.run(
            f"sudo snap install ./{snapcraft['name']}_{version}_amd64.snap --dangerous".split(),
            check=True,
        )


@pytest.mark.run(after="test_install")
def test_missing_password_manager_service():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)

        to_fail = subprocess.run(
            f"/snap/bin/{snapcraft['name']}", capture_output=True, text=True
        )

        assert to_fail.returncode == 127
        assert "password-manager-service not connected" in to_fail.stdout


@pytest.mark.run(after="test_missing_password_manager_service")
def test_with_password_manager_service():
    with open("snap/snapcraft.yaml") as file:
        snapcraft = yaml.safe_load(file)

        connect_if = subprocess.run(
            f"sudo snap connect {snapcraft['name']}:password-manager-service".split(),
            capture_output=True,
            text=True,
        )

        assert connect_if.returncode == 0

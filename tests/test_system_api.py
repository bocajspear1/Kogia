import shutil
import os
import time

import pytest
import backend.server
from fastapi.testclient import TestClient

SUBMISSION_DIR="./submissions-test"
BACKUP_DIR=SUBMISSION_DIR+"-backup"

@pytest.fixture()
def app():
    
    app = backend.server.create_app(config_path="./tests/test-config.json")

    if os.path.exists(SUBMISSION_DIR):
        shutil.rmtree(SUBMISSION_DIR)
        os.mkdir(SUBMISSION_DIR)

    yield app


@pytest.fixture()
def client(app):
    client = TestClient(app)
    client.submission_count = 0
    return client


def test_api_version(client):
    response = client.get("/api/v1/system/version")
    assert response.status_code == 200, response.text
    assert response.json()['version'] is not None, response.json()
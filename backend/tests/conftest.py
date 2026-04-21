import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


TEST_ROOT = Path(__file__).parent
os.environ["DATABASE_URL"] = f"sqlite:///{(TEST_ROOT / 'test.db').as_posix()}"
os.environ["PROOF_STORAGE_DIR"] = (TEST_ROOT / ".test_artifacts" / "proofs").as_posix()

from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def auth_headers(client: TestClient):
    response = client.post(
        "/api/v1/auth/dev-login",
        json={"device_id": "test-device", "nickname": "小林"},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

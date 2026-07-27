from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_xml_path(fixtures_dir: Path) -> Path:
    return fixtures_dir / "valid_feed.xml"


@pytest.fixture
def valid_xml_content(valid_xml_path: Path) -> bytes:
    return valid_xml_path.read_bytes()
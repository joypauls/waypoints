import pytest
from waypoints.storage import LocalStorage, _short_hash

PIPELINE = "test-pipeline"
RUN = "test-run"


@pytest.fixture()
def storage(tmp_path):
    return LocalStorage(base_dir=tmp_path / "wp")


def test_short_hash_length():
    assert len(_short_hash(b"hello")) == 6


def test_short_hash_deterministic():
    assert _short_hash(b"x") == _short_hash(b"x")


def test_short_hash_differs():
    assert _short_hash(b"a") != _short_hash(b"b")

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


def test_step_not_present_initially(storage):
    assert not storage.step_exists(PIPELINE, RUN, "s")


def test_save_and_exists(storage):
    storage.save_step(PIPELINE, RUN, "s", {"a": 1})
    assert storage.step_exists(PIPELINE, RUN, "s")


def test_save_returns_hash(storage):
    h = storage.save_step(PIPELINE, RUN, "s", 42)
    assert isinstance(h, str) and len(h) == 6


def test_load_roundtrip(storage):
    storage.save_step(PIPELINE, RUN, "s", {"key": "value"})
    value, h = storage.load_step(PIPELINE, RUN, "s")
    assert value == {"key": "value"}
    assert len(h) == 6


def test_load_missing_raises(storage):
    with pytest.raises(FileNotFoundError):
        storage.load_step(PIPELINE, RUN, "ghost")


def test_delete_removes_step(storage):
    storage.save_step(PIPELINE, RUN, "s", 99)
    storage.delete_step(PIPELINE, RUN, "s")
    assert not storage.step_exists(PIPELINE, RUN, "s")


def test_delete_nonexistent_is_silent(storage):
    # should not raise
    storage.delete_step(PIPELINE, RUN, "ghost")


@pytest.mark.parametrize("value", [42, 3.14, "hello", [1, 2], {"a": 1}, None])
def test_pickle_roundtrip(storage, value):
    storage.save_step(PIPELINE, RUN, "s", value)
    loaded, _ = storage.load_step(PIPELINE, RUN, "s")
    assert loaded == value

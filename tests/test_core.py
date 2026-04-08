import pytest
from waypoints._state import _state
from waypoints._cache import (
    init_run,
    # cache_write,
    # cache_read,
    # cache_exists,
    # cache_clear,
    # make_arg_key,
    # capture_env,
)


@pytest.fixture(autouse=True)
def reset(tmp_path):
    _state.reset()
    yield tmp_path
    _state.reset()


def start(tmp_path, pipeline="test-pipeline", run=None):
    init_run(pipeline, run=run, base_dir=str(tmp_path))


class TestInitRun:
    def test_creates_cache_dir(self, tmp_path):
        start(tmp_path)
        # print(_state.cache_dir)
        assert _state.cache_dir.exists()

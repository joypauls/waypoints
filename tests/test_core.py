import pytest
from waypoints._state import _state
from waypoints._cache import (
    init_run,
    cache_write,
    cache_read,
    cache_exists,
    cache_clear,
    make_arg_key,
    env_snapshot,
)
from waypoints._run import start as wp_start, tag, done


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


class TestStart:
    def test_prints_starting_on_first_run(self, tmp_path, capsys):
        wp_start("my-pipe", base_dir=str(tmp_path))
        out = capsys.readouterr().out
        assert "starting" in out
        assert "my-pipe" in out

    def test_prints_resuming_when_cache_exists(self, tmp_path, capsys):
        wp_start("my-pipe", base_dir=str(tmp_path))
        cache_write("step1", 42)
        _state.reset()
        wp_start("my-pipe", base_dir=str(tmp_path))
        out = capsys.readouterr().out
        assert "resuming" in out

    def test_writes_env_json(self, tmp_path):
        wp_start("my-pipe", base_dir=str(tmp_path))
        env_file = tmp_path / "my-pipe" / "env.json"
        assert env_file.exists()

    def test_env_json_contains_python_version(self, tmp_path):
        wp_start("my-pipe", base_dir=str(tmp_path))
        import json

        env = json.loads((tmp_path / "my-pipe" / "env.json").read_text())
        assert "python" in env

    def test_sets_start_time(self, tmp_path):
        wp_start("my-pipe", base_dir=str(tmp_path))
        assert _state.start_time is not None


class TestTag:
    def test_stores_tag(self, tmp_path):
        wp_start("my-pipe", base_dir=str(tmp_path))
        tag("accuracy", 0.91)
        assert _state.tags["accuracy"] == 0.91

    def test_multiple_tags(self, tmp_path):
        wp_start("my-pipe", base_dir=str(tmp_path))
        tag("accuracy", 0.91)
        tag("n_rows", 1200)
        assert len(_state.tags) == 2

    def test_requires_active_run(self):
        with pytest.raises(RuntimeError, match="wp.start"):
            tag("x", 1)


class TestDone:
    def test_writes_history_file(self, tmp_path):
        wp_start("my-pipe", base_dir=str(tmp_path))
        tag("accuracy", 0.91)
        done()
        history_files = list((tmp_path / "my-pipe" / "runs" / "my-pipe").glob("*.json"))
        assert len(history_files) == 1

    def test_history_contains_tags(self, tmp_path):
        import json

        wp_start("my-pipe", base_dir=str(tmp_path))
        tag("accuracy", 0.91)
        done()
        history_file = list((tmp_path / "my-pipe" / "runs" / "my-pipe").glob("*.json"))[
            0
        ]
        data = json.loads(history_file.read_text())
        assert data["tags"]["accuracy"] == 0.91

    def test_writes_tags_json(self, tmp_path):
        wp_start("my-pipe", base_dir=str(tmp_path))
        tag("x", 1)
        done()
        assert (tmp_path / "my-pipe" / "tags.json").exists()

    def test_requires_active_run(self):
        with pytest.raises(RuntimeError, match="wp.start"):
            done()

    def test_history_accumulates_across_sessions(self, tmp_path):
        import time

        wp_start("my-pipe", base_dir=str(tmp_path))
        tag("run", 1)
        done()
        time.sleep(1.1)
        wp_start("my-pipe", base_dir=str(tmp_path))
        tag("run", 2)
        done()
        history_files = list((tmp_path / "my-pipe" / "runs" / "my-pipe").glob("*.json"))
        assert len(history_files) == 2

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
        assert _state.cache_dir.exists()

    def test_creates_run_dir(self, tmp_path):
        start(tmp_path)
        assert _state.run_dir.exists()

    def test_run_defaults_to_pipeline_name(self, tmp_path):
        start(tmp_path, pipeline="my-pipeline")
        assert _state.run == "my-pipeline"

    def test_explicit_run_label(self, tmp_path):
        start(tmp_path, pipeline="my-pipeline", run="baseline")
        assert _state.run == "baseline"
        assert _state.pipeline == "my-pipeline"

    def test_different_runs_share_cache_dir(self, tmp_path):
        start(tmp_path, pipeline="shared", run="run-a")
        cache_a = _state.cache_dir
        _state.reset()
        start(tmp_path, pipeline="shared", run="run-b")
        cache_b = _state.cache_dir
        assert cache_a == cache_b

    def test_different_runs_have_separate_run_dirs(self, tmp_path):
        start(tmp_path, pipeline="shared", run="run-a")
        run_dir_a = _state.run_dir
        _state.reset()
        start(tmp_path, pipeline="shared", run="run-b")
        run_dir_b = _state.run_dir
        assert run_dir_a != run_dir_b

    def test_resets_tags_and_steps(self, tmp_path):
        start(tmp_path)
        _state.tags["x"] = 1
        _state.steps["y"] = {}
        start(tmp_path)
        assert _state.tags == {}
        assert _state.steps == {}


class TestCacheReadWrite:
    def test_write_and_read(self, tmp_path):
        start(tmp_path)
        cache_write("step1", [1, 2, 3])
        hit, value = cache_read("step1")
        assert hit is True
        assert value == [1, 2, 3]

    def test_read_miss(self, tmp_path):
        start(tmp_path)
        hit, value = cache_read("nonexistent")
        assert hit is False
        assert value is None

    def test_exists(self, tmp_path):
        start(tmp_path)
        assert cache_exists("step1") is False
        cache_write("step1", 42)
        assert cache_exists("step1") is True

    def test_survives_state_reset(self, tmp_path):
        start(tmp_path, pipeline="my-pipe")
        cache_write("load", {"data": 123})
        _state.reset()
        start(tmp_path, pipeline="my-pipe")
        hit, value = cache_read("load")
        assert hit is True
        assert value == {"data": 123}

    def test_write_returns_false_for_unpicklable(self, tmp_path):
        start(tmp_path)
        result = cache_write("bad", lambda x: x)
        assert result is False

    def test_unpicklable_does_not_create_file(self, tmp_path):
        start(tmp_path)
        cache_write("bad", lambda x: x)
        assert not cache_exists("bad")


class TestCacheClear:
    def test_clear_specific_step(self, tmp_path):
        start(tmp_path)
        cache_write("step1", 1)
        cache_write("step2", 2)
        cache_clear("step1")
        assert not cache_exists("step1")
        assert cache_exists("step2")

    def test_clear_all(self, tmp_path):
        start(tmp_path)
        cache_write("step1", 1)
        cache_write("step2", 2)
        count = cache_clear()
        assert count == 2
        assert not cache_exists("step1")
        assert not cache_exists("step2")

    def test_clear_nonexistent_returns_zero(self, tmp_path):
        start(tmp_path)
        count = cache_clear("ghost")
        assert count == 0

    def test_clear_hashed_variants(self, tmp_path):
        start(tmp_path)
        key = make_arg_key("train", (1,), {})
        cache_write(key, "model")
        cache_clear("train")
        assert not cache_exists(key)


class TestArgKey:
    def test_same_args_same_key(self, tmp_path):
        start(tmp_path)
        k1 = make_arg_key("fn", (1, 2), {"a": 3})
        k2 = make_arg_key("fn", (1, 2), {"a": 3})
        assert k1 == k2

    def test_different_args_different_key(self, tmp_path):
        start(tmp_path)
        k1 = make_arg_key("fn", (1,), {})
        k2 = make_arg_key("fn", (2,), {})
        assert k1 != k2

    def test_key_includes_function_name(self, tmp_path):
        start(tmp_path)
        k = make_arg_key("my_function", (), {})
        assert k.startswith("my_function_")


class TestEnvSnapshot:
    def test_returns_python_version(self):
        env = env_snapshot()
        assert "python" in env
        assert "platform" in env
        assert "timestamp" in env


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

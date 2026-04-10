import hashlib
import pickle
import platform
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from ._state import _state


def init_run(
    pipeline: str, run: Optional[str] = None, base_dir: str = ".waypoints"
) -> None:
    run_label = run or pipeline

    # don't want to reset everything
    _state.pipeline = pipeline
    _state.run = run_label
    _state.tags = {}
    _state.steps = {}

    pipeline_dir = Path(base_dir) / pipeline
    # cache directory (shared)
    _state.cache_dir = pipeline_dir / "cache"
    _state.cache_dir.mkdir(parents=True, exist_ok=True)
    # run directory (specific to this run)
    _state.run_dir = pipeline_dir / "runs" / run_label
    _state.run_dir.mkdir(parents=True, exist_ok=True)

    _state.start_time = datetime.now()


def cache_write(key: str, value: Any) -> bool:
    path = _state.cache_dir / f"{key}.pkl"
    try:
        path.write_bytes(pickle.dumps(value))
        return True
    except (pickle.PicklingError, TypeError):
        return False


def cache_read(key: str) -> tuple[bool, Any]:
    path = _state.cache_dir / f"{key}.pkl"
    if not path.exists():
        return False, None
    return True, pickle.loads(path.read_bytes())


def cache_exists(key: str) -> bool:
    return (_state.cache_dir / f"{key}.pkl").exists()


def cache_clear(key: Optional[str] = None) -> int:
    if key is None:
        files = list(_state.cache_dir.glob("*.pkl"))
        for f in files:
            f.unlink()
        return len(files)
    matches = list(_state.cache_dir.glob(f"{key}.pkl")) + list(
        _state.cache_dir.glob(f"{key}_*.pkl")
    )
    for f in matches:
        f.unlink()
    return len(matches)


def make_arg_key(fn_name: str, args: tuple, kwargs: dict) -> str:
    arg_hash = hashlib.md5(pickle.dumps((args, kwargs))).hexdigest()[:8]
    return f"{fn_name}_{arg_hash}"


def env_snapshot() -> dict:
    env = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "timestamp": datetime.now().isoformat(),
    }
    # not critical but try to grab commit hash
    try:
        commit = (
            subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
        env["git_commit"] = commit
    except Exception:
        pass

    return env

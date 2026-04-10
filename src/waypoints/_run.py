import json

# from datetime import datetime
# from pathlib import Path

from ._state import _state
from ._cache import init_run, capture_env


def start(pipeline: str, run: str = None) -> None:
    init_run(pipeline, run=run)

    env = capture_env()
    env_file = _state.cache_dir.parent / "env.json"
    env_file.write_text(json.dumps(env, indent=2))

    cached = list(_state.cache_dir.glob("*.pkl"))
    if cached:
        print(f"waypoints: resuming '{pipeline}' ({len(cached)} step(s) cached)")
    else:
        print(f"waypoints: starting '{pipeline}'")

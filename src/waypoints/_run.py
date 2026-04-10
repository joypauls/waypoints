import json
from datetime import datetime
from pathlib import Path

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


def tag(key: str, value) -> None:
    if not _state.active:
        raise RuntimeError("No active run. Call wp.start() first.")
    _state.tags[key] = value


def _format_duration(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.1f}s"
    m, s = divmod(int(seconds), 60)
    return f"{m}m {s}s"


def done() -> None:
    if not _state.active:
        raise RuntimeError("No active run. Call wp.start() first.")

    elapsed = (
        (datetime.now() - _state.start_time).total_seconds() if _state.start_time else 0
    )

    summary = {
        "pipeline": _state.pipeline,
        "run": _state.run,
        "timestamp": datetime.now().isoformat(),
        "duration_seconds": round(elapsed, 2),
        "steps": _state.steps,
        "tags": _state.tags,
    }

    ts = datetime.now().strftime("%Y%m%dT%H%M%S")
    history_file = _state.run_dir / f"{ts}.json"
    history_file.write_text(json.dumps(summary, indent=2, default=str))

    if _state.tags:
        tags_file = _state.cache_dir.parent / "tags.json"
        tags_file.write_text(json.dumps(_state.tags, indent=2, default=str))

    cached = [k for k, v in _state.steps.items() if v.get("status") == "cached"]
    ran = [k for k, v in _state.steps.items() if v.get("status") == "completed"]

    print(f"\n✓  '{_state.run}' done in {_format_duration(elapsed)}")
    if ran:
        print(f"   Ran:    {', '.join(ran)}")
    if cached:
        print(f"   Cached: {', '.join(cached)}")
    if _state.tags:
        print("   Tags:")
        for k, v in _state.tags.items():
            print(f"     {k}: {v}")

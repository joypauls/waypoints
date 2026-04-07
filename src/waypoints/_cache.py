import hashlib
import importlib
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
    # run is optionally provided
    run_label = run or pipeline

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

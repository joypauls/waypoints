import hashlib
import pickle
from pathlib import Path
from typing import Any


def _short_hash(data: bytes, length: int = 6) -> str:
    return hashlib.sha256(data).hexdigest()[:length]


class LocalStorage:
    """
    Persist step results to a local directory.

    Layout:  .waypoints/<pipeline>/<run>/<step>.pkl
    """

    def __init__(self, base_dir: str | Path = ".waypoints") -> None:
        self.base_dir = Path(base_dir)

    def _step_path(self, pipeline: str, run_name: str, step_name: str) -> Path:
        return self.base_dir / pipeline / run_name / f"{step_name}.pkl"

    def step_exists(self, pipeline: str, run_name: str, step_name: str) -> bool:
        return self._step_path(pipeline, run_name, step_name).exists()

    def save_step(
        self, pipeline: str, run_name: str, step_name: str, value: Any
    ) -> str:
        """Pickle value and return a short content hash."""
        path = self._step_path(pipeline, run_name, step_name)
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
        path.write_bytes(raw)
        return _short_hash(raw)

    def load_step(
        self, pipeline: str, run_name: str, step_name: str
    ) -> tuple[Any, str]:
        """Return (value, short_hash). Raises FileNotFoundError if absent."""
        path = self._step_path(pipeline, run_name, step_name)
        raw = path.read_bytes()
        return pickle.loads(raw), _short_hash(raw)

    def delete_step(self, pipeline: str, run_name: str, step_name: str) -> None:
        path = self._step_path(pipeline, run_name, step_name)
        if path.exists():
            path.unlink()

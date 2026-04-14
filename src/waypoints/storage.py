import hashlib
import pickle
from pathlib import Path
from typing import Any


class LocalStorage:
    """
    Persist step results to a local directory.

    Layout:  .waypoints/<pipeline>/<run>/<step>.pkl
    """

    def __init__(self, base_dir: str | Path = ".waypoints") -> None:
        self.base_dir = Path(base_dir)

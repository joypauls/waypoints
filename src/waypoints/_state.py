from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from datetime import datetime


@dataclass
class RunState:
    pipeline: Optional[str] = None
    run: Optional[str] = None
    run_dir: Optional[Path] = None
    cache_dir: Optional[Path] = None
    tags: dict = field(default_factory=dict)
    steps: dict = field(default_factory=dict)
    start_time: Optional[datetime] = None

    def reset(self):
        self.pipeline = None
        self.run = None
        self.run_dir = None
        self.cache_dir = None
        self.tags = {}
        self.steps = {}
        self.start_time = None

    @property
    def active(self) -> bool:
        return self.run_dir is not None


# initialize shared state
_state = RunState()

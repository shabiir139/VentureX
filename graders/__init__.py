# ─── VentureX · Base Grader ─────────────────────────────────────────────────
"""Base class for task graders — all graders produce a score from 0.0 to 1.0."""
from __future__ import annotations
from abc import ABC, abstractmethod


class BaseGrader(ABC):
    """Base grader that scores simulation performance."""

    def __init__(self, task_name: str, description: str):
        self.task_name = task_name
        self.description = description

    @abstractmethod
    def grade(self, final_score: dict) -> dict:
        """
        Grade the simulation run.
        Args:
            final_score: dict from VentureXEnv.get_final_score()
        Returns:
            dict with keys: score (0.0-1.0), breakdown, feedback
        """
        ...

    def _clamp(self, value: float) -> float:
        """Clamp value to [0.0, 1.0]."""
        return max(0.0, min(1.0, round(value, 4)))

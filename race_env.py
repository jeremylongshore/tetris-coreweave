"""Shared, turn-based rules for The Race.

SPDX-License-Identifier: MIT

This adapter is original code. It imports the separately MIT-licensed
tetris-gymnasium environment; keep that package's license when redistributing it.
Tested against tetris-gymnasium 0.3.1's classic NumPy backend.
"""

from __future__ import annotations

from numbers import Integral
from typing import Any

import numpy as np

from tetris_gymnasium.envs.tetris import Tetris
from tetris_gymnasium.wrappers.grouped import GroupedActionsObservations


FEATURE_NAMES = [
    *[f"height_{i}" for i in range(10)],
    "max_height", "holes", "bumpiness", "lines_this_placement",
    "immediate_topout", "remaining_fraction",
]
FEATURE_DIM = len(FEATURE_NAMES)
ACTIONS = 40


def board_stats(board: np.ndarray) -> tuple[np.ndarray, int, int]:
    """Column heights, holes below an occupied cell, and adjacent-height gaps."""
    occupied = np.asarray(board) != 0
    heights = np.where(occupied.any(axis=0), occupied.shape[0] - occupied.argmax(axis=0), 0)
    holes = int((np.maximum.accumulate(occupied, axis=0) & ~occupied).sum())
    bumpiness = int(np.abs(np.diff(heights)).sum())
    return heights, holes, bumpiness


class RaceEnv:
    """One shared engine for the learner, human controls, and evaluation.

    Each action is ``4 * center_column + rotation``. Columns are 0..9 and
    rotations 0..3, using upstream rotation semantics. Both players can inspect
    the exact same after-placement board previews. Neither receives next pieces.
    A match ends at top-out or after ``cap`` placement decisions.
    """

    def __init__(self, seed: int = 1, cap: int = 50):
        if not isinstance(cap, Integral) or cap < 1:
            raise ValueError("cap must be a positive integer")
        self.cap = int(cap)
        self.base = Tetris(width=10, height=20, gravity=False, render_mode=None)
        self.env = GroupedActionsObservations(self.base)
        self.features = np.zeros((ACTIONS, FEATURE_DIM), dtype=np.float32)
        self.mask = np.zeros(ACTIONS, dtype=bool)
        self.reset(seed)

    def reset(self, seed: int) -> tuple[np.ndarray, np.ndarray]:
        # Upstream 0.3.1 ignores seed=0. Positive seeds are required here.
        if not isinstance(seed, Integral) or seed < 1:
            raise ValueError("Use a positive integer seed; upstream ignores seed=0")
        self.seed = int(seed)
        self.lines = 0
        self.points = 0
        self.pieces = 0
        self.done = False
        self.topout = False
        self.at_cap = False
        observation, info = self.env.reset(seed=self.seed)
        self._refresh(observation, info["action_mask"])
        return self.features.copy(), self.mask.copy()

    def _board(self) -> np.ndarray:
        # The public observation includes the active piece; base.board does not.
        return self.base.crop_padding(self.base.board).copy()

    def _refresh(self, candidates: np.ndarray, action_mask: np.ndarray) -> None:
        self.features = np.zeros((ACTIONS, FEATURE_DIM), dtype=np.float32)
        self.mask = np.asarray(action_mask, dtype=bool).copy()
        self.previews: list[list[list[int]] | None] = [None] * ACTIONS
        self.candidate_topout = [False] * ACTIONS
        self.candidate_lines = [0] * ACTIONS
        if self.done:
            self.mask[:] = False
            return
        settled = self._board()
        occupied_before = int(np.count_nonzero(settled))
        remaining = max(0, self.cap - self.pieces - 1) / self.cap
        for action in np.flatnonzero(self.mask):
            action = int(action)
            candidate = candidates[action]
            # Upstream encodes immediate top-out as an entirely zero PADDED
            # board. Ordinary empty boards retain nonzero boundary padding.
            topout = not bool(np.any(candidate))
            after = settled if topout else self.base.crop_padding(candidate)
            lines = 0 if topout else (occupied_before + 4 - int(np.count_nonzero(after))) // 10
            if not 0 <= lines <= 4:
                raise RuntimeError("Candidate occupancy is inconsistent with a tetromino placement")
            heights, holes, bumpiness = board_stats(after)
            self.features[action] = np.asarray([
                *(heights / 20.0), float(heights.max()) / 20.0,
                holes / 200.0, bumpiness / 180.0, lines / 4.0,
                float(topout), remaining,
            ], dtype=np.float32)
            self.previews[action] = after.astype(int).tolist()
            self.candidate_topout[action] = topout
            self.candidate_lines[action] = int(lines)

    def step(self, action: int) -> tuple[np.ndarray, np.ndarray, float, bool, dict[str, Any]]:
        if self.done:
            raise RuntimeError("This match has ended; call reset with a positive seed")
        if not isinstance(action, Integral) or not 0 <= action < ACTIONS or not self.mask[action]:
            raise ValueError("Choose an available placement (a true entry in the mask)")
        action = int(action)
        heights_before, holes_before, _ = board_stats(self._board())
        observation, _upstream_reward, terminated, truncated, raw_info = self.env.step(action)
        heights_after, holes_after, _ = board_stats(self._board())
        cleared = int(raw_info["lines_cleared"])
        self.lines += cleared
        self.points += 10 * cleared * cleared
        # Count placement decisions, including a final attempt that tops out.
        self.pieces += 1
        self.topout = bool(terminated)
        self.at_cap = self.pieces >= self.cap
        self.done = bool(terminated or truncated or self.at_cap)
        reward = (
            10.0 * cleared
            - 0.5 * (holes_after - holes_before)
            - 0.05 * (int(heights_after.sum()) - int(heights_before.sum()))
            - 5.0 * self.topout
        )
        info = {
            "lines_cleared": cleared,
            "lines": self.lines,
            "points": self.points,
            "pieces": self.pieces,
            "topout": self.topout,
            "cap_reached": self.at_cap,
            "done": self.done,
            "seed": self.seed,
            "reason": "topout" if self.topout else ("cap" if self.at_cap else ("truncated" if truncated else "playing")),
        }
        self._refresh(observation, raw_info["action_mask"])
        return self.features.copy(), self.mask.copy(), float(reward), self.done, info

    def frame(self) -> dict[str, Any]:
        """JSON-safe UI snapshot. Deliberately excludes queue, RNG, and hold."""
        return {
            "board": self._board().astype(int).tolist(),
            "piece": self.base.active_tetromino.matrix.astype(int).tolist() if not self.done else [],
            "previews": self.previews,
            "mask": self.mask.tolist(),
            "candidate_topout": self.candidate_topout,
            "candidate_lines": self.candidate_lines,
            "lines": self.lines,
            "points": self.points,
            "pieces": self.pieces,
            "cap": self.cap,
            "done": self.done,
            "topout": self.topout,
            "cap_reached": self.at_cap,
            "seed": self.seed,
        }

    def close(self) -> None:
        self.env.close()

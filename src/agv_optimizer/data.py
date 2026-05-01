from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd


DEPOT = "DEPOT"


@dataclass(frozen=True)
class Task:
    task_id: str
    coord: Tuple[int, int]
    service_time: int
    demand: int
    deadline: int


@dataclass(frozen=True)
class AGV:
    agv_id: str
    speed: int
    max_distance: int
    capacity: int


@dataclass
class ProblemData:
    tasks: Dict[str, Task]
    agvs: Dict[str, AGV]


def load_problem(task_path: str | Path, agv_path: str | Path) -> ProblemData:
    task_path = Path(task_path)
    agv_path = Path(agv_path)

    if not task_path.exists():
        raise FileNotFoundError(f"Task file not found: {task_path}")

    if not agv_path.exists():
        raise FileNotFoundError(f"AGV file not found: {agv_path}")

    task_df = pd.read_csv(task_path)
    agv_df = pd.read_csv(agv_path)

    required_task_cols = {"task_id", "x", "y", "service_time", "demand", "deadline"}
    required_agv_cols = {"agv_id", "speed_cells_per_sec", "max_distance", "capacity"}

    missing_task = required_task_cols - set(task_df.columns)
    missing_agv = required_agv_cols - set(agv_df.columns)

    if missing_task:
        raise ValueError(f"task.csv missing columns: {sorted(missing_task)}")

    if missing_agv:
        raise ValueError(f"agv.csv missing columns: {sorted(missing_agv)}")

    tasks = {
        str(row.task_id): Task(
            task_id=str(row.task_id),
            coord=(int(row.x), int(row.y)),
            service_time=int(row.service_time),
            demand=int(row.demand),
            deadline=int(row.deadline),
        )
        for _, row in task_df.iterrows()
    }

    agvs = {
        str(row.agv_id): AGV(
            agv_id=str(row.agv_id),
            speed=int(row.speed_cells_per_sec),
            max_distance=int(row.max_distance),
            capacity=int(row.capacity),
        )
        for _, row in agv_df.iterrows()
    }

    if not tasks:
        raise ValueError("No tasks loaded.")

    if not agvs:
        raise ValueError("No AGVs loaded.")

    return ProblemData(tasks=tasks, agvs=agvs)


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

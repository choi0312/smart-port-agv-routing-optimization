from __future__ import annotations

from pathlib import Path

import pandas as pd

from agv_optimizer.data import DEPOT
from agv_optimizer.solution import Solution, normalize_route


def solution_to_submission(solution: Solution) -> pd.DataFrame:
    rows = []

    for agv_id in sorted(solution.keys()):
        route = normalize_route(solution[agv_id])

        if route == [DEPOT, DEPOT]:
            continue

        output_route = [route[0]]

        for node in route[1:]:
            if node == DEPOT and output_route[-1] == DEPOT:
                continue
            output_route.append(node)

        rows.append(
            {
                "agv_id": agv_id,
                "route": ",".join(output_route),
            }
        )

    return pd.DataFrame(rows)


def save_submission(solution: Solution, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    df = solution_to_submission(solution)
    df.to_csv(path, index=False)

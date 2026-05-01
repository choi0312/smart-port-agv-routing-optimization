from __future__ import annotations

from agv_optimizer.data import DEPOT, ProblemData, manhattan
from agv_optimizer.solution import Solution, normalize_route


def compute_score(
    solution: Solution,
    problem: ProblemData,
    lambda_val: float = 2.0,
) -> float:
    total_travel = 0.0
    total_service = 0.0
    total_penalty = 0.0

    for agv_id, route in solution.items():
        agv = problem.agvs[agv_id]
        time_acc = 0.0
        prev = (0, 0)

        for node in normalize_route(route)[1:]:
            cur = (0, 0) if node == DEPOT else problem.tasks[node].coord
            distance = manhattan(prev, cur)
            travel_time = distance / agv.speed

            time_acc += travel_time
            total_travel += travel_time
            prev = cur

            if node != DEPOT:
                task = problem.tasks[node]
                time_acc += task.service_time
                total_service += task.service_time
                lateness = max(0.0, time_acc - task.deadline)
                total_penalty += lambda_val * lateness

    return total_travel + total_service + total_penalty

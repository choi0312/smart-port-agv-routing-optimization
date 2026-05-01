from __future__ import annotations

import random

from agv_optimizer.data import DEPOT, ProblemData, manhattan
from agv_optimizer.solution import Solution


def destroy_random(solution: Solution, problem: ProblemData, q: int = 10) -> list[str]:
    tasks = [node for route in solution.values() for node in route if node != DEPOT]
    return random.sample(tasks, min(q, len(tasks)))


def destroy_worst(solution: Solution, problem: ProblemData, q: int = 10) -> list[str]:
    scores = []

    for agv_id, route in solution.items():
        agv = problem.agvs[agv_id]
        time_acc = 0.0
        prev = (0, 0)

        for node in route[1:]:
            if node == DEPOT:
                prev = (0, 0)
                continue

            task = problem.tasks[node]
            distance = manhattan(prev, task.coord)
            time_acc += distance / agv.speed + task.service_time
            lateness = max(0.0, time_acc - task.deadline)
            scores.append((lateness, node))
            prev = task.coord

    return [node for _, node in sorted(scores, reverse=True)[:q]]


def destroy_shaw(
    solution: Solution,
    problem: ProblemData,
    q: int = 10,
    alpha: float = 1.0,
    beta: float = 0.5,
    gamma: float = 0.2,
) -> list[str]:
    all_tasks = [node for route in solution.values() for node in route if node != DEPOT]

    if not all_tasks:
        return []

    removed = [random.choice(all_tasks)]

    def relatedness(a: str, b: str) -> float:
        task_a = problem.tasks[a]
        task_b = problem.tasks[b]

        coord_distance = manhattan(task_a.coord, task_b.coord)
        deadline_distance = abs(task_a.deadline - task_b.deadline)
        demand_distance = abs(task_a.demand - task_b.demand)

        return alpha * coord_distance + beta * deadline_distance + gamma * demand_distance

    while len(removed) < min(q, len(all_tasks)):
        last = removed[-1]
        candidates = [node for node in all_tasks if node not in removed]

        if not candidates:
            break

        scored = sorted(
            [(node, relatedness(last, node)) for node in candidates],
            key=lambda x: x[1],
        )

        r = random.random()
        idx = int((r ** 2) * (len(scored) - 1))
        removed.append(scored[idx][0])

    return removed

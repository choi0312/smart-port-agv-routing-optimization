from __future__ import annotations

from agv_optimizer.data import DEPOT, ProblemData
from agv_optimizer.scoring import compute_score
from agv_optimizer.solution import Solution, clone_solution, per_tour_feasible


def insert_safe(solution: Solution, problem: ProblemData, removed: list[str]) -> Solution:
    solution = clone_solution(solution)

    for task_id in list(removed):
        inserted = False

        for agv_id in solution:
            route = solution[agv_id]

            for pos in range(1, len(route)):
                candidate_route = route[:pos] + [task_id] + route[pos:]

                if per_tour_feasible(candidate_route, agv_id, problem):
                    solution[agv_id] = candidate_route
                    inserted = True
                    break

            if inserted:
                break

        if not inserted:
            for agv_id in solution:
                candidate_route = solution[agv_id][:-1] + [DEPOT, task_id, DEPOT]

                if per_tour_feasible(candidate_route, agv_id, problem):
                    solution[agv_id] = candidate_route
                    inserted = True
                    break

        if not inserted:
            agv_id = list(solution.keys())[0]
            solution[agv_id] = solution[agv_id][:-1] + [task_id, DEPOT]

    return solution


def insert_regret(
    solution: Solution,
    problem: ProblemData,
    removed: list[str],
    k: int = 2,
    lambda_search: float = 1.0,
) -> Solution:
    solution = clone_solution(solution)
    removed = list(removed)

    while removed:
        best_task = None
        best_agv = None
        best_pos = None
        best_regret = -1.0

        for task_id in removed:
            options = []

            for agv_id in solution:
                route = solution[agv_id]

                for pos in range(1, len(route)):
                    candidate_route = route[:pos] + [task_id] + route[pos:]

                    if not per_tour_feasible(candidate_route, agv_id, problem):
                        continue

                    candidate = clone_solution(solution)
                    candidate[agv_id] = candidate_route
                    score = compute_score(candidate, problem, lambda_val=lambda_search)
                    options.append((score, agv_id, pos))

            if not options:
                continue

            options.sort(key=lambda x: x[0])
            best_score = options[0][0]

            regret = 0.0
            if len(options) >= k:
                for j in range(1, k):
                    regret += options[j][0] - best_score

            if regret > best_regret:
                best_regret = regret
                best_task = task_id
                best_agv = options[0][1]
                best_pos = options[0][2]

        if best_task is None:
            fallback_task = removed.pop(0)
            agv_id = list(solution.keys())[0]
            solution[agv_id] = solution[agv_id][:-1] + [fallback_task, DEPOT]
        else:
            solution[best_agv] = (
                solution[best_agv][:best_pos]
                + [best_task]
                + solution[best_agv][best_pos:]
            )
            removed.remove(best_task)

    return solution

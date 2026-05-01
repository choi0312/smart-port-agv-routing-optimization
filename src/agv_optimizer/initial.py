from __future__ import annotations

from agv_optimizer.data import DEPOT, ProblemData
from agv_optimizer.scoring import compute_score
from agv_optimizer.solution import clone_solution, empty_solution, per_tour_feasible


def build_initial_solution(problem: ProblemData, lambda_search: float = 1.0) -> dict:
    solution = empty_solution(problem)
    task_order = sorted(problem.tasks.keys(), key=lambda t: problem.tasks[t].deadline)

    for task_id in task_order:
        best_score = None
        best_solution = None

        for agv_id in solution:
            route = solution[agv_id]

            for pos in range(1, len(route)):
                candidate_route = route[:pos] + [task_id] + route[pos:]

                if not per_tour_feasible(candidate_route, agv_id, problem):
                    continue

                candidate = clone_solution(solution)
                candidate[agv_id] = candidate_route

                score = compute_score(candidate, problem, lambda_val=lambda_search)

                if best_score is None or score < best_score:
                    best_score = score
                    best_solution = candidate

        if best_solution is None:
            for agv_id in solution:
                candidate_route = solution[agv_id][:-1] + [DEPOT, task_id, DEPOT]

                if not per_tour_feasible(candidate_route, agv_id, problem):
                    continue

                candidate = clone_solution(solution)
                candidate[agv_id] = candidate_route
                score = compute_score(candidate, problem, lambda_val=lambda_search)

                if best_score is None or score < best_score:
                    best_score = score
                    best_solution = candidate

        if best_solution is None:
            agv_id = list(solution.keys())[0]
            candidate = clone_solution(solution)
            candidate[agv_id] = candidate[agv_id][:-1] + [task_id, DEPOT]
            best_solution = candidate

        solution = best_solution

    return solution

from __future__ import annotations

from agv_optimizer.data import DEPOT, ProblemData
from agv_optimizer.scoring import compute_score
from agv_optimizer.solution import Solution, clone_solution, per_tour_feasible


def local_2opt(
    solution: Solution,
    problem: ProblemData,
    lambda_search: float = 1.0,
) -> tuple[Solution, float]:
    best = clone_solution(solution)
    best_score = compute_score(best, problem, lambda_val=lambda_search)

    for agv_id, route in solution.items():
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route) - 1):
                if route[i] == DEPOT or route[j] == DEPOT:
                    continue

                candidate_route = route[:i] + list(reversed(route[i:j])) + route[j:]

                if not per_tour_feasible(candidate_route, agv_id, problem):
                    continue

                candidate = clone_solution(solution)
                candidate[agv_id] = candidate_route
                score = compute_score(candidate, problem, lambda_val=lambda_search)

                if score < best_score:
                    best = candidate
                    best_score = score

    return best, best_score


def relocate_one(
    solution: Solution,
    problem: ProblemData,
    lambda_search: float = 1.0,
) -> tuple[Solution, float]:
    best = clone_solution(solution)
    best_score = compute_score(best, problem, lambda_val=lambda_search)

    for source_agv in solution:
        for i, node in enumerate(solution[source_agv]):
            if node == DEPOT:
                continue

            removed_source_route = solution[source_agv][:i] + solution[source_agv][i + 1 :]

            for target_agv in solution:
                for pos in range(1, len(solution[target_agv])):
                    candidate = clone_solution(solution)
                    candidate[source_agv] = removed_source_route
                    candidate[target_agv] = (
                        candidate[target_agv][:pos]
                        + [node]
                        + candidate[target_agv][pos:]
                    )

                    if not per_tour_feasible(candidate[target_agv], target_agv, problem):
                        continue

                    if any(n != DEPOT for n in candidate[source_agv]):
                        if not per_tour_feasible(candidate[source_agv], source_agv, problem):
                            continue

                    score = compute_score(candidate, problem, lambda_val=lambda_search)

                    if score < best_score:
                        best = candidate
                        best_score = score

    return best, best_score


def swap_two(
    solution: Solution,
    problem: ProblemData,
    lambda_search: float = 1.0,
) -> tuple[Solution, float]:
    best = clone_solution(solution)
    best_score = compute_score(best, problem, lambda_val=lambda_search)
    agv_ids = list(solution.keys())

    for a in agv_ids:
        for b in agv_ids:
            for i in range(1, len(solution[a]) - 1):
                for j in range(1, len(solution[b]) - 1):
                    if solution[a][i] == DEPOT or solution[b][j] == DEPOT:
                        continue

                    candidate = clone_solution(solution)
                    candidate[a][i], candidate[b][j] = candidate[b][j], candidate[a][i]

                    if not per_tour_feasible(candidate[a], a, problem):
                        continue

                    if not per_tour_feasible(candidate[b], b, problem):
                        continue

                    score = compute_score(candidate, problem, lambda_val=lambda_search)

                    if score < best_score:
                        best = candidate
                        best_score = score

    return best, best_score


def cross_exchange(
    solution: Solution,
    problem: ProblemData,
    lambda_search: float = 1.0,
) -> tuple[Solution, float]:
    best = clone_solution(solution)
    best_score = compute_score(best, problem, lambda_val=lambda_search)
    agv_ids = list(solution.keys())

    for a_idx in range(len(agv_ids)):
        for b_idx in range(a_idx + 1, len(agv_ids)):
            a = agv_ids[a_idx]
            b = agv_ids[b_idx]
            route_a = solution[a]
            route_b = solution[b]

            for i in range(1, len(route_a) - 1):
                for j in range(1, len(route_b) - 1):
                    if route_a[i] == DEPOT or route_b[j] == DEPOT:
                        continue

                    candidate = clone_solution(solution)
                    candidate[a][i], candidate[b][j] = route_b[j], route_a[i]

                    if not per_tour_feasible(candidate[a], a, problem):
                        continue

                    if not per_tour_feasible(candidate[b], b, problem):
                        continue

                    score = compute_score(candidate, problem, lambda_val=lambda_search)

                    if score < best_score:
                        best = candidate
                        best_score = score

    return best, best_score


def apply_local_search(
    solution: Solution,
    problem: ProblemData,
    lambda_search: float = 1.0,
) -> tuple[Solution, float]:
    best = clone_solution(solution)
    best_score = compute_score(best, problem, lambda_val=lambda_search)
    improved = True

    while improved:
        improved = False

        for operator in [local_2opt, relocate_one, swap_two, cross_exchange]:
            candidate, score = operator(best, problem, lambda_search=lambda_search)

            if score < best_score:
                best = candidate
                best_score = score
                improved = True

    return best, best_score

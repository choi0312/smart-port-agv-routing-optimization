from __future__ import annotations

from typing import Dict, List

from agv_optimizer.data import DEPOT, ProblemData, manhattan


Route = List[str]
Solution = Dict[str, Route]


def clone_solution(solution: Solution) -> Solution:
    return {agv_id: list(route) for agv_id, route in solution.items()}


def normalize_route(route: Route) -> Route:
    clean = [node for node in route if node is not None]

    if not clean:
        return [DEPOT, DEPOT]

    if clean[0] != DEPOT:
        clean = [DEPOT] + clean

    if clean[-1] != DEPOT:
        clean = clean + [DEPOT]

    result = []
    for node in clean:
        if result and node == DEPOT and result[-1] == DEPOT:
            continue
        result.append(node)

    if len(result) == 1:
        result.append(DEPOT)

    return result


def normalize_solution(solution: Solution) -> Solution:
    return {agv_id: normalize_route(route) for agv_id, route in solution.items()}


def empty_solution(problem: ProblemData) -> Solution:
    return {agv_id: [DEPOT, DEPOT] for agv_id in sorted(problem.agvs.keys())}


def route_has_task(route: Route) -> bool:
    return any(node != DEPOT for node in route)


def all_assigned_tasks(solution: Solution) -> list[str]:
    return [node for route in solution.values() for node in route if node != DEPOT]


def per_tour_feasible(route: Route, agv_id: str, problem: ProblemData) -> bool:
    route = normalize_route(route)
    agv = problem.agvs[agv_id]

    prev = (0, 0)
    dist_tour = 0
    load = 0
    visited_task = False

    for node in route[1:]:
        cur = (0, 0) if node == DEPOT else problem.tasks[node].coord
        dist_tour += manhattan(prev, cur)
        prev = cur

        if node == DEPOT:
            if dist_tour > agv.max_distance:
                return False
            if load > agv.capacity:
                return False

            dist_tour = 0
            load = 0
        else:
            visited_task = True
            load += problem.tasks[node].demand

    if not visited_task:
        return False

    return True


def solution_feasible(solution: Solution, problem: ProblemData) -> bool:
    assigned = all_assigned_tasks(solution)

    if len(assigned) != len(set(assigned)):
        return False

    if set(assigned) != set(problem.tasks.keys()):
        return False

    for agv_id, route in solution.items():
        if not route_has_task(route):
            continue

        if not per_tour_feasible(route, agv_id, problem):
            return False

    return True

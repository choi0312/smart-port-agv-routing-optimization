from __future__ import annotations

import math
import random

import numpy as np
from tqdm import tqdm

from agv_optimizer.destroy import destroy_random, destroy_shaw, destroy_worst
from agv_optimizer.local_search import apply_local_search
from agv_optimizer.repair import insert_regret, insert_safe
from agv_optimizer.scoring import compute_score
from agv_optimizer.solution import Solution, clone_solution


def alns_optimize(
    initial_solution: Solution,
    problem,
    iterations: int = 3000,
    seed: int = 42,
    remove_count: int = 15,
    lambda_search: float = 1.0,
    lambda_score: float = 2.0,
    temperature_initial: float = 1000.0,
    temperature_min: float = 5.0,
    high_temp_threshold: float = 50.0,
    cooling_high: float = 0.9998,
    cooling_low: float = 0.9999,
    local_search_interval_high_temp: int = 20,
    verbose: bool = False,
) -> tuple[Solution, float]:
    random.seed(seed)
    np.random.seed(seed)

    current = clone_solution(initial_solution)
    current_score = compute_score(current, problem, lambda_val=lambda_search)

    best = clone_solution(current)
    best_score = current_score

    temperature = temperature_initial

    destroy_operators = [destroy_random, destroy_worst, destroy_shaw]
    repair_operators = [insert_safe, insert_regret]

    iterator = tqdm(range(iterations), disable=not verbose)

    for iteration in iterator:
        destroy = random.choice(destroy_operators)
        repair = random.choice(repair_operators)

        removed = destroy(current, problem, q=remove_count)
        removed_set = set(removed)

        candidate = clone_solution(current)

        for agv_id in candidate:
            new_route = [node for node in candidate[agv_id] if node not in removed_set]

            if not new_route or new_route[0] != "DEPOT":
                new_route = ["DEPOT"] + new_route

            if new_route[-1] != "DEPOT":
                new_route = new_route + ["DEPOT"]

            candidate[agv_id] = new_route

        if repair is insert_regret:
            candidate = repair(
                candidate,
                problem,
                removed,
                k=2,
                lambda_search=lambda_search,
            )
        else:
            candidate = repair(candidate, problem, removed)

        if temperature > high_temp_threshold:
            if iteration % local_search_interval_high_temp == 0:
                candidate, _ = apply_local_search(
                    candidate,
                    problem,
                    lambda_search=lambda_search,
                )
        else:
            candidate, _ = apply_local_search(
                candidate,
                problem,
                lambda_search=lambda_search,
            )

        candidate_score = compute_score(candidate, problem, lambda_val=lambda_search)

        accept = False
        if candidate_score < current_score:
            accept = True
        else:
            delta = current_score - candidate_score
            prob = math.exp(delta / (temperature + 1e-6))
            accept = random.random() < prob

        if accept:
            current = candidate
            current_score = candidate_score

            if candidate_score < best_score:
                best = clone_solution(candidate)
                best_score = candidate_score

        if temperature > high_temp_threshold:
            cooling = cooling_high
        else:
            cooling = cooling_low

        temperature = max(temperature * cooling, temperature_min)

    return best, compute_score(best, problem, lambda_val=lambda_score)

from __future__ import annotations

import json
import multiprocessing as mp
from pathlib import Path

import pandas as pd

from agv_optimizer.alns import alns_optimize
from agv_optimizer.config import load_config
from agv_optimizer.data import load_problem
from agv_optimizer.initial import build_initial_solution
from agv_optimizer.submission import save_submission


def run_single_seed(args):
    seed, config, problem = args

    initial_solution = build_initial_solution(
        problem,
        lambda_search=float(config["objective"].get("lambda_search", 1.0)),
    )

    best_solution, best_score = alns_optimize(
        initial_solution=initial_solution,
        problem=problem,
        iterations=int(config["alns"].get("iterations", 3000)),
        seed=int(seed),
        remove_count=int(config["alns"].get("remove_count", 15)),
        lambda_search=float(config["objective"].get("lambda_search", 1.0)),
        lambda_score=float(config["objective"].get("lambda_score", 2.0)),
        temperature_initial=float(config["alns"].get("temperature_initial", 1000.0)),
        temperature_min=float(config["alns"].get("temperature_min", 5.0)),
        high_temp_threshold=float(config["alns"].get("high_temp_threshold", 50.0)),
        cooling_high=float(config["alns"].get("cooling_high", 0.9998)),
        cooling_low=float(config["alns"].get("cooling_low", 0.9999)),
        local_search_interval_high_temp=int(
            config["alns"].get("local_search_interval_high_temp", 20)
        ),
        verbose=False,
    )

    return {
        "seed": int(seed),
        "score": float(best_score),
        "solution": best_solution,
    }


def run_pipeline(config_path: str | Path) -> dict:
    config = load_config(config_path)
    output_dir = Path(config["project"].get("output_dir", "outputs"))
    output_dir.mkdir(parents=True, exist_ok=True)

    problem = load_problem(
        task_path=config["data"]["task_path"],
        agv_path=config["data"]["agv_path"],
    )

    seeds = config["parallel"].get("seeds", [42])
    enabled_parallel = bool(config["parallel"].get("enabled", True))
    num_workers = int(config["parallel"].get("num_workers", 1))

    args = [(int(seed), config, problem) for seed in seeds]

    if enabled_parallel and num_workers > 1 and len(args) > 1:
        with mp.Pool(processes=min(num_workers, len(args))) as pool:
            results = pool.map(run_single_seed, args)
    else:
        results = [run_single_seed(arg) for arg in args]

    best = min(results, key=lambda row: row["score"])

    seed_rows = [
        {
            "seed": row["seed"],
            "score": row["score"],
        }
        for row in results
    ]

    pd.DataFrame(seed_rows).to_csv(output_dir / "seed_results.csv", index=False)

    submission_path = output_dir / config["submission"].get("filename", "submission.csv")
    save_submission(best["solution"], submission_path)

    summary = {
        "best_seed": int(best["seed"]),
        "best_score": float(best["score"]),
        "submission_path": str(submission_path),
        "n_tasks": len(problem.tasks),
        "n_agvs": len(problem.agvs),
        "seed_results": seed_rows,
    }

    with (output_dir / "run_summary.json").open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return summary

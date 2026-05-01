from agv_optimizer.data import AGV, ProblemData, Task
from agv_optimizer.scoring import compute_score


def test_score_non_negative():
    tasks = {
        "T1": Task("T1", (1, 0), 2, 1, 100),
    }
    agvs = {
        "A1": AGV("A1", speed=1, max_distance=10, capacity=2),
    }
    problem = ProblemData(tasks=tasks, agvs=agvs)
    solution = {"A1": ["DEPOT", "T1", "DEPOT"]}

    assert compute_score(solution, problem, lambda_val=2.0) >= 0


def test_lateness_penalty_increases_score():
    tasks = {
        "T1": Task("T1", (10, 0), 2, 1, 1),
    }
    agvs = {
        "A1": AGV("A1", speed=1, max_distance=30, capacity=2),
    }
    problem = ProblemData(tasks=tasks, agvs=agvs)
    solution = {"A1": ["DEPOT", "T1", "DEPOT"]}

    low_penalty = compute_score(solution, problem, lambda_val=0.0)
    high_penalty = compute_score(solution, problem, lambda_val=2.0)

    assert high_penalty > low_penalty

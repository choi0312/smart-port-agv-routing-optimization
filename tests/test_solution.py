from agv_optimizer.data import AGV, ProblemData, Task
from agv_optimizer.solution import per_tour_feasible, solution_feasible


def sample_problem():
    tasks = {
        "T1": Task("T1", (1, 0), 1, 1, 10),
        "T2": Task("T2", (2, 0), 1, 1, 10),
    }
    agvs = {
        "A1": AGV("A1", speed=1, max_distance=10, capacity=3),
    }
    return ProblemData(tasks=tasks, agvs=agvs)


def test_per_tour_feasible():
    problem = sample_problem()
    route = ["DEPOT", "T1", "T2", "DEPOT"]
    assert per_tour_feasible(route, "A1", problem)


def test_solution_feasible():
    problem = sample_problem()
    solution = {"A1": ["DEPOT", "T1", "T2", "DEPOT"]}
    assert solution_feasible(solution, problem)

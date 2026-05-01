from agv_optimizer.data import AGV, ProblemData, Task
from agv_optimizer.initial import build_initial_solution
from agv_optimizer.solution import all_assigned_tasks


def test_initial_assigns_all_tasks():
    tasks = {
        "T1": Task("T1", (1, 0), 1, 1, 10),
        "T2": Task("T2", (2, 0), 1, 1, 10),
        "T3": Task("T3", (3, 0), 1, 1, 10),
    }
    agvs = {
        "A1": AGV("A1", speed=1, max_distance=20, capacity=3),
    }
    problem = ProblemData(tasks=tasks, agvs=agvs)

    solution = build_initial_solution(problem)
    assigned = all_assigned_tasks(solution)

    assert set(assigned) == set(tasks.keys())

import json
import time
import random
from constraint import Problem, AllDifferentConstraint
from collections import defaultdict

with open("data/employees.json") as f:
    employees_all = json.load(f)

with open("data/uneven_shifts.json") as f:
    shifts = json.load(f)


def get_subset(employees, n):
    return dict(list(employees.items())[:n])


skills_list = ["Barista","Cashier","Cook","Cleaner","Supervisor"]
days = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]


def generate_employee(i):
    return {
        "max_hours": random.choice([16,20,24,28,32,36]),
        "availability": random.sample(days, k=random.randint(3,7)),
        "skills": random.sample(skills_list, k=random.randint(1,3))
    }


def generate_employees(n):
    return {f"Emp{i}": generate_employee(i) for i in range(n)}


def group_by_day(shifts):
    days = defaultdict(list)
    for s in shifts:
        days[s["day"]].append(s)
    return days


def degree(var, shifts):
    day, shift_name, _, _ = var.split("_")
    return sum(
        1 for s in shifts
        if s["day"] == day and s["shift"] == shift_name
    )

def build_problem(employees, shifts):
    problem = Problem()
    variables = []
    domains = {}
    var_durations = {}

    for shift in shifts:
        day = shift["day"]
        shift_name = shift["shift"]
        duration = shift["duration"]

        for i, role in enumerate(shift["roles"]):
            var = f"{day}_{shift_name}_{role}_{i}"

            domain = [
                e for e in employees
                if role in employees[e]["skills"]
                and day in employees[e]["availability"]
                and employees[e]["max_hours"] >= duration
            ]

            if not domain:
                return None

            variables.append(var)
            domains[var] = sorted(domain)
            var_durations[var] = duration  

    # MRV + Degree
    variables.sort(key=lambda v: (len(domains[v]), -degree(v, shifts)))

    for var in variables:
        problem.addVariable(var, domains[var])

    # Local Constraint (All differents per shift)
    for shift in shifts:
        vars_shift = [
            f"{shift['day']}_{shift['shift']}_{role}_{i}"
            for i, role in enumerate(shift["roles"])
        ]
        problem.addConstraint(AllDifferentConstraint(), vars_shift)

    emp_vars = defaultdict(list)

    for var in variables:
        for emp in employees:
            emp_vars[emp].append(var)

    for emp, vars_list in emp_vars.items():
        max_hours = employees[emp]["max_hours"]

        def constraint_factory(emp, vars_list, var_durations, max_hours):
            def constraint(*vals):
                total = 0
                for var, assigned_emp in zip(vars_list, vals):
                    if assigned_emp == emp:
                        total += var_durations[var]
                return total <= max_hours
            return constraint

        problem.addConstraint(
            constraint_factory(emp, vars_list, var_durations, max_hours),
            vars_list
        )

    return problem

def display_solution(solution):
    if solution is None:
        print("No solution found")
        return

    print("Assigned employees:", set(solution.values()))

def run_experiment(employees, shifts, runs=3):
    day_groups = group_by_day(shifts)

    times = []
    final_solution = {}

    for _ in range(runs):
        start = time.time()

        solution_global = {}

        for day_shifts in day_groups.values():
            problem = build_problem(employees, day_shifts)

            if problem is None:
                return None, None

            solution = problem.getSolution()

            if solution:
                solution_global.update(solution)

        end = time.time()
        times.append(end - start)

        if solution_global:
            final_solution = solution_global

    avg_time = sum(times) / len(times)
    return avg_time, final_solution


# -------------------------
# MAIN
# -------------------------
def run_all():
    configs = [
        ("5 employees", get_subset(employees_all, 5)),
        ("10 employees", get_subset(employees_all, 10)),
        ("50 employees", generate_employees(50)),
    ]

    for label, emp_set in configs:
        avg_time, solution = run_experiment(emp_set, shifts)

        print("\n==============================")
        print(label)
        print(f"Average time: {avg_time:.4f} seconds")
        display_solution(solution)


run_all()
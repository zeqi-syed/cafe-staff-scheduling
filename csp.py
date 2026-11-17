import json
import time
import random
from constraint import Problem, AllDifferentConstraint
from collections import defaultdict

with open("data/employees.json") as f:
    employees_all = json.load(f)

with open("data/shifts.json") as f:
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

# DEGREE HEURISTIC
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

    for shift in shifts:
        day = shift["day"]
        shift_name = shift["shift"]

        for i, role in enumerate(shift["roles"]):
            var = f"{day}_{shift_name}_{role}_{i}"

            domain = [
                e for e in employees
                if role in employees[e]["skills"]
                and day in employees[e]["availability"]
                and employees[e]["max_hours"] >= 4
            ]

            if not domain:
                return None

            variables.append(var)
            domains[var] = sorted(domain)

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

    # Max hours
    emp_vars = defaultdict(list)
    for var in variables:
        for emp in employees:
            emp_vars[emp].append(var)

    for emp, vars_list in emp_vars.items():
        max_shifts = employees[emp]["max_hours"] // 4

        def constraint_factory(emp, max_shifts):
            return lambda *vals: vals.count(emp) <= max_shifts

        problem.addConstraint(constraint_factory(emp, max_shifts), vars_list)

    return problem

def display_solution(solution):
    if solution is None:
        print("No solution found")
        return

    assigned_employees = sorted(set(solution.values()))

    print("Assigned employees:")
    print(assigned_employees)

def run_experiment(employees, shifts, label="", runs=3):
    day_groups = group_by_day(shifts)

    total_times = []
    final_solution = {}

    for i in range(runs):
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
        total_times.append(end - start)

        if solution_global:
            final_solution = solution_global

    avg_time = sum(total_times) / len(total_times)

    return avg_time, final_solution


# MAIN OUTPUT
def run_all():
    configs = [
        ("5 employees", get_subset(employees_all, 5)),
        ("10 employees", get_subset(employees_all, 10)),
        ("50 employees", generate_employees(50)),
    ]

    for label, emp_set in configs:
        avg_time, solution = run_experiment(emp_set, shifts, label)

        print("\n==============================")
        print(label)
        print(f"Average time: {avg_time:.4f} seconds")
        display_solution(solution)

run_all()
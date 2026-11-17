import heapq
import time
import random

WEEKDAYS   = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
WEEKEND    = ['Sat', 'Sun']
ALL_DAYS   = WEEKDAYS + WEEKEND
ALL_SKILLS = ['Barista', 'Cashier', 'Cook', 'Cleaner', 'Supervisor']

DAY_NAMES  = {
    'Mon': 'Monday', 'Tue': 'Tuesday', 'Wed': 'Wednesday',
    'Thu': 'Thursday', 'Fri': 'Friday', 'Sat': 'Saturday', 'Sun': 'Sunday'
}

TIME_LIMIT_SECONDS = 300
global_start = time.time()

EMPLOYEES_BASE = [
    {'name': 'Aleksandra', 'max_hours': 28, 'availability': ['Mon','Tue','Thu','Fri','Sat','Sun'], 'skills': ['Barista','Cashier','Supervisor']},
    {'name': 'Emilio',     'max_hours': 36, 'availability': ['Mon','Wed','Thu','Fri','Sun'],       'skills': ['Barista','Cook','Cleaner']},
    {'name': 'Leila',      'max_hours': 24, 'availability': ['Sat','Sun'],                         'skills': ['Barista','Cashier','Cleaner']},
    {'name': 'Hancheng',   'max_hours': 36, 'availability': ['Tue','Wed','Thu','Sat','Sun'],       'skills': ['Cashier','Cook','Supervisor']},
    {'name': 'Syed',       'max_hours': 28, 'availability': ['Mon','Tue','Wed','Fri','Sat','Sun'], 'skills': ['Barista','Cashier','Cleaner']},
    {'name': 'Zijian',     'max_hours': 16, 'availability': ['Mon','Tue','Wed','Fri','Sat','Sun'], 'skills': ['Cook','Cleaner']},
    {'name': 'Lena',       'max_hours': 20, 'availability': ['Wed','Thu','Fri','Sat','Sun'],       'skills': ['Barista','Supervisor']},
    {'name': 'Marco',      'max_hours': 28, 'availability': ['Tue','Thu','Fri','Sat'],             'skills': ['Cook','Cashier','Cleaner']},
    {'name': 'Clara',      'max_hours': 16, 'availability': ['Sat','Sun'],                         'skills': ['Cook','Cleaner']},
    {'name': 'Laura',      'max_hours': 32, 'availability': ['Sat','Sun'],                         'skills': ['Barista','Cashier','Cleaner']},
]

STD_WEEKDAY = [('Morning', 4, ['Barista', 'Cashier', 'Cleaner']),
               ('Afternoon', 4, ['Barista', 'Cook', 'Supervisor'])]
STD_WEEKEND = [('Morning', 4, ['Barista', 'Cashier', 'Supervisor']),
               ('Afternoon', 4, ['Barista', 'Barista', 'Cook', 'Cleaner']),
               ('Evening',   4, ['Cashier', 'Cook', 'Supervisor'])]

UNEVEN_WEEKDAY = [('Morning', 3, ['Barista', 'Cashier', 'Cleaner']),
                  ('Afternoon', 5, ['Barista', 'Cook', 'Supervisor'])]
UNEVEN_WEEKEND = [('Morning', 4, ['Barista', 'Cashier', 'Supervisor']),
                  ('Afternoon', 3, ['Barista', 'Barista', 'Cook', 'Cleaner']),
                  ('Evening',   5, ['Cashier', 'Cook', 'Supervisor'])]

def build_slots(days_to_include, weekday_cfg, weekend_cfg):
    slots = []
    for day in days_to_include:
        shifts = weekend_cfg if day in WEEKEND else weekday_cfg
        for shift_name, hours, roles in shifts:
            for role in roles:
                slots.append({'day': day, 'shift': shift_name, 'role': role, 'hours': hours})
    return slots

def generate_extra_employees(total_needed):
    current_list = list(EMPLOYEES_BASE)
    if total_needed <= len(current_list):
        return current_list[:total_needed]
    for i in range(len(current_list) + 1, total_needed + 1):
        emp = {
            'name': f'Employee_{i}',
            'max_hours': random.choice([16, 20, 24, 28, 32, 36]),
            'availability': random.sample(ALL_DAYS, random.randint(4, 7)),
            'skills': random.sample(ALL_SKILLS, random.randint(1, 3))
        }
        current_list.append(emp)
    return current_list

def heuristic(remaining_slots, employees, hours_used):
    unassigned_slots = len(remaining_slots)

    if unassigned_slots == 0:
        return 0
    
    for slot in remaining_slots:
        day   = slot['day']
        role  = slot['role']
        hours = slot['hours']

        eligible_count = 0
        for emp in employees:
            name = emp['name']

            if role not in emp['skills']: continue
            if day not in emp['availability']: continue
            if hours_used[name] + hours > emp['max_hours']: continue
            
            eligible_count += 1

        if eligible_count == 0:
            return float('inf') 

    return unassigned_slots

def solve_astar(slots, employees, current_idx=0, schedule=None, hours_used=None):
    if schedule is None: schedule = []
    if hours_used is None: hours_used = {e['name']: 0 for e in employees}

    emp_names = [e['name'] for e in employees]
    init_hours = tuple(hours_used[n] for n in emp_names)

    counter = 0
    heap = [(0, 0, 0, schedule, init_hours)]

    while heap:
        if time.time() - global_start >= TIME_LIMIT_SECONDS:
            return "TIMEOUT"

        f, _, g, partial, hours_tuple = heapq.heappop(heap)

        if g == len(slots):
            return partial

        slot = slots[g]
        hours_dict = dict(zip(emp_names, hours_tuple))
        current_shift_workers = {
            n for s, n in partial 
            if s['day'] == slot['day'] and s['shift'] == slot['shift']
        }

        sorted_employees = sorted(
            employees,
            key=lambda e: e['max_hours'] - hours_dict[e['name']],
            reverse=True
        )

        for emp in sorted_employees:
            name = emp['name']

            if slot['role'] not in emp['skills']: continue
            if slot['day'] not in emp['availability']: continue
            if hours_dict[name] + slot['hours'] > emp['max_hours']: continue
            if name in current_shift_workers: continue

            idx = emp_names.index(name)
            new_hours_tuple = (
                hours_tuple[:idx]
                + (hours_tuple[idx] + slot['hours'],)
                + hours_tuple[idx+1:]
            )

            new_g = g + 1
            remaining = slots[new_g:]
            new_h = heuristic(remaining, employees, dict(zip(emp_names, new_hours_tuple)))

            if new_h == float('inf'):
                continue 

            new_f = new_g + new_h
            counter += 1
   
            heapq.heappush(heap, (new_f, -counter, new_g, partial + [(slot, name)], new_hours_tuple))

    return None

def print_day_table(day, result):
    shifts_dict = {}
    for slot, emp_name in result:
        key = (slot['shift'], slot['hours'])
        if key not in shifts_dict:
            shifts_dict[key] = []
        shifts_dict[key].append((slot['role'], emp_name))

    col_role = 14
    col_emp  = 16
    print(f"\n  {DAY_NAMES[day]}")
    print(f"  {'─'*52}")
    print(f"  {'Shift':<16} {'Role':<{col_role}} {'Assigned To':<{col_emp}}")
    print(f"  {'─'*52}")
    for (shift_name, hours), assignments in shifts_dict.items():
        shift_label = f"{shift_name} ({hours}h)"
        for i, (role, emp_name) in enumerate(assignments):
            label = shift_label if i == 0 else ""
            print(f"  {label:<16} {role:<{col_role}} {emp_name:<{col_emp}}")
        print(f"  {'·'*52}")

def run_benchmark(label, weekday_cfg, weekend_cfg):
    print(f"  {label}")
    

    for count in [5, 10, 50]:
        global global_start
        global_start = time.time()
        test_emps = generate_extra_employees(count)

        print(f"\n  >> {count} Employees <<")

        week_slots = build_slots(ALL_DAYS, weekday_cfg, weekend_cfg)

        result = solve_astar(week_slots, test_emps)

        elapsed = time.time() - global_start

        if result == "TIMEOUT":
            print(f"\n  Result: TIMEOUT | Time: {elapsed:.2f}s")
        elif result is None:
            print(f"\n  Result: NO SOLUTION | Time: {elapsed:.2f}s")
        else:
            for day in ALL_DAYS:
                day_result = [(slot, emp_name) for slot, emp_name in result if slot['day'] == day]
                if day_result:
                    print_day_table(day, day_result)
            print(f"\n  Result: FOUND | Time: {elapsed:.2f}s")

        print(f"\n{'─'*56}")

if __name__ == "__main__":
    print(" A* EMPLOYEE SCHEDULING (Full Week Execution)")
    print(f" Time limit per run: {TIME_LIMIT_SECONDS // 60} minutes")

    run_benchmark("Standard Configuration", STD_WEEKDAY, STD_WEEKEND)
    run_benchmark("Harder Q1: Uneven Slots", UNEVEN_WEEKDAY, UNEVEN_WEEKEND)
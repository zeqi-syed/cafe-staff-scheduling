# Café Staff Scheduling with AI Search

Building a weekly staff schedule for a small café: 10 employees, each with their own skills, available days and maximum weekly hours. The week has 50 roles to fill. The problem is solved with four AI techniques, which are then compared.

This was a team project for an AI course at Université Toulouse Capitole.

## The problem
- **Roles:** Barista, Cashier, Cook, Cleaner, Supervisor
- **Shifts:** 2 per weekday and 3 per weekend day, 50 roles in total
- **Rules:** an employee needs the right skill, must be available that day, cannot go over their weekly hours, and cannot hold two roles in the same shift
- **Harder version:** shifts of uneven length (3, 4 or 5 hours) instead of a fixed 4 hours
- Each solver is tested with 5, 10 and 50 employees (extra employees are generated at random)

## Algorithms
| File | Method |
|---|---|
| `bfs.py` | Breadth-First Search: explores every partial schedule level by level (FIFO queue, 5-minute time limit) |
| `dfs.ipynb` | Depth-First Search with backtracking |
| `csp.py` | Constraint Satisfaction Problem (python-constraint): AllDifferent per shift, max-hours constraint, MRV and degree heuristics, solved day by day |
| `csp_uneven_shifts.py` | CSP for the uneven shift-length version |
| `astar.py` | A* search with an MRV-style heuristic: a branch is dropped as soon as any remaining role has no eligible employee; employees with the most hours left are tried first |

## Main takeaways
- BFS only works on very small instances. It runs out of time or memory as soon as the problem grows.
- DFS is fast on standard shifts but slows down a lot with uneven shift lengths.
- CSP and A* scale best, because their heuristics spot dead ends early.
- With 5 employees there is no valid schedule: their total weekly hours are lower than the 200 hours needed.

## Run it
```bash
pip install -r requirements.txt
python astar.py
python bfs.py                  # can take several minutes: it stops at a 5-minute limit per run
python csp.py
python csp_uneven_shifts.py
jupyter notebook dfs.ipynb
```

The employee and shift data is in `data/`.

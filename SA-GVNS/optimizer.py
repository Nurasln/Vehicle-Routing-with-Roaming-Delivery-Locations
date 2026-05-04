import math
import random
import json
import time


# ──────────────────────────────────────────────────────────────────────
# Koordinatlar km, zaman pencereleri saat cinsinden.
# travel_time = distance / SPEED
# ──────────────────────────────────────────────────────────────────────
SPEED = 60.0   # km/h


# ══════════════════════════════════════════════
#  DATA CLASSES
# ══════════════════════════════════════════════

class Location:
    def __init__(self, loc_id, x, y, tw_start, tw_end):
        self.id       = loc_id
        self.x        = x
        self.y        = y
        self.tw_start = tw_start
        self.tw_end   = tw_end


class Customer:
    def __init__(self, cust_id, demand, locations):
        self.id        = cust_id
        self.demand    = demand
        self.locations = locations   # List[Location]


class Route:
    def __init__(self, capacity, depot):
        self.path           = [depot, depot]
        self.capacity       = capacity
        self.load           = 0.0
        self.total_distance = 0.0


# ══════════════════════════════════════════════
#  LOAD DATA
# ══════════════════════════════════════════════

def load_data(file_path, instance_key):
    with open(file_path) as f:
        data = json.load(f)

    inst = data["instances"][instance_key]

    d = inst["depot"]
    depot = Location(d["id"], d["x"], d["y"], d["tw_start"], d["tw_end"])

    customers = {}
    for c in inst["customers"]:
        locs = [Location(l["id"], l["x"], l["y"], l["tw_start"], l["tw_end"])
                for l in c["locations"]]
        customers[c["id"]] = Customer(c["id"], c["demand"], locs)

    return depot, customers, inst["vehicle_capacity"], inst["distance_matrix"]


# ══════════════════════════════════════════════
#  FEASIBILITY
# ══════════════════════════════════════════════

def _loc_to_customer(loc_id, customers):
    for cid, c in customers.items():
        if any(l.id == loc_id for l in c.locations):
            return cid
    return None


def is_feasible(path, capacity, customers, dist_matrix):
    """Returns (feasible, total_distance, total_load)."""
    current_time = 0.0
    current_load = 0.0
    total_dist   = 0.0

    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        dist          = dist_matrix[u.id][v.id]
        travel_time   = dist / SPEED
        total_dist   += dist
        current_time += travel_time

        if v.id == 0:
            continue

        cid = _loc_to_customer(v.id, customers)
        if cid is None:
            return False, 0.0, 0.0

        current_load += customers[cid].demand
        if current_load > capacity:
            return False, 0.0, 0.0

        if current_time > v.tw_end:
            return False, 0.0, 0.0
        if current_time < v.tw_start:
            current_time = v.tw_start

    return True, total_dist, current_load


# ══════════════════════════════════════════════
#  DEEP COPY
# ══════════════════════════════════════════════

def copy_solution(routes):
    copied = []
    for r in routes:
        nr = Route(r.capacity, r.path[0])
        nr.path           = list(r.path)
        nr.total_distance = r.total_distance
        nr.load           = r.load
        copied.append(nr)
    return copied


# ══════════════════════════════════════════════
#  INITIAL SOLUTION
# ══════════════════════════════════════════════

def get_initial_solution(depot, customers, capacity, dist_matrix):
    routes = []

    for cust in customers.values():
        placed = False

        for r in routes:
            best = None
            best_delta = float("inf")
            for loc in cust.locations:
                for pos in range(1, len(r.path)):
                    test = r.path[:pos] + [loc] + r.path[pos:]
                    ok, d, l = is_feasible(test, capacity, customers, dist_matrix)
                    if ok:
                        delta = d - r.total_distance
                        if delta < best_delta:
                            best_delta = delta
                            best = (test, d, l)
            if best:
                r.path, r.total_distance, r.load = best
                placed = True
                break

        if not placed:
            for loc in cust.locations:
                test = [depot, loc, depot]
                ok, d, l = is_feasible(test, capacity, customers, dist_matrix)
                if ok:
                    nr = Route(capacity, depot)
                    nr.path, nr.total_distance, nr.load = test, d, l
                    routes.append(nr)
                    placed = True
                    break

            if not placed:
                nr = Route(capacity, depot)
                loc = cust.locations[0]
                nr.path           = [depot, loc, depot]
                nr.total_distance = dist_matrix[0][loc.id] * 2
                nr.load           = cust.demand
                routes.append(nr)

    return routes


# ══════════════════════════════════════════════
#  OPERATORS
# ══════════════════════════════════════════════

def op_swap(route, customers, capacity, dist_matrix):
    if len(route.path) < 4:
        return
    path = list(route.path)
    i, j = random.sample(range(1, len(path) - 1), 2)
    path[i], path[j] = path[j], path[i]
    ok, d, l = is_feasible(path, capacity, customers, dist_matrix)
    if ok and d < route.total_distance:
        route.path, route.total_distance, route.load = path, d, l


def op_relocate(route, customers, capacity, dist_matrix):
    if len(route.path) <= 3:
        return
    path = list(route.path)
    ri   = random.randint(1, len(path) - 2)
    loc  = path.pop(ri)
    best_path, best_dist, best_load = None, float("inf"), 0.0
    for pos in range(1, len(path)):
        candidate = path[:pos] + [loc] + path[pos:]
        ok, d, l = is_feasible(candidate, capacity, customers, dist_matrix)
        if ok and d < best_dist:
            best_path, best_dist, best_load = candidate, d, l
    if best_path and best_dist < route.total_distance:
        route.path, route.total_distance, route.load = best_path, best_dist, best_load
    else:
        path.insert(ri, loc)
        route.path = path


def op_location_change(route, customers, capacity, dist_matrix):
    if len(route.path) <= 2:
        return
    path = list(route.path)
    idx  = random.randint(1, len(path) - 2)
    cur  = path[idx]
    cid  = _loc_to_customer(cur.id, customers)
    if cid is None:
        return
    alts = [l for l in customers[cid].locations if l.id != cur.id]
    if not alts:
        return
    path[idx] = random.choice(alts)
    ok, d, l = is_feasible(path, capacity, customers, dist_matrix)
    if ok and d < route.total_distance:
        route.path, route.total_distance, route.load = path, d, l


def vnd(solution, customers, capacity, dist_matrix, rounds=15):
    ops = [op_swap, op_relocate, op_location_change]
    for _ in range(rounds):
        improved = False
        for route in solution:
            before = route.total_distance
            for op in ops:
                op(route, customers, capacity, dist_matrix)
            if route.total_distance < before:
                improved = True
        if not improved:
            break


# ══════════════════════════════════════════════
#  SA-GVNS
# ══════════════════════════════════════════════

def solution_cost(sol):
    return sum(r.total_distance for r in sol)


def solve_sa_gvns(initial_solution, customers, capacity, dist_matrix,
                  T=1000.0, alpha=0.99, max_iter=2000):
    current   = copy_solution(initial_solution)
    best      = copy_solution(current)
    best_cost = solution_cost(best)

    convergence = []
    it = 0

    while T > 0.01 and it < max_iter:
        it += 1

        candidate = copy_solution(current)
        target    = random.choice(candidate)
        op        = random.choice([op_swap, op_relocate, op_location_change])
        op(target, customers, capacity, dist_matrix)

        vnd(candidate, customers, capacity, dist_matrix, rounds=10)

        cur_cost  = solution_cost(current)
        cand_cost = solution_cost(candidate)
        delta     = cand_cost - cur_cost

        if delta < 0:
            current = candidate
            if cand_cost < best_cost:
                best      = copy_solution(candidate)
                best_cost = cand_cost
        elif random.random() < math.exp(-delta / T):
            current = candidate

        T *= alpha

        if it % 100 == 0:
            convergence.append((it, best_cost))

    convergence.append((it, best_cost))
    return best, convergence


# ══════════════════════════════════════════════
#  MAIN
# ══════════════════════════════════════════════

if __name__ == "__main__":
    import os
    INSTANCE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instances.json")
    RUNS          = 5
    T_INIT        = 1000.0
    ALPHA         = 0.99

    all_instances = [
        "general_15",  "realistic_15",
        "general_30",  "realistic_30",
        "general_60",  "realistic_60",
        "general_120", "realistic_120",
    ]

    print(f"{'Instance':<22} {'Best':>8} {'Mean':>8} {'Std':>7} {'AvgTime':>9} {'Routes':>7}")
    print("─" * 70)

    for inst_key in all_instances:
        depot, customers, capacity, dist_matrix = load_data(INSTANCE_FILE, inst_key)

        run_costs = []
        run_times = []
        best_sol  = None
        best_cost = float("inf")

        for run in range(RUNS):
            t0           = time.time()
            init_sol     = get_initial_solution(depot, customers, capacity, dist_matrix)
            final_sol, _ = solve_sa_gvns(init_sol, customers, capacity, dist_matrix,
                                          T=T_INIT, alpha=ALPHA)
            elapsed      = time.time() - t0
            cost         = solution_cost(final_sol)
            run_costs.append(cost)
            run_times.append(elapsed)
            if cost < best_cost:
                best_cost = cost
                best_sol  = final_sol

        mean  = sum(run_costs) / RUNS
        std   = math.sqrt(sum((c - mean) ** 2 for c in run_costs) / RUNS)
        avg_t = sum(run_times) / RUNS

        print(f"{inst_key:<22} {best_cost:>8.2f} {mean:>8.2f} {std:>7.2f} {avg_t:>8.1f}s {len(best_sol):>6}")
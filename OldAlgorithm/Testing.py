import math
import random
import time
import pandas as pd
import matplotlib.pyplot as plt

# ---  CLASSs ---
class Location:
    def __init__(self, loc_id, x, y, tw_start, tw_end):
        self.id = loc_id
        self.x = x
        self.y = y
        self.tw_start = tw_start
        self.tw_end = tw_end

class Customer:
    def __init__(self, cust_id, demand):
        self.id = cust_id
        self.demand = demand
        self.locations = []

class Route:
    def __init__(self, capacity, depot):
        self.path = [depot, depot]
        self.capacity = capacity
        self.load = 0.0
        self.total_distance = 0.0

# ---  HESAPLAMA VE KONTROL ---
def calculate_distance(l1, l2):
    return math.sqrt((l1.x - l2.x)**2 + (l1.y - l2.y)**2)

def is_feasible(path, capacity, customers):
    if len(path) < 3: return True, 0.0, 0.0
    t, load, dist = 0.0, 0.0, 0.0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        d = calculate_distance(u, v)
        dist += d
        t += d
        if v.id != 0:
            c = next((cust for cust in customers if any(l.id == v.id for l in cust.locations)), None)
            if c:
                load += c.demand
                if load > capacity: return False, 0, 0
            if t > v.tw_end: return False, 0, 0
            if t < v.tw_start: t = v.tw_start
    return True, dist, load

# ---  VERİ  ---
def generator_a1(n_cust, horizon=14.0):
    depot = Location(0, 0, 0, 0, horizon)
    customers = []
    for i in range(1, n_cust + 1):
        c = Customer(i, random.randint(1, 3))
        for j in range(random.randint(1, 3)):
            x, y = random.uniform(-30, 30), random.uniform(-30, 30)
            d_depot = math.sqrt(x**2 + y**2)
            s = random.uniform(d_depot, horizon - 4)
            e = s + random.uniform(2, 4)
            c.locations.append(Location(i*100 + j, x, y, s, e))
        customers.append(c)
    return depot, customers

# --- ALGORİTMA ---
def get_initial_solution(depot, customers, cap):
    routes = []
    for cust in customers:
        found = False
        for r in routes:
            for loc in cust.locations:
                test_path = list(r.path)
                test_path.insert(-1, loc)
                f, d, l = is_feasible(test_path, cap, customers)
                if f:
                    r.path, r.total_distance, r.load = test_path, d, l
                    found = True; break
            if found: break
        if not found:
            new_r = Route(cap, depot)
            for loc in cust.locations:
                test_path = [depot, loc, depot]
                f, d, l = is_feasible(test_path, cap, customers)
                if f:
                    new_r.path, new_r.total_distance, new_r.load = test_path, d, l
                    routes.append(new_r); break
    return routes

def solve_baseline(depot, customers, cap, iters=1000):
    current_sol = get_initial_solution(depot, customers, cap)
    best_cost = sum(r.total_distance for r in current_sol)
    history = [best_cost]
    
    for _ in range(iters):
        temp_sol = [Route(cap, depot) for _ in current_sol]
        for i, r in enumerate(current_sol):
            temp_sol[i].path, temp_sol[i].total_distance = list(r.path), r.total_distance
        
        valid_r = [r for r in temp_sol if len(r.path) > 2]
        if not valid_r: continue
        
        sel_r = random.choice(valid_r)
        rem_loc = sel_r.path.pop(random.randint(1, len(sel_r.path) - 2))
        cust = next(c for c in customers if any(l.id == rem_loc.id for l in c.locations))
        
        b_inc, b_pos, b_r_idx, b_loc = float('inf'), None, None, None
        for ri, r in enumerate(temp_sol):
            for loc in cust.locations:
                for p in range(1, len(r.path)):
                    tp = list(r.path); tp.insert(p, loc)
                    f, d, _ = is_feasible(tp, cap, customers)
                    if f:
                        inc = d - r.total_distance
                        if inc < b_inc: b_inc, b_pos, b_r_idx, b_loc = inc, p, ri, loc
        
        if b_loc:
            temp_sol[b_r_idx].path.insert(b_pos, b_loc)
            _, d, l = is_feasible(temp_sol[b_r_idx].path, cap, customers)
            temp_sol[b_r_idx].total_distance, temp_sol[b_r_idx].load = d, l
            
            if sum(r.total_distance for r in temp_sol) < best_cost:
                current_sol = temp_sol
                best_cost = sum(r.total_distance for r in current_sol)
        
        history.append(best_cost)
    return best_cost, history

# --- TEST MERKEZİ ---
if __name__ == "__main__":
    scenarios = [15, 30, 60, 120]
    repeats = 5 # 5 tur bilimsel kanitlama icin
    final_table = []

    print("=== BASELINE TESTs ===")
    for n in scenarios:
        print(f"\Scenario: {n} Customer")
        costs, times = [], []
        best_run_log = []
        best_run_cost = float('inf')

        for i in range(repeats):
            start = time.time()
            depot, customers = generator_a1(n)
            cost, log = solve_baseline(depot, customers, 10)
            end = time.time()
            
            costs.append(cost)
            times.append(end - start)
            if cost < best_run_cost:
                best_run_cost, best_run_log = cost, log
            print(f"  Deneme {i+1}: {cost:.2f} km")

        final_table.append({
            "Customer": n,
            "Best": min(costs),
            "Avarage": sum(costs)/repeats,
            "Time": sum(times)/repeats
        })

        # Grafik 
        plt.figure(figsize=(6, 3))
        plt.plot(best_run_log)
        plt.title(f"Baseline - {n} Customer")
        plt.savefig(f"baseline_{n}.png")
        plt.close()

    df = pd.DataFrame(final_table)
    print("\n" + "="*40)
    print("RESULTS")
    print("="*40)
    print(df.to_string(index=False))
    df.to_csv("baseline_results.csv", index=False)
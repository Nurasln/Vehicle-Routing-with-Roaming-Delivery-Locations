import math
import random

class Location:
    def __init__(self, loc_id, x, y, tw_start, tw_end):
        self.id = loc_id
        self.x = x
        self.y = y
        self.tw_start = tw_start
        self.tw_end = tw_end

class Customer:
    def __init__(self, cust_id, demand, locations):
        self.id = cust_id
        self.demand = demand
        self.locations = locations # Location nesneleri listesi

class Route:
    def __init__(self, capacity, depot_loc):
        self.path = [depot_loc, depot_loc] # Rota depo ile başlar ve biter[cite: 8]
        self.capacity = capacity
        self.load = 0.0
        self.total_distance = 0.0

def is_feasible(path, capacity, customers_dict):
    """
    path: List of Location objects
    capacity: Maximum load of the vehicle (Q)
    customers_dict: Glossary for quick access to customer information.
    """
    current_time = 0.0
    current_load = 0.0
    total_dist = 0.0
    
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        dist = math.sqrt((u.x - v.x)**2 + (u.y - v.y)**2)
        total_dist += dist
        current_time += dist # Hız 1 birim kabul edildi[cite: 8]
        
        if v.id != 0: # Eğer hedef depo (0) değilse
            # Kapasite kontrolü
            cust_id = v.id // 100 # Örnek: 101 id'li lokasyon 1 nolu müşterinindir
            current_load += customers_dict[cust_id].demand
            if current_load > capacity:
                return False, 0, 0
            
            # Zaman Penceresi Kontrolü[cite: 8]
            if current_time > v.tw_end:
                return False, 0, 0 # Geç kaldık[cite: 8]
            if current_time < v.tw_start:
                current_time = v.tw_start # Erken geldik, bekliyoruz[cite: 8]
                
    return True, total_dist, current_load


def location_change_operator(route, customers_dict, capacity):
    """Changes the customer's location (Home/Work) without disrupting their queue.[cite: 8]."""
    if len(route.path) <= 2: return route
    
    new_path = list(route.path)
    # Rastgele bir müşteri lokasyonu seç
    idx = random.randint(1, len(new_path) - 2)
    current_loc = new_path[idx]
    cust_id = current_loc.id // 100
    
    # Müşterinin diğer lokasyonlarından birini seç
    new_loc = random.choice(customers_dict[cust_id].locations)
    new_path[idx] = new_loc
    
    feasible, dist, load = is_feasible(new_path, capacity, customers_dict)
    if feasible:
        route.path = new_path
        route.total_distance = dist
        route.load = load
    return route

def swap_operator(route, customers_dict, capacity):
    """Change the order of two customers on the route.[cite: 8]."""
    if len(route.path) < 4: return route
    
    new_path = list(route.path)
    i, j = random.sample(range(1, len(new_path) - 1), 2)
    new_path[i], new_path[j] = new_path[j], new_path[i]
    
    feasible, dist, load = is_feasible(new_path, capacity, customers_dict)
    if feasible:
        route.path = new_path
        route.total_distance = dist
        route.load = load
    return route


def solve_sa_gvns(initial_solution, customers_dict, capacity, T=1000.0, alpha=0.95):
    current_sol = initial_solution
    best_sol = initial_solution
    
    while T > 0.01:
        # Shaking ve VND aşaması[cite: 8]
        # Örnek: Mevcut rotalardan birini seç ve operatörleri uygula
        candidate_sol = [Route(capacity, r.path[0]) for r in current_sol] # Kopya oluştur
        # ... (Operatörleri candidate_sol üzerinde çalıştır)
        
        current_cost = sum(r.total_distance for r in current_sol)
        candidate_cost = sum(r.total_distance for r in candidate_sol)
        delta = candidate_cost - current_cost
        
        if delta < 0:
            current_sol = candidate_sol
            if candidate_cost < sum(r.total_distance for r in best_sol):
                best_sol = candidate_sol
        else:
            # SA Kabul Kriteri[cite: 8]
            if random.random() < math.exp(-delta / T):
                current_sol = candidate_sol
        
        T *= alpha # Soğuma[cite: 8]
    return best_sol



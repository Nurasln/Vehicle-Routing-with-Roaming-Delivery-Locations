import math
import random
import time
import json
import matplotlib.pyplot as plt
import numpy as np

#  CLASSs


class Location:
    """Delivery Locations."""

    def __init__(self, loc_id, x, y, tw_start, tw_end, type="home"):
        self.id = loc_id
        self.x = x
        self.y = y
        self.tw_start = tw_start
        self.tw_end = tw_end
        self.type = type


class Customer:
    """Profile of the customer and their mobile location."""

    def __init__(self, cust_id, demand):
        self.id = cust_id
        self.demand = demand
        self.locations = []  # List of Location objects


class Route:
    def __init__(self, vehicle_capacity, depot): 
        self.path = [depot, depot]  # Her rota depodan başlar ve biter
        self.capacity = vehicle_capacity
        self.load = 0.0
        self.total_distance = 0.0


# YARDIMCI FONKSİYONLAR

def calculate_distance(loc1, loc2):
    """Calculates the Euclidean distance between two locations."""
    return math.sqrt((loc1.x - loc2.x) ** 2 + (loc1.y - loc2.y) ** 2)


def is_feasible(path, vehicle_capacity, customers_data):
    if len(path) < 3:  # Sadece başlangıç ve bitiş deposu varsa
        return True, 0.0, 0.0

    current_time = 0.0
    current_load = 0.0
    total_dist = 0.0

    for i in range(len(path) - 1):
        u = path[i]
        v = path[i + 1]

        dist = calculate_distance(u, v)
        total_dist += dist
        current_time += dist

        if v.id != 0:
            # Kapasite Kontrolü
            customer = next(
                (c for c in customers_data if any(l.id == v.id for l in c.locations)),
                None,
            )
            if customer:
                current_load += customer.demand
                if current_load > vehicle_capacity:
                    return False, 0, 0

            # Zaman Kontrolü
            if current_time > v.tw_end:
                return False, 0, 0  # Müşteri evden çıkmışsa bu hamle iptal

            if current_time < v.tw_start:
                current_time = v.tw_start  # Erken geldiysek kapıda bekliyoruz

    return True, total_dist, current_load


# VERİ SETİ  


def generator_a1_general(n_customers, horizon=14.0):
    """Generates random scenarios"""
    depot = Location(0, 0, 0, 0, horizon, "depot")
    customers = []

    for i in range(1, n_customers + 1):
        c = Customer(i, random.randint(1, 3))
        for j in range(random.randint(1, 3)):
            x, y = random.uniform(-30, 30), random.uniform(-30, 30)
            dist_from_depot = math.sqrt(x**2 + y**2)

            # tw_start mesafeden daha büyük - yetişebilmek için
            start = random.uniform(dist_from_depot, horizon - 3)
            end = start + random.uniform(2, 4)
            c.locations.append(Location(i * 100 + j, x, y, start, end))
        customers.append(c)
    return depot, customers

    # OLD ALGORİTMA (DESTROY & RECREATE)


def initial_solution(depot, customers, capacity):
    routes = []
    for cust in customers:
        placed = False
        for r in routes:
            for loc in cust.locations:
                temp_path = list(r.path)
                temp_path.insert(-1, loc)
                feasible, dist, load = is_feasible(temp_path, capacity, customers)
                if feasible:
                    r.path = temp_path
                    r.total_distance = dist
                    r.load = load
                    placed = True
                    break
            if placed:
                break

        if not placed:
            new_r = Route(capacity, depot)
            for loc in cust.locations:
                temp_path = [depot, loc, depot]
                feasible, dist, load = is_feasible(temp_path, capacity, customers)
                if feasible:
                    new_r.path = temp_path
                    new_r.total_distance = dist
                    new_r.load = load
                    routes.append(new_r)
                    break
    return routes


def solve_baseline(depot, customers, vehicle_capacity, iterations=2000, L=3):
    """The article's original algorithm (Restricted Acceptance)."""
    current_routes = initial_solution(depot, customers, vehicle_capacity)
    best_routes = list(current_routes)

    history = []
    start_cpu = time.time()

    for i in range(iterations):
        # 1. DESTROY (YIKIM)
        # Bazı müşterileri rastgele rotalardan çıkar
        removed_customers = []
        new_routes = []
        for r in current_routes:
            temp_path = list(r.path)
            # Depolar hariç müşteri lokasyonlarını bul
            indices = [idx for idx, loc in enumerate(temp_path) if loc.id != 0]
            if indices and len(removed_customers) < L:
                target_idx = random.choice(indices)
                removed_loc = temp_path.pop(target_idx)
                # Lokasyondan müşteriyi bul
                cust = next(
                    c
                    for c in customers
                    if any(l.id == removed_loc.id for l in c.locations)
                )
                removed_customers.append(cust)

                # Rotayı güncelle
                feasible, dist, load = is_feasible(
                    temp_path, vehicle_capacity, customers
                )
                r.path = temp_path
                r.total_distance = dist
                r.load = load

        #  RECREATE 
        for cust in removed_customers:
            best_insertion = (
                None,
                None,
                float("inf"),
            ) 
            best_loc = None

            for r_idx, r in enumerate(current_routes):
                for loc in cust.locations:  # Müşterinin TÜM gezici noktalarını dene
                    for pos in range(1, len(r.path)):
                        temp_path = list(r.path)
                        temp_path.insert(pos, loc)
                        feasible, dist, load = is_feasible(
                            temp_path, vehicle_capacity, customers
                        )
                        if feasible:
                            cost_inc = dist - r.total_distance
                            if cost_inc < best_insertion[2]:
                                best_insertion = (r_idx, pos, cost_inc)
                                best_loc = loc

            if best_loc:
                r_idx, pos, _ = best_insertion
                current_routes[r_idx].path.insert(pos, best_loc)
                f, d, l = is_feasible(
                    current_routes[r_idx].path, vehicle_capacity, customers
                )
                current_routes[r_idx].total_distance = d
                current_routes[r_idx].load = l

        current_total_cost = sum(r.total_distance for r in current_routes)
        best_total_cost = sum(r.total_distance for r in best_routes)

        # KATI KABUL: Sadece iyiyse kabul et
        if current_total_cost < best_total_cost:
            best_routes = [Route(vehicle_capacity) for _ in current_routes]
            # Deep copy manual
            for idx, r in enumerate(current_routes):
                best_routes[idx].path = list(r.path)
                best_routes[idx].total_distance = r.total_distance
            best_total_cost = current_total_cost

        if i % 100 == 0:
            history.append(best_total_cost)
            print(f"Iteration {i}: Best Total Cost = {best_total_cost:.2f}")

    end_cpu = time.time()
    return best_routes, best_total_cost, end_cpu - start_cpu, history


# GÖRSELLEŞTİRME

if __name__ == "__main__":
    # Test parametreleri
    N_CUST = 30  # Farkli sonuclar icin degistiricez
    CAPACITY = 15

    print("--- Generates data set ---")
    depot, customers = generator_a1_general(N_CUST)

    print("--- Initializing the Original Algorithm (Baseline) ---")
    best_sol, best_cost, cpu_time, log = solve_baseline(depot, customers, CAPACITY)

    print(f"\n--- Results ---")
    print(f"Total Distance: {best_cost:.2f} km")
    print(f"Calculation Time: {cpu_time:.4f} second")

    # Yakınsama Grafiği
    plt.figure(figsize=(10, 5))
    plt.plot(range(0, 2000, 100), log, marker="o")
    plt.title("Original Algorithm Convergence Graph (Baseline)")
    plt.xlabel("Iteration (x100)")
    plt.ylabel("Total Distance (km)")
    plt.grid(True)
    plt.show()

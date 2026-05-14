from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import optimizer

app = FastAPI(title="SA-GVNS Optimizer API")

# Allow CORS for React frontend (which typically runs on port 3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INSTANCE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "instances.json")

@app.get("/api/instances")
def get_instances():
    """Returns a list of available instance keys from instances.json"""
    try:
        with open(INSTANCE_FILE) as f:
            data = json.load(f)
        return {"instances": list(data["instances"].keys())}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/run")
def run_optimizer(payload: dict):
    """
    Runs the SA-GVNS optimizer for a given instance key.
    Expects JSON payload: {"instance_key": "realistic_30"}
    """
    instance_key = payload.get("instance_key")
    if not instance_key:
        raise HTTPException(status_code=400, detail="instance_key is required")

    try:
        # Load the data
        depot, customers, capacity, dist_matrix = optimizer.load_data(INSTANCE_FILE, instance_key)
        
        # Build initial solution
        init_sol = optimizer.get_initial_solution(depot, customers, capacity, dist_matrix)
        init_cost = optimizer.solution_cost(init_sol)
        
        # Run SA-GVNS
        final_sol, convergence = optimizer.solve_sa_gvns(
            init_sol, customers, capacity, dist_matrix,
            T=1000.0, alpha=0.99, max_iter=2000
        )
        final_cost = optimizer.solution_cost(final_sol)
        
        # Format route data for the frontend
        # React RouteMap expects: { depot: {x,y}, routes: [{color, label, stops: [{x,y}...]}], customers: [{x,y,chosen, alt: {x,y}}] }
        
        routes_data = []
        # For simplicity in colors, we'll assign some hex codes
        colors = ["#818cf8", "#fbbf24", "#34d399", "#f472b6"]
        
        for i, r in enumerate(final_sol):
            stops = [{"x": loc.x, "y": loc.y} for loc in r.path]
            routes_data.append({
                "color": colors[i % len(colors)],
                "label": f"Route {i+1}",
                "stops": stops
            })
            
        # Format customers (all customers from the input, with chosen=true if they are in final_sol, alt={x,y})
        # This requires tracking which locations were chosen.
        chosen_loc_ids = set()
        for r in final_sol:
            for loc in r.path:
                chosen_loc_ids.add(loc.id)
                
        customers_data = []
        for cid, cust in customers.items():
            # Find which location was chosen
            chosen_loc = None
            alt_loc = None
            for loc in cust.locations:
                if loc.id in chosen_loc_ids:
                    chosen_loc = loc
                else:
                    alt_loc = loc
            
            if chosen_loc:
                customers_data.append({
                    "x": chosen_loc.x,
                    "y": chosen_loc.y,
                    "chosen": True,
                    "alt": {"x": alt_loc.x, "y": alt_loc.y} if alt_loc else None
                })
                
        # Send back detailed info
        return {
            "instance": instance_key,
            "initial_cost": round(init_cost, 2),
            "final_cost": round(final_cost, 2),
            "gap": round(((init_cost - final_cost) / init_cost) * 100, 2) if init_cost > 0 else 0,
            "convergence": convergence,  # list of [iter, cost]
            "route_data": {
                "depot": {"x": depot.x, "y": depot.y},
                "routes": routes_data,
                "customers": customers_data
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port)

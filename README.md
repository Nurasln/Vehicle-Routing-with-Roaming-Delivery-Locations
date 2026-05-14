# Vehicle Routing with Roaming Delivery Locations (VRRDL)

This project implements a Metaheuristic approach (SA-GVNS) to solve the Vehicle Routing Problem with Roaming Delivery Locations. It includes a Python-based optimization engine and a React-based interactive dashboard.

## Project Structure

- `backend/`: FastAPI application containing the SA-GVNS optimizer.
  - `api.py`: The FastAPI server.
  - `optimizer.py`: The core optimization logic.
  - `instances.json`: Benchmark instances for VRRDL.
- `frontend/`: React dashboard for results visualization.
  - `src/App.js`: Main dashboard implementation with "Live Run" feature.
- `Results/`: Static charts and results from baseline tests.
- `OldAlgorithm/`: Previous iterations of the algorithm.

## Getting Started

### 1. Backend Setup

Prerequisites: Python 3.8+

```bash
cd backend
pip install -r requirements.txt
python api.py
```
The API will be available at `http://localhost:8000`.

### 2. Frontend Setup

Prerequisites: Node.js 16+

```bash
cd frontend
npm install
npm start
```
The dashboard will open at `http://localhost:3000`.

## Features

- **SA-GVNS Algorithm**: Simulated Annealing integrated with General Variable Neighborhood Search.
- **Dynamic Operators**: Swap, Relocate, and Location Change (specific to VRRDL).
- **Interactive Dashboard**: Real-time convergence tracking and route visualization.
- **Live Run**: Execute the optimizer directly from the UI and see the results instantly.

## License

MIT License - see [LICENSE](LICENSE) for details.

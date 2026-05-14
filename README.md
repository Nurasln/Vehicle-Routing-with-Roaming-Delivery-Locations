# Vehicle Routing with Roaming Delivery Locations (VRRDL)

This project implements a Metaheuristic approach (SA-GVNS) to solve the Vehicle Routing Problem with Roaming Delivery Locations. It includes a Python-based optimization engine and a React-based interactive dashboard.

## 🚀 Live Demo

- **Dashboard (Frontend):** [https://vehicle-routing-with-roaming-delive-brown.vercel.app](https://vehicle-routing-with-roaming-delive-brown.vercel.app)
- **API Documentation (Backend):** [https://vehicle-routing-with-roaming-delivery.onrender.com/docs](https://vehicle-routing-with-roaming-delivery.onrender.com/docs)

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

## Deployment

### Backend (Render)
1. Deploy the `backend/` folder as a **Web Service**.
2. **Build Command:** `pip install -r requirements.txt`
3. **Start Command:** `uvicorn api:app --host 0.0.0.0 --port $PORT`

### Frontend (Vercel)
1. Deploy the `frontend/` folder.
2. Set Environment Variable: `REACT_APP_API_URL` = `https://vehicle-routing-with-roaming-delivery.onrender.com`

## License

MIT License - see [LICENSE](LICENSE) for details.

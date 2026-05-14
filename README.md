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

## Deployment Guide

### Backend (Render)
1. Sign up at [Render](https://render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub repository.
4. Set the following configurations:
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn api:app --host 0.0.0.0 --port $PORT`
5. Once deployed, copy your backend URL (e.g., `https://your-app.onrender.com`).

### Frontend (Vercel)
1. Connect your GitHub repository to [Vercel](https://vercel.com/).
2. Create a new project and set the **Root Directory** to `frontend`.
3. In the **Environment Variables** section, add:
   - `REACT_APP_API_URL`: Your Railway backend URL (from the previous step).
4. Click **Deploy**.

## License

MIT License - see [LICENSE](LICENSE) for details.

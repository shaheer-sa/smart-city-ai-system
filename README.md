# Neural Traffic Command | Smart City AI System

An AI-powered traffic management and emergency response system that utilizes Neural Networks, Constraint Satisfaction Problems (CSP), and advanced Graph Search algorithms (A*, UCS, BFS) to optimize city-wide transit.

## Core Features
- **ANN Priority Assessment**: Multi-layer perceptron for real-time request classification. The model uses a deterministic, manually weighted architecture without relying on external training datasets, ensuring fully explainable output behavior. Features are mapped from strict deterministic inputs (like request category and severity).
- **Expert System Knowledge Base**: Rule-based policy engine for emergency authorizations based on time sensitivity and vehicle class.
- **CSP Signal Scheduler**: Backtracking-based conflict-free signal phase allocation, precisely calibrated to the specific intersections in the city topology graph.
- **Neural Mapping & Navigation**: Interactive city graph with optimal pathfinding, accurately mapped to visual coordinates.

## Tech Stack
- **Backend**: Python, Flask
- **Frontend**: Vanilla JavaScript, Canvas API, CSS3
- **AI/Logic**: Pure Python implementations of ANN, CSP, and Search algorithms.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Start the server: `python backend/app.py`
3. Open in browser: `http://localhost:5000`

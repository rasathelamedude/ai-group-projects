# 8-Puzzle Solver - Best-First Search

Solves randomly generated 8-puzzle using Best-First Search algorithm.

## Setup

```bash
# Backend
cd week-2-project/rasyar
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python index.py

# Frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

## Features

- Random puzzle generation
- Best-First Search solver
- Solution saved to `solution.txt`
- Modern React GUI with step animation

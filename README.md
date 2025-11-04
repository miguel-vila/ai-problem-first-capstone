# Trading Bot - AI-Powered Investor Assistant

## Getting Started

### Prerequisites
- Python 3.11 or higher
- Node.js 18+ and npm (for frontend development)
- uv (Python package manager)

### Installation

1. Install Python dependencies:
```bash
uv sync
```

2. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Running Locally

#### Option 1: Run backend and frontend separately

**Terminal 1 - Backend:**
```bash
uv run python main.py
# or
uv run uvicorn backend.app.main:app --reload
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

The frontend will be available at http://localhost:3000 and will proxy API requests to the backend at http://localhost:8000.

#### Option 2: Run only the backend (API testing)

```bash
uv run python main.py
```

Visit http://localhost:8000/docs for the interactive API documentation (Swagger UI).

#### Option 3: Run production build locally (integrated frontend + backend)

This mimics the production deployment where the backend serves the frontend:

```bash
# Build the frontend
npm run build --prefix frontend

# Run the backend (which will serve the built frontend)
uv run python main.py
```

Visit http://localhost:8000 to see the complete application!

## Deployment to Railway

The application is configured for **single-service deployment** - Railway will automatically:
1. Install Python and Node.js dependencies
2. Build the React frontend
3. Start the FastAPI backend (which serves the built frontend)

### Via Railway CLI

1. Install Railway CLI:
```bash
npm i -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Initialize and deploy:
```bash
railway init
railway up
```

Railway will execute the `build.sh` script to build the frontend before starting the backend server.

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

## API Endpoints

### `POST /generate-strategy`

Generate an investment strategy based on user inputs.

**Request Body:**
```json
{
  "ticker_symbol": "AAPL",
  "risk_appetite": "Medium",
  "investment_experience": "Intermediate",
  "time_horizon": "Medium-term"
}
```

**Response:**
```json
{
  "suggested_action": "Buy",
  "reasoning": "Based on your profile..."
}
```

## Deployment to Railway

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

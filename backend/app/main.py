from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .models import InvestmentRequest, InvestmentResponse, Action

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Trading Bot API",
    description="AI-powered investor assistant API",
    version="0.1.0"
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Trading Bot API is running"}


@app.post("/generate-strategy", response_model=InvestmentResponse)
async def generate_strategy(request: InvestmentRequest):
    """
    Generate investment strategy based on user inputs.

    This is a placeholder implementation. The actual AI logic will be
    implemented in future iterations.
    """
    # Placeholder logic - to be replaced with actual AI implementation
    reasoning = (
        f"Based on your profile (Risk: {request.risk_appetite.value}, "
        f"Experience: {request.investment_experience.value}, "
        f"Horizon: {request.time_horizon.value}), "
        f"this is a placeholder recommendation for {request.ticker_symbol}. "
        "AI implementation coming soon."
    )

    return InvestmentResponse(
        suggested_action=Action.NOT_BUY,
        reasoning=reasoning
    )

from enum import Enum
from pydantic import BaseModel, Field


class RiskAppetite(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class InvestmentExperience(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    EXPERT = "Expert"


class TimeHorizon(str, Enum):
    SHORT_TERM = "Short-term"
    MEDIUM_TERM = "Medium-term"
    LONG_TERM = "Long-term"


class InvestmentRequest(BaseModel):
    ticker_symbol: str = Field(..., description="Stock ticker symbol (e.g., AAPL, MSFT)")
    risk_appetite: RiskAppetite
    investment_experience: InvestmentExperience
    time_horizon: TimeHorizon


class Action(str, Enum):
    BUY = "Buy"
    NOT_BUY = "Not Buy"


class InvestmentResponse(BaseModel):
    suggested_action: Action
    reasoning: str = Field(..., description="Detailed reasoning behind the suggested action")

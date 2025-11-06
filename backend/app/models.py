from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, TypedDict

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
    """Possible actions for investment decisions."""
    BUY = "Buy"
    NOT_BUY = "Not Buy"
    
class ServiceResponse(BaseModel):
    suggested_action: Action = Field(..., description="Suggested investment action")
    reasoning: str = Field(..., description="Detailed reasoning behind the suggested action")
    sources: Optional[List[str]] = Field(None, description="Sources of information used for the suggestion")

class InvestmentResponse(BaseModel):
    """Final response model for investment suggestion based on the profile and the ticker symbol."""
    suggested_action: Action = Field(..., description="Suggested investment action")
    reasoning: str = Field(..., description="Detailed reasoning behind the suggested action")

class SummaryResponse(BaseModel):
    summary: str = Field(..., description="Summary of recent news articles")
    sources: List[str] = Field(..., description="Sources of the news articles")

class Overview(BaseModel):
    description: str
    market_capitalization: float
    pe_ratio: float
    peg_ratio: float
    book_value: float
    dividend_yield: float
    dividend_per_share: float
    eps: float
    beta: float
    sector: str
    industry: str
    
    def to_prompt_segment(self, line_prefix: str = '          ') -> str:
        lines = [
            f"- Description: {self.description}",
            f"- Market Capitalization: {self.market_capitalization}",
            f"- P/E Ratio: {self.pe_ratio}",
            f"- PEG Ratio: {self.peg_ratio}",
            f"- Book Value: {self.book_value}",
            f"- Dividend Yield: {self.dividend_yield}",
            f"- Dividend Per Share: {self.dividend_per_share}",
            f"- EPS: {self.eps}",
            f"- Beta: {self.beta}",
            f"- Sector: {self.sector}",
            f"- Industry: {self.industry}",
        ]
        return f"\n{line_prefix}".join(lines)
    
class AdvisorState(TypedDict):
    ticker_symbol: str
    risk_appetite: str
    investment_experience: str
    time_horizon: str
    recent_news_results: str
    recent_news_summary_result: SummaryResponse
    overview: Overview
    response: InvestmentResponse

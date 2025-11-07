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
    time_horizon: TimeHorizon


class Action(str, Enum):
    """Possible actions for investment decisions."""
    BUY = "Buy"
    NOT_BUY = "Not Buy"
    
class InvestmentResponse(BaseModel):
    """Final response model for investment suggestion based on the profile and the ticker symbol."""
    suggested_action: Action = Field(..., description="Suggested investment action")
    reasoning: str = Field(..., description="Detailed reasoning behind the suggested action")
    
class SummarizedSearchResult(BaseModel):
    title: str = Field(..., description="Title of the news")
    url: str = Field(..., description="URL of the news")

class ServiceResponse(BaseModel):
    suggested_action: Action = Field(..., description="Suggested investment action")
    reasoning: str = Field(..., description="Detailed reasoning behind the suggested action")
    sources: Optional[List[SummarizedSearchResult]] = Field(None, description="Sources of information used for the suggestion")
    guardrail_override: Optional[InvestmentResponse] = Field(None, description="Override response if any guardrail was triggered")

class WebSearchResult(BaseModel):
    title: str
    content: str
    url: str
    
    def to_prompt_segment(self, line_prefix: str = '          ') -> str:
        return f"{line_prefix}- Title: {self.title}\n{line_prefix}  URL: {self.url}\n{line_prefix}  Content: {self.content}"

class SummaryResponse(BaseModel):
    summary: str = Field(..., description="Summary of recent news articles")
    sources: List[SummarizedSearchResult] = Field(..., description="Sources of the news articles")

class Overview(BaseModel):
    description: str
    market_capitalization: Optional[float]
    pe_ratio: Optional[float]
    peg_ratio: Optional[float]
    book_value: Optional[float]
    dividend_yield: Optional[float]
    dividend_per_share: Optional[float]
    eps: Optional[float]
    beta: Optional[float]
    sector: str
    industry: str
    
    def to_prompt_segment(self, line_prefix: str = '          ') -> str:
        lines = [
            f"- Description: {self.description}",
            f"- Market Capitalization: {self.market_capitalization or 'N/A'}",
            f"- P/E Ratio: {self.pe_ratio or 'N/A'}",
            f"- PEG Ratio: {self.peg_ratio or 'N/A'}",
            f"- Book Value: {self.book_value or 'N/A'}",
            f"- Dividend Yield: {self.dividend_yield or 'N/A'}",
            f"- Dividend Per Share: {self.dividend_per_share or 'N/A'}",
            f"- EPS: {self.eps or 'N/A'}",
            f"- Beta: {self.beta or 'N/A'}",
            f"- Sector: {self.sector}",
            f"- Industry: {self.industry}",
        ]
        return f"\n{line_prefix}".join(lines)
    
class AdvisorState(TypedDict):
    ticker_symbol: str
    risk_appetite: RiskAppetite
    time_horizon: TimeHorizon
    recent_news_results: list[WebSearchResult]
    recent_news_summary_result: SummaryResponse
    overview: Overview
    response: InvestmentResponse
    guardrails_override: Optional[InvestmentResponse]
    trace_id: str

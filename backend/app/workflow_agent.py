import json
from backend.app.models import InvestmentResponse
from backend.app.cache import OverviewCache
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph
from typing import Dict, List, Optional, TypedDict
from langchain_core.tools.base import BaseTool
from pydantic import BaseModel
from langgraph.constants import START

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
    recent_news_summary: str
    overview: Overview
    response: InvestmentResponse

class WorkflowAgent:
    overview_tool: BaseTool
    def __init__(self, overview_tool: BaseTool):
        self.overview_tool = overview_tool
        self.overview_cache = OverviewCache(ttl_days=7)
        self.tavily_client = TavilySearch(
            max_results=10,
            include_answer=False,
            include_raw_content=True,
            include_images=False,
            search_depth="basic",
        )
        self.llm = init_chat_model("gpt-4o-mini", model_provider="openai")
        response_model = self.llm.with_structured_output(InvestmentResponse)
        prompt = ChatPromptTemplate.from_template("""You are a research assistant that helps users decide on investment strategies.
        You will analyze recent news and stock performance for a given ticker symbol.
        Based on this information and the user's risk appetite, investment experience, and time horizon,
        you will suggest an investment action: BUY, SELL, or NOT_BUY.
        Provide a detailed reasoning for your suggestion.
        
        Ticker Symbol: {ticker_symbol}
        Risk Appetite: {risk_appetite}
        Investment Experience: {investment_experience}
        Time Horizon: {time_horizon}
        Overview:
          {overview}
        Recent News: {recent_news_summary}
        """)
        self.response_chain = prompt | response_model
        graph_builder = StateGraph(AdvisorState)
        graph_builder.add_node('recent_news', self.recent_news)
        graph_builder.add_node('web_search_results_summarization', self.web_search_results_summarization)
        graph_builder.add_node('get_overview', self.get_overview)
        graph_builder.add_node('investment_suggestion', self.investment_suggestion)
        graph_builder.add_edge(START, 'recent_news')
        graph_builder.add_edge(START, 'get_overview')
        graph_builder.add_edge('recent_news', 'web_search_results_summarization')
        graph_builder.add_edge(start_key=['web_search_results_summarization', 'get_overview'], end_key='investment_suggestion')
        # graph_builder.set_entry_point(START)
        graph_builder.set_finish_point('investment_suggestion')
        self.graph = graph_builder.compile()

    async def ainvoke(self, state: AdvisorState):
        return await self.graph.ainvoke(state)

    def recent_news(self, state: AdvisorState):
        search_query = f"Recent news about {state['ticker_symbol']} stock"
        results = self.tavily_client.invoke({'query': search_query})['results']
        return {'recent_news_results': results}
    
    def web_search_results_summarization(self, state: AdvisorState):
        prompt = ChatPromptTemplate.from_template("""Summarize the following news articles about {ticker_symbol} stock:
        {recent_news_results}
        Provide key insights relevant to investment decisions.""")
        chain = prompt | self.llm
        
        summary = chain.invoke({
            'ticker_symbol': state['ticker_symbol'],
            'recent_news_results': state['recent_news_results']
        })
        return {'recent_news_summary': summary}
    
    async def get_overview(self, state: AdvisorState):
        symbol = state['ticker_symbol']

        # Check cache first
        cached_data = self.overview_cache.get(symbol)

        if cached_data:
            print(f"Using cached overview data for {symbol}")
            response = cached_data
        else:
            # Cache miss, fetch from API
            print(f"Cache miss for {symbol}, fetching from API")
            response = json.loads(await self.overview_tool.ainvoke({'symbol': symbol}))
            print(f"Overview tool response: {response}, type: {type(response)}")

            # Store in cache
            self.overview_cache.set(symbol, response)

        overview = Overview(
            description=response['Description'],
            market_capitalization=float(response['MarketCapitalization']),
            pe_ratio=float(response['PERatio']),
            peg_ratio=float(response['PEGRatio']),
            book_value=float(response['BookValue']),
            dividend_yield=float(response['DividendYield']),
            dividend_per_share=float(response['DividendPerShare']),
            eps=float(response['EPS']),
            beta=float(response['Beta']),
            sector=response['Sector'],
            industry=response['Industry']
        )
        return {'overview': overview}
    
    def investment_suggestion(self, state: AdvisorState):
        response = self.response_chain.invoke({
            'ticker_symbol': state['ticker_symbol'],
            'risk_appetite': state['risk_appetite'],
            'investment_experience': state['investment_experience'],
            'time_horizon': state['time_horizon'],
            'recent_news_summary': state['recent_news_summary'],
            'overview': state['overview'].to_prompt_segment()
        })
        return {'response': response}

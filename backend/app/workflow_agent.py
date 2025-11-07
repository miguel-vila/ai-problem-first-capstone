import json
from typing import Optional
from backend.app.models import InvestmentResponse
from backend.app.cache import OverviewCache
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph
from langchain_core.tools.base import BaseTool
from langgraph.constants import START
from .models import Action, Overview, AdvisorState, RiskAppetite, SummaryResponse, WebSearchResult
import opik

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
        
        # Final response chain
        response_model = self.llm.with_structured_output(InvestmentResponse)
        prompt = ChatPromptTemplate.from_template("""You are a research assistant that helps users decide on investment strategies.
You will analyze recent news and stock performance for a given ticker symbol.
Based on this information and the user's risk appetite, investment experience, and time horizon,
you will suggest an investment action: BUY, or NOT_BUY.
Provide a detailed reasoning for your suggestion.

Ticker Symbol: {ticker_symbol}
Risk Appetite: {risk_appetite}
Investment Experience: {investment_experience}
Time Horizon: {time_horizon}
Overview:
    {overview}
Recent News: {recent_news_summary}""")
        self.response_chain = prompt | response_model
        
        # Summary chain
        summary_prompt = ChatPromptTemplate.from_template("""Summarize the following news articles about {ticker_symbol} stock:
{recent_news_results}
Provide key insights relevant to investment decisions.
Include sources in the summary.""")
        self.summary_chain = summary_prompt | self.llm.with_structured_output(SummaryResponse)
        
        # Build workflow graph
        graph_builder = StateGraph(AdvisorState)
        graph_builder.add_node('recent_news', self.recent_news)
        graph_builder.add_node('web_search_results_summarization', self.web_search_results_summarization)
        graph_builder.add_node('get_overview_indicators', self.get_overview_indicators)
        graph_builder.add_node('investment_suggestion', self.investment_suggestion)
        graph_builder.add_node('risk_appetite_beta_guardrail', self.risk_appetite_beta_guardrail)
        graph_builder.add_edge(START, 'recent_news')
        graph_builder.add_edge(START, 'get_overview_indicators')
        graph_builder.add_edge('recent_news', 'web_search_results_summarization')
        graph_builder.add_edge(start_key=['web_search_results_summarization', 'get_overview_indicators'], end_key='investment_suggestion')
        graph_builder.add_edge('investment_suggestion', 'risk_appetite_beta_guardrail')
        graph_builder.set_finish_point('risk_appetite_beta_guardrail')
        self.graph = graph_builder.compile()

    @opik.track(name="investment_workflow")
    async def ainvoke(self, state: AdvisorState):
        """
        Execute the investment workflow with Opik tracking.

        This method is decorated with @opik.track to automatically log
        inputs, outputs, and execution traces for evaluation.
        """
        result = await self.graph.ainvoke(state)
        return result

    def recent_news(self, state: AdvisorState):
        search_query = f"Recent news about {state['ticker_symbol']} stock"
        results = self.tavily_client.invoke({'query': search_query})['results']
        web_search_results: list[WebSearchResult] = []
        for result in results:
            web_search_results.append(WebSearchResult(
                title=result['title'],
                url=result['url'],
                content=result['content']
            ))
        return {'recent_news_results': web_search_results}

    def web_search_results_summarization(self, state: AdvisorState):
        recent_news_results = state['recent_news_results']
        recent_news_results_str = "\n".join([res.to_prompt_segment() for res in recent_news_results])
        summary = self.summary_chain.invoke({
            'ticker_symbol': state['ticker_symbol'],
            'recent_news_results': recent_news_results_str
        })
        return {'recent_news_summary_result': summary}
    
    async def get_overview_indicators(self, state: AdvisorState):
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

            # Store in cache
            self.overview_cache.set(symbol, response)

        overview = Overview(
            description=response['Description'],
            market_capitalization=maybe_float_from_str(response['MarketCapitalization']),
            pe_ratio=maybe_float_from_str(response['PERatio']),
            peg_ratio=maybe_float_from_str(response['PEGRatio']),
            book_value=maybe_float_from_str(response['BookValue']),
            dividend_yield=maybe_float_from_str(response['DividendYield']),
            dividend_per_share=maybe_float_from_str(response['DividendPerShare']),
            eps=maybe_float_from_str(response['EPS']),
            beta=maybe_float_from_str(response['Beta']),
            sector=response['Sector'],
            industry=response['Industry']
        )
        return {'overview': overview}
    
    def risk_appetite_beta_guardrail(self, state: AdvisorState):
        if state['response'].suggested_action == Action.BUY and state['risk_appetite'] in [RiskAppetite.LOW] and state['overview'].beta > 1.0:
            return {'guardrails_override': { 'action': 'NOT_BUY', 'reasoning': 'High beta stock not suitable for low risk appetite'}}
        return state
    
    def investment_suggestion(self, state: AdvisorState):
        recent_news_summary_result = state['recent_news_summary_result']
        response = self.response_chain.invoke({
            'ticker_symbol': state['ticker_symbol'],
            'risk_appetite': state['risk_appetite'].value,
            'investment_experience': state['investment_experience'].value,
            'time_horizon': state['time_horizon'].value,
            'recent_news_summary': recent_news_summary_result.summary,
            'overview': state['overview'].to_prompt_segment()
        })
        return {'response': response}


def maybe_float_from_str(value: str) -> Optional[float]:
    if value == 'None':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

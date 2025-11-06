import json
from backend.app.models import InvestmentResponse
from backend.app.cache import OverviewCache
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph
from langchain_core.tools.base import BaseTool
from langgraph.constants import START
from .models import Overview, AdvisorState, SummaryResponse

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
        Recent News: {recent_news_summary}
        """)
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
        graph_builder.add_edge(START, 'recent_news')
        graph_builder.add_edge(START, 'get_overview_indicators')
        graph_builder.add_edge('recent_news', 'web_search_results_summarization')
        graph_builder.add_edge(start_key=['web_search_results_summarization', 'get_overview_indicators'], end_key='investment_suggestion')
        graph_builder.set_finish_point('investment_suggestion')
        self.graph = graph_builder.compile()

    async def ainvoke(self, state: AdvisorState):
        return await self.graph.ainvoke(state)

    def recent_news(self, state: AdvisorState):
        search_query = f"Recent news about {state['ticker_symbol']} stock"
        results = self.tavily_client.invoke({'query': search_query})['results']
        return {'recent_news_results': results}
    
    def web_search_results_summarization(self, state: AdvisorState):
        summary = self.summary_chain.invoke({
            'ticker_symbol': state['ticker_symbol'],
            'recent_news_results': state['recent_news_results']
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
        recent_news_summary_result = state['recent_news_summary_result']
        response = self.response_chain.invoke({
            'ticker_symbol': state['ticker_symbol'],
            'risk_appetite': state['risk_appetite'],
            'investment_experience': state['investment_experience'],
            'time_horizon': state['time_horizon'],
            'recent_news_summary': recent_news_summary_result.summary,
            'overview': state['overview'].to_prompt_segment()
        })
        return {'response': response}

from backend.app.models import InvestmentResponse
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch
from langgraph.graph import StateGraph
from typing import Dict, List, Optional, TypedDict

class AdvisorState(TypedDict):
    ticker_symbol: str
    risk_appetite: str
    investment_experience: str
    time_horizon: str
    recent_news_results: str
    recent_news_summary: str
    response: InvestmentResponse

class WorkflowAgent:
    def __init__(self):
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
        Recent News: {recent_news_summary}
        """)
        self.response_chain = prompt | response_model
        graph_builder = StateGraph(AdvisorState)
        graph_builder.set_entry_point('recent_news')
        graph_builder.add_node('recent_news', self.recent_news)
        graph_builder.add_node('web_search_results_summarization', self.web_search_results_summarization)
        graph_builder.add_edge('recent_news', 'web_search_results_summarization')
        graph_builder.add_node('investment_suggestion', self.investment_suggestion)
        graph_builder.add_edge('web_search_results_summarization', 'investment_suggestion')
        graph_builder.set_finish_point('investment_suggestion')
        self.graph = graph_builder.compile()

    def invoke(self, state: AdvisorState):
        return self.graph.invoke(state)

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
    
    def investment_suggestion(self, state: AdvisorState):
        response = self.response_chain.invoke({
            'ticker_symbol': state['ticker_symbol'],
            'risk_appetite': state['risk_appetite'],
            'investment_experience': state['investment_experience'],
            'time_horizon': state['time_horizon'],
            'recent_news_summary': state['recent_news_summary']
        })
        return {'response': response}

import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, Response
from dotenv import load_dotenv
from .workflow_agent import WorkflowAgent
from .models import InvestmentRequest, ServiceResponse
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from langchain_mcp_adapters.tools import load_mcp_tools
from contextlib import asynccontextmanager

# Load environment variables
load_dotenv()

alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
alpha_vantage_mcp_url = f'https://mcp.alphavantage.co/mcp?apikey={alpha_vantage_api_key}'

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with streamablehttp_client(alpha_vantage_mcp_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools = await load_mcp_tools(session)
            overview_tool = [tool for tool in tools if tool.name == 'COMPANY_OVERVIEW'][0]
            app.state.workflow = WorkflowAgent(overview_tool=overview_tool)
            yield
    
app = FastAPI(
    title="Trading Bot API",
    description="AI-powered investor assistant API",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Trading Bot API is running"}


@app.post("/generate-strategy", response_model=ServiceResponse)
async def generate_strategy(request: InvestmentRequest, response: Response):
    """
    Generate investment strategy based on user inputs.

    This is a placeholder implementation. The actual AI logic will be
    implemented in future iterations.
    """
    # Placeholder logic - to be replaced with actual AI implementation
    
    workflow_result = await app.state.workflow.ainvoke({
        'ticker_symbol': request.ticker_symbol,
        'risk_appetite': request.risk_appetite,
        'investment_experience': request.investment_experience,
        'time_horizon': request.time_horizon
    })
    if 'guardrail_override' in workflow_result:
        response.status_code = 500
        return ServiceResponse(
            suggested_action=workflow_result['response'].suggested_action,
            reasoning=workflow_result['response'].reasoning,
            sources=workflow_result['recent_news_summary_result'].sources,
            guardrail_override=workflow_result['guardrails_override']
        )
        
    return ServiceResponse(
        suggested_action=workflow_result['response'].suggested_action,
        reasoning=workflow_result['response'].reasoning,
        sources=workflow_result['recent_news_summary_result'].sources,
        guardrail_override=None
    )


@app.get("/workflow-graph")
async def get_workflow_graph():
    """
    Generate and return a visualization of the workflow graph.
    Returns a PNG image of the LangGraph workflow.
    """
    try:
        # Get the graph from the workflow agent
        graph = app.state.workflow.graph.get_graph()

        # Generate PNG image using Mermaid
        png_bytes = graph.draw_mermaid_png()

        # Return as PNG image
        return Response(content=png_bytes, media_type="image/png")
    except Exception as e:
        # If graph generation fails, return an error
        return Response(
            content=f"Error generating graph: {str(e)}",
            status_code=500,
            media_type="text/plain"
        )


# Serve static files from the frontend build (for production)
# Get the path to frontend/dist relative to the backend directory
frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"

if frontend_dist.exists() and (frontend_dist / "index.html").exists():
    # Mount static assets directory
    app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")

    # Catch-all route to serve index.html for SPA routing
    # This must be defined AFTER all API routes
    @app.get("/")
    async def serve_root():
        """Serve the frontend app at root"""
        return FileResponse(frontend_dist / "index.html")

    @app.get("/{catchall:path}")
    async def serve_spa(catchall: str):
        """
        Catch-all route to serve the React SPA.
        This allows client-side routing to work.
        API routes defined above take precedence.
        """
        # If it's a file in the dist folder, serve it
        path = frontend_dist / catchall
        if path.is_file():
            return FileResponse(path)

        # Otherwise serve index.html (SPA routing)
        return FileResponse(frontend_dist / "index.html")

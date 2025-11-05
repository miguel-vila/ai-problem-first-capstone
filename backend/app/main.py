from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from .workflow_agent import WorkflowAgent

from .models import InvestmentRequest, InvestmentResponse

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Trading Bot API",
    description="AI-powered investor assistant API",
    version="0.1.0"
)

workflow = WorkflowAgent()

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


@app.post("/generate-strategy", response_model=InvestmentResponse)
async def generate_strategy(request: InvestmentRequest):
    """
    Generate investment strategy based on user inputs.

    This is a placeholder implementation. The actual AI logic will be
    implemented in future iterations.
    """
    # Placeholder logic - to be replaced with actual AI implementation
    
    response = workflow.invoke({
        'ticker_symbol': request.ticker_symbol,
        'risk_appetite': request.risk_appetite.value,
        'investment_experience': request.investment_experience.value,
        'time_horizon': request.time_horizon.value
    })['response']
        
    return response


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

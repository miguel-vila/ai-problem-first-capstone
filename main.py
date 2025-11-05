import os
import uvicorn


def main():
    """Run the FastAPI application"""
    # Get port from environment variable (Railway sets this)
    # Default to 8000 for local development
    port = int(os.environ.get("PORT", 8000))

    # Disable reload in production (when PORT is set by Railway)
    reload = "PORT" not in os.environ

    uvicorn.run(
        "backend.app.main:app",
        host="0.0.0.0",
        port=port,
        reload=reload
    )


if __name__ == "__main__":
    main()

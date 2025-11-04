# Technical Decisions and Rationale

This document outlines the technical choices made during the project setup that were not explicitly specified in the initial requirements.

## Backend Architecture

### 1. FastAPI Application Structure

**Decision**: Organized the FastAPI application in a modular structure under `backend/app/` directory with separate files for models and main application logic.

**Rationale**:
- **Separation of Concerns**: Keeping models separate from routing logic makes the codebase more maintainable
- **Scalability**: This structure allows easy addition of new modules (services, repositories, utilities) as the project grows
- **Best Practice**: Follows industry-standard Python application layout

### 2. Pydantic Models with Enums

**Decision**: Used Pydantic Enums for risk appetite, investment experience, and time horizon instead of plain strings.

**Rationale**:
- **Type Safety**: Enums provide compile-time type checking and prevent invalid values
- **API Documentation**: FastAPI automatically generates better documentation with enum values clearly listed
- **Validation**: Automatic validation of incoming requests against allowed values
- **IDE Support**: Better autocomplete and type hints for developers

### 3. CORS Middleware Configuration

**Decision**: Added CORS middleware with permissive settings for development (`allow_origins=["*"]`).

**Rationale**:
- **Development Experience**: Allows the frontend (running on port 3000) to communicate with the backend (port 8000)
- **Note**: Included a comment indicating this should be configured properly for production
- **Future-Ready**: Easy to restrict to specific origins when deploying

### 4. Port Configuration

**Decision**: Backend runs on port 8000, which is the standard FastAPI/uvicorn default.

**Rationale**:
- **Convention**: Port 8000 is widely recognized for Python web applications
- **Documentation**: Most FastAPI tutorials and examples use port 8000
- **Railway Compatibility**: Railway can override this with the PORT environment variable

## Frontend Architecture

### 1. React with Vite

**Decision**: Chose Vite + React instead of Create React App or Next.js.

**Rationale**:
- **Performance**: Vite offers extremely fast hot module replacement (HMR) and build times
- **Modern**: Vite is the current recommended tool by the React team
- **Simplicity**: Matches the requirement for a "very simple" frontend
- **Developer Experience**: Faster iteration cycles during development
- **Lightweight**: Smaller footprint compared to Next.js, which is overkill for this use case

### 2. Proxy Configuration

**Decision**: Configured Vite to proxy `/generate-strategy` requests to the backend.

**Rationale**:
- **Development Convenience**: No need to configure absolute URLs or deal with CORS during development
- **Environment Parity**: Similar behavior between dev and production
- **Clean Code**: Frontend code uses relative URLs that work in all environments

### 3. Modern CSS with Gradients

**Decision**: Used pure CSS with a gradient-based design instead of a CSS framework like Tailwind or Material-UI.

**Rationale**:
- **Simplicity**: No additional dependencies or build configuration needed
- **Modern Look**: Gradient design creates a contemporary, professional appearance
- **Performance**: No framework overhead
- **Customization**: Easy to modify without learning a framework's conventions
- **File Size**: Minimal CSS compared to including an entire component library

### 4. Form State Management

**Decision**: Used React's built-in `useState` hook for form management instead of libraries like Formik or React Hook Form.

**Rationale**:
- **Simplicity**: The form is straightforward with only 4 fields
- **No Extra Dependencies**: Keeps the bundle size small
- **Readability**: The code is easy to understand for developers of all skill levels
- **Sufficient**: Built-in React state is adequate for this use case

## Deployment Configuration

### 1. Railway.json + Procfile

**Decision**: Included both `railway.json` and `Procfile` for Railway deployment.

**Rationale**:
- **Flexibility**: Railway supports multiple configuration methods
- **Nixpacks**: `railway.json` explicitly uses Nixpacks builder for Python
- **Clarity**: `Procfile` clearly documents the start command
- **Fallback**: If one configuration method fails, the other serves as backup

### 2. Integrated Single-Service Deployment

**Decision**: Configured Railway to deploy both frontend and backend as a single service, with FastAPI serving the built React frontend.

**Rationale**:
- **Simplicity**: Single `railway up` command deploys everything
- **Cost Efficiency**: One service instead of two reduces Railway costs
- **Automatic Builds**: Railway automatically builds the frontend during deployment via `build.sh`
- **No CORS Complexity**: Frontend and backend on same origin eliminates CORS configuration
- **Monorepo Benefits**: Both parts of the application versioned and deployed together

**Implementation Details**:
- `build.sh`: Script that installs Node.js dependencies and builds the React app
- `nixpacks.toml`: Ensures Railway installs both Python and Node.js
- `backend/app/main.py`: Serves static files from `frontend/dist` using FastAPI's StaticFiles
- Catch-all route serves `index.html` for client-side routing
- API routes (defined first) take precedence over static file serving

### 3. Environment Variables Structure

**Decision**: Created `.env.example` with all potential environment variables documented.

**Rationale**:
- **Documentation**: New developers know exactly what variables are needed
- **Security**: The actual `.env` file is gitignored, but the template is shared
- **Convenience**: Easy to copy and fill in with actual values
- **Production Readiness**: Clear guidance on what Railway needs configured

## Dependency Management

### 1. Specific Versions for AI Libraries

**Decision**: Used exact versions (==) for LangChain-related libraries as specified, but used flexible versions (>=) for FastAPI and other core dependencies.

**Rationale**:
- **Stability**: LangChain ecosystem is rapidly evolving; pinning versions ensures consistency
- **Flexibility**: Core dependencies like FastAPI are more stable and can accept minor updates
- **Future-Proofing**: Allows security patches for general dependencies while maintaining AI library compatibility

### 2. Additional Dependencies

**Decision**: Added FastAPI, uvicorn[standard], and pydantic beyond the specified dependencies.

**Rationale**:
- **Core Requirements**: These are essential for running a FastAPI application
- **Production-Ready**: `uvicorn[standard]` includes all necessary production features
- **Version 2**: Using Pydantic v2 for better performance and features

## File Organization

### 1. Backend and Frontend Separation

**Decision**: Created separate `backend/` and `frontend/` directories at the project root.

**Rationale**:
- **Clarity**: Clear separation between frontend and backend code
- **Monorepo Pattern**: Both parts of the application in one repository
- **Development Workflow**: Can work on either part independently
- **Deployment Flexibility**: Can deploy separately if needed

### 2. Main.py as Entry Point

**Decision**: Kept `main.py` at the root as the application entry point that imports from backend.

**Rationale**:
- **Convention**: Follows Python convention of having a main entry point
- **Railway Compatibility**: Simple command `python main.py` to start the app
- **Flexibility**: Easy to add additional startup logic or configuration

## Testing and Development

### 1. Development Server with Reload

**Decision**: Configured uvicorn with `reload=True` in the main.py.

**Rationale**:
- **Developer Experience**: Automatic reload on code changes speeds up development
- **Best Practice**: Standard configuration for development environments
- **Production Override**: Can easily be disabled for production via environment variables

## Future Considerations

These decisions were made with future AI implementation in mind:

1. **Modular Structure**: Easy to add new modules for AI agents, tools, and workflows
2. **Environment Variables**: Ready for API keys needed by LangChain, OpenAI, etc.
3. **Type Safety**: Pydantic models will integrate seamlessly with LangChain
4. **Async/Await**: FastAPI's async support will handle LLM API calls efficiently
5. **Observability**: Opik dependency is included and ready to integrate

## Summary

All technical decisions prioritize:
- **Simplicity**: Easy to understand and maintain
- **Modern Best Practices**: Using current industry-standard tools
- **Developer Experience**: Fast iteration and clear code organization
- **Production Readiness**: Can be deployed to Railway with minimal configuration
- **Future Growth**: Architecture supports adding AI functionality without major refactoring

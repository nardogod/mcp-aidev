"""
MCP-AIDev Server

FastAPI application exposing MCP protocol via HTTP
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from database.connection import init_db, get_db
from database.models import Project, Phase
from mcp.protocol import MCPProtocol
from mcp.tools import MCPTools
from services.project_service import ProjectService


# Lifespan handler for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown"""
    # Startup: Initialize database
    db_url = os.getenv("DATABASE_URL", "sqlite:///./data/mcp_aidev.db")
    init_db(db_url)
    print(f"✅ Database initialized: {db_url}")
    yield
    # Shutdown: cleanup if needed
    print("👋 Server shutting down")


# Initialize FastAPI app
app = FastAPI(
    title="MCP-AIDev",
    description="MCP Server for orchestrating AI-powered development workflows between Claude Web and Cursor IDE",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration - allow connections from Claude and Cursor
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency to get database session
def get_database():
    """Database session dependency"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


# Pydantic models for request/response
class ExecuteToolRequest(BaseModel):
    """Request body for tool execution"""
    tool: str
    arguments: Dict[str, Any]


class ExecuteToolResponse(BaseModel):
    """Response from tool execution"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint with welcome message"""
    return {
        "message": "Welcome to MCP-AIDev Server",
        "description": "MCP Server for orchestrating AI-powered development workflows",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check(db: Session = Depends(get_database)):
    """Health check endpoint"""
    # Test database connection
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "healthy",
        "version": "0.1.0",
        "database": db_status
    }


# MCP Tools endpoints
@app.get("/mcp/tools")
async def list_tools():
    """List all available MCP tools"""
    tools = MCPTools()
    return {"tools": tools.get_all_tools()}


@app.get("/mcp/tools/{tool_name}")
async def get_tool(tool_name: str):
    """Get specific tool definition"""
    tools = MCPTools()
    tool = tools.get_tool(tool_name)
    
    if not tool:
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
    
    return tool


# MCP Execute endpoint
@app.post("/mcp/execute", response_model=ExecuteToolResponse)
async def execute_tool(
    request: ExecuteToolRequest,
    db: Session = Depends(get_database)
):
    """Execute an MCP tool"""
    protocol = MCPProtocol(db)
    result = protocol.execute_tool(request.tool, request.arguments)
    
    return ExecuteToolResponse(**result)


# Projects endpoints
@app.get("/projects")
async def list_projects(db: Session = Depends(get_database)):
    """List all projects"""
    service = ProjectService(db)
    projects = service.list_projects()
    return {"projects": projects}


@app.get("/projects/{project_id}")
async def get_project(project_id: str, db: Session = Depends(get_database)):
    """Get project details with phases"""
    project = db.query(Project).filter_by(id=project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")
    
    # Get all phases for this project
    phases = db.query(Phase).filter_by(project_id=project_id).order_by(Phase.phase_number).all()
    
    return {
        "project_id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "created_at": project.created_at.isoformat(),
        "updated_at": project.updated_at.isoformat(),
        "phases": [
            {
                "phase_id": p.id,
                "phase_number": p.phase_number,
                "title": p.title,
                "status": p.status,
                "specs": p.specs,
                "progress_data": p.progress_data
            }
            for p in phases
        ]
    }


# Run server if executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

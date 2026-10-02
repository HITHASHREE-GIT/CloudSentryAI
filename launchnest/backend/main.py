"""
LaunchNest — FastAPI Entry Point
=================================
Run: uvicorn main:app --reload --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import API_TITLE, API_DESCRIPTION, API_VERSION, ALLOWED_ORIGINS
from app.database import Base, engine
from app.routers import auth, projects, tasks, team, dashboard

# Create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)

# CORS — allow LaunchNest React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(team.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {
        "service": API_TITLE,
        "version": API_VERSION,
        "docs": "/docs",
        "endpoints": [
            "POST   /api/auth/register",
            "POST   /api/auth/login",
            "GET    /api/auth/me",
            "GET    /api/projects",
            "POST   /api/projects",
            "GET    /api/projects/{id}",
            "PUT    /api/projects/{id}",
            "DELETE /api/projects/{id}",
            "GET    /api/tasks",
            "POST   /api/tasks",
            "PUT    /api/tasks/{id}",
            "GET    /api/team",
            "GET    /api/dashboard/stats",
        ],
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "launchnest-api", "version": API_VERSION}
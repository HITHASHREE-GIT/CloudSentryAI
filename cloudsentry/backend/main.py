"""
CloudSentry AI — FastAPI entry point.
Run: uvicorn main:app --reload --port 8001
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import API_TITLE, API_DESCRIPTION, API_VERSION
from app.routers import health, scan, findings

app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)

# CORS — allow local + production frontends
allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
]

# Production frontend URL (set as env var on Render)
frontend_url = os.getenv("FRONTEND_URL")
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(scan.router)
app.include_router(findings.router)


@app.get("/")
def root():
    return {
        "service": API_TITLE,
        "version": API_VERSION,
        "docs": "/docs",
        "endpoints": [
            "GET  /health",
            "POST /scan",
            "GET  /findings",
            "GET  /findings/{finding_id}",
        ],
    }
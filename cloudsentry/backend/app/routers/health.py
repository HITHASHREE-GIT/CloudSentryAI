"""CloudSentry AI — Health endpoint."""

from fastapi import APIRouter
from app.config import API_TITLE, API_VERSION
from app.models import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        service=API_TITLE,
        version=API_VERSION,
    )
"""
LaunchNest — Dashboard Router
==============================
Aggregated stats for the customer dashboard.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=schemas.DashboardStats)
def stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    total_projects = db.query(models.Project).count()
    active_projects = db.query(models.Project).filter(models.Project.status == "active").count()

    total_tasks = db.query(models.Task).count()
    completed_tasks = db.query(models.Task).filter(models.Task.status == "completed").count()
    in_progress_tasks = db.query(models.Task).filter(models.Task.status == "in_progress").count()
    todo_tasks = db.query(models.Task).filter(models.Task.status == "todo").count()

    team_members = db.query(models.User).count()
    total_documents = db.query(models.Document).count()

    return schemas.DashboardStats(
        total_projects=total_projects,
        active_projects=active_projects,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        in_progress_tasks=in_progress_tasks,
        todo_tasks=todo_tasks,
        team_members=team_members,
        total_documents=total_documents,
    )
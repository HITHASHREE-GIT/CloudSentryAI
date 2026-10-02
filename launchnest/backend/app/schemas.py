"""
LaunchNest — Pydantic Schemas
==============================
Request/response models for the API.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


# ═══════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "developer"


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(UserBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ═══════════════════════════════════════════════════════
# PROJECTS
# ═══════════════════════════════════════════════════════

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = ""
    status: str = "active"
    progress: int = 0


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None


class ProjectOut(ProjectBase):
    project_id: int
    owner_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════
# TASKS
# ═══════════════════════════════════════════════════════

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = ""
    project_id: int
    assigned_to: Optional[int] = None
    status: str = "todo"
    priority: str = "medium"


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    assigned_to: Optional[int] = None
    status: Optional[str] = None
    priority: Optional[str] = None


class TaskOut(TaskBase):
    task_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ═══════════════════════════════════════════════════════
# DASHBOARD
# ═══════════════════════════════════════════════════════

class DashboardStats(BaseModel):
    total_projects: int
    active_projects: int
    total_tasks: int
    completed_tasks: int
    in_progress_tasks: int
    todo_tasks: int
    team_members: int
    total_documents: int
"""
LaunchNest — SQLAlchemy Models
================================
Tables: users, projects, tasks, documents, activity
"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.orm import relationship

from app.database import Base


# ═══════════════════════════════════════════════════════
# USERS
# ═══════════════════════════════════════════════════════

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="developer")  # admin, developer, intern
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owned_projects = relationship("Project", back_populates="owner")
    assigned_tasks = relationship("Task", back_populates="assignee")


# ═══════════════════════════════════════════════════════
# PROJECTS
# ═══════════════════════════════════════════════════════

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    description = Column(Text, default="")
    owner_id = Column(Integer, ForeignKey("users.user_id"))
    status = Column(String(20), default="active")  # active, planning, archived
    progress = Column(Integer, default=0)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="owned_projects")
    tasks = relationship("Task", back_populates="project")
    documents = relationship("Document", back_populates="project")


# ═══════════════════════════════════════════════════════
# TASKS
# ═══════════════════════════════════════════════════════

class Task(Base):
    __tablename__ = "tasks"

    task_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    assigned_to = Column(Integer, ForeignKey("users.user_id"))
    status = Column(String(20), default="todo")  # todo, in_progress, completed
    priority = Column(String(20), default="medium")  # low, medium, high
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="tasks")
    assignee = relationship("User", back_populates="assigned_tasks")


# ═══════════════════════════════════════════════════════
# DOCUMENTS
# ═══════════════════════════════════════════════════════

class Document(Base):
    __tablename__ = "documents"

    document_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.project_id"))
    filename = Column(String(255), nullable=False)
    s3_key = Column(String(255), default="")
    uploaded_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="documents")


# ═══════════════════════════════════════════════════════
# ACTIVITY LOG
# ═══════════════════════════════════════════════════════

class Activity(Base):
    __tablename__ = "activity"

    activity_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    action = Column(String(255))
    timestamp = Column(DateTime, default=datetime.utcnow)
"""
LaunchNest — Demo Data Seeder
==============================
Populates the SQLite database with realistic demo data:
- 8 users
- 12 projects
- 29 tasks
- 15 documents
- 6 activity entries
"""

from app.database import SessionLocal, Base, engine
from app import models
from app.security import hash_password


USERS = [
    {"name": "Hira Sharma",   "email": "hira@gmail.com",    "role": "admin"},
    {"name": "Priya Patel",   "email": "priya@gmail.com",   "role": "developer"},
    {"name": "Amit Kumar",    "email": "amit@gmail.com",    "role": "developer"},
    {"name": "Sneha Reddy",   "email": "sneha@gmail.com",   "role": "developer"},
    {"name": "Vikram Singh",  "email": "vikram@gmail.com",  "role": "developer"},
    {"name": "Ananya Iyer",   "email": "ananya@gmail.com",  "role": "intern"},
    {"name": "Karthik Nair",  "email": "karthik@gmail.com", "role": "intern"},
    {"name": "Divya Menon",   "email": "divya@gmail.com",   "role": "developer"},
]

PROJECTS = [
    {"name": "Website Redesign",     "status": "active",   "progress": 72},
    {"name": "Mobile Application",   "status": "active",   "progress": 45},
    {"name": "Cloud Migration",      "status": "active",   "progress": 90},
    {"name": "API v2 Development",   "status": "active",   "progress": 60},
    {"name": "Customer Portal",      "status": "active",   "progress": 30},
    {"name": "Analytics Dashboard",  "status": "active",   "progress": 55},
    {"name": "Payment Integration",  "status": "planning", "progress": 10},
    {"name": "Email Automation",     "status": "active",   "progress": 80},
    {"name": "Documentation Site",   "status": "active",   "progress": 65},
    {"name": "Security Audit",       "status": "planning", "progress": 5},
    {"name": "Mobile App v2",        "status": "planning", "progress": 0},
    {"name": "Data Backup System",   "status": "active",   "progress": 40},
]

TASKS = [
    # project_id 1 - Website Redesign
    {"project_id": 1, "title": "Design login page",           "status": "completed",   "priority": "high",   "assigned_to": 2},
    {"project_id": 1, "title": "Create wireframes",           "status": "completed",   "priority": "medium", "assigned_to": 4},
    {"project_id": 1, "title": "Implement responsive layout", "status": "in_progress", "priority": "high",   "assigned_to": 3},
    {"project_id": 1, "title": "Test on mobile",              "status": "todo",        "priority": "low",    "assigned_to": 6},

    # project_id 2 - Mobile Application
    {"project_id": 2, "title": "Setup React Native",          "status": "completed",   "priority": "high",   "assigned_to": 5},
    {"project_id": 2, "title": "API integration",             "status": "in_progress", "priority": "high",   "assigned_to": 2},
    {"project_id": 2, "title": "Push notifications",          "status": "todo",        "priority": "medium", "assigned_to": 8},

    # project_id 3 - Cloud Migration
    {"project_id": 3, "title": "Configure database",          "status": "completed",   "priority": "high",   "assigned_to": 1},
    {"project_id": 3, "title": "Security testing",            "status": "in_progress", "priority": "high",   "assigned_to": 3},
    {"project_id": 3, "title": "Write documentation",         "status": "todo",        "priority": "low",    "assigned_to": 6},

    # project_id 4 - API v2 Development
    {"project_id": 4, "title": "Design endpoints",            "status": "completed",   "priority": "high",   "assigned_to": 2},
    {"project_id": 4, "title": "Implement authentication",    "status": "in_progress", "priority": "high",   "assigned_to": 4},
    {"project_id": 4, "title": "Add rate limiting",           "status": "todo",        "priority": "medium", "assigned_to": 5},

    # project_id 5 - Customer Portal
    {"project_id": 5, "title": "User dashboard",              "status": "in_progress", "priority": "high",   "assigned_to": 3},
    {"project_id": 5, "title": "Settings page",               "status": "todo",        "priority": "medium", "assigned_to": 8},

    # project_id 6 - Analytics Dashboard
    {"project_id": 6, "title": "Chart components",            "status": "in_progress", "priority": "high",   "assigned_to": 2},
    {"project_id": 6, "title": "Data aggregation API",        "status": "todo",        "priority": "high",   "assigned_to": 4},

    # project_id 7 - Payment Integration
    {"project_id": 7, "title": "Choose payment provider",     "status": "in_progress", "priority": "high",   "assigned_to": 1},
    {"project_id": 7, "title": "Implement checkout flow",     "status": "todo",        "priority": "high",   "assigned_to": 3},

    # project_id 8 - Email Automation
    {"project_id": 8, "title": "Template engine",             "status": "completed",   "priority": "medium", "assigned_to": 4},
    {"project_id": 8, "title": "Send schedule",               "status": "completed",   "priority": "medium", "assigned_to": 5},
    {"project_id": 8, "title": "Unsubscribe flow",            "status": "in_progress", "priority": "low",    "assigned_to": 8},

    # project_id 9 - Documentation Site
    {"project_id": 9, "title": "Write intro",                 "status": "completed",   "priority": "low",    "assigned_to": 6},
    {"project_id": 9, "title": "API reference",               "status": "in_progress", "priority": "medium", "assigned_to": 3},

    # project_id 10 - Security Audit
    {"project_id": 10, "title": "Scope definition",           "status": "in_progress", "priority": "high",   "assigned_to": 1},
    {"project_id": 10, "title": "Run scanner",                "status": "todo",        "priority": "high",   "assigned_to": 4},

    # project_id 11 - Mobile App v2
    {"project_id": 11, "title": "Requirements gathering",     "status": "todo",        "priority": "medium", "assigned_to": 2},

    # project_id 12 - Data Backup System
    {"project_id": 12, "title": "Select storage",             "status": "completed",   "priority": "high",   "assigned_to": 1},
    {"project_id": 12, "title": "Backup schedule",            "status": "in_progress", "priority": "high",   "assigned_to": 5},
]

DOCUMENTS = [
    {"project_id": 1,  "filename": "redesign-spec.pdf",       "s3_key": "documents/redesign-spec.pdf",        "uploaded_by": 2},
    {"project_id": 1,  "filename": "wireframes-v2.fig",       "s3_key": "documents/wireframes-v2.fig",        "uploaded_by": 4},
    {"project_id": 2,  "filename": "mobile-requirements.docx","s3_key": "documents/mobile-requirements.docx", "uploaded_by": 5},
    {"project_id": 3,  "filename": "migration-plan.xlsx",     "s3_key": "documents/migration-plan.xlsx",      "uploaded_by": 1},
    {"project_id": 4,  "filename": "api-v2-spec.md",          "s3_key": "documents/api-v2-spec.md",           "uploaded_by": 2},
    {"project_id": 5,  "filename": "portal-mockup.png",       "s3_key": "documents/portal-mockup.png",        "uploaded_by": 3},
    {"project_id": 6,  "filename": "dashboard-metrics.xlsx",  "s3_key": "documents/dashboard-metrics.xlsx",   "uploaded_by": 2},
    {"project_id": 8,  "filename": "email-templates.zip",     "s3_key": "documents/email-templates.zip",      "uploaded_by": 4},
    {"project_id": 9,  "filename": "docs-outline.md",         "s3_key": "documents/docs-outline.md",          "uploaded_by": 6},
    {"project_id": 10, "filename": "audit-scope.pdf",         "s3_key": "documents/audit-scope.pdf",          "uploaded_by": 1},
    {"project_id": 12, "filename": "backup-strategy.docx",    "s3_key": "documents/backup-strategy.docx",     "uploaded_by": 5},
    {"project_id": 3,  "filename": "aws-architecture.png",    "s3_key": "documents/aws-architecture.png",     "uploaded_by": 1},
    {"project_id": 4,  "filename": "postman-collection.json", "s3_key": "documents/postman-collection.json",  "uploaded_by": 2},
    {"project_id": 6,  "filename": "chart-library-notes.md",  "s3_key": "documents/chart-library-notes.md",   "uploaded_by": 3},
    {"project_id": 12, "filename": "backup-test-results.txt", "s3_key": "documents/backup-test-results.txt",  "uploaded_by": 5},
]


def seed(force: bool = False):
    """Populate DB with demo data."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing = db.query(models.User).count()
        if existing > 0 and not force:
            print(f"⏭️  Skipping seed — {existing} users already exist.")
            return

        if force:
            print("🧹 Clearing existing data...")
            db.query(models.Activity).delete()
            db.query(models.Document).delete()
            db.query(models.Task).delete()
            db.query(models.Project).delete()
            db.query(models.User).delete()
            db.commit()

        # Users
        print("👥 Creating 8 users...")
        for u in USERS:
            user = models.User(
                name=u["name"],
                email=u["email"],
                password_hash=hash_password("demo123"),
                role=u["role"],
            )
            db.add(user)
        db.commit()

        # Projects
        print("📁 Creating 12 projects...")
        for p in PROJECTS:
            project = models.Project(
                name=p["name"],
                description=f"Demo project: {p['name']}",
                status=p["status"],
                progress=p["progress"],
                owner_id=1,
            )
            db.add(project)
        db.commit()

        # Tasks
        print(f"✅ Creating {len(TASKS)} tasks...")
        for t in TASKS:
            task = models.Task(
                title=t["title"],
                description="",
                project_id=t["project_id"],
                assigned_to=t["assigned_to"],
                status=t["status"],
                priority=t["priority"],
            )
            db.add(task)
        db.commit()

        # Documents
        print(f"📄 Creating {len(DOCUMENTS)} documents...")
        for d in DOCUMENTS:
            doc = models.Document(
                project_id=d["project_id"],
                filename=d["filename"],
                s3_key=d["s3_key"],
                uploaded_by=d["uploaded_by"],
            )
            db.add(doc)
        db.commit()

        # Activity
        print("📝 Creating activity log...")
        actions = [
            (1, "registered as admin"),
            (2, "created project 'Website Redesign'"),
            (3, "completed task 'Design login page'"),
            (4, "uploaded document 'redesign-spec.pdf'"),
            (5, "created task 'Setup React Native'"),
            (1, "updated project 'Cloud Migration'"),
        ]
        for uid, action in actions:
            db.add(models.Activity(user_id=uid, action=action))
        db.commit()

        print()
        print("=" * 50)
        print("✅ Seed complete!")
        print(f"   Users     : {db.query(models.User).count()}")
        print(f"   Projects  : {db.query(models.Project).count()}")
        print(f"   Tasks     : {db.query(models.Task).count()}")
        print(f"   Documents : {db.query(models.Document).count()}")
        print(f"   Activity  : {db.query(models.Activity).count()}")
        print("=" * 50)
        print()
        print("Demo login:")
        print("   Email    : hira@gmail.com")
        print("   Password : demo123")
        print()

    finally:
        db.close()


if __name__ == "__main__":
    import sys
    force = "--force" in sys.argv
    seed(force=force)
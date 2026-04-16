"""
Handlungskompetenz-Tracker – REST API
FastAPI + SQLAlchemy + MSSQL
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
import uuid
import json
import os

from database import engine, get_db, Base
import models

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')

# Tabellen erstellen falls noch nicht vorhanden
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Kompetenz-Tracker API", version="1.0")

# CORS: erlaubt dem Browser (Frontend) die API aufzurufen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Pydantic-Schemas (Datenvalidierung) ──────────────────────

class UserCreate(BaseModel):
    name: str
    specialty: str  # "platform" oder "app"
    start_date: date  # YYYY-MM-DD

class UserOut(BaseModel):
    id: str
    name: str
    specialty: str
    start_date: date
    class Config:
        from_attributes = True

class GoalEntryUpsert(BaseModel):
    goal_id: str
    level: int
    comment: Optional[str] = ""

class GoalEntryOut(BaseModel):
    id: str
    user_id: str
    goal_id: str
    level: int
    comment: Optional[str]
    updated_at: datetime
    class Config:
        from_attributes = True

# ── Endpunkte: Users ─────────────────────────────────────────

@app.get("/users", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    """Alle Lernenden zurückgeben."""
    return db.query(models.User).order_by(models.User.name).all()


@app.post("/users", response_model=UserOut, status_code=201)
def create_user(body: UserCreate, db: Session = Depends(get_db)):
    """Neuen Lernenden erfassen."""
    user = models.User(
        id=str(uuid.uuid4()),
        name=body.name,
        specialty=body.specialty,
        start_date=body.start_date,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: str, body: UserCreate, db: Session = Depends(get_db)):
    """Lernenden bearbeiten."""
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Person nicht gefunden")
    user.name       = body.name
    user.specialty  = body.specialty
    user.start_date = body.start_date
    db.commit()
    db.refresh(user)
    return user


@app.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Lernenden löschen (inkl. alle Bewertungen)."""
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Person nicht gefunden")
    db.delete(user)
    db.commit()

# ── Endpunkte: GoalEntries ───────────────────────────────────

@app.get("/users/{user_id}/goals", response_model=list[GoalEntryOut])
def get_goals(user_id: str, db: Session = Depends(get_db)):
    """Alle Bewertungen einer Person zurückgeben."""
    return (
        db.query(models.GoalEntry)
        .filter(models.GoalEntry.user_id == user_id)
        .all()
    )


@app.put("/users/{user_id}/goals/{goal_id}", response_model=GoalEntryOut)
def upsert_goal(
    user_id: str, goal_id: str, body: GoalEntryUpsert, db: Session = Depends(get_db)
):
    """Bewertung speichern (neu anlegen oder aktualisieren)."""
    entry = (
        db.query(models.GoalEntry)
        .filter_by(user_id=user_id, goal_id=goal_id)
        .first()
    )
    if entry:
        entry.level      = body.level
        entry.comment    = body.comment
        entry.updated_at = datetime.utcnow()
    else:
        entry = models.GoalEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            goal_id=goal_id,
            level=body.level,
            comment=body.comment,
        )
        db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


# ── Endpunkte: Kompetenzen ───────────────────────────────────

@app.get("/competencies")
def list_competency_files():
    """Verfügbare Kompetenz-JSONs auflisten."""
    files = [f.replace('.json', '') for f in os.listdir(DATA_DIR) if f.endswith('.json')]
    return files


@app.get("/competencies/{name}")
def get_competencies(name: str):
    """Kompetenz-JSON nach Name laden (ohne .json-Endung)."""
    path = os.path.join(DATA_DIR, f"{name}.json")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Kompetenz-Datei nicht gefunden")
    with open(path, encoding='utf-8') as f:
        return json.load(f)


# ── Startpunkt ───────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

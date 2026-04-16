"""
SQLAlchemy-Modelle – spiegeln die Tabellen in der DB
"""
import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Date, DateTime, Text, ForeignKey, UniqueConstraint
from datetime import date as DateType
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database import Base


class User(Base):
    __tablename__ = "Users"

    id: Mapped[str] = mapped_column(
        "Id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str]       = mapped_column("Name",      String(100), nullable=False)
    specialty: Mapped[str]  = mapped_column("Specialty", String(20),  nullable=False)
    start_date: Mapped[DateType] = mapped_column("StartDate", Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        "CreatedAt", DateTime, default=datetime.utcnow
    )

    goal_entries: Mapped[list["GoalEntry"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class GoalEntry(Base):
    __tablename__ = "GoalEntries"

    id: Mapped[str] = mapped_column(
        "Id", String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        "UserId", String(36), ForeignKey("Users.Id", ondelete="CASCADE"), nullable=False
    )
    goal_id: Mapped[str]   = mapped_column("GoalId",    String(20),  nullable=False)
    level: Mapped[int]     = mapped_column("Level",     Integer,     default=0)
    comment: Mapped[str]   = mapped_column("Comment",   Text,        nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        "UpdatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    user: Mapped["User"] = relationship(back_populates="goal_entries")

    __table_args__ = (
        UniqueConstraint("UserId", "GoalId", name="UQ_User_Goal"),
    )

from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False)
    email: str = Field(index=True, nullable=False)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    tasks: List["Task"] = Relationship(back_populates="owner")


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    priority: int = Field(default=1)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")

    owner: Optional[User] = Relationship(back_populates="tasks")
    time_entries: List["TimeEntry"] = Relationship(back_populates="task")
    tags: List["TaskTag"] = Relationship(back_populates="task")


class TimeEntry(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    duration: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    task_id: Optional[int] = Field(default=None, foreign_key="task.id")

    task: Optional[Task] = Relationship(back_populates="time_entries")


class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True)

    tasks: List["TaskTag"] = Relationship(back_populates="tag")


class TaskTag(SQLModel, table=True):
    task_id: Optional[int] = Field(default=None, foreign_key="task.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)
    note: Optional[str] = None

    task: Optional[Task] = Relationship(back_populates="tags")
    tag: Optional[Tag] = Relationship(back_populates="tasks")


class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True, nullable=False)

    participants: List["Participant"] = Relationship(back_populates="team")


class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str
    nickname: str = Field(index=True, unique=True)
    email: str
    phone: str
    skill: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    team_id: Optional[int] = Field(default=None, foreign_key="team.id")
    team: Optional[Team] = Relationship(back_populates="participants")
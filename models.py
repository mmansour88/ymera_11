from datetime import datetime
from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy import Integer, String, DateTime, Boolean, Text, Float, ForeignKey
Base = declarative_base()
class User(Base):
    __tablename__="users"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    email: Mapped[str]=mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str]=mapped_column(String(255))
    role: Mapped[str]=mapped_column(String(50), default="user")
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class Team(Base):
    __tablename__="teams"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    name: Mapped[str]=mapped_column(String(100), unique=True)
    head_agent_id: Mapped[int|None]=mapped_column(ForeignKey("agents.id"), nullable=True)
class Agent(Base):
    __tablename__="agents"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    name: Mapped[str]=mapped_column(String(100), unique=True)
    specialization: Mapped[str]=mapped_column(String(100))
    team_id: Mapped[int|None]=mapped_column(ForeignKey("teams.id"))
    active: Mapped[bool]=mapped_column(Boolean, default=True)
class Task(Base):
    __tablename__="tasks"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    title: Mapped[str]=mapped_column(String(200))
    description: Mapped[str]=mapped_column(Text)
    status: Mapped[str]=mapped_column(String(50), default="queued")
    team_id: Mapped[int|None]=mapped_column(ForeignKey("teams.id"))
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime|None]=mapped_column(DateTime, default=datetime.utcnow)
class Report(Base):
    __tablename__="reports"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    task_id: Mapped[int]=mapped_column(ForeignKey("tasks.id"))
    summary: Mapped[str]=mapped_column(Text)
    flag: Mapped[str]=mapped_column(String(20), default="green")
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)
class Rating(Base):
    __tablename__="ratings"
    id: Mapped[int]=mapped_column(Integer, primary_key=True)
    agent_id: Mapped[int]=mapped_column(ForeignKey("agents.id"))
    dimension: Mapped[str]=mapped_column(String(100))
    score: Mapped[float]=mapped_column(Float)
    created_at: Mapped[datetime]=mapped_column(DateTime, default=datetime.utcnow)


class Budget(Base):
    __tablename__ = "budgets"
    id = Column(Integer, primary_key=True)
    provider = Column(String, index=True)  # openai/anthropic/...
    daily_limit_usd = Column(Float, default=1.0)
    spent_today_usd = Column(Float, default=0.0)

class Policy(Base):
    __tablename__ = "policies"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    enabled = Column(Boolean, default=True)
    data = Column(JSON, default={})

class ToolUseLog(Base):
    __tablename__ = "tool_use_logs"
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    tool = Column(String)
    input = Column(JSON, default={})
    output = Column(JSON, default={})


class UserQuota(Base):
    __tablename__ = "user_quotas"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    daily_calls = Column(Integer, default=100)
    used_today = Column(Integer, default=0)


class UserProviderQuota(Base):
    __tablename__ = "user_provider_quotas"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    provider = Column(String, index=True)
    daily_calls = Column(Integer, default=50)
    used_today = Column(Integer, default=0)


class AgentProfile(Base):
    __tablename__ = "agent_profiles"
    id = Column(Integer, primary_key=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), unique=True)
    avatar_url = Column(String, nullable=True)
    settings = Column(JSON, default={})


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    head_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    paused = Column(Boolean, default=False)

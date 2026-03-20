"""
Database models and connection for persistent chat/session storage.

Uses SQLAlchemy async with asyncpg for PostgreSQL.
"""

import os
from datetime import datetime, timezone

from sqlalchemy import Column, String, Text, Integer, DateTime, JSON, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://pradaagent:pradaagent@db:5432/pradaagent",
)

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(32), primary_key=True)
    task = Column(Text, nullable=False)
    model_name = Column(String(100), nullable=False)
    max_iterations = Column(Integer, default=30)
    status = Column(String(20), default="pending")  # pending | running | completed | error
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    messages = relationship("ChatMessage", back_populates="session", order_by="ChatMessage.seq")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(32), ForeignKey("chat_sessions.id"), nullable=False, index=True)
    seq = Column(Integer, nullable=False)
    source = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    msg_type = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("ChatSession", back_populates="messages")


async def init_db():
    """Create tables if they don't exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

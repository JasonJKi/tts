import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship

from app.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def _uuid() -> str:
    return str(uuid.uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Voice(Base):
    __tablename__ = "voices"

    id = Column(String, primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    description = Column(Text, default="")
    language = Column(String, default="en")
    reference_audio_path = Column(String, nullable=False)
    audio_duration_s = Column(Float, nullable=True)
    # The voice identifier used when calling vLLM (builtin name or custom ref)
    vllm_voice_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=_now)
    updated_at = Column(DateTime, default=_now, onupdate=_now)

    generations = relationship("Generation", back_populates="voice", cascade="all, delete-orphan")


class Generation(Base):
    __tablename__ = "generations"

    id = Column(String, primary_key=True, default=_uuid)
    voice_id = Column(String, ForeignKey("voices.id"), nullable=False)
    text = Column(Text, nullable=False)
    language = Column(String, default="en")
    output_format = Column(String, default="wav")
    audio_path = Column(String, nullable=True)
    duration_s = Column(Float, nullable=True)
    created_at = Column(DateTime, default=_now)

    voice = relationship("Voice", back_populates="generations")


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session

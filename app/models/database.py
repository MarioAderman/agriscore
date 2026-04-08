import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# --- Enums ---


class ApplicationStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class MessageType(str, enum.Enum):
    text = "text"
    voice = "voice"
    image = "image"
    location = "location"
    document = "document"


class ChallengeStatus(str, enum.Enum):
    sent = "sent"
    completed = "completed"
    expired = "expired"


# --- Models ---


class Farmer(Base):
    __tablename__ = "farmers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str | None] = mapped_column(String(100))
    onboarded: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    parcelas: Mapped[list["Parcela"]] = relationship(back_populates="farmer", cascade="all, delete-orphan")
    applications: Mapped[list["Application"]] = relationship(back_populates="farmer", cascade="all, delete-orphan")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="farmer", cascade="all, delete-orphan")
    challenges: Mapped[list["Challenge"]] = relationship(back_populates="farmer", cascade="all, delete-orphan")


class Parcela(Base):
    __tablename__ = "parcelas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farmers.id"))
    name: Mapped[str | None] = mapped_column(String(100))
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    area_hectares: Mapped[float | None] = mapped_column(Float)
    crop_type: Mapped[str | None] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    farmer: Mapped["Farmer"] = relationship(back_populates="parcelas")
    applications: Mapped[list["Application"]] = relationship(back_populates="parcela", cascade="all, delete-orphan")


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farmers.id"))
    parcela_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("parcelas.id"))
    status: Mapped[ApplicationStatus] = mapped_column(SAEnum(ApplicationStatus), default=ApplicationStatus.pending)
    step_functions_arn: Mapped[str | None] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    farmer: Mapped["Farmer"] = relationship(back_populates="applications")
    parcela: Mapped["Parcela"] = relationship(back_populates="applications")
    satellite_data: Mapped["SatelliteData | None"] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    climate_data: Mapped["ClimateData | None"] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    socioeconomic_data: Mapped["SocioeconomicData | None"] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )
    agriscore_result: Mapped["AgriScoreResult | None"] = relationship(
        back_populates="application", cascade="all, delete-orphan"
    )


class SatelliteData(Base):
    __tablename__ = "satellite_data"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id"), unique=True)
    ndvi_mean: Mapped[float] = mapped_column(Float)
    ndvi_tile_s3_key: Mapped[str | None] = mapped_column(String(256))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    raw_data: Mapped[dict | None] = mapped_column(JSON)

    application: Mapped["Application"] = relationship(back_populates="satellite_data")


class ClimateData(Base):
    __tablename__ = "climate_data"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id"), unique=True)
    avg_temperature: Mapped[float] = mapped_column(Float)
    total_precipitation: Mapped[float] = mapped_column(Float)
    et0: Mapped[float] = mapped_column(Float)
    soil_moisture: Mapped[float] = mapped_column(Float)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    raw_data: Mapped[dict | None] = mapped_column(JSON)

    application: Mapped["Application"] = relationship(back_populates="climate_data")


class SocioeconomicData(Base):
    __tablename__ = "socioeconomic_data"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id"), unique=True)
    population: Mapped[int | None] = mapped_column(Integer)
    agri_establishments: Mapped[int | None] = mapped_column(Integer)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    raw_data: Mapped[dict | None] = mapped_column(JSON)

    application: Mapped["Application"] = relationship(back_populates="socioeconomic_data")


class AgriScoreResult(Base):
    __tablename__ = "agriscore_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    application_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("applications.id"), unique=True)
    total_score: Mapped[float] = mapped_column(Float)
    sub_productive: Mapped[float] = mapped_column(Float)
    sub_climate: Mapped[float] = mapped_column(Float)
    sub_behavioral: Mapped[float] = mapped_column(Float)
    sub_esg: Mapped[float] = mapped_column(Float)
    explanation: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    application: Mapped["Application"] = relationship(back_populates="agriscore_result")


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farmers.id"), index=True)
    role: Mapped[MessageRole] = mapped_column(SAEnum(MessageRole))
    content: Mapped[str] = mapped_column(Text)
    message_type: Mapped[MessageType] = mapped_column(SAEnum(MessageType), default=MessageType.text)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )

    farmer: Mapped["Farmer"] = relationship(back_populates="conversations")


class Challenge(Base):
    __tablename__ = "challenges"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    farmer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farmers.id"), index=True)
    challenge_type: Mapped[str] = mapped_column(String(50))
    status: Mapped[ChallengeStatus] = mapped_column(SAEnum(ChallengeStatus), default=ChallengeStatus.sent)
    photo_s3_key: Mapped[str | None] = mapped_column(String(256))
    ai_tag: Mapped[str | None] = mapped_column(String(100))
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    farmer: Mapped["Farmer"] = relationship(back_populates="challenges")

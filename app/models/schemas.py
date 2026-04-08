import uuid
from datetime import datetime

from pydantic import BaseModel

# --- Farmer ---


class FarmerBase(BaseModel):
    phone: str
    name: str | None = None


class FarmerCreate(FarmerBase):
    pass


class FarmerResponse(FarmerBase):
    id: uuid.UUID
    onboarded: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Parcela ---


class ParcelaCreate(BaseModel):
    latitude: float
    longitude: float
    name: str | None = None
    area_hectares: float | None = None
    crop_type: str | None = None


class ParcelaResponse(ParcelaCreate):
    id: uuid.UUID
    farmer_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# --- AgriScore ---


class AgriScoreResponse(BaseModel):
    total_score: float
    sub_productive: float
    sub_climate: float
    sub_behavioral: float
    sub_esg: float
    explanation: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Application ---


class ApplicationResponse(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    parcela_id: uuid.UUID
    status: str
    created_at: datetime
    completed_at: datetime | None = None

    model_config = {"from_attributes": True}


# --- Bank ---


class FarmerSummary(BaseModel):
    id: uuid.UUID
    phone: str
    name: str | None
    agriscore: float | None = None
    status: str | None = None
    last_updated: datetime | None = None


class BankStats(BaseModel):
    total_farmers: int
    avg_score: float | None
    active_applications: int


# --- Pipeline ---


class PipelineStepResult(BaseModel):
    application_id: str
    step: str
    status: str
    data: dict | None = None

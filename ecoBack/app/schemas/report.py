from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.report import ReportStatus


class ReportCreate(BaseModel):
    waste_type_id: UUID
    title: str = Field(..., max_length=255)
    description: str | None = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: str | None = Field(None, max_length=500)


class ReportUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    status: ReportStatus | None = None
    address: str | None = Field(None, max_length=500)


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    waste_type_id: UUID
    title: str
    description: str | None
    latitude: float
    longitude: float
    address: str | None
    status: ReportStatus
    cleaned_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ReportFilters(BaseModel):
    status: ReportStatus | None = None
    waste_type_id: UUID | None = None
    date_from: date | None = None
    date_to: date | None = None
    lat: float | None = Field(None, ge=-90, le=90)
    lng: float | None = Field(None, ge=-180, le=180)
    radius_km: float | None = Field(None, ge=0.1, le=1000)


class ReportImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    report_id: UUID
    image_url: str
    is_before: bool
    created_at: datetime

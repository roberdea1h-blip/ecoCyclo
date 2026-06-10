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
    estimated_quantity: float | None = None


class ReportUpdate(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    status: ReportStatus | None = None
    address: str | None = Field(None, max_length=500)
    estimated_quantity: float | None = None


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
    estimated_quantity: float | None
    status: ReportStatus
    cleaner_id: UUID | None
    cleaned_at: datetime | None
    validated_at: datetime | None = None
    validator_id: UUID | None = None
    cleaner_name: str | None = None
    validator_name: str | None = None
    waste_type_name: str | None = None
    user_name: str | None = None
    image_url: str | None = None
    created_at: datetime
    updated_at: datetime


class CompleteReportRequest(BaseModel):
    collected_weight: float | None = None
    notes: str | None = None


class VerifyReportRequest(BaseModel):
    pass


class RejectReportRequest(BaseModel):
    reason: str | None = Field(None, max_length=500)


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

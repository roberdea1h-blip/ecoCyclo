from uuid import UUID

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    size: int
    pages: int


class MessageResponse(BaseModel):
    message: str


class IdResponse(BaseModel):
    id: UUID

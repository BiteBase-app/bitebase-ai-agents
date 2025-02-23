from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator

class LocationInput(BaseModel):
    lat: float = Field(..., description="Latitude coordinate")
    lng: float = Field(..., description="Longitude coordinate")
    address: Optional[str] = Field(None, description="Optional full address")

class TimeframeInput(BaseModel):
    start_date: datetime
    end_date: datetime

    @validator('end_date')
    def end_date_must_be_after_start_date(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

class PaginationParams(BaseModel):
    limit: int = Field(10, ge=1, le=100)
    offset: int = Field(0, ge=0)

class SortParams(BaseModel):
    by: str = Field(..., description="Field to sort by")
    order: str = Field("desc", regex="^(asc|desc)$")

class BaseResponse(BaseModel):
    status: str = Field(..., regex="^(success|error)$")
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ErrorResponse(BaseResponse):
    status: str = "error"
    error_code: str
    error_details: Optional[Dict[str, Any]] = None

class SuccessResponse(BaseResponse):
    status: str = "success"
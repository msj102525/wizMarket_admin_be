from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class BusinessDetail(BaseModel):
    business_name: str
    growth_rate: float


class Location(BaseModel):
    city: str
    district: str
    sub_district: str


class RisingBusinessCreate(BaseModel):
    location: Location
    rising_top5: dict[str, BusinessDetail]


class RisingBusinessOutput(BaseModel):
    id: int
    city: str
    district: str
    sub_district: str
    business_name: str
    growth_rate: float
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

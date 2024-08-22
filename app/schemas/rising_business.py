from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RisingBusiness(BaseModel):
    rising_business_id: Optional[int]
    region_id: int
    business_name: Optional[str] = None
    growth_rate: Optional[float] = None
    sub_district_rank: Optional[int] = None
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class RisingBusinessInsert(BaseModel):
    region_id: int
    business_name: Optional[str] = None
    growth_rate: Optional[float] = None
    sub_district_rank: Optional[int] = None

    class Config:
        from_attributes = True

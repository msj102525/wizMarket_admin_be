from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RisingBusiness(BaseModel):
    REGION_ID: int
    BUSINESS_NAME: Optional[str] = None
    GROWTH_RATE: Optional[float] = None
    SUB_DISTRICT_RANK: Optional[int] = None

    class Config:
        from_attributes = True

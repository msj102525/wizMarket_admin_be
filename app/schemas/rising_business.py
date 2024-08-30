from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class RisingBusiness(BaseModel):
    rising_business_id: Optional[int]
    city_id: int
    district_id: int
    sub_district_id: int

    biz_main_category_id: int
    biz_sub_category_id: int
    biz_detail_category_id: int

    growth_rate: float
    rank: int

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RisingBusinessInsert(BaseModel):
    city_id: int
    district_id: int
    sub_district_id: int

    biz_main_category_id: int
    biz_sub_category_id: int
    biz_detail_category_id: int

    growth_rate: float
    rank: int

    class Config:
        from_attributes = True

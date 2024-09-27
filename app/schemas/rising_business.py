from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime, timedelta


class RisingBusiness(BaseModel):
    rising_business_id: int
    city_id: int
    district_id: int
    sub_district_id: int

    biz_main_category_id: int
    biz_sub_category_id: int
    biz_detail_category_id: int

    growth_rate: float
    sub_district_rank: int

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
    sub_district_rank: int

    y_m: date = None 

    class Config:
        from_attributes = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.y_m is None:
            self.y_m = date.today().replace(day=1) - timedelta(days=1)  # 1달 전으로 설정


class RisingBusinessOutput(BaseModel):
    rising_business_id: int
    city_name: str
    district_name: str
    sub_district_name: str

    biz_main_category_name: str
    biz_sub_category_name: str
    biz_detail_category_name: str

    growth_rate: Optional[float] = None
    sub_district_rank: Optional[int] = None

    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

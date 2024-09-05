from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class LocationInfo(BaseModel):
    loc_info_id: Optional[int] = None # Primary Key, Auto Increment
    city_id: int
    district_id: int
    sub_district_id: int
    shop: Optional[int] = None
    move_pop: Optional[int] = None
    sales: Optional[int] = None
    work_pop: Optional[int] = None
    income: Optional[int] = None
    spend: Optional[int] = None
    house: Optional[int] = None
    resident: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    y_m: Optional[date] = None

    class Config:
        from_attributes = True

class LocationRequest(BaseModel):
    city_name: str
    district_name: str
    sub_district_name: str

class FilterRequest(BaseModel):
    city: Optional[str] = None  # 기본값 None을 설정
    district: Optional[str] = None
    sub_district: Optional[str] = None

    shopMin: Optional[int] = None
    move_popMin: Optional[int] = None
    salesMin: Optional[int] = None
    work_popMin: Optional[int] = None
    incomeMin: Optional[int] = None
    spendMin: Optional[int] = None
    houseMin: Optional[int] = None
    residentMin: Optional[int] = None

    shopMax: Optional[int] = None
    move_popMax: Optional[int] = None
    salesMax: Optional[int] = None
    work_popMax: Optional[int] = None
    incomeMax: Optional[int] = None
    spendMax: Optional[int] = None
    houseMax: Optional[int] = None
    residentMax: Optional[int] = None
    
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime 
from fastapi import UploadFile, File


class AdsList(BaseModel):
    local_store_content_id: int
    store_business_number: str
    store_name:str
    road_name:str
    status: str
    title :str
    content :str
    created_at:datetime  

    class Config:
        from_attributes = True


class AdsInitInfo(BaseModel):
    store_business_number: str
    store_name:str
    road_name:str
    city_name: str
    district_name: str
    sub_district_name: str
    detail_category_name: str
    loc_info_average_sales_k: float
    commercial_district_max_sales_day : Optional[float]
    commercial_district_max_sales_time: Optional[float]
    commercial_district_max_sales_m_age: Optional[float]
    commercial_district_max_sales_f_age: Optional[float]


    class Config:
        from_attributes = True


class AdsInitInfoOutPut(BaseModel):
    pass
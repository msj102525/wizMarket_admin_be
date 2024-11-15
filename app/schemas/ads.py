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
    road_name_address:str
    city_name: str
    district_name: str
    sub_district_name: str
    detail_category_name: str
    loc_info_average_sales_k: float

    commercial_district_average_sales_percent_mon: Optional[float]
    commercial_district_average_sales_percent_tue: Optional[float]
    commercial_district_average_sales_percent_wed: Optional[float]
    commercial_district_average_sales_percent_thu: Optional[float]
    commercial_district_average_sales_percent_fri: Optional[float]
    commercial_district_average_sales_percent_sat: Optional[float]
    commercial_district_average_sales_percent_sun: Optional[float]

    commercial_district_average_sales_percent_06_09: Optional[float]
    commercial_district_average_sales_percent_09_12: Optional[float]
    commercial_district_average_sales_percent_12_15: Optional[float]
    commercial_district_average_sales_percent_15_18: Optional[float]
    commercial_district_average_sales_percent_18_21: Optional[float]
    commercial_district_average_sales_percent_21_24: Optional[float]

    commercial_district_avg_client_per_m_20s: Optional[float]
    commercial_district_avg_client_per_m_30s: Optional[float]
    commercial_district_avg_client_per_m_40s: Optional[float]
    commercial_district_avg_client_per_m_50s: Optional[float]
    commercial_district_avg_client_per_m_60_over: Optional[float]

    commercial_district_avg_client_per_f_20s: Optional[float]
    commercial_district_avg_client_per_f_30s: Optional[float]
    commercial_district_avg_client_per_f_40s: Optional[float]
    commercial_district_avg_client_per_f_50s: Optional[float]
    commercial_district_avg_client_per_f_60_over: Optional[float]


    class Config:
        from_attributes = True


class AdsInitInfoOutPut(BaseModel):
    pass
from pydantic import BaseModel
from typing import Optional

class FilterRequest(BaseModel):
    city: Optional[int] = None  # 기본값 None을 설정
    district: Optional[int] = None
    subDistrict: Optional[int] = None
    storeName: Optional[str] = None
    matchType: Optional[str] = '='  # = 또는 LIKE 검색
    mainCategory: Optional[str] = None
    subCategory: Optional[str] = None
    detailCategory: Optional[str] = None
    page: Optional[int] = 1  # 페이지 번호 (기본값 1)
    page_size: Optional[int] = 20  # 페이지 크기 (기본값 20)



class LocalStoreSubdistrict(BaseModel):
    local_store_id: int
    store_business_number: str
    sub_district_id: int
    sub_district_name: str

    class Config:
        from_attributes = True


class LocalStoreCityDistrictSubDistrict(BaseModel):
    local_store_id: int
    store_business_number: str
    store_name: str
    city_id: int
    city_name: str
    district_id: int
    district_name: str
    sub_district_id: int
    sub_district_name: str
    large_category_name: str
    medium_category_name: str
    small_category_name: str
    reference_id: int

    class Config:
        from_attributes = True
    
class BusinessAreaCategoryReportOutput(BaseModel):
    business_area_category_id: int

    class Config:
        from_attributes = True   

class BizDetailCategoryIdOutPut(BaseModel):
    rep_id: int
    biz_detail_category_name: str

    class Config:
        from_attributes = True  

class RisingMenuOutPut(BaseModel):
    market_size: float
    average_sales: int
    average_payment: int
    usage_count: int
    avg_profit_per_mon: float
    avg_profit_per_tue: float
    avg_profit_per_wed: float
    avg_profit_per_thu: float
    avg_profit_per_fri: float
    avg_profit_per_sat: float
    avg_profit_per_sun: float
    avg_profit_per_06_09: float
    avg_profit_per_09_12: float
    avg_profit_per_12_15: float
    avg_profit_per_15_18: float
    avg_profit_per_18_21: float
    avg_profit_per_21_24: float
    avg_profit_per_24_06: float
    top_menu_1: str
    top_menu_2: str
    top_menu_3: str
    top_menu_4: str
    top_menu_5: str

    class Config:
        from_attributes = True  
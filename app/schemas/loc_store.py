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

    class Config:
        from_attributes = True
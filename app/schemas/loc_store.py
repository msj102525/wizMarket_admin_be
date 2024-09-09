from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date

class FilterRequest(BaseModel):
    city: Optional[int] = None  # 기본값 None을 설정
    district: Optional[int] = None
    subDistrict: Optional[int] = None
    storeName: Optional[str] = None
    selectedQuarter: Optional[str] = None
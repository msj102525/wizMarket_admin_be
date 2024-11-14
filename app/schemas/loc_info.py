from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date


class LocationInfo(BaseModel):
    loc_info_id: Optional[int] = None  # Primary Key, Auto Increment
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
    city: Optional[int] = None  # 기본값 None을 설정
    district: Optional[int] = None
    subDistrict: Optional[int] = None

    shopMin: Optional[int] = None
    move_popMin: Optional[int] = None
    salesMin: Optional[int] = None
    work_popMin: Optional[int] = None
    incomeMin: Optional[int] = None
    spendMin: Optional[int] = None
    houseMin: Optional[int] = None
    residentMin: Optional[int] = None
    jScoreMin: Optional[int] = None

    shopMax: Optional[int] = None
    move_popMax: Optional[int] = None
    salesMax: Optional[int] = None
    work_popMax: Optional[int] = None
    incomeMax: Optional[int] = None
    spendMax: Optional[int] = None
    houseMax: Optional[int] = None
    residentMax: Optional[int] = None
    jScoreMax: Optional[int] = None
    selectedOptions: Optional[List[str]] 



class LocationInfoReportOutput(BaseModel):
    resident: Optional[int] = None
    work_pop: Optional[int] = None
    house: Optional[int] = None
    shop: Optional[int] = None
    income: Optional[int] = None

    class Config:
        from_attributes = True


class InsertRecordSchema(BaseModel):
    city_id: int
    district_id: int
    sub_district_id: int
    created_at: datetime
    updated_at: datetime
    reference_id: int
    shop: Optional[int] = None
    move_pop: Optional[int] = None
    sales: Optional[int] = None
    work_pop: Optional[int] = None
    income: Optional[int] = None
    spend: Optional[int] = None
    house: Optional[int] = None
    resident: Optional[int] = None

    class Config:
        from_attributes = True


# loc_info_result 모델
class LocInfoResult(BaseModel):
    shop: int
    move_pop: int
    sales: int
    work_pop: int
    income: int
    spend: int
    house: int
    resident: int

# statistics_result 모델
class StatisticsResult(BaseModel):
    j_score: float

# 상위 모델 - 두 결과를 함께 포함하는 모델
class LocalInfoStatisticsResponse(BaseModel):
    loc_info: LocInfoResult
    statistics: List[StatisticsResult]

    class Config:
        from_attributes = True

    

class StatDataForExetend(BaseModel):
    city_id: int
    city_name: str
    district_id: int
    district_name: str
    sub_district_id: int
    sub_district_name: str
    target_item: str
    avg_val: Optional[float]
    med_val: Optional[float]
    std_val: Optional[float]
    max_val: Optional[float]
    min_val: Optional[float]
    j_score_per: Optional[float]
    j_score_rank: Optional[float]
    j_score: Optional[float]
    j_score_per_non_outliers: Optional[float]
    j_score_non_outliers: Optional[float]
    ref_date : date

    class Config:
        from_attributes = True


class StatDataByCityForExetend(BaseModel):
    city_id: int
    city_name: str
    district_name:Optional[str]
    sub_district_id: int
    sub_district_name: str
    target_item: str
    avg_val: float
    med_val: float
    std_val: float
    max_val: float
    min_val: float
    j_score_per: Optional[float]
    j_score_rank: Optional[float]
    j_score: Optional[float]
    j_score_per_non_outliers: Optional[float]
    j_score_non_outliers: Optional[float]
    ref_date : date

    class Config:
        from_attributes = True

class StatDataByDistrictForExetend(BaseModel):
    city_name: Optional[str]
    district_id: int
    district_name: str
    sub_district_id: int
    sub_district_name: str
    target_item: str
    avg_val: float
    med_val: float
    std_val: float
    max_val: float
    min_val: float
    j_score_per: Optional[float]
    j_score_rank: Optional[float]
    j_score: Optional[float]
    j_score_per_non_outliers: Optional[float]
    j_score_non_outliers: Optional[float]
    ref_date : date

    class Config:
        from_attributes = True
    


class StatDataForNation(BaseModel):
    city_id: int
    city_name: str
    district_id: int
    district_name: str
    sub_district_id: int
    sub_district_name: str
    target_item: str
    j_score: Optional[float]
    j_score_per: Optional[float]
    j_score_rank: Optional[float]
    j_score_per_non_outliers: Optional[float]
    j_score_non_outliers: Optional[float]
    ref_date : date

    class Config:
        from_attributes = True


class StatDataForInit(BaseModel):
    city_id: int
    city_name: str
    district_id: int
    district_name: str
    sub_district_id: int
    sub_district_name: str
    target_item: str
    avg_val: Optional[float]
    med_val: Optional[float]
    std_val: Optional[float]
    max_val: Optional[float]
    min_val: Optional[float]
    ref_date : date


class LocInfoDataDate(BaseModel):
    y_m: date

    class Config:
        from_attributes = True
from pydantic import BaseModel
from datetime import datetime


class Statistics(BaseModel):
    statistics_id: int
    stat_item_id: int
    city_id: int | None = None
    district_id: int | None = None
    sub_district_id: int | None = None
    avg_val: float | None = None
    med_val: float | None = None
    std_val: float | None = None
    max_value: float | None = None
    min_value: float | None = None
    j_score: float | None = None
    created_at: datetime
    referenc_id: int | None = None

    class Config:
        from_attributes = True


class StatisticsJscoreOutput(BaseModel):
    j_score: float | None = None

    class Config:
        from_attributes = True


class LocStatisticsOutput(BaseModel):
    resident_jscore: float
    work_pop_jscore: float
    house_jscore: float
    shop_jscore: float
    income_jscore: float

    class Config:
        from_attributes = True
        

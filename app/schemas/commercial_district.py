from pydantic import BaseModel
from typing import Dict, List


# 세부 정보 모델 정의
class Density(BaseModel):
    national: str
    city: str
    district: str
    sub_district: str


class AverageProfit(BaseModel):
    amount: str
    percent: str


class SalesByDay(BaseModel):
    most_profitable_day: str
    percent: str
    details: Dict[str, str]


class SalesByTime(BaseModel):
    most_profitable_time: str
    percent: str
    details: Dict[str, str]


class ClientDemographics(BaseModel):
    dominant_gender: str
    dominant_gender_percent: float
    dominant_age_group: str
    age_groups: Dict[str, float]  # Changed from List to Dict
    male_percents: Dict[str, float]  # Changed from List to Dict
    female_percents: Dict[str, float]  # Changed from List to Dict
    most_visitor_age: str


class Location(BaseModel):
    city: str
    district: str
    sub_district: str


class CommercialDistrictCreate(BaseModel):
    location: Location
    category: Dict[str, str]
    density: Density
    market_size: str
    average_sales: str
    average_price: str
    usage_count: str
    average_profit: AverageProfit
    sales_by_day: SalesByDay
    sales_by_time: SalesByTime
    client_demographics: ClientDemographics
    top5_menus: Dict[str, str]

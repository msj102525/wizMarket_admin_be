from pydantic import BaseModel
from typing import List, Optional


class Location(BaseModel):
    city: str
    district: str
    sub_district: str


class Category(BaseModel):
    main: str
    sub: str
    detail: str


class Density(BaseModel):
    national: str
    city: str
    district: str
    sub_district: str


class AverageProfit(BaseModel):
    amount: str
    percent: str


class SalesDetails(BaseModel):
    Monday: Optional[str] = None
    Tuesday: Optional[str] = None
    Wednesday: Optional[str] = None
    Thursday: Optional[str] = None
    Friday: Optional[str] = None
    Saturday: Optional[str] = None
    Sunday: Optional[str] = None


class SalesByDay(BaseModel):
    most_profitable_day: str
    percent: str
    details: SalesDetails


class SalesByTimeDetails(BaseModel):
    _06_09: str
    _09_12: str
    _12_15: str
    _15_18: str
    _18_21: str
    _21_24: str
    _24_06: str


class SalesByTime(BaseModel):
    most_profitable_time: str
    percent: str
    details: SalesByTimeDetails


class ClientDemographics(BaseModel):
    dominant_gender: str
    dominant_gender_percent: float
    dominant_age_group: str
    age_groups: List[str]
    male_percents: List[float]
    female_percents: List[float]
    most_visitor_age: str


class Top5Menus(BaseModel):
    top5_menu_1: str
    top5_menu_2: str
    top5_menu_3: str
    top5_menu_4: str
    top5_menu_5: str


class CommercialDistrictCreate(BaseModel):
    location: Location
    category: Category
    density: Density
    market_size: str
    average_sales: str
    average_price: str
    usage_count: str
    average_profit: AverageProfit
    sales_by_day: SalesByDay
    sales_by_time: SalesByTime
    client_demographics: ClientDemographics
    top5_menus: Top5Menus

from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional, Dict


class Location(BaseModel):
    city: str
    district: str
    sub_district: str


class Category(BaseModel):
    main: str
    sub: str
    detail: str


class Density(BaseModel):
    national: Optional[str] = None
    city: Optional[str] = None
    district: Optional[str] = None
    sub_district: Optional[str] = None


class AverageProfit(BaseModel):
    sales: Optional[str] = None
    operating_cost: Optional[str] = None
    percent: Optional[str] = None
    food: Optional[str] = None
    employee: Optional[str] = None
    rental: Optional[str] = None
    tax: Optional[str] = None
    family_employee: Optional[str] = None
    ceo: Optional[str] = None
    etc: Optional[str] = None


class SalesByDayDetails(BaseModel):
    Monday: Optional[str] = None
    Tuesday: Optional[str] = None
    Wednesday: Optional[str] = None
    Thursday: Optional[str] = None
    Friday: Optional[str] = None
    Saturday: Optional[str] = None
    Sunday: Optional[str] = None


class SalesByDay(BaseModel):
    most_profitable_day: Optional[str] = None
    percent: Optional[str] = None
    details: SalesByDayDetails


class SalesByTimeDetails(BaseModel):
    _06_09: Optional[str] = None
    _09_12: Optional[str] = None
    _12_15: Optional[str] = None
    _15_18: Optional[str] = None
    _18_21: Optional[str] = None
    _21_24: Optional[str] = None
    _24_06: Optional[str] = None


class SalesByTime(BaseModel):
    most_profitable_time: Optional[str] = None
    percent: Optional[str] = None
    details: SalesByTimeDetails


class ClientDemographics(BaseModel):
    dominant_gender: Optional[str] = None
    dominant_gender_percent: Optional[float] = None
    dominant_age_group: Optional[str] = None
    age_groups: Optional[List[str]] = None
    male_percents: Optional[Dict[str, float]] = None
    female_percents: Optional[Dict[str, float]] = None
    most_visitor_age: Optional[str] = None


class Top5Menus(BaseModel):
    top5_menu_1: Optional[str] = None
    top5_menu_2: Optional[str] = None
    top5_menu_3: Optional[str] = None
    top5_menu_4: Optional[str] = None
    top5_menu_5: Optional[str] = None


class CommercialDistrictCreate(BaseModel):
    location: Location
    category: Category
    density: Density
    market_size: Optional[str] = None
    average_sales: Optional[str] = None
    average_price: Optional[str] = None
    usage_count: Optional[str] = None
    average_profit: AverageProfit
    sales_by_day: SalesByDay
    sales_by_time: SalesByTime
    client_demographics: ClientDemographics
    top5_menus: Top5Menus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class CommercialDistrictOutput(BaseModel):
    id: int
    city: str
    district: str
    sub_district: str
    main_category: Optional[str] = None
    sub_category: Optional[str] = None
    detail_category: Optional[str] = None
    national_density: Optional[str] = None
    city_density: Optional[str] = None
    district_density: Optional[str] = None
    sub_district_density: Optional[str] = None
    market_size: Optional[str] = None
    average_sales: Optional[str] = None
    average_operating_cost: Optional[str] = None
    average_food: Optional[str] = None
    average_employee: Optional[str] = None
    average_rental: Optional[str] = None
    average_tax: Optional[str] = None
    average_family_employee: Optional[str] = None
    average_ceo: Optional[str] = None
    average_etc: Optional[str] = None
    average_payment_cost: Optional[str] = None
    usage_count: Optional[str] = None
    average_profit_amount: Optional[str] = None
    average_profit_percent: Optional[str] = None
    most_profitable_day: Optional[str] = None
    day_percent: Optional[str] = None
    sales_monday: Optional[str] = None
    sales_tuesday: Optional[str] = None
    sales_wednesday: Optional[str] = None
    sales_thursday: Optional[str] = None
    sales_friday: Optional[str] = None
    sales_saturday: Optional[str] = None
    sales_sunday: Optional[str] = None
    most_profitable_time: Optional[str] = None
    time_percent: Optional[str] = None
    sales_06_09: Optional[str] = None
    sales_09_12: Optional[str] = None
    sales_12_15: Optional[str] = None
    sales_15_18: Optional[str] = None
    sales_18_21: Optional[str] = None
    sales_21_24: Optional[str] = None
    sales_24_06: Optional[str] = None
    dominant_gender: Optional[str] = None
    dominant_gender_percent: Optional[float] = None
    dominant_age_group: Optional[str] = None
    most_visitor_age: Optional[str] = None
    male_20s: Optional[float] = None
    male_30s: Optional[float] = None
    male_40s: Optional[float] = None
    male_50s: Optional[float] = None
    male_60s: Optional[float] = None
    female_20s: Optional[float] = None
    female_30s: Optional[float] = None
    female_40s: Optional[float] = None
    female_50s: Optional[float] = None
    female_60s: Optional[float] = None
    total_male_percent: Optional[float] = None
    total_female_percent: Optional[float] = None
    top_menu_1: Optional[str] = None
    top_menu_2: Optional[str] = None
    top_menu_3: Optional[str] = None
    top_menu_4: Optional[str] = None
    top_menu_5: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


########################

class CommercialDistrict(BaseModel):
    COMMERCIAL_DISTRICT_ID: int
    REGION_ID: int
    CATEGORY_ID: int
    NATIONAL_DENSITY: float
    CITY_DENSITY: float
    DISTRICT_DENSITY: float
    SUB_DISTRICT_DENSITY: float
    MARKET_SIZE: int
    AVERAGE_SALES: int
    AVERAGE_PAYMENT: int
    USAGE_COUNT: int
    OPERATING_COST: int
    FOOD_COST: int
    EMPLOYEE_COST: int
    RENTAL_COST: int
    TAX_COST: int
    FAMILY_EMPLOYEE_COST: int
    CEO_COST: int
    ETC_COST: int
    AVERAGE_PROFIT: int
    AVG_PROFIT_PER_MON: float
    AVG_PROFIT_PER_TUES: float
    AVG_PROFIT_PER_WED: float
    AVG_PROFIT_PER_THU: float
    AVG_PROFIT_PER_FRI: float
    AVG_PROFIT_PER_SAT: float
    AVG_PROFIT_PER_SUN: float
    AVG_PROFIT_PER_06_09: float
    AVG_PROFIT_PER_09_12: float
    AVG_PROFIT_PER_12_15: float
    AVG_PROFIT_PER_15_18: float
    AVG_PROFIT_PER_18_21: float
    AVG_PROFIT_PER_21_24: float
    AVG_CLIENT_PER_M_20: float
    AVG_CLIENT_PER_M_30: float
    AVG_CLIENT_PER_M_40: float
    AVG_CLIENT_PER_M_50: float
    AVG_CLIENT_PER_M_60: float
    AVG_CLIENT_PER_F_20: float
    AVG_CLIENT_PER_F_30: float
    AVG_CLIENT_PER_F_40: float
    AVG_CLIENT_PER_F_50: float
    AVG_CLIENT_PER_F_60: float
    TOP_MENU_1: str
    TOP_MENU_2: str
    TOP_MENU_3: str
    TOP_MENU_4: str
    TOP_MENU_5: str

    class Config:
        from_attributes  = True

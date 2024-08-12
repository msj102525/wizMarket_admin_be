from pydantic import BaseModel

class BusinessDetail(BaseModel):
    business_name: str
    growth_rate: float

class Location(BaseModel):
    city: str
    district: str
    sub_district: str

class RisingBusinessCreate(BaseModel):
    location: Location
    rising_top5: dict[str, BusinessDetail]
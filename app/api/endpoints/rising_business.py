from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.rising_business import RisingBusinessOutput
from app.service.rising_business import get_all_rising_business_by_region_name


router = APIRouter()


@router.get("", response_model=List[RisingBusinessOutput])
def get_rising_business(city: str, district: str, sub_district: str):
    print(f"city: {city}, district: {district}, sub_d: {sub_district}")
    try:
        results = get_all_rising_business_by_region_name(city, district, sub_district)
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.commercial_district import CommercialDistrict, CommercialDistrictOutput
from app.service.commercial_district import (
    get_all_commercial_district_by_region_name,
)

router = APIRouter()


@router.get("", response_model=List[CommercialDistrictOutput])
def get_commercial_district(city: str, district: str, sub_district: str):
    print(f"city: {city}, district: {district}, sub_d: {sub_district}")
    try:
        results = get_all_commercial_district_by_region_name(
            city, district, sub_district
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

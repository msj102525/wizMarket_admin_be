from fastapi import APIRouter, HTTPException
from typing import List
from app.crud.region import select_region_id_by_city_sub_district
from app.schemas.rising_business import RisingBusiness


router = APIRouter()


@router.get("/", response_model=List[RisingBusiness])
def get_commercial_district(city: str, sub_district: str):
    print(city, sub_district)
    try:
        refion_id = select_region_id_by_city_sub_district(city, sub_district)
        if not refion_id:
            raise HTTPException(status_code=404, detail="No data found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

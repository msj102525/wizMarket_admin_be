from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.rising_business import RisingBusinessOutput
from app.crud.rising_business import select_all_rising_business_by_sub_district

router = APIRouter()


@router.get("/", response_model=List[RisingBusinessOutput])
def get_commercial_district(sub_district: str):
    print(sub_district)
    try:
        results = select_all_rising_business_by_sub_district(sub_district)
        if not results:
            raise HTTPException(status_code=404, detail="No data found")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

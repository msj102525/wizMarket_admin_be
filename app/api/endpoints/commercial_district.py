from fastapi import APIRouter, HTTPException
from typing import List

from app.crud.commercial_district import select_all_commercial_district_by_sub_district
from app.schemas.commercial_district import CommercialDistrictOutput

router = APIRouter()


@router.get("/", response_model=List[CommercialDistrictOutput])
def get_commercial_district(sub_district: str):
    print(sub_district)
    try:
        results = select_all_commercial_district_by_sub_district(sub_district)
        if not results:
            raise HTTPException(status_code=404, detail="No data found")
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

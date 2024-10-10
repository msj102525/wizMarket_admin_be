from fastapi import APIRouter, HTTPException
from typing import List


router = APIRouter()


@router.get("", response_model=List[None])
def get_district_list_by_city_id(city_id: int):
    # print(f"city_id: {city_id}")
    try:

        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

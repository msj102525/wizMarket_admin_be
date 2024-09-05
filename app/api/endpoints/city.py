from fastapi import APIRouter, HTTPException
from typing import List


router = APIRouter()


@router.get("", response_model=List[None])
def get_city_list(city_id: int):
    print(f"city_id: {city_id}")
    try:
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import FastAPI, HTTPException, APIRouter
from typing import List
import pymysql
from app.db.connect import *
from app.service.city import get_locations_service

router = APIRouter()

@router.get("/locations")
async def get_locations():
    locations = await get_locations_service()  # 서비스 호출
    print(locations)
    return locations
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

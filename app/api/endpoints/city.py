from fastapi import FastAPI, HTTPException, APIRouter
from typing import List
import pymysql
from app.db.connect import *
from app.service.city import get_locations_service

router = APIRouter()


@router.get("/locations")
async def get_locations():
    locations = await get_locations_service() 
    print(locations)
    return locations

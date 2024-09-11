from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.service.business_area_category import *


router = APIRouter()

@router.get("/business_area_category")
async def get_business_area_category(reference_id: int = Query(...)):
    print(f"Received reference_id: {reference_id}")
    
    # 서비스 레이어에 reference_id 전달
    result = await get_business_area_category_service(reference_id)
    print(type(result))
    
    return result
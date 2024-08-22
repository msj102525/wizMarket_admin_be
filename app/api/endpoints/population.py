from fastapi import APIRouter, HTTPException, Body
from app.service.population import get_population_data, insert_population_data, check_population_exists
from app.db.connect import get_db_connection

router = APIRouter()

import logging
logger = logging.getLogger(__name__)

@router.post("/check_population")
async def check_population(year_month: int = Body(..., embed=True)):
    try:
        year_month = int(year_month)  # int로 변환
        exists = await check_population_exists(year_month)
        return {"exists": exists}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_population")
async def get_population(
    start_date: int = Body(...),
    end_date: int = Body(...),
    city: str = Body(...),
    district: str = Body(...),
    sub_district: str = Body(...)
):
    try:
        data = await get_population_data(start_date, end_date, city, district, sub_district)
        if not data:
            raise HTTPException(status_code=404, detail="No data found")
        print(data)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_regions")
async def get_regions():
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT CITY, DISTRICT, SUB_DISTRICT FROM region")
        regions = cursor.fetchall()
        return regions
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

@router.post("/insert_population")
async def insert_population():
    try:
        # 서비스 레이어에서 실제 인서트 작업 수행
        await insert_population_data()
        return {"message": "Population data inserted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
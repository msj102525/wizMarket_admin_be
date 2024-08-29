from fastapi import APIRouter, HTTPException, Body
from app.service.population import insert_population_data
from app.db.connect import get_db_connection
from typing import List
import pymysql
from app.schemas.city import SidoRequest
from app.schemas.district import DistrictRequest
from app.schemas.population import PopulationRequest
from app.service.population import *


router = APIRouter()

# 전체 시/도 반환
@router.get("/get_cities", response_model=List[str])
async def get_city():
    try:
        return fetch_cities()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 시/도를 기반으로 시/군/구 리스트를 반환
@router.post("/get_districts", response_model=List[str])
async def get_districts(sido_request: SidoRequest):
    try:
        # 시/도명을 통해 시/군/구 리스트를 가져옴
        return fetch_districts_for_sido(sido_request.city_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# 시/군/구를 기반으로 읍/면/동(sub_district) 리스트를 반환
@router.post("/get_sub_districts", response_model=List[str])
async def get_sub_districts(district_request: DistrictRequest):
    try:
        # 시/군/구명을 통해 읍/면/동 이름 리스트를 가져옴
        return fetch_sub_districts_for_district(district_request.district_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# 선택 된 지역 인구 데이터 가져오기
@router.post("/get_population")
async def get_population(data: PopulationRequest):
    try:
        population_data = fetch_population(data.city_name, data.district_name, data.sub_district_name)
        return population_data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/insert_population")
async def insert_population():
    try:
        # 서비스 레이어에서 실제 인서트 작업 수행
        await insert_population_data()
        return {"message": "Population data inserted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

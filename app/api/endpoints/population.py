from fastapi import APIRouter, HTTPException, Body
from app.service.population import insert_population_data
from app.db.connect import get_db_connection
from typing import List
import pymysql
from app.schemas.city import SidoRequest
from app.schemas.district import DistrictRequest
from app.schemas.population import *
from app.service.population import *
from fastapi.responses import JSONResponse

router = APIRouter()


@router.post("/select_population")
async def select_population(filters: PopulationSearch):
    # 입력된 필터 데이터만 딕셔너리로 변환 (unset된 필드는 제외)
    filters_dict = filters.dict(exclude_unset=True)
    print(filters_dict)
    try:
        # 필터 데이터를 서비스 레이어로 전달하여 결과 가져옴
        result = await filter_population_data(filters_dict)
        return {"filtered_data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"검색 중 오류가 발생했습니다: {str(e)}")
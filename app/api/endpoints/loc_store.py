from fastapi import APIRouter, HTTPException
from app.service.loc_store import *
from app.schemas.loc_store import *
from fastapi import Request


router = APIRouter()



# 엔드포인트
@router.post("/select_loc_store")
async def filter_data(filters: FilterRequest):
    # 필터 정보를 서비스 레이어로 전달
    data, total_items = await filter_loc_store(filters)

    return {
        "filtered_data": data,     # 페이징된 데이터
        "total_items": total_items  # 총 데이터 개수
    }
    
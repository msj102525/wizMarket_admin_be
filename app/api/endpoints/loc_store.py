from fastapi import APIRouter, HTTPException
from app.service.loc_store import (
    filter_loc_store,
    select_loc_store_for_content_by_store_business_number as service_select_loc_store_for_content_by_store_business_number
)
from app.schemas.loc_store import *
from fastapi import Request
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# 엔드포인트
@router.post("/select_loc_store")
async def filter_data(filters: FilterRequest):
    # 필터 정보를 서비스 레이어로 전달
    data, total_items = await filter_loc_store(filters)

    return {
        "filtered_data": data,     # 페이징된 데이터
        "total_items": total_items  # 총 데이터 개수
    }
    

@router.post("/select_loc_store_for_content", response_model=LocStoreInfoForContentOutPut)
def select_loc_store_for_content_by_store_business_number(store_business_number: str):
    # 쿼리 매개변수로 전달된 store_business_number 값 수신
    try:
        data = service_select_loc_store_for_content_by_store_business_number(store_business_number)
        return data
    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex
    except Exception as e:
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)



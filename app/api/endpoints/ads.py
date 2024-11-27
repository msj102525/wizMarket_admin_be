from fastapi import (
    APIRouter, HTTPException
)
from app.schemas.ads import (
    AdsListOutPut, UpdateStatusRequest, FilterRequest
)

import logging
from typing import List
from app.service.ads import (
    select_ads_list as service_select_ads_list,
    update_ads_status as service_update_ads_status,
    select_filters_list as service_select_filters_list
)
from pathlib import Path
from dotenv import load_dotenv
import os

router = APIRouter()
logger = logging.getLogger(__name__)

REPORT_PATH = Path(os.getenv("REPORT_PATH"))
IMAGE_DIR = Path(os.getenv("IMAGE_DIR"))
FULL_PATH = REPORT_PATH / IMAGE_DIR.relative_to("/") / "ads"
FULL_PATH.mkdir(parents=True, exist_ok=True)

# ADS 리스트 조회
@router.get("/select/list", response_model=List[AdsListOutPut])
def select_ads_list():
    try:
        # 서비스에서 데이터를 가져와 result 변수에 저장
        result: AdsListOutPut = service_select_ads_list()
        return result  # result를 반환

    except HTTPException as http_ex:
        # service 계층에서 발생한 HTTP 예외는 그대로 전달
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex

    except Exception as e:
        # 예상치 못한 에러
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


# 게시 여부 상태 변경
@router.post("/update/status")
def update_ads_status(request: UpdateStatusRequest):
    try:
        # 서비스 레이어를 통해 업데이트 작업 수행
        service_update_ads_status(
            request.ads_id,
            request.status
        )
        return {"message": "Publish status updated successfully"}
    except Exception as e:
        # 예외 처리
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# 필터 검색
@router.post("/select/filters/list")
async def select_filters_list(request: FilterRequest):
    # 필터 정보를 서비스 레이어로 전달
    filters = request.dict()
    data =  service_select_filters_list(filters)
    print(data)
    return {
        "data": data,     # 페이징된 데이터
    }
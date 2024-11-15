from fastapi import (
    APIRouter, UploadFile, File, Form, HTTPException
)
from app.schemas.ads import (
    AdsList, AdsInitInfo

)
from fastapi import Request
import logging
from typing import List
from app.service.ads import (
    select_ads_list as service_select_ads_list,
    select_ads_init_info as service_select_ads_init_info,
)
from pathlib import Path
import shutil
from typing import Optional
from dotenv import load_dotenv
import os
import uuid
router = APIRouter()
logger = logging.getLogger(__name__)


# 매장 리스트에서 모달창 띄우기
@router.post("/select/init/info", response_model=AdsInitInfo)
def select_ads_init_info(store_business_number: str):
    # 쿼리 매개변수로 전달된 store_business_number 값 수신
    try:
        data = service_select_ads_init_info(store_business_number)
        return data
    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex
    except Exception as e:
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)



# ADS 리스트 조회
@router.get("/select/list", response_model=List[AdsList])
def select_ads_list():
    try:
        # 서비스에서 데이터를 가져와 result 변수에 저장
        result: AdsList = service_select_ads_list()
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
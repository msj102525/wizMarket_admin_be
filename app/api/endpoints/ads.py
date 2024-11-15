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
    combine_ads as service_combine_ads
)
from pathlib import Path
import shutil
from typing import Optional
from dotenv import load_dotenv
import os
import uuid
router = APIRouter()
logger = logging.getLogger(__name__)


REPORT_PATH = Path(os.getenv("REPORT_PATH"))
IMAGE_DIR = Path(os.getenv("IMAGE_DIR"))
FULL_PATH = REPORT_PATH / IMAGE_DIR.relative_to("/") / "ads"

FULL_PATH.mkdir(parents=True, exist_ok=True)

# 매장 리스트에서 모달창 띄우기
@router.post("/select/init/info", response_model=AdsInitInfo)
def select_ads_init_info(store_business_number: str):
    print(store_business_number)
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
    

# ADS 텍스트, 이미지 합성
@router.post("/combine/image/text")
def combine_ads(
    store_business_number: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    store_name: str = Form(...),
    road_name: str = Form(...),
    city_name: str = Form(...),
    district_name: str = Form(...),
    sub_district_name: str = Form(...),
    detail_category_name: str = Form(...),
    loc_info_average_sales_k: str = Form(...),
    commercial_district_max_sales_day: Optional[str] = Form(None),
    commercial_district_max_sales_time: Optional[str] = Form(None),
    commercial_district_max_sales_m_age: Optional[str] = Form(None),
    commercial_district_max_sales_f_age: Optional[str] = Form(None),
    image: UploadFile = File(None)  # 단일 이미지 파일
):
    
    # 서비스 호출
    service_combine_ads(
        store_business_number, title, content, 
        store_name, road_name,
        city_name, district_name, sub_district_name,
        detail_category_name, loc_info_average_sales_k,
        commercial_district_max_sales_day, commercial_district_max_sales_time,
        commercial_district_max_sales_m_age, commercial_district_max_sales_f_age,
        image
    )

    # 응답 반환
    return {
        "store_business_number": store_business_number,
        "title": title,
        "content": content,
        "image_filename": image
    }
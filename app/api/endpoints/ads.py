from fastapi import (
    APIRouter, UploadFile, File, Form, HTTPException
)
from app.schemas.ads import (
    AdsList, AdsInitInfoOutPut,
    AdsGenerateContentOutPut, AdsContentRequest,
    AdsGenerateImageOutPut, AdsImageRequest
)
from fastapi import Request
from PIL import Image
import logging
from typing import List
from app.service.ads import (
    select_ads_list as service_select_ads_list,
    select_ads_init_info as service_select_ads_init_info,
    combine_ads as service_combine_ads,
    generate_content as service_generate_content,
    generate_image as service_generate_image
)
from pathlib import Path
from fastapi.responses import JSONResponse
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


# 매장 리스트에서 모달창 띄우기
@router.post("/select/init/info", response_model=AdsInitInfoOutPut)
def select_ads_init_info(store_business_number: str):
    # 쿼리 매개변수로 전달된 store_business_number 값 수신
    try:
        return service_select_ads_init_info(store_business_number)
    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex
    except Exception as e:
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    
    

# 모달창에서 문구 생성하기
@router.post("/generate/content", response_model=AdsGenerateContentOutPut)
def generate_content(request: AdsContentRequest):
    try:
        # 서비스 레이어 호출: 요청의 데이터 필드를 unpack
        data = service_generate_content(
            request.use_option,
            request.title,
            request.store_name, 
            request.road_name,
            request.city_name, 
            request.district_name, 
            request.sub_district_name,
            request.detail_category_name, 
            request.loc_info_average_sales_k,
            request.max_sales_day, 
            request.max_sales_day_value,
            request.max_sales_time, 
            request.max_sales_time_value,
            request.max_sales_male, 
            request.max_sales_male_value,
            request.max_sales_female, 
            request.max_sales_female_value
        )
        return {"content": data}  
    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex
    except Exception as e:
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)


# 모달창에서 이미지 생성하기
@router.post("/generate/image", response_model=AdsGenerateImageOutPut)
def generate_image(request: AdsImageRequest):
    try:
        print("이미지 생성")
        # 서비스 레이어 호출: 요청의 데이터 필드를 unpack
        data = service_generate_image(
            request.use_option,
            request.ai_model_option,
            request.title,
            request.store_name, 
            request.detail_category_name, 
        )
        return data
    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        raise http_ex
    except Exception as e:
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# ADS 텍스트, 이미지 합성
@router.post("/combine/image/text")
def combine_ads(
    store_name: str = Form(...),
    content: str = Form(...),
    image_width: int = Form(...),
    image_height: int = Form(...),
    image: UploadFile = File(...)
):
    # UploadFile -> Pillow.Image 변환
    try:
        pil_image = Image.open(image.file)
    except Exception as e:
        return {"error": f"Failed to open image: {str(e)}"}

    # 서비스 레이어 호출 (Base64 이미지 반환)
    base64_image = service_combine_ads(store_name, content, image_width, image_height, pil_image)

    # JSON 응답으로 Base64 이미지 반환
    return JSONResponse(content={"image": base64_image})
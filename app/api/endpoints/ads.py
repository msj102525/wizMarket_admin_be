from fastapi import (
    APIRouter, UploadFile, File, Form, HTTPException
)
from app.schemas.ads import (
    AdsList, AdsInitInfoOutPut, AdsListOutPut,
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
    generate_content as service_generate_content,
    generate_image as service_generate_image,
    combine_ads as service_combine_ads,
    combine_ads_ver1 as service_combine_ads_ver1,
    insert_ads as service_insert_ads
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
@router.get("/select/list", response_model=List[AdsListOutPut])
def select_ads_list():
    try:
        # 서비스에서 데이터를 가져와 result 변수에 저장
        result: AdsListOutPut = service_select_ads_list()
        # print(result)
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
        # 요청 정보 출력
        # logger.info(f"Request received from {request.client.host}:{request.client.port}")
        # logger.info(f"Request headers: {request.headers}")
        # logger.info(f"Request path: {request.url.path}")
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
            request.prompt,
            request.gpt_role,
            request.detail_content
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
        # 서비스 레이어 호출: 요청의 데이터 필드를 unpack
        data = service_generate_image(
            request.use_option,
            request.ai_model_option,
            request.ai_prompt,
        )
        return data
    except HTTPException as http_ex:
        logger.error(f"HTTP error occurred: {http_ex.detail}")
        print(f"HTTPException 발생: {http_ex.detail}")  # 추가 디버깅 출력
        raise http_ex
    except Exception as e:
        error_msg = f"Unexpected error while processing request: {str(e)}"
        logger.error(error_msg)
        print(f"Exception 발생: {error_msg}")  # 추가 디버깅 출력
        raise HTTPException(status_code=500, detail=error_msg)

# ADS 텍스트, 이미지 합성 템플릿 2개
# @router.post("/combine/image/text")
# def combine_ads(
#     store_name: str = Form(...),
#     road_name: str = Form(...),
#     content: str = Form(...),
#     image_width: int = Form(...),
#     image_height: int = Form(...),
#     image: UploadFile = File(...)
# ):
#     try:
#         pil_image = Image.open(image.file)
#     except Exception as e:
#         return {"error": f"Failed to open image: {str(e)}"}
#     # 서비스 레이어 호출 (Base64 이미지 반환)
#     image_1, image_2 = service_combine_ads(store_name, road_name, content, image_width, image_height, pil_image)
#     # JSON 응답으로 두 이미지를 반환
#     return JSONResponse(content={"images": [image_1, image_2]})

# ADS 텍스트, 이미지 합성
@router.post("/combine/image/text")
def combine_ads(
    store_name: str = Form(...),
    road_name: str = Form(...),
    content: str = Form(...),
    image_width: int = Form(...),
    image_height: int = Form(...),
    image: UploadFile = File(...)
):
    try:
        pil_image = Image.open(image.file)
    except Exception as e:
        return {"error": f"Failed to open image: {str(e)}"}
    # 서비스 레이어 호출 (Base64 이미지 반환)
    base64_image = service_combine_ads_ver1(store_name, road_name, content, image_width, image_height, pil_image)

    # JSON 응답으로 Base64 이미지 반환
    return JSONResponse(content={"image": base64_image})


# ADS DB에 저장
from fastapi import HTTPException, status

@router.post("/insert")
def insert_ads(
    store_business_number: str = Form(...),
    use_option: str = Form(...),
    title: str = Form(...),
    detail_title: Optional[str] = Form(None),  # 선택적 필드
    content: str = Form(...),
    image: UploadFile = File(None)  # 단일 이미지 파일
):
    # 이미지 파일 처리
    image_url = None
    try:
        if image:
            # 고유 이미지 명 생성
            filename, ext = os.path.splitext(image.filename)
            unique_filename = f"{filename}_jyes_{uuid.uuid4()}{ext}"

            # 파일 저장 경로 지정
            file_path = FULL_PATH / unique_filename

            # 파일 저장
            try:
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error saving image file: {str(e)}"
                )
            
            # 이미지 URL 생성
            image_url = f"/static/images/ads/{unique_filename}"

        # 데이터 저장 호출
        try:
            service_insert_ads(store_business_number, use_option, title, detail_title, content, image_url)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error inserting ad data: {str(e)}"
            )

    except HTTPException as http_exc:
        raise http_exc  # 이미 정의된 HTTPException은 그대로 전달
    except Exception as e:
        # 기타 예상치 못한 오류 처리
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

    # 성공 응답 반환
    return {
        "store_business_number": store_business_number,
        "use_option": use_option,
        "title": title,
        "detail_title": detail_title,
        "content": content,
        "image_filename": image_url
    }


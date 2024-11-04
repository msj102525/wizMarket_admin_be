from fastapi import (
    APIRouter, UploadFile, File, Form, HTTPException
)
from app.schemas.local_store_content import (
    LocStoreContentList,
    LocStoreCategoryList,
    StoreBusinessNumberListRequest,
    UpdatePublishStatusRequest,
    LocStoreDetailContentResponse,
    LocStoreDetailRequest
)
from fastapi import Request
import logging
from typing import List
from app.service.local_store_content import (
    insert_store_content as service_insert_store_content,
    select_loc_store_content_list as service_select_loc_store_content_list,
    select_loc_store_category as service_select_loc_store_category,
    update_loc_store_is_publish as service_update_loc_store_is_publish,
    select_loc_store_for_detail_content as service_select_loc_store_for_detail_content
)
from pathlib import Path
import shutil

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
IMAGE_DIR = BASE_DIR / "static/images/content"

# 신규 등록
@router.post("/insert_store_content_image")
def save_store_content(
    store_business_number: str = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    images: List[UploadFile] = File(None)  # 이미지 파일을 리스트로 받음, 최대 4장
):
    # 이미지 파일 처리
    image_urls = []
    if images:
        for image in images:
            # 파일 저장 경로 지정
            file_path = IMAGE_DIR / image.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            # 이미지 URL 생성 (예: "/static/images/content/filename.jpg")
            image_url = f"/static/images/content/{image.filename}"
            image_urls.append(image_url)

    service_insert_store_content(store_business_number, title, content, image_urls)

    # 예시 응답 데이터
    return {
        "store_business_number": store_business_number,
        "title": title,
        "content": content,
        "image_filenames": image_urls
    }



# 리스트 컨텐츠 정보 조회
@router.get("/select_loc_store_content_list", response_model=List[LocStoreContentList])
def get_store_content():
    try:
        # 서비스에서 데이터를 가져와 result 변수에 저장
        result: LocStoreContentList = service_select_loc_store_content_list()
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
    

# 업종 조회
@router.post("/select_loc_store_category", response_model=List[LocStoreCategoryList])
def get_store_category(request: StoreBusinessNumberListRequest):
    store_business_number_list = request.store_business_number_list
    try:
        # 서비스에서 데이터를 가져와 result 변수에 저장
        result = service_select_loc_store_category(store_business_number_list)
        return result  # result를 반환
    except Exception as e:
        # 예외 처리
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# 계시 여부 상태 변경
@router.post("/update_loc_store_is_publish")
def update_loc_store_is_publish(request: UpdatePublishStatusRequest):
    try:
        # 서비스 레이어를 통해 업데이트 작업 수행
        service_update_loc_store_is_publish(
            request.local_store_content_id,
            request.is_publish
        )
        return {"message": "Publish status updated successfully"}
    except Exception as e:
        # 예외 처리
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 상세 조회
@router.post("/select_loc_store_for_detail_content", response_model=LocStoreDetailContentResponse)
def select_loc_store_for_detail_content(request: LocStoreDetailRequest):
    local_store_content_id = request.local_store_content_id

    try:
        result = service_select_loc_store_for_detail_content(local_store_content_id)
        return result
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
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
    update_loc_store_content_status as service_update_loc_store_content_status,
    select_loc_store_for_detail_content as service_select_loc_store_for_detail_content,
    delete_loc_store_content_status as service_delete_loc_store_content_status,
    update_loc_store_content as service_update_loc_store_content
)
from pathlib import Path
import shutil
from typing import Optional
from dotenv import load_dotenv
import os
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

load_dotenv()

REPORT_PATH = Path(os.getenv("REPORT_PATH"))
IMAGE_DIR = Path(os.getenv("IMAGE_DIR"))
FULL_PATH = REPORT_PATH / IMAGE_DIR.relative_to("/") / "content"

FULL_PATH.mkdir(parents=True, exist_ok=True)

# 신규 등록
@router.post("/insert/content")
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
            # 고유 이미지 명 생성
            filename, ext = os.path.splitext(image.filename)
            unique_filename = f"{filename}_jyes_{uuid.uuid4()}{ext}"

            # 파일 저장 경로 지정
            file_path = FULL_PATH / unique_filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            # 이미지 URL 생성 (예: "/static/images/content/filename.jpg")
            image_url = f"/static/images/content/{unique_filename}"
            image_urls.append(image_url)
    print(image_urls)
    service_insert_store_content(store_business_number, title, content, image_urls)

    # 예시 응답 데이터
    return {
        "store_business_number": store_business_number,
        "title": title,
        "content": content,
        "image_filenames": image_urls
    }



# 리스트 컨텐츠 정보 조회
@router.get("/select/list", response_model=List[LocStoreContentList])
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
@router.post("/select/category", response_model=List[LocStoreCategoryList])
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


# 게시 여부 상태 변경
@router.post("/update/status")
def update_loc_store_content_status(request: UpdatePublishStatusRequest):
    try:
        # 서비스 레이어를 통해 업데이트 작업 수행
        service_update_loc_store_content_status(
            request.local_store_content_id,
            request.status
        )
        return {"message": "Publish status updated successfully"}
    except Exception as e:
        # 예외 처리
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 상세 조회
@router.post("/select/detail/content", response_model=LocStoreDetailContentResponse)
def select_loc_store_for_detail_content(request: LocStoreDetailRequest):
    local_store_content_id = request.local_store_content_id

    try:
        result = service_select_loc_store_for_detail_content(local_store_content_id)
        return result
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 게시글 삭제
@router.post("/delete/content")
def delete_loc_store_content_status(request: LocStoreDetailRequest):
    try:
        # 서비스 레이어를 통해 업데이트 작업 수행
        service_delete_loc_store_content_status(
            request.local_store_content_id,
        )
        return {"message": "Publish status updated successfully"}
    except Exception as e:
        # 예외 처리
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 게시글 수정
@router.post("/update/content")
async def update_loc_store_content(
    local_store_content_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    existing_images: str = Form("[]"),  
    new_images: List[UploadFile] = File(None)
):
    try:
        # 새로운 이미지가 있을 때 파일 저장 경로를 생성하여 URL 목록 작성
        existing_images = existing_images or []
        new_image_urls = []
        
        if new_images:
            for image in new_images:
                filename, ext = os.path.splitext(image.filename)
                unique_filename = f"{filename}_jyes_{uuid.uuid4()}{ext}"
                
                # 파일 저장 경로 지정
                file_path = FULL_PATH / unique_filename
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                
                # 이미지 URL 생성
                image_url = f"/static/images/content/{unique_filename}"
                new_image_urls.append(image_url)

        # 서비스 레이어 호출
        updated_item = service_update_loc_store_content(
            local_store_content_id=local_store_content_id,
            title=title,
            content=content,
            existing_images=existing_images,
            new_image_urls=new_image_urls
        )

        if not updated_item:
            raise HTTPException(status_code=404, detail="Content not found for updating")

        return updated_item

    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

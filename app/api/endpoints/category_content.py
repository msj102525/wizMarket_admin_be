from fastapi import (
    APIRouter, UploadFile, File, Form, HTTPException
)
import json
from app.schemas.category_content import (
    CategoryContentList,
    CategoryBizCategoryList,
    BizCategoryNumberListRequest,
    UpdatePublishStatusRequest,
    CategoryDetailContentResponse,
    CategoryDetailRequest
)
from fastapi import Request
from datetime import datetime
import logging
from typing import List
from app.service.category_content import (
    insert_category_content as service_insert_category_content,
    select_category_content_list as service_select_category_content_list,
    select_category_biz_category as service_select_category_biz_category,
    update_category_content_status as service_update_category_content_status,
    select_category_for_detail_content as service_select_category_for_detail_content,
    delete_category_content_status as service_delete_category_content_status,
    update_category_content as service_update_category_content
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
FULL_PATH = REPORT_PATH / IMAGE_DIR.relative_to("/") / "category"

FULL_PATH.mkdir(parents=True, exist_ok=True)

# 신규 등록
@router.post("/insert/content")
def insert_category_content(
    detail_category: int = Form(...),
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
            today = datetime.now().strftime("%Y%m%d")
            unique_filename = f"{filename}_jyes_category_content_{today}_{uuid.uuid4()}{ext}"
            # 파일 저장 경로 지정
            file_path = FULL_PATH / unique_filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
            
            # 이미지 URL 생성 (예: "/static/images/content/filename.jpg")
            image_url = f"/static/images/category/{unique_filename}"
            image_urls.append(image_url)

    insert_item = service_insert_category_content(detail_category, title, content, image_urls)

    return insert_item



# 리스트 컨텐츠 정보 조회
@router.get("/select/list", response_model=List[CategoryContentList])
def get_category_content():
    try:
        # 서비스에서 데이터를 가져와 result 변수에 저장
        result: CategoryContentList = service_select_category_content_list()
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
@router.post("/select/biz/category/list", response_model=List[CategoryBizCategoryList])
def get_category_biz_category(request: BizCategoryNumberListRequest):
    biz_category_number_list = request.biz_category_number_list

    try:
        # 서비스에서 데이터를 가져와 result 변수에 저장
        result = service_select_category_biz_category(biz_category_number_list)
        return result  # result를 반환
    except Exception as e:
        # 예외 처리
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# 게시 여부 상태 변경
@router.post("/update/status")
def update_category_content_status(request: UpdatePublishStatusRequest):
    try:
        # 서비스 레이어를 통해 업데이트 작업 수행
        service_update_category_content_status(
            request.biz_detail_category_content_id,
            request.status
        )
        return {"message": "Publish status updated successfully"}
    except Exception as e:
        # 예외 처리
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 상세 조회
@router.post("/select/detail/content", response_model=CategoryDetailContentResponse)
def select_category_for_detail_content(request: CategoryDetailRequest):
    biz_detail_category_content_id = request.biz_detail_category_content_id
    try:
        result = service_select_category_for_detail_content(biz_detail_category_content_id)
        return result
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 게시글 삭제
@router.post("/delete/content")
def delete_loc_store_content_status(request: CategoryDetailRequest):
    try:
        # 서비스 레이어를 통해 업데이트 작업 수행
        service_delete_category_content_status(
            request.biz_detail_category_content_id,
        )
        return {"message": "Publish status updated successfully"}
    except Exception as e:
        # 예외 처리
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 게시글 수정
@router.post("/update/content")
async def update_loc_store_content(
    biz_detail_category_content_id: int = Form(...),
    title: str = Form(...),
    content: str = Form(...),
    existing_images: str = Form("[]"),  # 기존 이미지를 문자열로 받아 JSON 디코딩
    new_images: List[UploadFile] = File(None)
):
    try:
        # 새로운 이미지가 있을 때 파일 저장 경로를 생성하여 URL 목록 작성
        existing_images = existing_images or []
        new_image_urls = []
        if new_images:
            for image in new_images:
                # 고유한 파일명 생성
                filename, ext = os.path.splitext(image.filename)
                today = datetime.now().strftime("%Y%m%d")
                unique_filename = f"{filename}_jyes_category_content_{today}_{uuid.uuid4()}{ext}"
                file_path = FULL_PATH / unique_filename
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)
                image_url = f"/static/images/category/{unique_filename}"
                new_image_urls.append(image_url)

        # 서비스 레이어 호출
        updated_item = service_update_category_content(
            biz_detail_category_content_id=biz_detail_category_content_id,
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
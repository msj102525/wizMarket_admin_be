from typing import List
from app.crud.local_store_content import (
    insert_store_content as crud_insert_store_content,
    select_loc_store_content_list as crud_select_loc_store_content_list,
    select_loc_store_category as crud_select_loc_store_category,
    update_loc_store_content_status as crud_update_loc_store_content_status,
    select_loc_store_for_detail_content as crud_select_loc_store_for_detail_content,
    delete_loc_store_content_status as crud_delete_loc_store_content_status,
    update_loc_store_content as crud_update_loc_store_content,
    select_loc_store_existing_image as crud_select_loc_store_existing_image,
    delete_loc_store_existing_image as crud_delete_loc_store_existing_image,
    insert_loc_store_new_image as crud_insert_loc_store_new_image

)
from app.crud.local_store_content_image import(
    insert_store_content_image as crud_insert_store_content_image
)
from fastapi import HTTPException
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


# 추가 정보 저장
def insert_store_content(
    store_business_number : str, title : str, content : str, image_urls : List[str]
):
    # 글 먼저 저장
    store_content_pk = crud_insert_store_content(store_business_number, title, content)

    # 글 pk 로 이미지 저장
    crud_insert_store_content_image(store_content_pk, image_urls)


# 추가 정보 불러오기
def select_loc_store_content_list():

    try:
        return crud_select_loc_store_content_list()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service loc_store_content_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service loc_store_content_list Error: {str(e)}"
        )
    

# 업종 조회
def select_loc_store_category(store_business_number_list: List[str]):
    results = []
    try:
        for store_business_number in store_business_number_list:
            # 각 store_business_number에 대해 CRUD 레이어 호출
            result = crud_select_loc_store_category(store_business_number)
            results.append(result)  # 각 결과를 results 리스트에 추가
        return results
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Service loc_store_content_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service loc_store_content_list Error: {str(e)}"
        )

# 게시 여부 상태 변경
def update_loc_store_content_status(local_store_content_id: int, status: str):
    try:
        # CRUD 레이어에 값을 전달하여 업데이트 작업 수행
        success = crud_update_loc_store_content_status(local_store_content_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="Content not found for updating")
    except Exception as e:
        print(f"Service error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 글 상세 조회
def select_loc_store_for_detail_content(local_store_content_id: int):
    try:
        result = crud_select_loc_store_for_detail_content(local_store_content_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Service loc_store_content_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service loc_store_content_list Error: {str(e)}"
        )
    
# 게시글 삭제
def delete_loc_store_content_status(local_store_content_id: int):
    try:
        # CRUD 레이어에 값을 전달하여 업데이트 작업 수행
        success = crud_delete_loc_store_content_status(local_store_content_id)
        if not success:
            raise HTTPException(status_code=404, detail="Content not found for updating")
    except Exception as e:
        print(f"Service error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 게시글 수정
load_dotenv()

REPORT_PATH = Path(os.getenv("REPORT_PATH"))
IMAGE_DIR = Path(os.getenv("IMAGE_DIR"))
FULL_PATH = REPORT_PATH / IMAGE_DIR.relative_to("/") / "content"


def update_loc_store_content(local_store_content_id: int, title: str, content: str, existing_images: List[str], new_image_urls: List[bytes]):
    try:
        # 1. 제목, 글은 무조건 update
        updated_item = crud_update_loc_store_content(local_store_content_id, title, content)
        
        # 2. 이미지
        # current_images에서 URL만 추출
        current_image_urls = [img.local_store_image_url for img in crud_select_loc_store_existing_image(local_store_content_id)]
        
        # 2-1. 기존 이미지 삭제 되었을 경우
        images_to_delete = [img for img in current_image_urls if img not in existing_images]
        if images_to_delete:
            for image_url in images_to_delete:
                # 파일 시스템에서 이미지 파일 삭제
                file_path = FULL_PATH / image_url.split("/")[-1]  # 이미지 파일 경로 추출
                if os.path.exists(file_path):
                    os.remove(file_path)
            # DB 에서 삭제
            crud_delete_loc_store_existing_image(local_store_content_id, images_to_delete)

        # 2-2. 새로 이미지 추가 됬었을 경우
        if new_image_urls:
            crud_insert_loc_store_new_image(local_store_content_id, new_image_urls)

        return updated_item

    except Exception as e:
        print(f"Service error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

from typing import List

from app.schemas.category_content import CategoryContentListOutPut
from app.crud.category_content import (
    insert_category_content as crud_insert_category_content,
    select_category_content_list as crud_select_category_content_list,
    select_category_biz_category as crud_select_category_biz_category,
    update_category_content_status as crud_update_category_content_status,
    select_category_for_detail_content as crud_select_category_for_detail_content,
    delete_category_content_status as crud_delete_category_content_status,
    update_category_content as crud_update_category_content,
    select_category_existing_image as crud_select_category_existing_image,
    delete_category_existing_image as crud_delete_category_existing_image,
    insert_category_new_image as crud_insert_category_new_image,
    select_category_image_list as crud_select_category_image_list

)
from app.crud.category_content_image import(
    insert_category_content_image as crud_insert_category_content_image
)
from fastapi import HTTPException
import logging
import os
from pathlib import Path
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


def insert_category_content(
    detail_category: int, title: str, content: str, image_urls: List[str]
):
    # 글 먼저 저장하고, category_content_pk와 created_at 값을 반환받음
    insert_item = crud_insert_category_content(detail_category, title, content)
    ##### print(insert_item) # 가상서버 깃 감지 테스트용
    category_content_pk = insert_item.biz_detail_category_content_id
    status = insert_item.status
    created_at = insert_item.created_at

    # 글 pk로 이미지 저장
    crud_insert_category_content_image(category_content_pk, image_urls)

    insert_item = {
        "biz_detail_category_content_id": category_content_pk,
        "detail_category_id": detail_category,
        "title": title,
        "content": content,
        "status": status,
        "created_at": created_at, 
        "images": image_urls
    }
    return insert_item


# 컨텐츠 정보 리스트 불러오기
def select_category_content_list():
    try:
        category_content_list = crud_select_category_content_list()
        result_list = []

        # 각 카테고리에 대한 이미지 조회 및 합치기
        for category in category_content_list:
            # 이미지 리스트 대신 하나의 이미지만 가져오기
            category_content_image = crud_select_category_image_list(category.biz_detail_category_content_id)
            
            # 이미지가 있는 경우
            if category_content_image:
                result_list.append(
                    CategoryContentListOutPut(
                        biz_detail_category_content_id=category.biz_detail_category_content_id,
                        detail_category_id=category.detail_category_id,
                        status=category.status,
                        title=category.title,
                        content=category.content,
                        created_at=category.created_at,
                        biz_detail_category_content_image_id=category_content_image.biz_detail_category_content_image_id,
                        biz_detail_category_content_image_url=category_content_image.biz_detail_category_content_image_url,
                    )
                )
            else:
                # 이미지가 없는 경우에도 추가
                result_list.append(
                    CategoryContentListOutPut(
                        biz_detail_category_content_id=category.biz_detail_category_content_id,
                        detail_category_id=category.detail_category_id,
                        status=category.status,
                        title=category.title,
                        content=category.content,
                        created_at=category.created_at,
                    )
                )
        # print(result_list)
        return result_list

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service category_content_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service category_content_list Error: {str(e)}"
        )


    

# 업종 조회
def select_category_biz_category(biz_category_number_list: List[int]):
    results = []
    try:
        for biz_category_number in biz_category_number_list:
            # 각 store_business_number에 대해 CRUD 레이어 호출
            result = crud_select_category_biz_category(biz_category_number)
            results.append(result)  # 각 결과를 results 리스트에 추가
        return results
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Service category_content_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service category_content_list Error: {str(e)}"
        )

# 게시 여부 상태 변경
def update_category_content_status(biz_detail_category_content_id: int, status: str):
    try:
        # CRUD 레이어에 값을 전달하여 업데이트 작업 수행
        success = crud_update_category_content_status(biz_detail_category_content_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="Content not found for updating")
    except Exception as e:
        print(f"Service error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 글 상세 조회
def select_category_for_detail_content(biz_detail_category_content_id: int):
    try:
        result = crud_select_category_for_detail_content(biz_detail_category_content_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Service category_content_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service category_content_list Error: {str(e)}"
        )
    
# 게시글 삭제
def delete_category_content_status(biz_detail_category_content_id: int):
    try:
        # CRUD 레이어에 값을 전달하여 업데이트 작업 수행
        success = crud_delete_category_content_status(biz_detail_category_content_id)
        if not success:
            raise HTTPException(status_code=404, detail="Content not found for updating")
    except Exception as e:
        print(f"Service error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# 게시글 수정
def update_category_content(biz_detail_category_content_id: int, title: str, content: str, existing_images: List[str], new_image_urls: List[bytes]):
    try:
        # 1. 제목, 글은 무조건 update
        updated_item = crud_update_category_content(biz_detail_category_content_id, title, content)

        # 2. 이미지
        # current_images에서 URL만 추출
        current_image_urls = [img.biz_detail_category_content_image_url for img in crud_select_category_existing_image(biz_detail_category_content_id)]

        # 2-1. 기존 이미지 삭제 되었을 경우
        images_to_delete = [img for img in current_image_urls if img not in existing_images]
        if images_to_delete:
            # 데이터베이스에서 이미지 URL 삭제
            crud_delete_category_existing_image(biz_detail_category_content_id, images_to_delete)

        # 2-2. 새로 이미지 추가 됬었을 경우
        if new_image_urls:
            crud_insert_category_new_image(biz_detail_category_content_id, new_image_urls)

        return updated_item

    except Exception as e:
        print(f"Service error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

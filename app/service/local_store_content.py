from typing import List
from app.crud.local_store_content import (
    insert_store_content as crud_insert_store_content,
    select_loc_store_content_list as crud_select_loc_store_content_list,
    select_loc_store_category as crud_select_loc_store_category,
    update_loc_store_is_publish as crud_update_loc_store_is_publish,
    select_loc_store_for_detail_content as crud_select_loc_store_for_detail_content
)
from app.crud.local_store_content_image import(
    insert_store_content_image as crud_insert_store_content_image
)
from fastapi import HTTPException
import logging

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

# 계시 여부 상태 변경
def update_loc_store_is_publish(local_store_content_id: int, is_publish: bool):
    try:
        # CRUD 레이어에 값을 전달하여 업데이트 작업 수행
        success = crud_update_loc_store_is_publish(local_store_content_id, is_publish)
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
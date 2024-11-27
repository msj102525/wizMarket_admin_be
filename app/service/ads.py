from app.crud.ads import (
    select_ads_list as crud_select_ads_list,
    select_ads_image_list as crud_select_ads_image_list,
    update_ads_status as crud_update_ads_status,
    select_filters_list as crud_select_filters_list
)
from app.schemas.ads import(
    AdsListOutPut
)
from fastapi import HTTPException
import logging
import os
from dotenv import load_dotenv
from openai import OpenAI



logger = logging.getLogger(__name__)
load_dotenv()

# OpenAI API 키 설정
api_key = os.getenv("GPT_KEY")
client = OpenAI(api_key=api_key)


# ADS 리스트 조회
def select_ads_list():
    try:
        ads_list = crud_select_ads_list()  # 광고 리스트 조회

        # 최종 반환 리스트
        result_list = []

        # ads_id별 이미지 리스트 조회 및 합치기
        for ads in ads_list:
            # print(ads.ads_id)
            ads_image_list = crud_select_ads_image_list(ads.ads_id)  # ads_id로 이미지 조회
            # print(ads_image_list)
            # 이미지 리스트를 순회하며 AdsListOutPut 형태로 변환
            for image in ads_image_list:
                result_list.append(
                    AdsListOutPut(
                        ads_id=ads.ads_id,
                        store_business_number=ads.store_business_number,
                        store_name=ads.store_name,
                        road_name=ads.road_name,
                        status=ads.status,
                        use_option=ads.use_option,
                        title=ads.title,
                        detail_title=ads.detail_title,
                        content=ads.content,
                        created_at=ads.created_at,
                        ads_image_id=image.ads_image_id,
                        ads_image_url=image.ads_image_url,
                        ads_final_image_url=image.ads_final_image_url,
                    )
                )

        # 광고에 이미지가 없는 경우도 추가
        for ads in ads_list:
            if not any(out.ads_id == ads.ads_id for out in result_list):
                result_list.append(
                    AdsListOutPut(
                        ads_id=ads.ads_id,
                        store_business_number=ads.store_business_number,
                        store_name=ads.store_name,
                        road_name=ads.road_name,
                        status=ads.status,
                        use_option=ads.use_option,
                        title=ads.title,
                        detail_title=ads.detail_title,
                        content=ads.content,
                        created_at=ads.created_at,
                    )
                )
        return result_list
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service ads_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service ads_list Error: {str(e)}"
        )



# 게시 여부 상태 변경
def update_ads_status(ads_id: int, status: str):
    try:
        # CRUD 레이어에 값을 전달하여 업데이트 작업 수행
        success = crud_update_ads_status(ads_id, status)
        if not success:
            raise HTTPException(status_code=404, detail="Content not found for updating")
    except Exception as e:
        print(f"Service error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    

# 필터 조회
def select_filters_list(filters):
    try:
        ads_list = crud_select_filters_list(filters)  # 광고 리스트 조회
        # 최종 반환 리스트
        result_list = []
        # ads_id별 이미지 리스트 조회 및 합치기
        for ads in ads_list:
            # print(ads.ads_id)
            ads_image_list = crud_select_ads_image_list(ads.ads_id)  # ads_id로 이미지 조회
            # print(ads_image_list)
            # 이미지 리스트를 순회하며 AdsListOutPut 형태로 변환
            for image in ads_image_list:
                result_list.append(
                    AdsListOutPut(
                        ads_id=ads.ads_id,
                        store_business_number=ads.store_business_number,
                        store_name=ads.store_name,
                        road_name=ads.road_name,
                        status=ads.status,
                        use_option=ads.use_option,
                        title=ads.title,
                        detail_title=ads.detail_title,
                        content=ads.content,
                        created_at=ads.created_at,
                        ads_image_id=image.ads_image_id,
                        ads_image_url=image.ads_image_url,
                    )
                )

        # 광고에 이미지가 없는 경우도 추가
        for ads in ads_list:
            if not any(out.ads_id == ads.ads_id for out in result_list):
                result_list.append(
                    AdsListOutPut(
                        ads_id=ads.ads_id,
                        store_business_number=ads.store_business_number,
                        store_name=ads.store_name,
                        road_name=ads.road_name,
                        status=ads.status,
                        use_option=ads.use_option,
                        title=ads.title,
                        detail_title=ads.detail_title,
                        content=ads.content,
                        created_at=ads.created_at,
                    )
                )
        return result_list
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service ads_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service ads_list Error: {str(e)}"
        )
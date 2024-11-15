from typing import List
from app.crud.ads import (
    select_ads_list as crud_select_ads_list,
    select_ads_init_info as crud_select_ads_init_info
)
from app.schemas.ads import(
    AdsInitInfoOutPut
)

from fastapi import HTTPException
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


# ADS 리스트 조회
def select_ads_list():
    try:
        return crud_select_ads_list()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service loc_store_content_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service loc_store_content_list Error: {str(e)}"
        )

# 초기 데이터 가져오기
def select_ads_init_info(
    store_business_number:str
) -> AdsInitInfoOutPut:
    
    results = crud_select_ads_init_info(store_business_number)
    if not results:
        raise HTTPException(status_code=404, detail="report loc_info not found")
    return results
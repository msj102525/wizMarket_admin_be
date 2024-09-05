from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.biz_main_category import BizMainCategory
from service.biz_main_category import (
    get_all_biz_main_category as service_get_all_biz_main_category,
)

router = APIRouter()

@router.get("", response_model=List[BizMainCategory])
def get_all_biz_main_category():
    try:
        results = service_get_all_biz_main_category()
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

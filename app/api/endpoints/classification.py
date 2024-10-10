from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.schemas.biz_detail_category import BizDetailCategoryOutput
from app.schemas.biz_main_category import BizMainCategoryOutput
from app.schemas.biz_sub_category import BizSubCategoryOutput
from app.service.classification import (
    get_all_classification_main_category as service_get_all_classification_main_category,
    get_all_classification_sub_category_by_main_category_code as service_get_all_classification_sub_category_by_main_category_code,
    get_all_classification_detail_category_by_sub_category_code as service_get_all_classification_detail_category_by_sub_category_code,
)

router = APIRouter()


@router.get("", response_model=List[BizMainCategoryOutput])
def get_all_classification_main_category(
    reference_id: int = Query(True),
):
    try:
        results = service_get_all_classification_main_category(reference_id)
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/sub", response_model=List[BizSubCategoryOutput])
def get_all_classification_sub_category_by_biz_main_category_id(
    main_category_code: str = Query(True),
):
    try:
        results = service_get_all_classification_sub_category_by_main_category_code(
            main_category_code
        )
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/detail", response_model=List[BizDetailCategoryOutput])
def get_all_classification_detail_category_by_sub_category_code(
    sub_category_code: int = Query(True),
):
    # print(f"endpoint/detail: {sub_category_code}")
    try:
        results = service_get_all_classification_detail_category_by_sub_category_code(
            sub_category_code
        )
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

from typing import List
from fastapi import HTTPException

from app.crud.classification import (
    get_all_classification_main_category as crud_get_all_classification_main_category,
    get_all_classification_sub_category_by_main_category_code as crud_get_all_classification_sub_category_by_main_category_code,
    get_all_classification_detail_category_by_sub_category_code as crud_get_all_classification_detail_category_by_sub_category_code,
)
from app.schemas.biz_main_category import BizMainCategoryOutput
from app.schemas.biz_sub_category import BizSubCategoryOutput


def get_all_classification_main_category(
    reference_id: int,
) -> List[BizMainCategoryOutput]:
    results = []
    results = crud_get_all_classification_main_category(reference_id)
    if not results:
        raise HTTPException(status_code=404, detail="Business main category not found")
    return results


def get_all_classification_sub_category_by_main_category_code(
    main_category_code: str,
) -> List[BizSubCategoryOutput]:
    results = []
    results = crud_get_all_classification_sub_category_by_main_category_code(
        main_category_code
    )
    if not results:
        raise HTTPException(status_code=404, detail="Business main category not found")
    return results


def get_all_classification_detail_category_by_sub_category_code(
    sub_category_code: int,
) -> List[BizSubCategoryOutput]:
    results = []
    results = crud_get_all_classification_detail_category_by_sub_category_code(
        sub_category_code
    )
    if not results:
        raise HTTPException(status_code=404, detail="Business main category not found")
    return results

from typing import List
from fastapi import HTTPException

from app.crud.biz_main_category import (
    get_all_main_category as crud_get_all_main_category,
)
from app.schemas.biz_main_category import BizMainCategoryOutput


def get_all_biz_main_category(reference_id: int) -> List[BizMainCategoryOutput]:
    results = []
    results = crud_get_all_main_category(reference_id)
    if not results:
        raise HTTPException(status_code=404, detail="Business main category not found")
    return results

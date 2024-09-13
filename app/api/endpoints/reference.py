from fastapi import APIRouter, HTTPException
from typing import List

from app.schemas.reference import Reference, ReferenceCategoryCountOutput
from app.service.reference import get_all_reference as service_get_all_reference


router = APIRouter()


@router.get("", response_model=List[ReferenceCategoryCountOutput])
def get_all_biz_main_category():
    try:
        results = service_get_all_reference()
        print(f"end: {results}")

        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

from fastapi import APIRouter, HTTPException, Query
from typing import List

from app.schemas.common_information import CommonInformation
from app.service.common_information import (
    get_all_report_common_information as service_get_all_report_common_information,
)

router = APIRouter()


@router.get("/info/common", response_model=List[CommonInformation])
def get_all_report_common_information():
    try:
        results = service_get_all_report_common_information()
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

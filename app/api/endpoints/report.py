from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.schemas.common_information import CommonInformationOutput
from app.service.common_information import (
    get_all_report_common_information as service_get_all_report_common_information,
)

router = APIRouter()


# @router.get("/rising", response_model=List[CommonInformationOutput])
@router.get("/rising")
def get_all_report_common_information(storeBusinessNumber: str):
    try:
        print(storeBusinessNumber)
        results = "rising"
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/info/common", response_model=List[CommonInformationOutput])
def get_all_report_common_information():
    try:
        results = service_get_all_report_common_information()
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")

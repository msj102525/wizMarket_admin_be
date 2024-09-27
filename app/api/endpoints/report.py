from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.service.common_information import (
    get_all_report_common_information as service_get_all_report_common_information,
)
from app.service.rising_business import (
    select_top3_rising_business_by_store_business_number as service_select_top3_rising_business_by_store_business_number,
    select_top5_rising_business as service_select_top5_rising_business,
)

from app.schemas.common_information import CommonInformationOutput
from app.schemas.rising_business import (
    RisingBusinessNationwideTop5AndSubDistrictTop3,
    RisingBusinessOutput,
)


router = APIRouter()


@router.get("/rising", response_model=RisingBusinessNationwideTop5AndSubDistrictTop3)
def select_top5_rising_business(store_business_id: str):
    try:
        nationwide_top5: List[RisingBusinessOutput] = (
            service_select_top5_rising_business()
        )

        sub_district_top3_data: List[RisingBusinessOutput] = (
            service_select_top3_rising_business_by_store_business_number(
                store_business_id
            )
        )

        result = RisingBusinessNationwideTop5AndSubDistrictTop3(
            nationwide_top5=nationwide_top5,
            sub_district_top3_data=sub_district_top3_data,
        )

        return result

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

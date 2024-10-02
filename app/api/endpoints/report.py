from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional

from app.schemas.population import PopulationJScoreOutput, PopulationOutput
from app.schemas.statistics import LocInfoStatisticsDataRefOutput, LocInfoStatisticsOutput
from app.service.common_information import (
    get_all_report_common_information as service_get_all_report_common_information,
)
from app.service.loc_info import (
    select_report_loc_info_by_store_business_number as service_select_report_loc_info_by_store_business_number,
)
from app.service.population import (
    select_report_population_by_store_business_number as service_select_report_population_by_store_business_number,
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


@router.get("/info/common", response_model=List[CommonInformationOutput])
def get_all_report_common_information():
    try:
        results = service_get_all_report_common_information()
        return results
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/rising", response_model=RisingBusinessNationwideTop5AndSubDistrictTop3)
def select_rising_business_top5_top3(store_business_id: str):
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


@router.get("/population", response_model=PopulationJScoreOutput)
def select_population_report_data(store_business_id: str):
    try:
        sub_district_population_data = (
            service_select_report_population_by_store_business_number(store_business_id)
        )

        return sub_district_population_data

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}Internal Server Error")


@router.get("/location/info", response_model=LocInfoStatisticsDataRefOutput)
def select_loc_info_report_data(store_business_id: str):
    # print(store_business_id)
    try:
        sub_district_population_data = (
            service_select_report_loc_info_by_store_business_number(store_business_id)
        )

        return sub_district_population_data

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}Internal Server Error")

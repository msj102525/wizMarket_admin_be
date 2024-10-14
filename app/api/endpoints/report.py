from fastapi import APIRouter, HTTPException
from typing import List, Optional
import requests

from app.schemas.loc_store import LocalStoreInfo, LocalStoreInfoWeaterInfo, WeatherInfo
from app.schemas.population import PopulationJScoreOutput, PopulationOutput
from app.schemas.statistics import (
    LocInfoAvgJscoreOutput,
    LocInfoStatisticsDataRefOutput,
    LocInfoStatisticsOutput,
    PopulationCompareResidentWorkPop,
)
from app.service.common_information import (
    get_all_report_common_information as service_get_all_report_common_information,
)
from app.service.loc_info import (
    select_report_loc_info_by_store_business_number as service_select_report_loc_info_by_store_business_number,
)
from app.service.loc_store import (
    get_lat_lng_by_store_business_id as service_get_lat_lng_by_store_business_id,
    get_report_store_info_by_store_business_id as service_get_report_store_info_by_store_business_id,
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
from app.service.statistics import (
    fetch_living_env as service_fetch_living_env,
    select_avg_j_score as service_select_avg_j_score,
)


router = APIRouter()


router = APIRouter()


@router.get("/store/info", response_model=LocalStoreInfoWeaterInfo)
def get_report_store_info(store_business_id: str):
    try:
        results = service_get_report_store_info_by_store_business_id(store_business_id)

        location = service_get_lat_lng_by_store_business_id(store_business_id)
        lat = location.latitude
        lng = location.longitude
        lang = "kr"

        print(lat, lng)

        apikey = "c6cf8cca80cf321d319d6eb75d11e8ce"
        api = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={apikey}&lang={lang}&units=metric"

        result = requests.get(api)

        if result.status_code != 200:
            raise HTTPException(
                status_code=result.status_code,
                detail=f"Weather API Error: {result.text}",
            )

        weather_data = result.json()

        print(weather_data)

        weather_info = WeatherInfo(
            icon=weather_data["weather"][0]["icon"], temp=weather_data["main"]["temp"]
        )

        response_data = LocalStoreInfoWeaterInfo(
            localStoreInfo=results, weatherInfo=weather_info
        )

        return response_data

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/common/info", response_model=List[CommonInformationOutput])
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


@router.get("/location/average/jscore", response_model=LocInfoAvgJscoreOutput)
def select_loc_info_avg_j_score(store_business_id: str):
    # print(store_business_id)
    try:
        loc_info_avg_j_score = service_select_avg_j_score(store_business_id)

        # print(loc_info_avg_j_score)

        return loc_info_avg_j_score

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}Internal Server Error")


@router.get("/population/compare", response_model=PopulationCompareResidentWorkPop)
def select_population_compare_resident_work(store_business_id: str):
    # print(store_business_id)
    try:
        compare_resident_work_data = service_fetch_living_env(store_business_id)

        # print(loc_info_avg_j_score)

        return compare_resident_work_data

    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"{e}Internal Server Error")

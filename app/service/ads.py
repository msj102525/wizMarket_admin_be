from typing import List
from app.crud.ads import (
    select_ads_list as crud_select_ads_list,
    select_ads_init_info as crud_select_ads_init_info
)
from app.schemas.ads import(
    AdsInitInfoOutPut, AdsInitInfo
)
from openai import OpenAI
from fastapi import HTTPException
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import requests


logger = logging.getLogger(__name__)
load_dotenv()

# OpenAI API 키 설정
api_key = os.getenv("GPT_KEY")
client = OpenAI(api_key=api_key)


# ADS 리스트 조회
def select_ads_list():
    try:
        return crud_select_ads_list()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service loc_store_content_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service loc_store_content_list Error: {str(e)}"
        )

# 초기 데이터 가져오기
def select_ads_init_info(
    store_business_number:str
) -> AdsInitInfo:
    
    results = crud_select_ads_init_info(store_business_number)
    if not results:
        raise HTTPException(status_code=404, detail="ads init data not found")
    return results

def combine_ads(
    store_business_number, title, content, 
    store_name, road_name,
    city_name, district_name, sub_district_name,
    detail_category_name, loc_info_average_sales_k,
    commercial_district_max_sales_day, commercial_district_max_sales_time,
    commercial_district_max_sales_m_age, commercial_district_max_sales_f_age,
    image
):
   
    # 문자열 포매팅 방식 (추천)
    full_region = f"{city_name} {district_name} {sub_district_name}"

    # gpt 영역
    gpt_content = """
        당신은 광고 카피라이터입니다. 
        입력된 매장의 정보를 통해 매장의 특징을 간단히 분석해주고 
        주제에 맞게 호기심을 끌고 매장을 잘 표현한 매장 슬로건을 3개 작성해주세요.
    """    

    content = f"""
        주제 : {title}
        가게명 : {store_name}
        업종 : {detail_category_name}
        주소 : {road_name}
        {full_region}의 평균 월 매출 : {loc_info_average_sales_k} * k
        {full_region}의 매출이 가장 높은 요일 : {commercial_district_max_sales_day}
        {full_region}의 매출이 가장 높은 시간대 : {commercial_district_max_sales_time}
        {full_region}의 매출이 가장 높은 남자 연령대 : {commercial_district_max_sales_m_age}
        {full_region}의 매출이 가장 높은 여자 연령대 : {commercial_district_max_sales_f_age}

    """

    client = OpenAI(api_key=os.getenv("GPT_KEY"))

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": gpt_content},
            {"role": "user", "content": content},
        ],
    )
    report = completion.choices[0].message.content

    return report

if __name__ == "__main__":
    pass
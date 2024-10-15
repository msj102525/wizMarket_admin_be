import pandas as pd
import os
from dotenv import load_dotenv
from app.db.connect import *
from app.crud.crime import *
from app.schemas.crime import CrimeRequest
from app.crud.loc_store import (
    select_local_store_by_store_business_number, select_business_area_category_id_by_reference_id, select_biz_detail_category_id_by_detail_category_id,
    select_rising_menu_by_sub_district_id_rep_id, select_categories_name_by_rep_id
)
from app.crud.loc_info import select_local_info_statistics_by_sub_district_id
from app.crud.population import select_age_pop_list_by_sub_district_id, select_gender_pop_list_by_sub_district_id
import openai
from dotenv import load_dotenv
import openai
from datetime import datetime, timezone, timedelta

gpt_content = """
    당신은 전문 조언자입니다. 
    귀하의 역할은 사용자의 질문을 분석하고, 주요 측면을 식별하고, 질문의 맥락을 기반으로 운영 지침과 통찰력을 제공하는 것입니다. 
    접근 방식을 최적화하는 데 도움이 되는 전략이나 솔루션을 제공합니다.
"""


# 프롬프트에 전달 할 지역의 정보 가져오기
def get_region_info(store_business_id):

    ########## 입지 정보 관련 정보 ##########
    # 1. 전달받은 건물 관리 번호로 지역 명 및 카테고리 조회
    region = select_local_store_by_store_business_number(store_business_id)
    sub_district_id = region.get('SUB_DISTRICT_ID')
    city_name = region.get('CITY_NAME')
    district_name = region.get('DISTRICT_NAME')
    sub_district_name = region.get('SUB_DISTRICT_NAME')
    region_name = region.get('CITY_NAME', '') + ' ' + region.get('DISTRICT_NAME', '') + ' ' + region.get('SUB_DISTRICT_NAME')
    large_category_name = region.get('LARGE_CATEGORY_NAME')
    medium_category_name = region.get('MEDIUM_CATEGORY_NAME')
    small_category_name = region.get('SMALL_CATEGORY_NAME')
    category_name = region.get('LARGE_CATEGORY_NAME', '') + '>' + region.get('MEDIUM_CATEGORY_NAME', '') + '>' + region.get('SMALL_CATEGORY_NAME')
    store_name = region.get('STORE_NAME')
    reference_id = region.get('REFERENCE_ID')

    # 2. 지역 id 값으로 입지 정보 값 및 통계 값 조회 후 쌍으로 묶기
    loc_info_result, statistics_result = select_local_info_statistics_by_sub_district_id(sub_district_id)

    # loc_info와 statistics 데이터 추출
    loc_info = loc_info_result[1]  # LocInfoResult 객체 추출
    statistics = statistics_result[1]  # StatisticsResult 리스트 추출

    # 각각 변수에 할당
    shop = loc_info.shop
    shop_jscore = statistics[0].j_score
    move_pop = loc_info.move_pop
    move_pop_jscore = statistics[1].j_score
    sales = loc_info.sales
    sales_jscore = statistics[2].j_score
    work_pop = loc_info.work_pop
    work_pop_jscore = statistics[3].j_score
    income = loc_info.income
    income_jscore = statistics[4].j_score
    spend = loc_info.spend
    spend_jscore = statistics[5].j_score
    house = loc_info.house
    house_jscore = statistics[6].j_score
    resident = loc_info.resident
    resident_jscore = statistics[7].j_score

    # 3. 연령 별 인구 조회
    age_pop_list = select_age_pop_list_by_sub_district_id(sub_district_id)
    age_under_10 = age_pop_list['age_under_10']
    age_10s = age_pop_list['age_10s']
    age_20s = age_pop_list['age_20s']
    age_30s = age_pop_list['age_30s']
    age_40s = age_pop_list['age_40s']
    age_50s = age_pop_list['age_50s']
    age_60_plus = age_pop_list['age_60_plus']

    # 4. 성별 인구 조회
    gender_pop_list = select_gender_pop_list_by_sub_district_id(sub_district_id)
    male_population = gender_pop_list[0]['male_population']
    female_population = gender_pop_list[1]['female_population']
    total_population = male_population + female_population
    male_percentage = int((male_population / total_population) * 100)
    female_percentage = int((female_population / total_population) * 100)

    ########## ~ 매장에서 가장 많이 주문하는 메뉴 관련 정보 ##########
    # 1. 상권 정보의 카테고리 값으로 상권정보 분류표의 pk 값 가져오기
    business_area_category = select_business_area_category_id_by_reference_id(reference_id, small_category_name)
    business_area_category_id = business_area_category.business_area_category_id

    # 2. pk 값으로 매핑한 비즈맵의 디테일 카테고리 대표 id 값 가져오기
    categories = select_biz_detail_category_id_by_detail_category_id(business_area_category_id)
    rep_id = categories.rep_id
    biz_detail_category_name = categories.biz_detail_category_name

    # 3. 디테일 카테고리 대표 id 값으로 이름 가져오기
    categories_name = select_categories_name_by_rep_id(rep_id) 
    biz_main_category_name = categories_name.biz_main_category_name
    biz_sub_category_name = categories_name.biz_sub_category_name

    # 3. 해당 동의 해당 업종의 상권 정보 값 들 가져오기
    commercial_data = select_rising_menu_by_sub_district_id_rep_id(sub_district_id, rep_id)

    market_size = commercial_data.market_size
    average_sales = commercial_data.average_sales
    average_payment = commercial_data.average_payment
    usage_count = commercial_data.usage_count
    avg_profit_per_mon = commercial_data.avg_profit_per_mon
    avg_profit_per_tue= commercial_data.avg_profit_per_mon
    avg_profit_per_wed = commercial_data.avg_profit_per_wed
    avg_profit_per_thu = commercial_data.avg_profit_per_thu
    avg_profit_per_fri = commercial_data.avg_profit_per_fri
    avg_profit_per_sat = commercial_data.avg_profit_per_sat
    avg_profit_per_sun = commercial_data.avg_profit_per_sun
    avg_profit_per_06_09 = commercial_data.avg_profit_per_06_09
    avg_profit_per_09_12 = commercial_data.avg_profit_per_09_12
    avg_profit_per_12_15 = commercial_data.avg_profit_per_12_15
    avg_profit_per_15_18 = commercial_data.avg_profit_per_15_18
    avg_profit_per_18_21 = commercial_data.avg_profit_per_18_21
    avg_profit_per_21_24 = commercial_data.avg_profit_per_21_24
    avg_profit_per_24_06 = commercial_data.avg_profit_per_24_06
    avg_client_per_m_20 = commercial_data.avg_client_per_m_20
    avg_client_per_m_30 = commercial_data.avg_client_per_m_30
    avg_client_per_m_40 = commercial_data.avg_client_per_m_40
    avg_client_per_m_50 = commercial_data.avg_client_per_m_50
    avg_client_per_m_60 = commercial_data.avg_client_per_m_60
    avg_client_per_f_20 = commercial_data.avg_client_per_m_20
    avg_client_per_f_30 = commercial_data.avg_client_per_m_30
    avg_client_per_f_40 = commercial_data.avg_client_per_m_40
    avg_client_per_f_50 = commercial_data.avg_client_per_m_50
    avg_client_per_f_60 = commercial_data.avg_client_per_m_60
    top_menu_1 = commercial_data.top_menu_1
    top_menu_2 = commercial_data.top_menu_2
    top_menu_3 = commercial_data.top_menu_3
    top_menu_4 = commercial_data.top_menu_4
    top_menu_5 = commercial_data.top_menu_5

    days_slots = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
    profits_per_day = [
        avg_profit_per_mon,
        avg_profit_per_tue,
        avg_profit_per_wed,
        avg_profit_per_thu,
        avg_profit_per_fri,
        avg_profit_per_sat,
        avg_profit_per_sun
    ]

    # 시간대별 레이블과 값
    time_slots = ['06-09시', '09-12시', '12-15시', '15-18시', '18-21시', '21-24시', '24-06시']
    profits_per_time = [
        avg_profit_per_06_09,
        avg_profit_per_09_12,
        avg_profit_per_12_15,
        avg_profit_per_15_18,
        avg_profit_per_18_21,
        avg_profit_per_21_24,
        avg_profit_per_24_06
    ]

    # 성별 연령대별 레이블과 값
    gender_slots = ['20대 남성', '30대 남성', '40대 남성', '50대 남성', '60대 남성', '20대 여성', '30대 여성', '40대 여성', '50대 여성', '60대 여성']
    profits_per_gender = [
        avg_client_per_m_20,
        avg_client_per_m_30,
        avg_client_per_m_40,
        avg_client_per_m_50,
        avg_client_per_m_60,
        avg_client_per_f_20,
        avg_client_per_f_30,
        avg_client_per_f_40,
        avg_client_per_f_50,
        avg_client_per_f_60
    ]


    # 최대값과 해당 요일 찾기
    top_day_profit, top_day_label = max(zip(profits_per_day, days_slots))
    # 최대값과 해당 시간대 찾기
    top_time_profit, top_time_label = max(zip(profits_per_time, time_slots))
    # 최대값과 해당 성별 연령대 찾기
    top_gender_profit, top_gender_label = max(zip(profits_per_gender, gender_slots))

    return (
        region, sub_district_id, city_name, district_name, sub_district_name, region_name, 
        large_category_name, medium_category_name, small_category_name, category_name, store_name,
        shop, move_pop, sales, work_pop, income, spend, house, resident,
        shop_jscore, move_pop_jscore, sales_jscore, work_pop_jscore, income_jscore, spend_jscore, house_jscore, resident_jscore,
        age_under_10, age_10s, age_20s, age_30s, age_40s, age_50s, age_60_plus, male_percentage, female_percentage,
        market_size, average_sales, average_payment, usage_count, 
        top_menu_1, top_menu_2, top_menu_3, top_menu_4, top_menu_5, top_day_profit, top_day_label, top_time_profit, top_time_label, top_gender_profit, top_gender_label,
        biz_main_category_name, biz_sub_category_name, biz_detail_category_name
    )
            


# 입지 정보 관련 리포트 생성
def report_loc_info(store_business_id):    
    load_dotenv()

    (
        _, _, _, _, sub_district_name, region_name,
        _, _, _, category_name, store_name, 
        shop, move_pop, sales, work_pop, income, spend, house, resident,
        shop_jscore, move_pop_jscore, sales_jscore, work_pop_jscore, income_jscore, spend_jscore, house_jscore, resident_jscore,
        age_under_10, age_10s, age_20s, age_30s, age_40s, age_50s, age_60_plus, male_percentage, female_percentage,
        _, _, _, _, 
        _, _, _, _, _, _, _,
        _
    ) = get_region_info(store_business_id)
     

    # 3. 보낼 프롬프트 설정
    content = f"""
        다음과 같은 매장정보 입지 현황을 바탕으로 매장 입지 특징을 분석하시고 입지에 따른 매장운영 가이드를 제시해주세요. 
        답변은 반드시 한글로 해주고 답변 내용 첫줄에 매장 정보를 넣어주세요.
        각 항목의 점수는 전체 지역 대비 순위를 나타낸것으로 1~10점으로 구성됩니다.

        5줄로 요약해줘
    
        매장 정보 입지 현황
        - 위치 : {region_name} 
        - 업종 : {category_name}
        - 매장이름 : {store_name}

        - {sub_district_name}의 업소수 : {shop}개/ {shop_jscore}점
        - {sub_district_name}의 지역 평균매출 : {sales}원/ {sales_jscore}점
        - {sub_district_name}의 월 평균소득 : {income}원/ {income_jscore}점
        - {sub_district_name}의 월 평균소비 : {spend}원/ {spend_jscore}점
        - {sub_district_name}의 월 평균소비 : {work_pop}명/ {work_pop_jscore}점
        - {sub_district_name}의 유동인구 수 : {move_pop}명/ {move_pop_jscore}점
        - {sub_district_name}의 주거인구 수 : {resident}명/ {resident_jscore}점
        - {sub_district_name}의 세대 수 : {house}개/{house_jscore}점
        - {sub_district_name}의 인구 분포 : 10세 미만 {age_under_10}명, 10대 {age_10s}명, 20대 {age_20s}명, 
                                            30대 {age_30s}명, 40대 {age_40s}명, 50대 {age_50s}명, 60대 이상 {age_60_plus}명,    
                                            여성 {female_percentage}%, 남성 {male_percentage}%
    """

    openai_api_key = os.getenv("GPT_KEY")
    
    # OpenAI API 키 설정
    openai.api_key = openai_api_key

    completion = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system", 
            "content": gpt_content
        },
        {"role": "user", "content": content}  
    ]
    )

    report = completion.choices[0].message.content

    return report


# 업종 별 뜨는 메뉴 리포트 생성
def report_rising_menu(store_business_id):    
    load_dotenv()
    
    now = datetime.now()
    current_time = now.strftime("%Y년 %m월 %d일 %H:%M")
    weekday = now.strftime("%A")

    result = get_region_info(store_business_id)
    region_name = result[5]
    top_menu_1 = result[40]
    top_menu_2 = result[41]
    top_menu_3 = result[42]
    top_menu_4 = result[43]
    top_menu_5 = result[44]
    biz_detail_category_name = result[47]


    # 3. 보낼 프롬프트 설정
    content = f"""
        아래 지역 업종의 뜨는 메뉴가 다음과 같습니다. 
        해당 업종의 매장이 고객을 위해 주요 전략으로 가져가야 할 점이 무엇일지 백종원 쉐프 스타일로 조언을 해주세요.
        단, 말투나 전문적 용어는 점주 성향에 맞추고 조언은 4줄 이하로 해주세요. 

        - 매장 업종 : {biz_detail_category_name}
        - 매장 위치 : {region_name}
        - 뜨는 메뉴 : 1위 {top_menu_1}, 2위 {top_menu_2}, 3위 {top_menu_3}, 4위 {top_menu_4}, 5위 {top_menu_5}
        - 적용날짜 : {current_time}  {weekday} 

    """

    openai_api_key = os.getenv("GPT_KEY")
    
    # OpenAI API 키 설정
    openai.api_key = openai_api_key

    completion = openai.chat.completions.create(
    model="gpt-4o",
    messages=[
        {
            "role": "system", 
            "content": gpt_content
        },
        {"role": "user", "content": content}  
    ]
    )

    report = completion.choices[0].message.content

    return report


# 오늘의 팁 리포트 생성
def report_today_tip(store_business_id, weather_info):    
    load_dotenv()
    
    weather = weather_info.weather
    temp = weather_info.temp
    sunset = weather_info.sunset

    sunset_utc_time = datetime.fromtimestamp(sunset, tz=timezone.utc)
    sunset_korean_time = sunset_utc_time + timedelta(hours=9)

    # 알아보기 쉽게 한국 시간 형식으로 출력
    sunset_korean_time_formatted = sunset_korean_time.strftime("%H:%M")

    now = datetime.now()
    current_time = now.strftime("%Y년 %m월 %d일 %H:%M")
    weekday = now.strftime("%A")

    (
        _, _, _, _, sub_district_name, region_name,
        _, _, _, _, store_name, 
        shop, move_pop, sales, work_pop, income, spend, house, resident,
        _, _, _, _, _, _, _, _,
        _, _, _, _, _, _, _, _, _,
        market_size, average_sales, average_payment, usage_count, 
        _, _, _, _, _, _, top_day_label, _, top_time_label, _, top_gender_label,
        biz_main_category_name, biz_sub_category_name, biz_detail_category_name
    ) = get_region_info(store_business_id)


    category = biz_main_category_name + ' > ' + biz_sub_category_name + ' > ' + biz_detail_category_name

    # 3. 보낼 프롬프트 설정
    content = f"""
        다음과 같은 매장정보 입지 및 상권 현황과 현재 환경상황에 맞게 '현재 매장 운영 팁' 이라는 내용으로 매장 운영 가이드를 주세요. 
        매장 정보 입지 및 상권 현황
        - 위치 : {region_name}
        - 업종 : {category}
        - 매장이름 : {store_name}
        - {sub_district_name} 업소 수 : {shop}개
        - {sub_district_name} 지역 평균매출 : {sales}원
        - {sub_district_name} 월 평균소득 : {income}원
        - {sub_district_name} 월 평균소비 : {spend}원
        - {sub_district_name} 유동인구 수 : {move_pop}명
        - {sub_district_name} 주거인구 수 : {resident}명
        - {sub_district_name} 직장인구 수 : {work_pop}명
        - {sub_district_name} 세대 수 : {house}개
        - {sub_district_name} {biz_detail_category_name} 시장규모 : {market_size} 개
        - {sub_district_name} {biz_detail_category_name} 업종 평균매출 : {average_sales}원
        - {sub_district_name} {biz_detail_category_name} 업종 평균결제액 : {average_payment}원
        - {sub_district_name} {biz_detail_category_name} 업종 평균건수 : {usage_count}건
        - {sub_district_name} {biz_detail_category_name} 업종 가장 매출이 높은 요일 : {top_day_label}
        - {sub_district_name} {biz_detail_category_name} 가장 매출이 높은 시간대 : {top_time_label}
        - {sub_district_name} {biz_detail_category_name} 가장 매출이 높은 연령.성별 : {top_gender_label}

        현재 환경상황
        - 날씨 : {weather}
        - 기온 : {temp} 도
        - 일몰시간 : {sunset_korean_time_formatted}
        - 현재 시간 : {current_time} {weekday}  
        
        작성 가이드 : 
        1. 5항목 이하, 항목당 2줄 이내로 작성해주세요.
    """

    print(content)

    result = "ji"
    return  result, weather_info
    # openai_api_key = os.getenv("GPT_KEY")
    
    # # OpenAI API 키 설정
    # openai.api_key = openai_api_key

    # completion = openai.chat.completions.create(
    # model="gpt-4o",
    # messages=[
    #     {
    #         "role": "system", 
    #         "content": gpt_content
    #     },
    #     {"role": "user", "content": content}  
    # ]
    # )

    # report = completion.choices[0].message.content

    # return report

################ 클로드 결제 후 사용 #################
# import anthropic

# def testCLAUDE():
#     api_key = os.getenv("CLAUDE_KEY")
    
#     # OpenAI API 키 설정
#     openai.api_key = api_key
#     client = anthropic.Anthropic(
#     api_key={api_key},  # 환경 변수를 설정했다면 생략 가능
#     )

#     message = client.messages.create(
#         model="claude-3-opus-20240229",
#         max_tokens=1000,
#         temperature=0.0,
#         system="Respond only in Yoda-speak.",
#         messages=[
#             {"role": "user", "content": "How are you today?"}
#         ]
#     )

#     print(message.content)


############### 라마 ##################
# import ollama

# def testOLLAMA():
#     response = ollama.chat(model='llama3.1:8b', messages=[
#     {
#         'role': 'user',
#         'content': content,
#     },
#     ])
#     print(response['message']['content'])





if __name__ == "__main__":
    # process_crime_data()
    # report_loc_info("MA010120220803674032")
    # get_region_info("MA010120220803674032")
    # report_rising_menu("MA010120220803674032")
    report_today_tip("MA010120220803674032")
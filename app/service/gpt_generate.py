import pandas as pd
import os
from dotenv import load_dotenv
from app.db.connect import *
from app.crud.crime import *
from app.schemas.crime import CrimeRequest
from app.crud.loc_store import select_local_store_by_store_business_number
from app.crud.loc_info import select_local_info_statistics_by_sub_district_id
from app.crud.population import select_age_pop_list_by_sub_district_id, select_gender_pop_list_by_sub_district_id

gpt_content = """
    당신은 전문 조언자입니다. 
    귀하의 역할은 사용자의 질문을 분석하고, 주요 측면을 식별하고, 질문의 맥락을 기반으로 운영 지침과 통찰력을 제공하는 것입니다. 
    접근 방식을 최적화하는 데 도움이 되는 전략이나 솔루션을 제공합니다.
"""

import openai
from dotenv import load_dotenv
import openai

load_dotenv()

def report_loc_info(store_business_id):
    
    # 1. 전달받은 건물 관리 번호로 지역 명 및 카테고리 조회
    region = select_local_store_by_store_business_number(store_business_id)
    sub_district_id = region.get('SUB_DISTRICT_ID')
    region_name = region.get('CITY_NAME', '') + ' ' + region.get('DISTRICT_NAME', '') + ' ' + region.get('SUB_DISTRICT_NAME')
    sub_district_name = region.get('SUB_DISTRICT_NAME')
    category = region.get('large_category_name', '') + '>' + region.get('medium_category_name', '') + '>' + region.get('small_category_name')
    store_name = region.get('store_name')

    # 2. 지역 id 값으로 입지 정보 및 통계 값 조회 후 쌍으로 묶기
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

    # 3. 보낼 프롬프트 설정
    content = f"""
        다음과 같은 매장정보 입지 현황을 바탕으로 매장 입지 특징을 분석하시고 입지에 따른 매장운영 가이드를 제시해주세요. 
        답변은 반드시 한글로 해주고 답변 내용 첫줄에 매장 정보를 넣어주세요.
        각 항목의 점수는 전체 지역 대비 순위를 나타낸것으로 1~10점으로 구성됩니다.

        매장 정보 입지 현황
        - 위치 : {region_name} 
        - 업종 : {category}
        - 매장이름 : {store_name}

        - {sub_district_name}의 업소수 : {shop}개/ {shop_jscore}점
        - {sub_district_name}의 지역 평균매출 : {sales}원/ {sales_jscore}점
        - {sub_district_name}의 월 평균소득 : {income}원/ {income_jscore}점
        - {sub_district_name}의 월 평균소비 : {spend}원/ {spend_jscore}점
        - {sub_district_name}의 월 평균소비 : {work_pop}명/ {work_pop_jscore}점
        - {sub_district_name}의 유동인구 수 : {move_pop}명/ {move_pop_jscore}점
        - {sub_district_name}의 주거인구 수 : {resident}명/ {resident_jscore}점
        - {sub_district_name}의 세대 수 : {house}개/{house_jscore}점
        - {sub_district_name}의 인구 분포 : 10세 미만 {age_under_10}명, 10대 {age_10s}, 20대 {age_20s}, 
                                            30대 {age_30s}, 40대 {age_40s}, 50대 {age_50s}, 60대 이상 {age_60_plus},    
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
    print(report)
    return report

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
    report_loc_info("MA010120220803781837")
    # time_fnc()
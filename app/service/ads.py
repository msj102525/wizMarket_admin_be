from app.crud.ads import (
    select_ads_list as crud_select_ads_list,
    select_ads_init_info as crud_select_ads_init_info
)
from app.schemas.ads import(
    AdsInitInfoOutPut, AdsInitInfo
)
from translate import Translator
from fastapi import HTTPException
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import os
from typing import List
import base64

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
def select_ads_init_info(store_business_number: str) -> AdsInitInfoOutPut:
    try:
        raw_data = crud_select_ads_init_info(store_business_number)

        # 최대 매출 요일 계산
        sales_day_columns = [
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_MON", raw_data.commercial_district_average_percent_mon),
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_TUE", raw_data.commercial_district_average_percent_tue),
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_WED", raw_data.commercial_district_average_percent_wed),
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_THU", raw_data.commercial_district_average_percent_thu),
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_FRI", raw_data.commercial_district_average_percent_fri),
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_SAT", raw_data.commercial_district_average_percent_sat),
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_SUN", raw_data.commercial_district_average_percent_sun)
        ]
        # None을 0으로 대체하되, 모두 None인지 확인
        if all(value is None for _, value in sales_day_columns):
            max_sales_day = (None, None)  # 모든 값이 None인 경우
        else:
            # None은 0으로 대체하여 계산
            max_sales_day = max(sales_day_columns, key=lambda x: x[1] or 0)  # (컬럼명, 값)

        # 최대 매출 시간대 계산 
        sales_time_columns = [
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_06_09", raw_data.commercial_district_average_percent_06_09),
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_09_12", raw_data.commercial_district_average_percent_09_12),
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_12_15", raw_data.commercial_district_average_percent_12_15),
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_15_18", raw_data.commercial_district_average_percent_15_18),
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_18_21", raw_data.commercial_district_average_percent_18_21),
            ("COMMERCIAL_DISTRICT_AVERAGE_SALES_PERCENT_21_24", raw_data.commercial_district_average_percent_21_24)
        ]
        if all(value is None for _, value in sales_time_columns):
            max_sales_time = (None, None) 
        else:
            max_sales_time = max(sales_time_columns, key=lambda x: x[1] or 0) 

        # 최대 남성 연령대 계산
        male_age_columns = [
            ("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_20S", raw_data.commercial_district_avg_client_per_m_20s),
            ("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_30S", raw_data.commercial_district_avg_client_per_m_30s),
            ("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_40S", raw_data.commercial_district_avg_client_per_m_40s),
            ("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_50S", raw_data.commercial_district_avg_client_per_m_50s),
            ("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_M_60_OVER", raw_data.commercial_district_avg_client_per_m_60_over)
        ]
        if all(value is None for _, value in male_age_columns):
            max_male_age = (None, None)  
        else:
            max_male_age = max(male_age_columns, key=lambda x: x[1] or 0) 

        # 최대 여성 연령대 계산
        female_age_columns = [
            ("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_20S", raw_data.commercial_district_avg_client_per_f_20s),
            ("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_30S", raw_data.commercial_district_avg_client_per_f_30s),
            ("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_40S", raw_data.commercial_district_avg_client_per_f_40s),
            ("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_50S", raw_data.commercial_district_avg_client_per_f_50s),
            ("COMMERCIAL_DISTRICT_AVG_CLIENT_PER_F_60_OVER", raw_data.commercial_district_avg_client_per_f_60_over)
        ]
        if all(value is None for _, value in female_age_columns):
            max_female_age = (None, None)  
        else:
            max_female_age = max(female_age_columns, key=lambda x: x[1] or 0) 

        # 결과 반환
        return AdsInitInfoOutPut(
            store_business_number=raw_data.store_business_number,
            store_name=raw_data.store_name,
            road_name=raw_data.road_name,
            city_name=raw_data.city_name,
            district_name=raw_data.district_name,
            sub_district_name=raw_data.sub_district_name,
            detail_category_name=raw_data.detail_category_name,
            loc_info_average_sales_k=raw_data.loc_info_average_sales_k,
            commercial_district_max_sales_day=max_sales_day,  
            commercial_district_max_sales_time=max_sales_time,
            commercial_district_max_sales_m_age=max_male_age,  
            commercial_district_max_sales_f_age=max_female_age,  
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service loc_store_content_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service loc_store_content_list Error: {str(e)}"
        )

# 문구 생성
def generate_content(
    use_option, title, store_name, road_name,
    city_name, district_name, sub_district_name,
    detail_category_name, loc_info_average_sales_k,
    max_sales_day, max_sales_day_value,
    max_sales_time, max_sales_time_value,
    max_sales_male, max_sales_male_value,
    max_sales_female, max_sales_female_value
):
    if use_option == 'MMS':
        use_option = 'MMS(문자)'
    elif use_option == 'youtube thumbnail':
        use_option = '유튜브 썸네일'
    elif use_option == 'instagram story':
        use_option = '인스타그램 스토리'
    elif use_option == 'instagram feed':
        use_option = '인스타그램 피드'
    elif use_option == 'naver blog':
        use_option = '네이버 블로그'
    else :
        use_option = '구글 광고 배너'

    full_region = f"{city_name} {district_name} {sub_district_name}"

    # gpt 영역
    gpt_content = """
        다음과 같은 내용을 바탕으로 온라인 광고 콘텐츠를 제작하려고 합니다. 
        내용에 부합하는 광고문구를 30자 이내로 작성해주세요.
        슬로건 마다 <br> 태그를 사용해서 줄 나눔 해주세요.
    """    
    content = f"""
        가게명 : {store_name}
        업종 : {detail_category_name}
        용도: {title}
        채널 : {use_option} 이미지에 사용
        주소 : {road_name}
        {full_region}의 평균 월 매출 : {loc_info_average_sales_k} * k
        {full_region}의 매출이 가장 높은 요일 : {max_sales_day}, {max_sales_day_value}%
        {full_region}의 매출이 가장 높은 시간대 : {max_sales_time}, {max_sales_time_value}%
        {full_region}의 매출이 가장 높은 남자 연령대 : {max_sales_male}, {max_sales_male_value}%
        {full_region}의 매출이 가장 높은 여자 연령대 : {max_sales_female}, {max_sales_female_value}%

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


# OpenAI API 키 설정
api_key = os.getenv("GPT_KEY")
client = OpenAI(api_key=api_key)

# 이미지 생성
def generate_image(
    use_option, model_option, title, content_info, store_name, detail_category_name, 
):
    # gpt 영역
    gpt_content = """
        영어로 번역해줘
    """    
    content = f"""
        다음과 같은 내용을 바탕으로 글씨가 없는 온라인 광고 콘텐츠 이미지를 생성해주세요. 
        형태 : {use_option}
        용도 : {title}
        가게명 : {store_name}
        업종 : {detail_category_name}
    """
    client = OpenAI(api_key=os.getenv("GPT_KEY"))
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": gpt_content},
            {"role": "user", "content": content},
        ],
    )
    prompt = completion.choices[0].message.content
    print(prompt)

    token = os.getenv("FACE_KEY")
    if model_option == 'basic':
        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-3.5-large"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"inputs": prompt}
        # API 요청 보내기
        try:
            # API 요청 보내기
            response = requests.post(API_URL, headers=headers, json=data)
            response.raise_for_status()  # 에러 발생 시 예외 처리

            # 응답 바이너리 데이터를 PIL 이미지로 변환
            image = Image.open(BytesIO(response.content))

            # 이미지를 Base64로 인코딩
            buffered = BytesIO()
            image.save(buffered, format="PNG")  # PNG 형식으로 저장
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # JSON 형식으로 Base64 이미지 반환
            return {"image": f"data:image/png;base64,{img_str}"}

        except requests.exceptions.RequestException as e:
            print(f"Failed to generate image: {e}")
            return {"error": str(e)}
        
    elif model_option == 'poster':
        API_URL = "https://api-inference.huggingface.co/models/alex1105/movie-posters-v2"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"inputs": prompt}
        # API 요청 보내기
        try:
            # API 요청 보내기
            response = requests.post(API_URL, headers=headers, json=data)
            response.raise_for_status()  # 에러 발생 시 예외 처리

            # 응답 바이너리 데이터를 PIL 이미지로 변환
            image = Image.open(BytesIO(response.content))

            # 이미지를 Base64로 인코딩
            buffered = BytesIO()
            image.save(buffered, format="PNG")  # PNG 형식으로 저장
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # JSON 형식으로 Base64 이미지 반환
            return {"image": f"data:image/png;base64,{img_str}"}

        except requests.exceptions.RequestException as e:
            print(f"Failed to generate image: {e}")
            return {"error": str(e)}
        
    elif model_option == 'food':
        API_URL = "https://api-inference.huggingface.co/models/its-magick/merlin-food"
        headers = {"Authorization": f"Bearer {token}"}
        data = {"inputs": prompt}
        # API 요청 보내기
        # 응답 처리
        try:
            # API 요청 보내기
            response = requests.post(API_URL, headers=headers, json=data)
            response.raise_for_status()  # 에러 발생 시 예외 처리

            # 응답 바이너리 데이터를 PIL 이미지로 변환
            image = Image.open(BytesIO(response.content))

            # 이미지를 Base64로 인코딩
            buffered = BytesIO()
            image.save(buffered, format="PNG")  # PNG 형식으로 저장
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

            # JSON 형식으로 Base64 이미지 반환
            return {"image": f"data:image/png;base64,{img_str}"}

        except requests.exceptions.RequestException as e:
            print(f"Failed to generate image: {e}")
            return {"error": str(e)}
        
    elif model_option == 'dalle':
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                n=1
            )
            image_url = response.data[0].url

            # 이미지 다운로드
            image_response = requests.get(image_url)
            image_response.raise_for_status()

            # Base64 인코딩
            img_str = base64.b64encode(image_response.content).decode("utf-8")
            return {"image": f"data:image/png;base64,{img_str}"}
        except Exception as e:
            return {"error": f"이미지 생성 중 오류 발생: {e}"}



# 주제 + 문구 + 이미지 합치기
def combine_ads(content, image):
    root_path = os.getenv("ROOT_PATH")
    font_path = os.path.join(root_path, "app", "font", "yang.otf") 
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)
    img_width, img_height = image.size
    draw = ImageDraw.Draw(image)

    # 텍스트를 세미콜론으로 구분하여 줄 나누기
    lines = content.split('<br>')  # 세미콜론으로 텍스트를 나누어 각 문장을 줄로 처리
    
    # 줄 높이 계산 (getbbox 사용)
    line_height = font.getbbox("A")[3] + 10  # 줄 간격을 약간 추가

    # 텍스트 위치 설정
    
    text_y = img_height - (line_height * len(lines)) - 40  # 하단에서 여백 확보

    # 여러 줄로 텍스트 추가
    for line in lines:
        line = line.strip()  # 각 문장 앞뒤 공백 제거
        text_width = font.getbbox(line)[2]  # 현재 줄의 텍스트 너비 계산
        text_x = (img_width - text_width) // 2
        draw.text((text_x, text_y), line, font=font, fill="white")
        text_y += line_height  # 다음 줄로 이동

    image.show()



if __name__ == "__main__":
    pass
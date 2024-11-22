from app.crud.ads import (
    select_ads_list as crud_select_ads_list,
    select_ads_init_info as crud_select_ads_init_info
)
from app.schemas.ads import(
    AdsInitInfoOutPut, AdsInitInfo, WeatherInfo
)
from fastapi import HTTPException
import logging
import io
import os
from dotenv import load_dotenv
import requests
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO
import os
from typing import List
import base64
import re
from datetime import datetime, timezone, timedelta

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


        wether_main_temp = get_weather_info_by_lat_lng(raw_data.latitude, raw_data.longitude)
        wether_main = translate_weather_id_to_main(wether_main_temp.id)

        # 결과 반환
        return AdsInitInfoOutPut(
            store_business_number=raw_data.store_business_number,
            store_name=raw_data.store_name,
            road_name=raw_data.road_name,
            city_name=raw_data.city_name,
            district_name=raw_data.district_name,
            sub_district_name=raw_data.sub_district_name,
            latitude = raw_data.latitude,
            longitude = raw_data.longitude,
            detail_category_name=raw_data.detail_category_name,
            loc_info_average_sales_k=raw_data.loc_info_average_sales_k,
            commercial_district_max_sales_day=max_sales_day,  
            commercial_district_max_sales_time=max_sales_time,
            commercial_district_max_sales_m_age=max_male_age,  
            commercial_district_max_sales_f_age=max_female_age,  
            id = wether_main_temp.id,
            main = wether_main,
            temp = wether_main_temp.temp
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service loc_store_content_list Error: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Service loc_store_content_list Error: {str(e)}"
        )


def get_weather_info_by_lat_lng(
    lat: float, lng: float, lang: str = "kr"
) -> WeatherInfo:
    try:
        apikey = os.getenv("OPENWEATHERMAP_API_KEY")
        if not apikey:
            raise HTTPException(
                status_code=500,
                detail="Weather API key not found in environment variables.",
            )
        api_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lng}&appid={apikey}&lang={lang}&units=metric"
        # logger.info(f"Requesting weather data for lat={lat}, lng={lng}")
        weather_response = requests.get(api_url)
        weather_data = weather_response.json()
        if weather_response.status_code != 200:
            error_msg = (
                f"Weather API Error: {weather_data.get('message', 'Unknown error')}"
            )
            logger.error(error_msg)
            raise HTTPException(
                status_code=weather_response.status_code, detail=error_msg
            )
        weather_info = WeatherInfo(
            id = weather_data["weather"][0]["id"],
            main=weather_data["weather"][0]["main"],
            temp=weather_data["main"]["temp"],
        )
        return weather_info
    except requests.RequestException as e:
        error_msg = f"Failed to fetch weather data: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=503, detail=error_msg)
    except (KeyError, ValueError) as e:
        error_msg = f"Error processing weather data: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"Weather service error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# 날씨 id 값 따라 한글 번역
def translate_weather_id_to_main(weather_id: int) -> str:
    if 200 <= weather_id < 300:
        return "뇌우"  # Thunderstorm
    elif 300 <= weather_id < 400:
        return "이슬비"  # Drizzle
    elif 500 <= weather_id < 600:
        return "비"  # Rain
    elif 600 <= weather_id < 700:
        return "눈"  # Snow
    elif 700 <= weather_id < 800:
        return "안개"  # Atmosphere (mist, fog, etc.)
    elif weather_id == 800:
        return "맑음"  # Clear
    elif 801 <= weather_id < 900:
        return "구름"  # Clouds
    else:
        return "알 수 없음"  # Unknown case


# 문구 생성
def generate_content(
    prompt, gpt_role, detail_content
):
    # gpt 영역
    gpt_content = gpt_role
    content = prompt + '\n내용 : ' + detail_content
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
    use_option, model_option, ai_prompt
):
    if use_option == '문자메시지':
        resize = (333, 458)
    elif use_option == '유튜브 썸네일':
        resize = (412, 232)
    elif use_option == '인스타그램 스토리':
        resize = (412, 732)
    elif use_option == '인스타그램 피드':
        resize = (412, 514)
    elif use_option == '배너':
        resize = (377, 377)
    else :
        resize= None

    # gpt 영역
    gpt_content = """
        당신은 전문 번역가입니다. 사용자가 제공한 내용을 정확히 영어로 번역하세요. 번역 외의 부가적인 설명이나 추가적인 내용을 작성하지 마세요.
    """    
    content = ai_prompt
    client = OpenAI(api_key=os.getenv("GPT_KEY"))
    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": gpt_content},
            {"role": "user", "content": content},
        ],
    )
    prompt = completion.choices[0].message.content

    token = os.getenv("FACE_KEY")
    if model_option == 'basic':
        # print(prompt)
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

            if resize:
                target_width = resize[0]  # 원하는 가로 크기
                original_width, original_height = image.size
                aspect_ratio = original_height / original_width  # 세로/가로 비율 계산

                # 새로운 세로 크기 계산
                target_height = int(target_width * aspect_ratio)

                # 리사이즈 수행
                image = image.resize((target_width, target_height), Image.LANCZOS)

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

            # 이미지 리사이즈
            if resize:
                target_width = resize[0]  # 원하는 가로 크기
                original_width, original_height = image.size
                aspect_ratio = original_height / original_width  # 세로/가로 비율 계산

                # 새로운 세로 크기 계산
                target_height = int(target_width * aspect_ratio)

                # 리사이즈 수행
                image = image.resize((target_width, target_height), Image.LANCZOS)

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

            # 이미지 리사이즈
            if resize:
                target_width = resize[0]  # 원하는 가로 크기
                original_width, original_height = image.size
                aspect_ratio = original_height / original_width  # 세로/가로 비율 계산

                # 새로운 세로 크기 계산
                target_height = int(target_width * aspect_ratio)

                # 리사이즈 수행
                image = image.resize((target_width, target_height), Image.LANCZOS)

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
            if use_option == '문자메시지':
                resize = (1024, 1792)
            elif use_option == '유튜브 썸네일':
                resize = (1792, 1024)
            elif use_option == '인스타그램 스토리':
                resize = (1024, 1792)
            elif use_option == '인스타그램 피드':
                resize = (1024, 1792)
            elif use_option == '배너':
                resize = (1024, 1024)
            else :
                resize= None
            resize_str = f"{resize[0]}x{resize[1]}"
            # prompt = ai_prompt 한글 주석
            # print(prompt) 
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=resize_str,
                quality="hd", 
                n=1
            )
            image_url = response.data[0].url

            # 이미지 다운로드
            image_response = requests.get(image_url)
            image_response.raise_for_status()

            # Pillow를 사용한 리사이즈
            img = Image.open(io.BytesIO(image_response.content))

            # 원하는 크기로 다시 리사이즈 (예: 800x800)
            if use_option == '문자메시지':
                final_size = (333, 458)
            elif use_option == '유튜브 썸네일':
                final_size = (412, 232)
            elif use_option == '인스타그램 스토리':
                final_size = (412, 732)
            elif use_option == '인스타그램 피드':
                final_size = (412, 514)
            elif use_option == '배너':
                final_size = (377, 377)
            else :
                final_size= None
            # 이미지 리사이즈
            if final_size:
                target_width = final_size[0]  # 원하는 가로 크기
                original_width, original_height = img.size
                aspect_ratio = original_height / original_width  # 세로/가로 비율 계산

                # 새로운 세로 크기 계산
                target_height = int(target_width * aspect_ratio)

                # 리사이즈 수행
                resized_img = img.resize((target_width, target_height), Image.LANCZOS)

            # Base64 인코딩
            buffer = io.BytesIO()
            resized_img.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return {"image": f"data:image/png;base64,{img_str}"}
        except Exception as e:
            return {"error": f"이미지 생성 중 오류 발생: {e}"}



# 텍스트 나누기
# def split_top_line(text, max_length=9):
#     """
#     top_line을 최대 글자 수(max_length)에 따라 나눔.
#     - 두 번째 띄어쓰기, 특수기호, 또는 중간에서 나누는 기준 적용.
#     """
#     split_idx = None
#     # 두 번째 띄어쓰기 찾기
#     space_matches = [m.start() for m in re.finditer(r' ', text)]
#     if len(space_matches) >= 2:
#         split_idx = space_matches[1]
#     # 특수기호 찾기 (띄어쓰기로 나눌 기준이 없을 때)
#     if not split_idx:
#         special_char_match = re.search(r'[!@#$%^&*()\-_=+[\]{};:\'",.<>?/]', text)
#         if special_char_match:
#             split_idx = special_char_match.start()
#     # 나눌 기준이 없으면 중간에서 나눔
#     if not split_idx and len(text) > max_length:
#         split_idx = len(text) // 2
#     # 문자열 나누기
#     if split_idx:
#         return text[:split_idx].strip(), text[split_idx:].strip()
#     else:
#         return text.strip(), None

def split_top_line(text, max_length):
    """
    입력된 text를 8글자를 기준으로 반복적으로 나눔.
    - text가 8글자 이하일 경우, 그대로 반환.
    - text가 8글자 초과일 경우, 띄어쓰기 기준으로 나눠 반환하며 각 줄은 max_length를 넘지 않음.
    """
    result = []
    words = text.split()

    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)
        # 현재 줄에 추가해도 max_length를 넘지 않으면 추가
        if current_length + word_length + (1 if current_line else 0) <= max_length:
            current_line.append(word)
            current_length += word_length + (1 if current_line else 0)
        else:
            # 현재 줄이 꽉 찼으면 result에 추가하고 새로운 줄 시작
            result.append(" ".join(current_line))
            current_line = [word]
            current_length = word_length

    # 마지막 줄 추가
    if current_line:
        result.append(" ".join(current_line))

    return result


def combine_ads (store_name, road_name, content, image_width, image_height, image, alignment="center"):
    image_1 = combine_ads_ver1(store_name, road_name, content, image_width, image_height, image, alignment="center")
    image_2 = combine_ads_ver2(store_name, road_name, content, image_width, image_height, image, alignment="center")
    return (image_1, image_2)

# 주제 + 문구 + 이미지 합치기
def combine_ads_ver1(store_name, road_name, content, image_width, image_height, image, alignment="center"):
    root_path = os.getenv("ROOT_PATH", ".")
    sp_image_path = os.path.join(root_path, "app", "image", "BG_snow.png") 
    # RGBA 모드로 변환
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # 검은 바탕 생성 및 합성
    black_overlay = Image.new("RGBA", (image_width, image_height), (0, 0, 0, int(255 * 0.4)))  # 검은 바탕(60% 투명도)

    image = Image.alpha_composite(image, black_overlay)

    # sp_image 불러오기 및 리사이즈
    sp_image = Image.open(sp_image_path).convert("RGBA")
    original_width, original_height = sp_image.size

    # sp_image의 가로 길이를 기존 이미지의 가로 길이에 맞추고, 세로는 비율에 맞게 조정
    new_width = image_width
    new_height = int((new_width / original_width) * original_height)
    sp_image = sp_image.resize((new_width, new_height))
    # 투명도 조정
    alpha = sp_image.split()[3]  # RGBA의 알파 채널 추출
    alpha = ImageEnhance.Brightness(alpha).enhance(0.8)  # 투명도를 0.6으로 조정
    sp_image.putalpha(alpha)  # 수정된 알파 채널을 다시 이미지에 적용

    # sp_image에 투명한 배경 추가하여 기존 이미지와 크기 맞춤
    padded_sp_image = Image.new("RGBA", (image_width, image_height), (0, 0, 0, 0))  # 투명 배경 생성
    # sp_image 배치
    offset_x = 0  # 기본 가로 정렬: 좌측
    if alignment == "center":
        offset_x = (image_width - new_width) // 2
    elif alignment == "right":
        offset_x = image_width - new_width

    offset_y = (image_height - new_height) // 2  # 세로 중앙 배치
    padded_sp_image.paste(sp_image, (offset_x, offset_y))  # sp_image를 배경 위에 붙임

    # sp_image와 기존 이미지 합성
    image = Image.alpha_composite(image.convert("RGBA"), padded_sp_image)

    # 텍스트 설정
    top_path = os.path.join(root_path, "app", "font", "JalnanGothicTTF.ttf") 
    bottom_path = os.path.join(root_path, "app", "font", "BMHANNA_11yrs_ttf.ttf") 
    store_name_path = os.path.join(root_path, "app", "font", "Pretendard-Bold.ttf") 
    road_name_path = os.path.join(root_path, "app", "font", "Pretendard-R.ttf") 
    top_font_size = image_width / 10
    bottom_font_size = (top_font_size * 5) / 8
    store_name_font_size = image_width / 20
    road_name_font_size = image_width / 22

    # 폰트 설정
    top_font = ImageFont.truetype(top_path, int(top_font_size))
    bottom_font = ImageFont.truetype(bottom_path, int(bottom_font_size))
    store_name_font = ImageFont.truetype(store_name_path, int(store_name_font_size))
    road_name_font = ImageFont.truetype(road_name_path, int(road_name_font_size))

    # 텍스트 렌더링 (합성 작업 후)
    draw = ImageDraw.Draw(image)

    # 텍스트를 '<br>'로 구분하여 줄 나누기
    # lines = content.split(' ')
    # lines = [re.sub(r'<[^>]+>', '', line).replace('\r', '').replace('\n', '') for line in lines]
    lines = re.split(r'[.!?,\n]', content)  # 구두점, 쉼표, 줄바꿈 모두 처리
    lines = [line.strip() for line in lines if line.strip()]
    if len(lines) > 0:
        top_line = lines[0].strip()
        lines_list = split_top_line(top_line, max_length=8)  # 반환값은 리스트
        # 첫 번째 줄 렌더링 Y 좌표 설정
        top_text_y = image_height / 10
        # 반복적으로 각 줄 렌더링
        for i, line in enumerate(lines_list):
            if line:  # 줄이 존재할 경우만 처리
                # 텍스트 너비 계산
                top_text_width = top_font.getbbox(line)[2]
                # 중앙 정렬 X 좌표 계산
                top_text_x = (image_width - top_text_width) // 2
                # 현재 줄 렌더링
                draw.text((top_text_x, top_text_y), line, font=top_font, fill=(255, 255, 255, int(255 * 0.8)))
                # Y 좌표를 다음 줄로 이동
                top_text_y += top_font.getbbox("A")[3] + 5

    # 하단 텍스트 추가
    bottom_lines = lines[1:]  # 첫 번째 줄을 제외한 나머지
    line_height = bottom_font.getbbox("A")[3] + 3
    text_y = (image_height * 3) // 5

    for line in bottom_lines:
        line = line.strip()
        # 하단 줄을 분리하여 20자 이상일 경우 나눔
        split_lines = split_top_line(line, max_length=20)

        for sub_line in split_lines:
            sub_line = sub_line.strip()
            text_width = bottom_font.getbbox(sub_line)[2]

            if alignment == "center":
                text_x = (image_width - text_width) // 2
            elif alignment == "left":
                text_x = 10
            elif alignment == "right":
                text_x = image_width - text_width - 10
            else:
                raise ValueError("Invalid alignment option. Choose 'center', 'left', or 'right'.")

            # 현재 줄 렌더링
            draw.text((text_x, text_y), sub_line, font=bottom_font, fill="#03FF57")
            text_y += line_height  # 다음 줄로 이동

    # store_name 추가
    store_name_width = store_name_font.getbbox(store_name)[2]
    store_name_x = (image_width - store_name_width) // 2
    store_name_y = image_height - (image_height / 7) # 분모가 작을수록 하단에 더 멀게
    draw.text((store_name_x, store_name_y), store_name, font=store_name_font, fill="white")

    # road_name 추가
    road_name_width = road_name_font.getbbox(road_name)[2]
    road_name_x = (image_width - road_name_width) // 2
    road_name_y = image_height - (image_height / 10) # 분모가 작을수록 하단에 더 멀게
    draw.text((road_name_x, road_name_y), road_name, font=road_name_font, fill="white")

    # 이미지 메모리에 저장
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    # Base64 인코딩
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{base64_image}"


def combine_ads_ver2(store_name, road_name, content, image_width, image_height, image, alignment="center"):
    root_path = os.getenv("ROOT_PATH", ".")
    sp_image_path = os.path.join(root_path, "app", "image", "new_imo.png") 
    
    # RGBA 모드로 변환
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # 검은 바탕 생성 및 합성
    black_overlay = Image.new("RGBA", (image_width, image_height), (0, 0, 0, int(255 * 0.4)))  # 검은 바탕(60% 투명도)
    image = Image.alpha_composite(image, black_overlay)

    # sp_image 불러오기 및 리사이즈
    sp_image = Image.open(sp_image_path).convert("RGBA")
    original_width, original_height = sp_image.size

    # sp_image의 가로 길이를 기존 이미지의 가로 길이의 1/4로 맞추고, 세로는 비율에 맞게 조정
    new_width = int(image_width / 4)
    new_height = int((new_width / original_width) * original_height)
    sp_image = sp_image.resize((new_width, new_height))

    # 4번 위치 (하단 오른쪽) 중심 좌표 계산
    offset_x = (image_width * 3 // 4) - (new_width // 2)  # 4등분 했을 때 하단 오른쪽 중심 X
    offset_y = (image_height * 3 // 4) - (new_height // 2)  # 4등분 했을 때 하단 오른쪽 중심 Y

    # sp_image를 기존 이미지 위에 합성 (투명도 제거)
    image.paste(sp_image, (offset_x, offset_y), sp_image)

    # 텍스트 설정
    top_path = os.path.join(root_path, "app", "font", "JalnanGothicTTF.ttf") 
    bottom_path = os.path.join(root_path, "app", "font", "BMHANNA_11yrs_ttf.ttf") 
    store_name_path = os.path.join(root_path, "app", "font", "Pretendard-Bold.ttf") 
    road_name_path = os.path.join(root_path, "app", "font", "Pretendard-R.ttf") 
    top_font_size = image_width / 20
    bottom_font_size = image_width / 10
    store_name_font_size = image_width / 24
    road_name_font_size = image_width / 26

    # 폰트 설정
    top_font = ImageFont.truetype(top_path, int(top_font_size))
    bottom_font = ImageFont.truetype(bottom_path, int(bottom_font_size))
    store_name_font = ImageFont.truetype(store_name_path, int(store_name_font_size))
    road_name_font = ImageFont.truetype(road_name_path, int(road_name_font_size))

    # 텍스트 렌더링 (합성 작업 후)
    draw = ImageDraw.Draw(image)

    # 텍스트를 '<br>'로 구분하여 줄 나누기
    # lines = content.split(' ')
    # lines = [re.sub(r'<[^>]+>', '', line).replace('\r', '').replace('\n', '') for line in lines]
    lines = re.split(r'[.!?,\n]', content)  # 구두점, 쉼표, 줄바꿈 모두 처리
    lines = [line.strip() for line in lines if line.strip()]
    if len(lines) > 0:
        top_line = lines[0].strip()
        lines_list = split_top_line(top_line, max_length=8)  # 반환값은 리스트
        # 첫 번째 줄 렌더링 Y 좌표 설정
        top_text_y = image_height / 10
        # 반복적으로 각 줄 렌더링
        for i, line in enumerate(lines_list):
            if line:  # 줄이 존재할 경우만 처리
                # 텍스트 너비 계산
                top_text_width = top_font.getbbox(line)[2]
                # 중앙 정렬 X 좌표 계산
                top_text_x = (image_width - top_text_width) // 2
                # 현재 줄 렌더링
                draw.text((top_text_x, top_text_y), line, font=top_font, fill=(255, 255, 255, int(255 * 0.8)))
                # Y 좌표를 다음 줄로 이동
                top_text_y += top_font.getbbox("A")[3] + 5

    # 하단 텍스트 추가
    bottom_lines = lines[1:]  # 첫 번째 줄을 제외한 나머지
    line_height = bottom_font.getbbox("A")[3] + 3
    text_y = (image_height ) // 3

    # 색상 리스트: 번갈아 사용할 색상
    colors = ["#FFFFFF", "#FFFF00"]  # 흰색, 노란색

    for line in bottom_lines:
        line = line.strip()
        # 하단 줄을 분리하여 20자 이상일 경우 나눔
        split_lines = split_top_line(line, max_length=10)

        for i, sub_line in enumerate(split_lines):
            sub_line = sub_line.strip()
            text_width = bottom_font.getbbox(sub_line)[2]

            if alignment == "center":
                text_x = (image_width - text_width) // 2
            elif alignment == "left":
                text_x = 10
            elif alignment == "right":
                text_x = image_width - text_width - 10
            else:
                raise ValueError("Invalid alignment option. Choose 'center', 'left', or 'right'.")

            # 현재 줄 렌더링, 색상은 colors[i % len(colors)]로 선택
            draw.text((text_x, text_y), sub_line, font=bottom_font, fill=colors[i % len(colors)])
            text_y += line_height  # 다음 줄로 이동

    # store_name 추가
    store_name_width = store_name_font.getbbox(store_name)[2]
    store_name_x = 10
    store_name_y = image_height - (image_height / 13) # 분모가 작을수록 하단에 더 멀게
    draw.text((store_name_x, store_name_y), store_name, font=store_name_font, fill="white")

    

    # 이미지 메모리에 저장
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    # Base64 인코딩
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{base64_image}"


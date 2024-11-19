from app.crud.ads import (
    select_ads_list as crud_select_ads_list,
    select_ads_init_info as crud_select_ads_init_info
)
from app.schemas.ads import(
    AdsInitInfoOutPut, AdsInitInfo
)
from fastapi import HTTPException
import logging
import os
from pathlib import Path
from dotenv import load_dotenv
import requests
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
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
    prompt, gpt_role, detail_content
):
    # gpt 영역
    gpt_content = gpt_role
    content = prompt + detail_content

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
    use_option, model_option, title, store_name, detail_category_name, 
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

    if use_option == 'MMS':
        resize = (262, 362)
    elif use_option == 'youtube thumbnail':
        resize = (412, 232)
    elif use_option == 'instagram story':
        resize = (412, 732)
    elif use_option == 'instagram feed':
        resize = (412, 514)
    elif use_option == 'google advertising banner':
        resize = (377, 377)
    else :
        resize= None


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

            # 이미지 리사이즈
            if resize:
                print(f"Resizing image to: {resize}")
                image = image.resize(resize, Image.LANCZOS)

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
                print(f"Resizing image to: {resize}")
                image = image.resize(resize, Image.LANCZOS)

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
                print(f"Resizing image to: {resize}")
                image = image.resize(resize, Image.LANCZOS)

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
            if use_option == 'MMS':
                resize = (256, 256)
            elif use_option == 'youtube thumbnail':
                resize = (1792, 1024)
            elif use_option == 'instagram story':
                resize = (1024, 1792)
            elif use_option == 'instagram feed':
                resize = (512, 512)
            elif use_option == 'google advertising banner':
                resize = (256, 256)
            else :
                resize= None
            resize_str = f"{resize[0]}x{resize[1]}"
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=resize_str,
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
def combine_ads(store_name, content, image_width, image_height, image, alignment="center", transparency=0.6):
    root_path = os.getenv("ROOT_PATH", ".")
    font_path = os.path.join(root_path, "app", "font", "yang.otf")  # Bold 폰트 사용
    top_font_size = 36
    bottom_font_size = 32

    # 폰트 설정
    top_font = ImageFont.truetype(font_path, top_font_size)
    bottom_font = ImageFont.truetype(font_path, bottom_font_size)
    store_name_font = ImageFont.truetype(font_path, 14)  # store_name은 작은 폰트 사용

    # RGBA 모드로 변환
    if image.mode != "RGBA":
        image = image.convert("RGBA")

    # 투명도 조정
    alpha = image.split()[3]  # 알파 채널
    alpha = ImageEnhance.Brightness(alpha).enhance(transparency)  # 투명도 적용 (0.6 = 60%)
    image.putalpha(alpha)

    draw = ImageDraw.Draw(image)

    # 텍스트를 '<br>'로 구분하여 줄 나누기
    lines = content.split('<br>')

    if len(lines) > 0:
        # 첫 번째 문장은 상단에 배치
        top_line = lines[0].strip()
        top_text_width = top_font.getbbox(top_line)[2]
        top_text_height = top_font.getbbox("A")[3] + 10  # 줄 높이 계산
        top_text_x = (image_width - top_text_width) // 2  # 중앙 정렬
        top_text_y = 60  # 상단에서 40px 여백

        # 흰색(80% 투명도)으로 top_line 추가
        draw.text((top_text_x, top_text_y), top_line, font=top_font, fill=(255, 255, 255, int(255 * 0.8)))  # 흰색 80% 투명도

    # 나머지 문장은 하단에 배치
    bottom_lines = lines[1:]  # 첫 번째 문장 제외
    line_height = bottom_font.getbbox("A")[3] + 10  # 줄 간격 포함
    text_y = (image_height * 3) // 4  # 이미지 높이의 3/4 지점에서 시작

    # 하단 텍스트 추가
    for line in bottom_lines:
        line = line.strip()
        text_width = bottom_font.getbbox(line)[2]

        # 정렬 설정
        if alignment == "center":
            text_x = (image_width - text_width) // 2
        elif alignment == "left":
            text_x = 10
        elif alignment == "right":
            text_x = image_width - text_width - 10
        else:
            raise ValueError("Invalid alignment option. Choose 'center', 'left', or 'right'.")

        # 초록색(100% 불투명도)으로 bottom_lines 추가
        draw.text((text_x, text_y), line, font=bottom_font, fill="#03FF57")  # 초록색
        text_y += line_height  # 다음 줄로 이동

    # store_name 추가 (하단의 하단)
    store_name_width = store_name_font.getbbox(store_name)[2]
    store_name_x = (image_width - store_name_width) // 2  # 중앙 정렬
    store_name_y = image_height -  50
    draw.text((store_name_x, store_name_y), store_name, font=store_name_font, fill="white")

    # 이미지 메모리에 저장
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)

    # Base64 인코딩
    base64_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{base64_image}"


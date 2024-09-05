import os
import pandas as pd
from dotenv import load_dotenv
from app.schemas.city import City
from app.schemas.district import District
from app.schemas.sub_district import SubDistrict
from app.crud.city import get_or_create_city
from app.crud.district import get_or_create_district
from app.crud.sub_district import get_or_create_sub_district
from app.db.connect import *



async def get_locations_service():
    """도시, 군/구, 읍/면/동 데이터를 한 번에 조회하는 서비스"""
    
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()

        # cities 데이터 조회
        cities_query = "SELECT city_id, city_name FROM city"
        cursor.execute(cities_query)
        cities = cursor.fetchall()

        # districts 데이터 조회
        districts_query = "SELECT district_id, city_id, district_name FROM district"
        cursor.execute(districts_query)
        districts = cursor.fetchall()

        # sub_districts 데이터 조회
        sub_districts_query = "SELECT sub_district_id, district_id, city_id, sub_district_name FROM sub_district"
        cursor.execute(sub_districts_query)
        sub_districts = cursor.fetchall()

        # 계층적 데이터 구조 생성
        return {
            "cities": cities,
            "districts": districts,
            "sub_districts": sub_districts,
        }

    finally:
        if cursor:
            cursor.close()
        connection.close()





1
# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# ROOT_PATH 환경 변수 불러오기
ROOT_PATH = os.getenv("ROOT_PATH")

# 엑셀 파일 경로 설정
excel_file_path = os.path.join(ROOT_PATH, "app", "data", "regionData", "regionData.xlsx")

def load_and_insert_city_data():
    # 엑셀 파일을 읽어옵니다.
    df = pd.read_excel(excel_file_path)

    # 모든 행을 순회하며 데이터 처리
    for index, row in df.iterrows():
        city_name = row['CITY']  # 'CITY' 열의 데이터
        district_name = row['DISTRICT']  # 'DISTRICT' 열의 데이터
        sub_district_name = row['SUB_DISTRICT']  # 'SUB_DISTRICT' 열의 데이터

        # City 처리
        city_data = City(city_name=city_name)
        city = get_or_create_city(city_data)

        # District 처리
        district_data = District(district_name=district_name, city_id=city.city_id)
        district = get_or_create_district(district_data)

        # SubDistrict 처리
        sub_district_data = SubDistrict(sub_district_name=sub_district_name, district_id=district.district_id, city_id=city.city_id)
        sub_district = get_or_create_sub_district(sub_district_data)

        print(f"Inserted/Found City: {city.city_name}, District: {district.district_name}, SubDistrict: {sub_district.sub_district_name}")

if __name__ == "__main__":
    load_and_insert_city_data()

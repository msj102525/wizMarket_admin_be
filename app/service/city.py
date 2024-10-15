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






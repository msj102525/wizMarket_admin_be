import pymysql
import pandas as pd
from app.db.connect import get_db_connection, close_connection, close_cursor, commit, rollback
from app.schemas.population import Population
from typing import List
from mysql.connector.cursor import MySQLCursorDict


def check_previous_month_data_exists(connection, previous_month):
    """저번 달 데이터가 DB에 존재하는지 확인하는 함수."""
    
    query = """
        SELECT COUNT(*) AS count
        FROM population
        WHERE reference_date = %s
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (previous_month,))
        result = cursor.fetchone()
    
    # COUNT 값을 반환
    return result[0] > 0


# 1. 전체 도시 리스트 출력
def get_all_cities() -> List[str]:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT city_name FROM city")
        cities = cursor.fetchall()
        return [city[0] for city in cities]
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# 2. 선택된 도시명으로 도시 ID 리턴
def get_city_id_by_name(city_name: str) -> int:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT city_id FROM city WHERE city_name = %s", (city_name,))
        city_id = cursor.fetchone()
        if not city_id:
            return None
        return city_id[0]
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# 3. 선택된 도시의 도시 ID로 해당하는 시/군/구 리스트 출력
def get_districts_by_city_id(city_id: int) -> List[str]:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT district_name FROM district WHERE city_id = %s", (city_id,))
        districts = cursor.fetchall()
        return [district[0] for district in districts]
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# 4. 선택된 시/군/구 명으로 시/군/구 ID 리턴
def get_district_id_by_name(district_name: str) -> int:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT district_id FROM district WHERE district_name = %s", (district_name,))
        district_id = cursor.fetchone()
        if not district_id:
            return None
        return district_id[0]
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# 5. 선택된 시/군/구 ID로 해당하는 읍/면/동 리스트 출력
def get_sub_districts_by_district_id(district_id: int) -> List[str]:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT sub_district_name FROM sub_district WHERE district_id = %s", (district_id,))
        sub_districts = cursor.fetchall()
        return [sub_district[0] for sub_district in sub_districts]  # sub_district 이름 리스트 반환
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# 선택된 지역 명으로 각각의 id 값 리턴 리턴 리턴
def get_ids_by_names(city_name: str, district_name: str, sub_district_name: str) -> dict:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()

        # 시/도 ID 조회
        cursor.execute("SELECT city_id FROM city WHERE city_name = %s", (city_name,))
        city_result = cursor.fetchone()
        if city_result is None:
            return None
        city_id = city_result[0]

        # 시/군/구 ID 조회
        cursor.execute("SELECT district_id FROM district WHERE district_name = %s AND city_id = %s", (district_name, city_id))
        district_result = cursor.fetchone()
        if district_result is None:
            return None
        district_id = district_result[0]

        # 읍/면/동 ID 조회
        cursor.execute("SELECT sub_district_id FROM sub_district WHERE sub_district_name = %s AND district_id = %s", (sub_district_name, district_id))
        sub_district_result = cursor.fetchone()
        if sub_district_result is None:
            return None
        sub_district_id = sub_district_result[0]

        return {
            "city_id": city_id,
            "district_id": district_id,
            "sub_district_id": sub_district_id
        }
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_population_data(city_id: int, district_id: int, sub_district_id: int, start_year_month: str) -> list:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        query = """
                SELECT *
                FROM population
                WHERE city_id = %s 
                  AND district_id = %s 
                  AND sub_district_id = %s 
                  AND reference_date = %s
                """
        cursor.execute(query, (city_id, district_id, sub_district_id, start_year_month))
        
        
        population = cursor.fetchall()
        
        if population:
            population_list = list(population)
            return population_list
        else:
            return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def insert_population_data(connection, population_data: Population):
    with connection.cursor() as cursor:
        insert_query = """
        INSERT INTO population (
            CITY_ID, DISTRICT_ID, SUB_DISTRICT_ID, GENDER_ID, admin_code, reference_date,
            province_name, district_name, subdistrict_name, total_population, male_population, female_population,
            age_0, age_1, age_2, age_3, age_4, age_5, age_6, age_7, age_8, age_9,
            age_10, age_11, age_12, age_13, age_14, age_15, age_16, age_17, age_18, age_19,
            age_20, age_21, age_22, age_23, age_24, age_25, age_26, age_27, age_28, age_29,
            age_30, age_31, age_32, age_33, age_34, age_35, age_36, age_37, age_38, age_39,
            age_40, age_41, age_42, age_43, age_44, age_45, age_46, age_47, age_48, age_49,
            age_50, age_51, age_52, age_53, age_54, age_55, age_56, age_57, age_58, age_59,
            age_60, age_61, age_62, age_63, age_64, age_65, age_66, age_67, age_68, age_69,
            age_70, age_71, age_72, age_73, age_74, age_75, age_76, age_77, age_78, age_79,
            age_80, age_81, age_82, age_83, age_84, age_85, age_86, age_87, age_88, age_89,
            age_90, age_91, age_92, age_93, age_94, age_95, age_96, age_97, age_98, age_99,
            age_100, age_101, age_102, age_103, age_104, age_105, age_106, age_107, age_108, age_109,
            age_110_over, created_at, updated_at
        ) VALUES (
            %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, NOW(), NOW()
        )
        """

        population_data_tuple = (
        population_data.city_id,
        population_data.district_id,
        population_data.sub_district_id,
        population_data.gender_id,
        population_data.admin_code,
        population_data.reference_date,
        population_data.province_name,
        population_data.district_name,
        population_data.subdistrict_name,
        population_data.total_population,
        population_data.male_population,
        population_data.female_population,
        population_data.age_0, population_data.age_1, population_data.age_2, population_data.age_3,
        population_data.age_4, population_data.age_5, population_data.age_6, population_data.age_7,
        population_data.age_8, population_data.age_9, population_data.age_10, population_data.age_11,
        population_data.age_12, population_data.age_13, population_data.age_14, population_data.age_15,
        population_data.age_16, population_data.age_17, population_data.age_18, population_data.age_19,
        population_data.age_20, population_data.age_21, population_data.age_22, population_data.age_23,
        population_data.age_24, population_data.age_25, population_data.age_26, population_data.age_27,
        population_data.age_28, population_data.age_29, population_data.age_30, population_data.age_31,
        population_data.age_32, population_data.age_33, population_data.age_34, population_data.age_35,
        population_data.age_36, population_data.age_37, population_data.age_38, population_data.age_39,
        population_data.age_40, population_data.age_41, population_data.age_42, population_data.age_43,
        population_data.age_44, population_data.age_45, population_data.age_46, population_data.age_47,
        population_data.age_48, population_data.age_49, population_data.age_50, population_data.age_51,
        population_data.age_52, population_data.age_53, population_data.age_54, population_data.age_55,
        population_data.age_56, population_data.age_57, population_data.age_58, population_data.age_59,
        population_data.age_60, population_data.age_61, population_data.age_62, population_data.age_63,
        population_data.age_64, population_data.age_65, population_data.age_66, population_data.age_67,
        population_data.age_68, population_data.age_69, population_data.age_70, population_data.age_71,
        population_data.age_72, population_data.age_73, population_data.age_74, population_data.age_75,
        population_data.age_76, population_data.age_77, population_data.age_78, population_data.age_79,
        population_data.age_80, population_data.age_81, population_data.age_82, population_data.age_83,
        population_data.age_84, population_data.age_85, population_data.age_86, population_data.age_87,
        population_data.age_88, population_data.age_89, population_data.age_90, population_data.age_91,
        population_data.age_92, population_data.age_93, population_data.age_94, population_data.age_95,
        population_data.age_96, population_data.age_97, population_data.age_98, population_data.age_99,
        population_data.age_100, population_data.age_101, population_data.age_102, population_data.age_103,
        population_data.age_104, population_data.age_105, population_data.age_106, population_data.age_107,
        population_data.age_108, population_data.age_109, population_data.age_110_over
        )

        cursor.execute(insert_query, population_data_tuple)




    
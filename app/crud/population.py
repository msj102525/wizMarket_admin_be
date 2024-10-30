import logging
import pymysql
import pandas as pd
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)
from app.schemas.population import Population, PopulationOutput, Population_by_ages, Population_by_gender, PopulationFindByFilter
from typing import List
from mysql.connector.cursor import MySQLCursorDict
from typing import List, Dict
import decimal


def download_data_ex(filters):
    # 데이터베이스 연결
    connection = get_db_connection()
    cursor = None

    # 연령대에 따른 나이 범위 매핑
    age_groups = {
        "age_under_10": range(0, 10),
        "age_10s": range(10, 20),
        "age_20s": range(20, 30),
        "age_30s": range(30, 40),
        "age_40s": range(40, 50),
        "age_50s": range(50, 60),
        "age_60_plus": range(60, 111),  # 60세 이상은 60세부터 110세까지 포함
    }

    try:
        # 기본 쿼리 시작
        query = """
            SELECT
                city.city_name,
                district.district_name,
                sub_district.sub_district_name,
                p.male_population,
                p.female_population,
                p.reference_date,
                gender.gender_name
        """

        # 나이 컬럼들을 동적으로 선택
        age_columns = []

        if filters.get("ageGroupMin") or filters.get("ageGroupMax"):
            # ageGroupMin 및 ageGroupMax 처리
            if filters.get("ageGroupMin"):
                min_age_range = age_groups[filters["ageGroupMin"]]
            else:
                min_age_range = age_groups["age_under_10"]

            if filters.get("ageGroupMax"):
                max_age_range = age_groups[filters["ageGroupMax"]]
            else:
                max_age_range = age_groups["age_60_plus"]

            # 최소 나이부터 최대 나이까지의 범위에 해당하는 컬럼을 동적으로 생성
            min_age = min(min_age_range)
            max_age = max(max_age_range)
            # print(min_age, max_age)

            # 선택된 나이 범위에 해당하는 모든 컬럼 추가
            age_columns = [f"p.age_{i}" for i in range(min_age, min(max_age + 1, 110))]

            if max_age >= 110:
                age_columns.append("p.age_110_over")  # age_110_over 추가

        else:
            # 나이 필터가 없으면 모든 나이대 컬럼을 추가
            age_columns = [f"p.age_{i}" for i in range(0, 110)]  # age_0 ~ age_109
            age_columns.append("p.age_110_over")  # age_110_over 추가

        # 나이 컬럼을 쿼리에 추가
        if age_columns:
            query += ", " + ", ".join(age_columns)

        query += """
            FROM population p
            JOIN city ON p.city_id = city.city_id
            JOIN district ON p.district_id = district.district_id
            JOIN sub_district ON p.sub_district_id = sub_district.sub_district_id
            JOIN gender ON p.gender_id = gender.gender_id
            WHERE p.reference_date = '2024-07-31'
        """

        # 파라미터 목록 초기화
        query_params = []

        # 필터 값에 따라 동적 쿼리 추가
        if filters.get("city"):
            query += " AND p.city_id = %s"
            query_params.append(filters["city"])

        if filters.get("district"):
            query += " AND p.district_id = %s"
            query_params.append(filters["district"])

        if filters.get("subDistrict"):
            query += " AND p.sub_district_id = %s"
            query_params.append(filters["subDistrict"])

        if filters.get("gender"):
            query += " AND p.gender_id = %s"
            query_params.append(filters["gender"])

        query += " ORDER BY city.city_name ASC, district.district_name ASC, sub_district.sub_district_name ASC"

        # 쿼리 실행
        cursor = connection.cursor()
        cursor.execute(query, query_params)
        result = cursor.fetchall()
        # print(query)
        return result

    except Exception as e:
        print(f"데이터베이스 조회 중 오류 발생: {e}")
        return None

    finally:
        if cursor:
            cursor.close()
        connection.close()


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


def convert_decimal_to_float(data):
    if isinstance(data, list):
        for item in data:
            for key, value in item.items():
                if isinstance(value, decimal.Decimal):
                    item[key] = float(value)
    return data


def get_filtered_population_data(filters):
    # 데이터베이스 연결
    connection = get_db_connection()
    cursor = None
    results = []
    # print(filters)
    try:
        # 나이대 범위 설정
        age_groups = {
            'age_under_10s': 'p.AGE_UNDER_10s',
            'age_10s': 'p.AGE_10s',
            'age_20s': 'p.AGE_20s',
            'age_30s': 'p.AGE_30s',
            'age_40s': 'p.AGE_40s',
            'age_50s': 'p.AGE_50s',
            'age_plus_60s': 'p.AGE_PLUS_60s'
        }

        age_keys = list(age_groups.keys())
        
        # 필터값에 따라 ageGroupMin과 ageGroupMax 설정
        if "ageGroupMin" in filters and "ageGroupMax" in filters:
            # min과 max가 모두 있는 경우
            min_index = age_keys.index(filters["ageGroupMin"])
            max_index = age_keys.index(filters["ageGroupMax"])
            selected_age_fields = [age_groups[key] for key in age_keys[min_index:max_index + 1]]
        elif "ageGroupMin" in filters:
            # min만 있는 경우 min부터 60대 이상까지
            min_index = age_keys.index(filters["ageGroupMin"])
            selected_age_fields = [age_groups[key] for key in age_keys[min_index:]]
        elif "ageGroupMax" in filters:
            # max만 있는 경우 10대 이하부터 max까지
            max_index = age_keys.index(filters["ageGroupMax"])
            selected_age_fields = [age_groups[key] for key in age_keys[:max_index + 1]]
        else:
            # min과 max 모두 없는 경우 모든 연령대 선택
            selected_age_fields = list(age_groups.values())

        # 동적으로 SELECT 필드 생성
        select_fields = ', '.join(selected_age_fields) + ", p.TOTAL_POPULATION_BY_GENDER, p.TOTAL_POPULATION, p.REF_DATE"

        query = f"""
            SELECT {select_fields},
                city.city_name AS CITY_NAME, 
                district.district_name AS DISTRICT_NAME, 
                sub_district.sub_district_name AS SUB_DISTRICT_NAME
            FROM population_age p
            JOIN city ON p.city_id = city.city_id
            JOIN district ON p.district_id = district.district_id
            JOIN sub_district ON p.sub_district_id = sub_district.sub_district_id
            WHERE 1=1 
        """

        # 필터 조건에 따라 WHERE 절 구성
        params = []

        # 시/도 필터
        if "city" in filters:
            query += " AND p.city_id = %s"
            params.append(filters["city"])

        # 군/구 필터
        if "district" in filters:
            query += " AND p.district_id = %s"
            params.append(filters["district"])

        # 읍/면/동 필터
        if "subDistrict" in filters:
            query += " AND p.sub_district_id = %s"
            params.append(filters["subDistrict"])

        # 시작 월 필터
        if "startDate" in filters:
            query += " AND p.ref_date >= %s"
            params.append(filters["startDate"])

        # 끝 월 필터
        if "endDate" in filters:
            query += " AND p.ref_date <= %s"
            params.append(filters["endDate"])

        # 성별 필터
        if "gender" in filters:
            query += " AND p.gender_id = %s"
            params.append(filters["gender"])

        # 쿼리 실행
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, params)
        rows = cursor.fetchall()

        for row in rows:
            population_age = PopulationFindByFilter(
                city_name=row.get("CITY_NAME"),
                district_name=row.get("DISTRICT_NAME"),
                sub_district_name=row.get("SUB_DISTRICT_NAME"),
                age_under_10s=row.get("AGE_UNDER_10s"),
                age_10s=row.get("AGE_10s"),
                age_20s=row.get("AGE_20s"),
                age_30s=row.get("AGE_30s"),
                age_40s=row.get("AGE_40s"),
                age_50s=row.get("AGE_50s"),
                age_plus_60s=row.get("AGE_PLUS_60s", 0),
                total_population_by_gender=row.get("TOTAL_POPULATION_BY_GENDER"),
                total_population=row.get("TOTAL_POPULATION"),
                ref_date=row.get("REF_DATE")
            )
            results.append(population_age)
        # print(results)
        return results

    finally:
        # 커서와 연결 닫기
        if cursor:
            cursor.close()
        if connection:
            connection.close()




###### gpt 프롬프트 용 ######
def select_age_pop_list_by_sub_district_id(
        SUB_DISTRICT_ID: int,
) -> Population_by_ages:
    # 데이터베이스 연결
    connection = get_db_connection()
    cursor = None
    # print(filters)
    try:
        cursor = connection.cursor()

        # 기본적으로 항상 선택할 컬럼
        pop_query = """
            SELECT 
                sum(age_0 + age_1 + age_2 + age_3 + age_4 + age_5 + age_6 + age_7 + age_8 + age_9) AS age_under_10,
                sum(age_10 + age_11 + age_12 + age_13 + age_14 + age_15 + age_16 + age_17 + age_18 + age_19) AS age_10s,
                sum(age_20 + age_21 + age_22 + age_23 + age_24 + age_25 + age_26 + age_27 + age_28 + age_29) AS age_20s,
                sum(age_30 + age_31 + age_32 + age_33 + age_34 + age_35 + age_36 + age_37 + age_38 + age_39) AS age_30s,
                sum(age_40 + age_41 + age_42 + age_43 + age_44 + age_45 + age_46 + age_47 + age_48 + age_49) AS age_40s,
                sum(age_50 + age_51 + age_52 + age_53 + age_54 + age_55 + age_56 + age_57 + age_58 + age_59) AS age_50s,
                sum(age_60 + age_61 + age_62 + age_63 + age_64 + p.age_65 + p.age_66 + age_67 + age_68 + age_69 + \
                        age_70 + age_71 + age_72 + age_73 + age_74 + age_75 + age_76 + age_77 + age_78 + age_79 + \
                        age_80 + age_81 + age_82 + age_83 + age_84 + age_85 + age_86 + age_87 + age_88 + age_89 + \
                        age_90 + age_91 + age_92 + age_93 + age_94 + age_95 + age_96 + age_97 + age_98 + age_99 + \
                        age_100 + age_101 + age_102 + age_103 + age_104 + age_105 + age_106 + age_107 + age_108 + \
                        age_109 + age_110_over) AS age_60_plus
            FROM population p
            WHERE sub_district_id = %s 
            AND reference_date = "2024-07-31"
        """

        # 쿼리 실행
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(pop_query, SUB_DISTRICT_ID )
        result: Population_by_ages = cursor.fetchone()
        return result
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def select_gender_pop_list_by_sub_district_id(
        SUB_DISTRICT_ID: int,
) -> Population_by_ages:
    # 데이터베이스 연결
    connection = get_db_connection()
    cursor = None
    # print(filters)
    try:
        cursor = connection.cursor()

        # 기본적으로 항상 선택할 컬럼
        pop_query = """
            SELECT 
                male_population, female_population
            FROM population p
            WHERE sub_district_id = %s 
            AND reference_date = "2024-07-31"
        """

        # 쿼리 실행
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(pop_query, SUB_DISTRICT_ID )
        result: Population_by_gender = cursor.fetchall()
        return result
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()




def get_latest_population_data_by_subdistrict_id(sub_district_id: int) -> PopulationOutput:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)
    try:
        base_select = """
            p.POPULATION_ID AS pop_id,                
            city.city_name AS city_name,              
            district.district_name AS district_name,   
            sub_district.sub_district_name AS sub_district_name,  
            p.male_population,  -- 남성 인구수
            p.female_population, -- 여성 인구수
            p.reference_date
        """
        age_groups = {
            "age_under_10": "(p.age_0 + p.age_1 + p.age_2 + p.age_3 + p.age_4 + p.age_5 + p.age_6 + p.age_7 + p.age_8 + p.age_9) AS age_under_10",
            "age_10s": "(p.age_10 + p.age_11 + p.age_12 + p.age_13 + p.age_14 + p.age_15 + p.age_16 + p.age_17 + p.age_18 + p.age_19) AS age_10s",
            "age_20s": "(p.age_20 + p.age_21 + p.age_22 + p.age_23 + p.age_24 + p.age_25 + p.age_26 + p.age_27 + p.age_28 + p.age_29) AS age_20s",
            "age_30s": "(p.age_30 + p.age_31 + p.age_32 + p.age_33 + p.age_34 + p.age_35 + p.age_36 + p.age_37 + p.age_38 + p.age_39) AS age_30s",
            "age_40s": "(p.age_40 + p.age_41 + p.age_42 + p.age_43 + p.age_44 + p.age_45 + p.age_46 + p.age_47 + p.age_48 + p.age_49) AS age_40s",
            "age_50s": "(p.age_50 + p.age_51 + p.age_52 + p.age_53 + p.age_54 + p.age_55 + p.age_56 + p.age_57 + p.age_58 + p.age_59) AS age_50s",
            "age_60_plus": "(p.age_60 + p.age_61 + p.age_62 + p.age_63 + p.age_64 + p.age_65 + p.age_66 + p.age_67 + p.age_68 + p.age_69 + \
                        p.age_70 + p.age_71 + p.age_72 + p.age_73 + p.age_74 + p.age_75 + p.age_76 + p.age_77 + p.age_78 + p.age_79 + \
                        p.age_80 + p.age_81 + p.age_82 + p.age_83 + p.age_84 + p.age_85 + p.age_86 + p.age_87 + p.age_88 + p.age_89 + \
                        p.age_90 + p.age_91 + p.age_92 + p.age_93 + p.age_94 + p.age_95 + p.age_96 + p.age_97 + p.age_98 + p.age_99 + \
                        p.age_100 + p.age_101 + p.age_102 + p.age_103 + p.age_104 + p.age_105 + p.age_106 + p.age_107 + p.age_108 + \
                        p.age_109 + p.age_110_over) AS age_60_plus",
        }

        selected_age_groups = list(age_groups.values())

        query = f"""
            SELECT 
                {base_select},
                {', '.join(selected_age_groups)}
            FROM population p
            JOIN city ON p.CITY_ID = city.city_id               
            JOIN district ON p.DISTRICT_ID = district.district_id 
            JOIN sub_district ON p.SUB_DISTRICT_ID = sub_district.sub_district_id
            WHERE p.sub_district_id = %s
            ORDER BY p.reference_date DESC
            LIMIT 2
        """

        cursor.execute(query, (sub_district_id,))
        rows = cursor.fetchall()  

        if rows:
            combined_population = {
                "pop_id": rows[0]["pop_id"],
                "city_name": rows[0]["city_name"],
                "district_name": rows[0]["district_name"],
                "sub_district_name": rows[0]["sub_district_name"],
                "male_population": 0,
                "female_population": 0,
                "total_population": 0,
                "male_population_percent": 0,
                "female_population_percent": 0,
                "reference_date": rows[0]["reference_date"],
                "age_under_10": 0,
                "age_10s": 0,
                "age_20s": 0,
                "age_30s": 0,
                "age_40s": 0,
                "age_50s": 0,
                "age_60_plus": 0,
            }

            for row in rows:
                if row["male_population"] > 0:
                    combined_population["male_population"] += row["male_population"]
                if row["female_population"] > 0:
                    combined_population["female_population"] += row["female_population"]

            combined_population["total_population"] = (
                combined_population["male_population"] + combined_population["female_population"]
            )

            for key in selected_age_groups:
                age_group_name = key.split(" AS ")[1]
                combined_population[age_group_name] += row.get(age_group_name, 0)

            # 소숫점 두 번째 자리에서 반올림
            combined_population["male_population"] = round(combined_population["male_population"], 2)
            combined_population["female_population"] = round(combined_population["female_population"], 2)
            combined_population["total_population"] = round(combined_population["total_population"], 2)

            # 남성과 여성 비율 계산
            if combined_population["total_population"] > 0:
                combined_population["male_population_percent"] = round((combined_population["male_population"] / combined_population["total_population"]) * 100, 1)
                combined_population["female_population_percent"] = round((combined_population["female_population"] / combined_population["total_population"]) * 100, 1)

            for key in selected_age_groups:
                age_group_name = key.split(" AS ")[1]
                combined_population[age_group_name] = round(combined_population[age_group_name], 2)

            population_output = PopulationOutput(**combined_population)
            return population_output
        
        return None  

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

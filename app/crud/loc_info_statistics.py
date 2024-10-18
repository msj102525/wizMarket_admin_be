import logging
from typing import Dict, List, Optional
import pymysql
from app.db.connect import get_db_connection, close_connection, close_cursor
from app.schemas.commercial_district import CommercialStatisticsData
from app.schemas.statistics import CommercialStatistics, StatisticsJscoreOutput

############### 값 조회 ######################
# 전국 J-Score 값 조회
def get_stat_data(filters_dict):
    # print(filters_dict)

    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None

    try:
        query = """
            SELECT 
                   city.city_name AS city_name, 
                   district.district_name AS district_name, 
                   sub_district.sub_district_name AS sub_district_name,
                   statistics.sub_district_id,
                   stat_item.column_name as column_name,
                   AVG_VAL, MED_VAL, STD_VAL, MAX_VALUE, MIN_VALUE, J_SCORE
            FROM statistics
            JOIN city ON statistics.city_id = city.city_id
            JOIN district ON statistics.district_id = district.district_id
            LEFT JOIN sub_district ON statistics.sub_district_id = sub_district.sub_district_id
            JOIN stat_item ON statistics.STAT_ITEM_ID = stat_item.STAT_ITEM_ID
            WHERE 1=1
        """
        query_params = []

        # 필터 값이 존재할 때만 쿼리에 조건 추가
        if filters_dict.get("city") is not None:
            query += " AND statistics.city_id = %s"
            query_params.append(filters_dict["city"])

        if filters_dict.get("district") is not None:
            query += " AND statistics.district_id = %s"
            query_params.append(filters_dict["district"])

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        result = cursor.fetchall()

        return result

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료

# 시/도 내의 동 끼리 비교 J-Score 값 조회
def get_stat_data_by_city(filters_dict):
    # print(filters_dict)

    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None

    try:
        query = """
            SELECT 
                   city.city_name AS city_name, 
                   district.district_name AS district_name, 
                   sub_district.sub_district_name AS sub_district_name,
                   statistics.sub_district_id,
                   stat_item.column_name as column_name,
                   AVG_VAL, MED_VAL, STD_VAL, MAX_VALUE, MIN_VALUE, J_SCORE
            FROM statistics
            JOIN city ON statistics.city_id = city.city_id
            JOIN district ON statistics.district_id = district.district_id
            LEFT JOIN sub_district ON statistics.sub_district_id = sub_district.sub_district_id
            JOIN stat_item ON statistics.STAT_ITEM_ID = stat_item.STAT_ITEM_ID
            WHERE 1=1
        """
        query_params = []

        # 필터 값이 존재할 때만 쿼리에 조건 추가
        if filters_dict.get("city") is not None:
            query += " AND statistics.city_id = %s"
            query_params.append(filters_dict["city"])

        if filters_dict.get("district") is not None:
            query += " AND statistics.district_id = %s"
            query_params.append(filters_dict["district"])

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        result = cursor.fetchall()

        return result

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료
    

# 시/군/구 내의 동 끼리 비교 J-Score 값 조회
def get_stat_data_by_distirct(filters_dict):
    # print(filters_dict)

    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None

    try:
        query = """
            SELECT 
                   city.city_name AS city_name, 
                   district.district_name AS district_name, 
                   sub_district.sub_district_name AS sub_district_name,
                   statistics.sub_district_id,
                   stat_item.column_name as column_name,
                   AVG_VAL, MED_VAL, STD_VAL, MAX_VALUE, MIN_VALUE, J_SCORE
            FROM statistics
            JOIN city ON statistics.city_id = city.city_id
            JOIN district ON statistics.district_id = district.district_id
            LEFT JOIN sub_district ON statistics.sub_district_id = sub_district.sub_district_id
            JOIN stat_item ON statistics.STAT_ITEM_ID = stat_item.STAT_ITEM_ID
            WHERE 1=1
        """
        query_params = []

        # 필터 값이 존재할 때만 쿼리에 조건 추가
        if filters_dict.get("city") is not None:
            query += " AND statistics.city_id = %s"
            query_params.append(filters_dict["city"])

        if filters_dict.get("district") is not None:
            query += " AND statistics.district_id = %s"
            query_params.append(filters_dict["district"])

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        result = cursor.fetchall()

        return result

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료
import pymysql
from app.db.connect import *
from typing import Optional
from app.schemas.loc_info import LocalInfoStatisticsResponse, StatisticsResult, LocInfoResult

def fetch_loc_info_by_ids(city_id: int, district_id: int, sub_district_id: int) -> Optional[dict]:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor()
        query = """
            SELECT * FROM loc_info
            WHERE city_id = %s AND district_id = %s AND sub_district_id = %s
        """
        cursor.execute(query, (city_id, district_id, sub_district_id))
        result = cursor.fetchone()
        return result
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

######## GPT 프롬프트 용 ######################
def select_local_info_statistics_by_sub_district_id(sub_district_id: int) -> LocalInfoStatisticsResponse:
    connection = get_db_connection()
    cursor = None
    try:
        cursor = connection.cursor(pymysql.cursors.DictCursor)  # DictCursor 사용
       
        # 첫 번째 쿼리: loc_info
        loc_info_query = """
            SELECT shop, move_pop, sales, work_pop, income, spend, house, resident 
            FROM loc_info
            WHERE sub_district_id = %s
        """
        cursor.execute(loc_info_query, (sub_district_id,))
        loc_info_result = cursor.fetchone()  # 이 결과는 DictCursor로 인해 딕셔너리로 반환됨

        # 두 번째 쿼리: statistics
        statistics_query = """
            SELECT j_score
            FROM statistics
            WHERE sub_district_id = %s
            AND stat_item_id between 1 and 8
        """
        cursor.execute(statistics_query, (sub_district_id,))
        statistics_result = cursor.fetchall()  # DictCursor로 딕셔너리 형태로 반환됨

        # Pydantic 모델로 변환
        loc_info_data = LocInfoResult(**loc_info_result)
        statistics_data = [StatisticsResult(j_score=row['j_score']) for row in statistics_result]

        return LocalInfoStatisticsResponse(loc_info=loc_info_data, statistics=statistics_data)
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def get_all_corr():
    """주어진 필터 조건을 바탕으로 데이터를 조회하는 함수"""

    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None

    try:
        query = """
            SELECT *
            FROM loc_info
            JOIN city ON loc_info.city_id = city.city_id
            JOIN district ON loc_info.district_id = district.district_id
            JOIN sub_district ON loc_info.sub_district_id = sub_district.sub_district_id
            WHERE 1=1
        """
        query_params = []

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        all_corr = cursor.fetchall()

        return all_corr

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료



def get_filter_corr(filters):
    """주어진 필터 조건을 바탕으로 데이터를 조회하는 함수"""

    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None

    try:
        query = """
            SELECT *
            FROM loc_info
            JOIN city ON loc_info.city_id = city.city_id
            JOIN district ON loc_info.district_id = district.district_id
            JOIN sub_district ON loc_info.sub_district_id = sub_district.sub_district_id
            WHERE 1=1
        """
        query_params = []

        # 필터 값이 존재할 때만 쿼리에 조건 추가
        if filters.get("city") is not None:
            query += " AND loc_info.city_id = %s"
            query_params.append(filters["city"])

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        filter_corr = cursor.fetchall()

        return filter_corr

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료



################################################        


def get_filtered_locations(filters):
    """주어진 필터 조건을 바탕으로 데이터를 조회하는 함수"""

    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None
    try:
        query = """
            SELECT 
                   city.city_name AS city_name, 
                   district.district_name AS district_name, 
                   sub_district.sub_district_name AS sub_district_name,
                   loc_info.loc_info_id,
                   loc_info.shop, loc_info.move_pop, loc_info.sales, loc_info.work_pop, 
                   loc_info.income, loc_info.spend, loc_info.house, loc_info.resident,
                   loc_info.y_m
            FROM loc_info
            JOIN city ON loc_info.city_id = city.city_id
            JOIN district ON loc_info.district_id = district.district_id
            JOIN sub_district ON loc_info.sub_district_id = sub_district.sub_district_id
            WHERE 1=1
        """
        query_params = []

        # 필터 값이 존재할 때만 쿼리에 조건 추가
        if filters.get("city") is not None:
            query += " AND loc_info.city_id = %s"
            query_params.append(filters["city"])

        if filters.get("district") is not None:
            query += " AND loc_info.district_id = %s"
            query_params.append(filters["district"])

        if filters.get("subDistrict") is not None:
            query += " AND loc_info.sub_district_id = %s"
            query_params.append(filters["subDistrict"])



        if filters.get("shopMin") is not None:
            query += " AND shop >= %s"
            query_params.append(filters["shopMin"])
        
        if filters.get("move_popMin") is not None:
            query += " AND move_pop >= %s"
            query_params.append(filters["move_popMin"])

        if filters.get("salesMin") is not None:
            query += " AND sales >= %s"
            query_params.append(filters["salesMin"])

        if filters.get("work_popMin") is not None:
            query += " AND work_pop >= %s"
            query_params.append(filters["work_popMin"])

        if filters.get("incomeMin") is not None:
            query += " AND income >= %s"
            query_params.append(filters["incomeMin"])
        
        if filters.get("spendMin") is not None:
            query += " AND spend >= %s"
            query_params.append(filters["spendMin"])

        if filters.get("houseMin") is not None:
            query += " AND house >= %s"
            query_params.append(filters["houseMin"])
        
        if filters.get("residentMin") is not None:
            query += " AND resident >= %s"
            query_params.append(filters["resident"])




        if filters.get("shopMax") is not None:
            query += " AND shop <= %s"
            query_params.append(filters["shopMax"])
        
        if filters.get("move_popMax") is not None:
            query += " AND move_pop <= %s"
            query_params.append(filters["move_popMax"])
        
        if filters.get("salesMax") is not None:
            query += " AND sales <= %s"
            query_params.append(filters["salesMax"])
        
        if filters.get("worK_popMax") is not None:
            query += " AND work_pop <= %s"
            query_params.append(filters["worK_popMax"])
        
        if filters.get("incomeMax") is not None:
            query += " AND income <= %s"
            query_params.append(filters["incomeMax"])
        
        if filters.get("spendMax") is not None:
            query += " AND spend <= %s"
            query_params.append(filters["spendMax"])
        
        if filters.get("houseMax") is not None:
            query += " AND house <= %s"
            query_params.append(filters["houseMax"])
        
        if filters.get("residentMax") is not None:
            query += " AND resident <= %s"
            query_params.append(filters["residentMax"])


        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        result = cursor.fetchall()

        for item in result:
            # 8개의 값이 모두 0인 경우에만 '정보 없음'으로 변환
            if (
                item['shop'] == 0 and item['move_pop'] == 0 and item['sales'] == 0 and
                item['work_pop'] == 0 and item['income'] == 0 and item['spend'] == 0 and
                item['house'] == 0 and item['resident'] == 0
            ):
                item['shop'] = '정보 없음'
                item['move_pop'] = '정보 없음'
                item['sales'] = '정보 없음'
                item['work_pop'] = '정보 없음'
                item['income'] = '정보 없음'
                item['spend'] = '정보 없음'
                item['house'] = '정보 없음'
                item['resident'] = '정보 없음'

        return result

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료


def get_all_region_id():
    """
    모든 city_id와 district_id, sub_district_id 쌍을 가져옴
    """
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # 모든 city_id와 district_id 쌍을 가져오는 쿼리
        query = """
            SELECT 
                   city.city_name AS city_name, 
                   city.city_id AS city_id, 
                   district.district_name AS district_name, 
                   district.district_id AS district_id, 
                   sub_district.sub_district_name AS sub_district_name,
                   sub_district.sub_district_id AS sub_district_id
            FROM sub_district
            JOIN city ON sub_district.city_id = city.city_id
            JOIN district ON sub_district.district_id = district.district_id
        """

        cursor.execute(query)
        result = cursor.fetchall()

        # city_id, district_id 쌍을 반환
        return result

    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)
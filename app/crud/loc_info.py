import pymysql
from app.db.connect import *
from typing import Optional
from app.schemas.loc_info import LocalInfoStatisticsResponse, StatisticsResult, LocInfoResult
from app.db.connect import get_db_connection, close_connection, close_cursor
from app.schemas.loc_info import (
    StatDataForExetend, StatDataByCityForExetend, StatDataByDistrictForExetend, StatDataForNation, StatDataForInit
)
import pandas as pd

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


def get_all_corr(year):
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
            WHERE loc_info.Y_M = %s
        """
        

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, (year,))
        all_corr = cursor.fetchall()

        return all_corr

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료



def get_filter_corr(filters, year):
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
            WHERE loc_info.Y_M = %s
        """
        query_params = [year]

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

    connection = get_db_connection()
    cursor = None
    try:
        # 지역 관련 필터 조건 생성
        query_params_loc_info = []
        query_params_statistics = []
        location_conditions = ""

        if filters.get("city") is not None:
            location_conditions += " AND city.city_id = %s"
            query_params_loc_info.append(filters["city"])
            query_params_statistics.append(filters["city"])

        if filters.get("district") is not None:
            location_conditions += " AND district.district_id = %s"
            query_params_loc_info.append(filters["district"])
            query_params_statistics.append(filters["district"])

        if filters.get("subDistrict") is not None:
            location_conditions += " AND sub_district.sub_district_id = %s"
            query_params_loc_info.append(filters["subDistrict"])
            query_params_statistics.append(filters["subDistrict"])

        # 날짜 관련 필터 조건 생성
        date_conditions_loc_info = ""
        date_conditions_statistics = ""
        
        if filters.get("selectedOptions"):
            date_placeholders_loc_info = " OR ".join(["loc_info.y_m = %s" for _ in filters["selectedOptions"]])
            date_conditions_loc_info = f" AND ({date_placeholders_loc_info})"
            query_params_loc_info.extend(filters["selectedOptions"])

            date_placeholders_stats = " OR ".join(["loc_info_statistics.ref_date = %s" for _ in filters["selectedOptions"]])
            date_conditions_statistics = f" AND ({date_placeholders_stats})"
            query_params_statistics.extend(filters["selectedOptions"])

        # loc_info 쿼리 (지역 필터 및 나머지 필터 조건)
        query_1 = f"""
            SELECT 
                city.city_name AS city_name, 
                district.district_name AS district_name, 
                sub_district.sub_district_name AS sub_district_name,
                city.city_id AS city_id, 
                district.district_id AS district_id, 
                sub_district.sub_district_id AS sub_district_id,
                loc_info.loc_info_id,
                loc_info.shop, loc_info.move_pop, loc_info.sales, loc_info.work_pop, 
                loc_info.income, loc_info.spend, loc_info.house, loc_info.resident,
                loc_info.y_m
            FROM loc_info
            LEFT JOIN city ON loc_info.city_id = city.city_id
            LEFT JOIN district ON loc_info.district_id = district.district_id
            LEFT JOIN sub_district ON loc_info.sub_district_id = sub_district.sub_district_id
            WHERE 1=1 {location_conditions} {date_conditions_loc_info}
        """

        # 나머지 필터 조건 추가 (loc_info에만 적용)
        additional_conditions = [
            ("shopMin", "shop >= %s"),
            ("move_popMin", "move_pop >= %s"),
            ("salesMin", "sales >= %s"),
            ("work_popMin", "work_pop >= %s"),
            ("incomeMin", "income >= %s"),
            ("spendMin", "spend >= %s"),
            ("houseMin", "house >= %s"),
            ("residentMin", "resident >= %s"),
            ("shopMax", "shop <= %s"),
            ("move_popMax", "move_pop <= %s"),
            ("salesMax", "sales <= %s"),
            ("work_popMax", "work_pop <= %s"),
            ("incomeMax", "income <= %s"),
            ("spendMax", "spend <= %s"),
            ("houseMax", "house <= %s"),
            ("residentMax", "resident <= %s"),
        ]

        for filter_key, condition in additional_conditions:
            if filters.get(filter_key) is not None:
                query_1 += f" AND {condition}"
                query_params_loc_info.append(filters[filter_key])

        # Execute the loc_info query
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query_1, query_params_loc_info)
        loc_info_results = cursor.fetchall()

        # loc_info_statistics 쿼리 (지역 및 날짜 필터 조건만 적용)
        query_2 = f"""
            SELECT
                city.city_name AS city_name, 
                district.district_name AS district_name, 
                sub_district.sub_district_name AS sub_district_name,
                city.city_id AS city_id, 
                district.district_id AS district_id, 
                sub_district.sub_district_id AS sub_district_id,
                loc_info_statistics.j_score_rank,
                loc_info_statistics.j_score_per,
                loc_info_statistics.j_score,
                loc_info_statistics.ref_date
            FROM loc_info_statistics
            LEFT JOIN city ON loc_info_statistics.city_id = city.city_id
            LEFT JOIN district ON loc_info_statistics.district_id = district.district_id
            LEFT JOIN sub_district ON loc_info_statistics.sub_district_id = sub_district.sub_district_id
            WHERE loc_info_statistics.target_item = 'j_score_avg' 
            {location_conditions} {date_conditions_statistics}
        """
        
        cursor.execute(query_2, query_params_statistics)
        statistics_results = cursor.fetchall()

        # loc_info_results와 statistics_results를 병합
        merged_results = []
        for loc_info in loc_info_results:
            matching_stats = next(
                (stats for stats in statistics_results 
                 if stats['city_id'] == loc_info['city_id'] and 
                    stats['district_id'] == loc_info['district_id'] and 
                    stats['sub_district_id'] == loc_info['sub_district_id'] and
                    stats['ref_date'] == loc_info['y_m']), 
                {}
            )
            merged_record = {**loc_info, **matching_stats}
            merged_results.append(merged_record)

        return merged_results

    finally:
        if cursor:
            cursor.close()
        connection.close()




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




################  값 조회 ######################
# 초기 데이터 : 통계값
def get_stat_data_avg()-> StatDataForInit:
    results = []
    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None

    try:
        query = """
            (SELECT 
                city.city_id AS CITY_ID, 
                city.city_name AS CITY_NAME, 
                district.district_id AS DISTRICT_ID, 
                district.district_name AS DISTRICT_NAME, 
                sub_district.sub_district_id AS SUB_DISTRICT_ID,
                sub_district.sub_district_name AS SUB_DISTRICT_NAME,
                TARGET_ITEM, REF_DATE,
                AVG_VAL, MED_VAL, STD_VAL, MAX_VAL, MIN_VAL
            FROM loc_info_statistics li
            JOIN city ON li.city_id = city.city_id
            JOIN district ON li.district_id = district.district_id
            JOIN sub_district ON li.sub_district_id = sub_district.sub_district_id
            WHERE li.city_id IS NOT NULL 
            AND li.district_id IS NOT NULL 
            AND li.sub_district_id IS NOT NULL
            AND li.REF_DATE = '2024-08-01'
            LIMIT 9)

            UNION ALL

            (SELECT 
                city.city_id AS CITY_ID, 
                city.city_name AS CITY_NAME, 
                district.district_id AS DISTRICT_ID, 
                district.district_name AS DISTRICT_NAME, 
                sub_district.sub_district_id AS SUB_DISTRICT_ID,
                sub_district.sub_district_name AS SUB_DISTRICT_NAME,
                TARGET_ITEM, REF_DATE,
                AVG_VAL, MED_VAL, STD_VAL, MAX_VAL, MIN_VAL
            FROM loc_info_statistics li
            JOIN city ON li.city_id = city.city_id
            JOIN district ON li.district_id = district.district_id
            JOIN sub_district ON li.sub_district_id = sub_district.sub_district_id
            WHERE li.city_id IS NOT NULL 
            AND li.district_id IS NOT NULL 
            AND li.sub_district_id IS NOT NULL
            AND li.REF_DATE = '2024-10-01'
            LIMIT 9);
        """
        query_params = []

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        rows = cursor.fetchall()

        for row in rows:
            loc_info_by_region = StatDataForInit(
                city_id= row.get("CITY_ID"),
                city_name= row.get("CITY_NAME"),
                district_id=row.get("DISTRICT_ID"),
                district_name=row.get("DISTRICT_NAME"),
                sub_district_id=row.get("SUB_DISTRICT_ID"),
                sub_district_name=row.get("SUB_DISTRICT_NAME"),
                target_item=row.get("TARGET_ITEM"),
                ref_date=row.get("REF_DATE"),
                avg_val=row.get("AVG_VAL"),
                med_val= row.get("MED_VAL"),
                std_val= row.get("STD_VAL"),
                max_val= row.get("MAX_VAL"),
                min_val= row.get("MIN_VAL")
            )
            results.append(loc_info_by_region)

        return results

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료



# 전국에서 동 끼리 비교 J-Score 값 조회
def get_stat_data(filters_dict)-> StatDataForExetend:

    results = []
    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None


    try:
        query = """
            SELECT 
                   city.city_id AS CITY_ID, 
                   city.city_name AS CITY_NAME, 
                   district.district_id AS DISTRICT_ID, 
                   district.district_name AS DISTRICT_NAME, 
                   sub_district.sub_district_id AS SUB_DISTRICT_ID,
                   sub_district.sub_district_name AS SUB_DISTRICT_NAME,
                   TARGET_ITEM, REF_DATE,
                   AVG_VAL, MED_VAL, STD_VAL, MAX_VAL, MIN_VAL, J_SCORE_PER, J_SCORE_RANK, J_SCORE
            FROM loc_info_statistics li
            JOIN city ON li.city_id = city.city_id
            JOIN district ON li.district_id = district.district_id
            JOIN sub_district ON li.sub_district_id = sub_district.sub_district_id
            WHERE li.city_id is not null and li.district_id is not null and li.sub_district_id is not null
        """
        query_params = []

        selected_options = filters_dict.get("selectedOptions")
        if selected_options:
            if len(selected_options) == 1:
                query += " AND li.ref_date = %s"
                query_params.append(selected_options[0])
            else:
                # 여러 개의 ref_date를 OR로 연결
                date_conditions = " OR ".join(["li.ref_date = %s" for _ in selected_options])
                query += f" AND ({date_conditions})"
                query_params.extend(selected_options)

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        rows = cursor.fetchall()

        for row in rows:
            loc_info_by_region = StatDataForExetend(
                city_id= row.get("CITY_ID"),
                city_name= row.get("CITY_NAME"),
                district_id=row.get("DISTRICT_ID"),
                district_name=row.get("DISTRICT_NAME"),
                sub_district_id=row.get("SUB_DISTRICT_ID"),
                sub_district_name=row.get("SUB_DISTRICT_NAME"),
                target_item=row.get("TARGET_ITEM"),
                ref_date=row.get("REF_DATE"),
                avg_val=row.get("AVG_VAL"),
                med_val= row.get("MED_VAL"),
                std_val= row.get("STD_VAL"),
                max_val= row.get("MAX_VAL"),
                min_val= row.get("MIN_VAL"),
                j_score= row.get("J_SCORE"),
                j_score_rank = row.get("J_SCORE_RANK"),
                j_score_per = row.get("J_SCORE_PER")
            )
            results.append(loc_info_by_region)
        
        return results

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료


# 시/도 내의 동 끼리 비교 J-Score 값 조회
def get_stat_data_by_city(filters_dict: dict) -> StatDataByCityForExetend:
    results = []
    connection = get_db_connection()
    cursor = None

    try:
        # 첫 번째 쿼리: loc_info_statistics 조회
        query1 = """
            SELECT 
                   city.city_id AS CITY_ID, 
                   city.city_name AS CITY_NAME, 
                   sub_district.sub_district_id AS SUB_DISTRICT_ID,
                   sub_district.sub_district_name AS SUB_DISTRICT_NAME,
                   TARGET_ITEM, REF_DATE,
                   AVG_VAL, MED_VAL, STD_VAL, MAX_VAL, MIN_VAL, J_SCORE_PER, J_SCORE_RANK, J_SCORE
            FROM loc_info_statistics li
            JOIN city ON li.city_id = city.city_id
            JOIN sub_district ON li.sub_district_id = sub_district.sub_district_id
            WHERE li.city_id IS NOT NULL 
              AND li.district_id IS NULL 
              AND li.sub_district_id IS NOT NULL
              
        """
        query_params = []

        if filters_dict.get("city") is not None:
            query1 += " AND li.city_id = %s"
            query_params.append(filters_dict["city"])

        selected_options = filters_dict.get("selectedOptions")
        if selected_options:
            if len(selected_options) == 1:
                query1 += " AND li.ref_date = %s"
                query_params.append(selected_options[0])
            else:
                # 여러 개의 ref_date를 OR로 연결
                date_conditions = " OR ".join(["li.ref_date = %s" for _ in selected_options])
                query1 += f" AND ({date_conditions})"
                query_params.extend(selected_options)

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query1, query_params)
        stat_rows = cursor.fetchall()

        # 두 번째 쿼리: district_name 조회
        query2 = """
            SELECT 
                   district.district_name AS DISTRICT_NAME,
                   sd.sub_district_id AS SUB_DISTRICT_ID
            FROM sub_district sd
            JOIN city ON sd.city_id = city.city_id
            JOIN district ON sd.district_id = district.district_id
            WHERE city.city_id = %s
        """
        cursor.execute(query2, (filters_dict["city"],))
        district_rows = cursor.fetchall()

        # sub_district_id를 기준으로 district_name을 매칭하여 결과 합치기
        district_map = {row["SUB_DISTRICT_ID"]: row["DISTRICT_NAME"] for row in district_rows}
        

        for row in stat_rows:
            sub_district_id = row.get("SUB_DISTRICT_ID")
            district_name = district_map.get(sub_district_id, "데이터 없음")

            loc_info_by_region = StatDataByCityForExetend(
                city_id= row.get("CITY_ID"),
                city_name= row.get("CITY_NAME"),
                sub_district_id=sub_district_id,
                sub_district_name=row.get("SUB_DISTRICT_NAME"),
                district_name=district_name,  # 추가된 district_name
                target_item=row.get("TARGET_ITEM"),
                ref_date=row.get("REF_DATE"),
                avg_val=row.get("AVG_VAL"),
                med_val= row.get("MED_VAL"),
                std_val= row.get("STD_VAL"),
                max_val= row.get("MAX_VAL"),
                min_val= row.get("MIN_VAL"),
                j_score= row.get("J_SCORE"),
                j_score_rank= row.get("J_SCORE_RANK"),
                j_score_per= row.get("J_SCORE_PER")
            )
            results.append(loc_info_by_region)

        
        return results

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료


    

# 시/군/구 내의 동 끼리 비교 J-Score 값 조회
def get_stat_data_by_distirct(filters_dict: dict) -> StatDataByDistrictForExetend:
    results = []
    connection = get_db_connection()
    cursor = None

    try:
        # 첫 번째 쿼리: loc_info_statistics 조회
        query1 = """
            SELECT 
                   district.district_id AS DISTRICT_ID, 
                   district.district_name AS DISTRICT_NAME, 
                   sub_district.sub_district_id AS SUB_DISTRICT_ID,
                   sub_district.sub_district_name AS SUB_DISTRICT_NAME,
                   TARGET_ITEM, REF_DATE,
                   AVG_VAL, MED_VAL, STD_VAL, MAX_VAL, MIN_VAL, J_SCORE_PER, J_SCORE_RANK, J_SCORE
            FROM loc_info_statistics li
            JOIN district ON li.district_id = district.district_id
            JOIN sub_district ON li.sub_district_id = sub_district.sub_district_id
            WHERE li.city_id IS NULL 
              AND li.district_id IS NOT NULL 
              AND li.sub_district_id IS NOT NULL
              
        """
        query_params = []

        if filters_dict.get("district") is not None:
            query1 += " AND li.district_id = %s"
            query_params.append(filters_dict["district"])

        selected_options = filters_dict.get("selectedOptions")
        if selected_options:
            if len(selected_options) == 1:
                query1 += " AND li.ref_date = %s"
                query_params.append(selected_options[0])
            else:
                # 여러 개의 ref_date를 OR로 연결
                date_conditions = " OR ".join(["li.ref_date = %s" for _ in selected_options])
                query1 += f" AND ({date_conditions})"
                query_params.extend(selected_options)

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query1, query_params)
        stat_rows = cursor.fetchall()


        # 두 번째 쿼리: district_name 조회
        query2 = """
            SELECT 
                   city.city_name AS CITY_NAME,
                   sd.sub_district_id AS SUB_DISTRICT_ID
            FROM sub_district sd
            JOIN city ON sd.city_id = city.city_id
            JOIN district ON sd.district_id = district.district_id
            WHERE district.district_id = %s
        """
        cursor.execute(query2, (filters_dict["district"],))
        city_rows = cursor.fetchall()
        # sub_district_id를 기준으로 district_name을 매칭하여 결과 합치기
        city_map = {row["SUB_DISTRICT_ID"]: row["CITY_NAME"] for row in city_rows}
        
        for row in stat_rows:
            sub_district_id = row.get("SUB_DISTRICT_ID")
            city_name = city_map.get(sub_district_id, "데이터 없음")

            loc_info_by_region = StatDataByDistrictForExetend(
                district_id= row.get("DISTRICT_ID"),
                district_name= row.get("DISTRICT_NAME"),
                sub_district_id=sub_district_id,
                sub_district_name=row.get("SUB_DISTRICT_NAME"),
                city_name=city_name,  
                target_item=row.get("TARGET_ITEM"),
                ref_date=row.get("REF_DATE"),
                avg_val=row.get("AVG_VAL"),
                med_val= row.get("MED_VAL"),
                std_val= row.get("STD_VAL"),
                max_val= row.get("MAX_VAL"),
                min_val= row.get("MIN_VAL"),
                j_score= row.get("J_SCORE"),
                j_score_rank = row.get("J_SCORE_RANK"),
                j_score_per= row.get("J_SCORE_PER")
            )
            results.append(loc_info_by_region)


        return results

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료


# 동 하나 J-Score 값 조회
def get_stat_data_by_sub_distirct(filters_dict: dict) -> StatDataForExetend:
    results = []
    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None

    try:
        query = """
            SELECT 
                   city.city_id AS CITY_ID, 
                   city.city_name AS CITY_NAME, 
                   district.district_id AS DISTRICT_ID, 
                   district.district_name AS DISTRICT_NAME, 
                   sub_district.sub_district_id AS SUB_DISTRICT_ID,
                   sub_district.sub_district_name AS SUB_DISTRICT_NAME,
                   TARGET_ITEM, REF_DATE,
                   AVG_VAL, MED_VAL, STD_VAL, MAX_VAL, MIN_VAL, J_SCORE_PER, J_SCORE_RANK, J_SCORE
            FROM loc_info_statistics li
            JOIN city ON li.city_id = city.city_id
            JOIN district ON li.district_id = district.district_id
            JOIN sub_district ON li.sub_district_id = sub_district.sub_district_id
            WHERE li.city_id is not null and li.district_id is not null and li.sub_district_id is not null
            
        """
        query_params = []

        # 필터 값이 존재할 때만 쿼리에 조건 추가
        if filters_dict.get("city") is not None:
            query += " AND li.city_id = %s"
            query_params.append(filters_dict["city"])

        if filters_dict.get("district") is not None:
            query += " AND li.district_id = %s"
            query_params.append(filters_dict["district"])
        
        if filters_dict.get("subDistrict") is not None:
            query += " AND li.sub_district_id = %s"
            query_params.append(filters_dict["subDistrict"])

        selected_options = filters_dict.get("selectedOptions")
        if selected_options:
            if len(selected_options) == 1:
                query += " AND li.ref_date = %s"
                query_params.append(selected_options[0])
            else:
                # 여러 개의 ref_date를 OR로 연결
                date_conditions = " OR ".join(["li.ref_date = %s" for _ in selected_options])
                query += f" AND ({date_conditions})"
                query_params.extend(selected_options)

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        rows = cursor.fetchall()

        for row in rows:
            loc_info_by_region = StatDataForExetend(
                city_id= row.get("CITY_ID"),
                city_name= row.get("CITY_NAME"),
                district_id=row.get("DISTRICT_ID"),
                district_name=row.get("DISTRICT_NAME"),
                sub_district_id=row.get("SUB_DISTRICT_ID"),
                sub_district_name=row.get("SUB_DISTRICT_NAME"),
                target_item=row.get("TARGET_ITEM"),
                ref_date=row.get("REF_DATE"),
                avg_val=row.get("AVG_VAL"),
                med_val= row.get("MED_VAL"),
                std_val= row.get("STD_VAL"),
                max_val= row.get("MAX_VAL"),
                min_val= row.get("MIN_VAL"),
                j_score= row.get("J_SCORE"),
                j_score_per= row.get("J_SCORE_PER"),
                j_score_rank= row.get("J_SCORE_RANK")
            )
            results.append(loc_info_by_region)
        print(results)
        return results

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료



########################


def get_nation_j_score(filters_dict)-> StatDataForNation:
    results = []
    # 여기서 직접 DB 연결을 설정
    connection = get_db_connection()
    cursor = None


    try:
        query = """
            SELECT 
                   city.city_id AS CITY_ID, 
                   city.city_name AS CITY_NAME, 
                   district.district_id AS DISTRICT_ID, 
                   district.district_name AS DISTRICT_NAME, 
                   sub_district.sub_district_id AS SUB_DISTRICT_ID,
                   sub_district.sub_district_name AS SUB_DISTRICT_NAME,
                   li.TARGET_ITEM, li.REF_DATE,
                   li.J_SCORE, li.J_SCORE_PER, li.J_SCORE_RANK,
                   li.REF_DATE
            FROM loc_info_statistics li
            JOIN city ON li.city_id = city.city_id
            JOIN district ON li.district_id = district.district_id
            JOIN sub_district ON li.sub_district_id = sub_district.sub_district_id
            WHERE li.city_id is not null and li.district_id is not null and li.sub_district_id is not null
        """
        query_params = []

        # 필터 값이 존재할 때만 쿼리에 조건 추가
        if filters_dict.get("city") is not None:
            query += " AND li.city_id = %s"
            query_params.append(filters_dict["city"])

        if filters_dict.get("district") is not None:
            query += " AND li.district_id = %s"
            query_params.append(filters_dict["district"])

        if filters_dict.get("subDistrict") is not None:
            query += " AND li.sub_district_id = %s"
            query_params.append(filters_dict["subDistrict"])

        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(query, query_params)
        rows = cursor.fetchall()

        for row in rows:
            loc_info_by_region = StatDataForNation(
                city_id= row.get("CITY_ID"),
                city_name= row.get("CITY_NAME"),
                district_id=row.get("DISTRICT_ID"),
                district_name=row.get("DISTRICT_NAME"),
                sub_district_id=row.get("SUB_DISTRICT_ID"),
                sub_district_name=row.get("SUB_DISTRICT_NAME"),
                target_item=row.get("TARGET_ITEM"),
                j_score = row.get("J_SCORE"),
                j_score_rank = row.get("J_SCORE_RANK"),
                j_score_per = row.get("J_SCORE_PER"),
                ref_date=row.get("REF_DATE")
            )
            results.append(loc_info_by_region)

        return results

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료







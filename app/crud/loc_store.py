import logging
from typing import List
import pymysql
from app.db.connect import close_connection, close_cursor, get_db_connection
from app.schemas.loc_info import LocationInfoReportOutput
from app.schemas.loc_store import (
    BusinessAreaCategoryReportOutput,
    BizDetailCategoryIdOutPut,
    RisingMenuOutPut,
    BizCategoriesNameOutPut,
    LocStoreInfoForContentOutPut,
)
from fastapi import HTTPException


def parse_quarter(quarter_str):
    year, quarter = quarter_str.split(".")
    return int(year), int(quarter)


def execute_query(connection, query, params=None, fetch="all"):
    """유틸리티 함수: 쿼리 실행 및 결과 반환"""
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SET SESSION MAX_EXECUTION_TIME=30000;")  # 30초 제한
        cursor.execute(query, params or [])
        return cursor.fetchall() if fetch == "all" else cursor.fetchone()


def build_query_with_filters(base_query, filters, additional_conditions=None):
    """필터 조건을 추가하여 쿼리 생성"""
    query = base_query
    params = []

    # 필터 조건 추가
    if filters.get("city"):
        query += " AND local_store.city_id = %s"
        params.append(filters["city"])

    if filters.get("district"):
        query += " AND local_store.district_id = %s"
        params.append(filters["district"])

    if filters.get("subDistrict"):
        query += " AND local_store.sub_district_id = %s"
        params.append(filters["subDistrict"])

    if filters.get("storeName"):
        if filters.get("matchType") == "=":
            query += " AND local_store.store_name = %s"
            params.append(filters["storeName"])
        else:
            query += " AND local_store.store_name LIKE %s"
            params.append(f"%{filters['storeName']}%")

    # 추가 조건이 있는 경우 처리
    if additional_conditions:
        query += additional_conditions["query"]
        params.extend(additional_conditions["params"])

    return query, params


def get_small_category_codes(connection, filters):
    """카테고리 매핑 로직: 소분류 코드 리스트 반환"""
    category_query = """
        SELECT b.biz_detail_category_id AS detail_id
        FROM biz_detail_category b
        JOIN biz_sub_category s ON b.biz_sub_category_id = s.biz_sub_category_id
        JOIN biz_main_category m ON s.biz_main_category_id = m.biz_main_category_id
        WHERE 1 = 1
    """
    query_params = []
    if filters.get("mainCategory"):
        category_query += " AND m.biz_main_category_id = %s"
        query_params.append(filters["mainCategory"])
    if filters.get("subCategory"):
        category_query += " AND s.biz_sub_category_id = %s"
        query_params.append(filters["subCategory"])
    if filters.get("detailCategory"):
        category_query += " AND b.biz_detail_category_id = %s"
        query_params.append(filters["detailCategory"])

    detail_ids = [item["detail_id"] for item in execute_query(connection, category_query, query_params)]

    if not detail_ids:
        return []

    placeholders = ", ".join(["%s"] * len(detail_ids))
    mapping_query = f"""
        SELECT detail_category_code
        FROM business_area_category
        WHERE business_area_category_id IN (
            SELECT business_area_category_id 
            FROM detail_category_mapping 
            WHERE detail_category_id IN ({placeholders})
        )
    """
    return [item["detail_category_code"] for item in execute_query(connection, mapping_query, detail_ids)]


def get_filtered_loc_store(filters: dict):
    """필터 조건에 따라 상권 정보 조회"""
    connection = get_db_connection()
    try:
        # 기본 쿼리
        base_count_query = """
            SELECT count(*) as total
            FROM local_store
            JOIN city ON local_store.city_id = city.city_id
            JOIN district ON local_store.district_id = district.district_id
            JOIN sub_district ON local_store.sub_district_id = sub_district.sub_district_id
            WHERE IS_EXIST = 1
        """
        base_data_query = """
            SELECT 
                local_store.store_business_number, local_store.store_name, local_store.branch_name, local_store.road_name_address,
                local_store.large_category_name, local_store.medium_category_name, local_store.small_category_name,
                local_store.industry_name, local_store.building_name, local_store.new_postal_code, local_store.dong_info,
                local_store.floor_info, local_store.unit_info, local_store.local_year, local_store.local_quarter,
                city.city_name AS city_name, 
                district.district_name AS district_name, 
                sub_district.sub_district_name AS sub_district_name
            FROM local_store
            JOIN city ON local_store.city_id = city.city_id
            JOIN district ON local_store.district_id = district.district_id
            JOIN sub_district ON local_store.sub_district_id = sub_district.sub_district_id
            WHERE IS_EXIST = 1
        """

        # 카테고리 관련 조건 추가
        additional_conditions = {"query": "", "params": []}
        if filters.get("reference") != 3:
            small_category_codes = get_small_category_codes(connection, filters)
            if small_category_codes:
                placeholders = ", ".join(["%s"] * len(small_category_codes))
                additional_conditions["query"] += f" AND local_store.small_category_code IN ({placeholders})"
                additional_conditions["params"].extend(small_category_codes)

        # 쿼리 생성
        count_query, count_params = build_query_with_filters(base_count_query, filters, additional_conditions)
        data_query, data_params = build_query_with_filters(base_data_query, filters, additional_conditions)

        # 페이징 처리
        page = filters.get("page", 1)
        page_size = filters.get("page_size", 20)
        offset = (page - 1) * page_size
        data_query += " ORDER BY local_store.store_name LIMIT %s OFFSET %s"
        data_params.extend([page_size, offset])

        # 쿼리 실행
        total_items = execute_query(connection, count_query, count_params, fetch="one")
        result = execute_query(connection, data_query, data_params)

        return result, total_items
    finally:
        connection.close()


# 엑셀 다운로드
def select_download_store_list(filters: dict):
    """필터 조건에 따라 상권 정보 조회"""
    connection = get_db_connection()
    try:
        # 기본 쿼리
        base_data_query = """
            SELECT 
                local_store.store_business_number, local_store.store_name, local_store.branch_name, local_store.road_name_address,
                local_store.large_category_name, local_store.medium_category_name, local_store.small_category_name,
                local_store.industry_name, local_store.building_name, local_store.new_postal_code, local_store.dong_info,
                local_store.floor_info, local_store.unit_info, local_store.local_year, local_store.local_quarter,
                city.city_name AS city_name, 
                district.district_name AS district_name, 
                sub_district.sub_district_name AS sub_district_name
            FROM local_store
            JOIN city ON local_store.city_id = city.city_id
            JOIN district ON local_store.district_id = district.district_id
            JOIN sub_district ON local_store.sub_district_id = sub_district.sub_district_id
            WHERE IS_EXIST = 1
        """

        # 카테고리 관련 조건 추가
        additional_conditions = {"query": "", "params": []}
        if filters.get("reference") != 3:
            small_category_codes = get_small_category_codes(connection, filters)
            if small_category_codes:
                placeholders = ", ".join(["%s"] * len(small_category_codes))
                additional_conditions["query"] += f" AND local_store.small_category_code IN ({placeholders})"
                additional_conditions["params"].extend(small_category_codes)

        # 쿼리 생성
        data_query, data_params = build_query_with_filters(base_data_query, filters, additional_conditions)

        # 쿼리 실행
        result = execute_query(connection, data_query, data_params)

        return result
    finally:
        connection.close()





def check_previous_quarter_data_exists(connection, year, quarter):
    """저번 분기의 데이터가 DB에 있는지 확인하는 함수"""

    # SQL 쿼리 작성 (저번 분기의 데이터가 존재하는지 확인)
    query = "SELECT COUNT(*) AS count FROM local_store WHERE local_year = %s AND local_quarter = %s"

    with connection.cursor() as cursor:
        cursor.execute(query, (year, quarter))
        result = cursor.fetchone()

    # count 값이 0이면 데이터가 없는 것
    return result[0] > 0


# 읍/면/동 id로 주거인구, 직장인구, 세대수, 업소수, 소득 조회
def select_loc_info_report_data_by_sub_district_id(
    sub_district_id: int,
) -> LocationInfoReportOutput:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        select_query = """
            SELECT 
                RESIDENT, -- 주거인구
                WORK_POP, -- 직장인구
                HOUSE, -- 세대수
                SHOP, -- 업소수
                INCOME -- 소득
            FROM loc_info
            WHERE sub_district_id = %s;
        """

        cursor.execute(select_query, (sub_district_id,))
        row = cursor.fetchone()

        if row:
            return LocationInfoReportOutput(
                resident=row["RESIDENT"],
                work_pop=row["WORK_POP"],
                house=row["HOUSE"],
                shop=row["SHOP"],
                income=row["INCOME"],
            )
        else:
            return None  # 데이터가 없을 경우

    finally:
        if cursor:
            cursor.close()
        connection.close()


def select_business_area_category_id_by_reference_id(
    reference_id: int, small_category_name: str
) -> BusinessAreaCategoryReportOutput:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        select_query = """
            SELECT 
                BUSINESS_AREA_CATEGORY_ID
            FROM BUSINESS_AREA_CATEGORY
            WHERE reference_id = %s
            AND detail_category_name = %s;
        """

        cursor.execute(select_query, (reference_id, small_category_name))
        row = cursor.fetchone()

        if row:
            return BusinessAreaCategoryReportOutput(
                business_area_category_id=row["BUSINESS_AREA_CATEGORY_ID"]
            )
        else:
            return None  # 데이터가 없을 경우

    finally:
        if cursor:
            cursor.close()
        connection.close()


def select_biz_detail_category_id_by_detail_category_id(
    business_area_category_id: int,
) -> List[BizDetailCategoryIdOutPut]:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        select_query = """
            SELECT 
                dcm.REP_ID,
                bdc.BIZ_DETAIL_CATEGORY_NAME
            FROM DETAIL_CATEGORY_MAPPING dcm
            JOIN biz_detail_category bdc 
                ON dcm.REP_ID = bdc.biz_detail_category_id
            WHERE dcm.business_area_category_id = %s;
        """

        cursor.execute(select_query, (business_area_category_id))
        row = cursor.fetchone()

        if row:
            return BizDetailCategoryIdOutPut(
                rep_id=row["REP_ID"],
                biz_detail_category_name=row["BIZ_DETAIL_CATEGORY_NAME"],
            )
        else:
            return None  # 데이터가 없을 경우

    finally:
        if cursor:
            cursor.close()
        connection.close()


def select_categories_name_by_rep_id(
    business_area_category_id: int,
) -> BizCategoriesNameOutPut:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        select_query = """
            SELECT 
                bmc.BIZ_MAIN_CATEGORY_NAME,
                bsc.BIZ_SUB_CATEGORY_NAME,
                bdc.BIZ_DETAIL_CATEGORY_NAME
            FROM BIZ_DETAIL_CATEGORY bdc
            JOIN BIZ_SUB_CATEGORY bsc
                ON bsc.BIZ_SUB_CATEGORY_ID = bdc.BIZ_SUB_CATEGORY_ID
            JOIN BIZ_MAIN_CATEGORY bmc
                ON bsc.BIZ_MAIN_CATEGORY_ID = bmc.BIZ_MAIN_CATEGORY_ID
            WHERE bdc.BIZ_DETAIL_CATEGORY_ID = %s;
        """

        cursor.execute(select_query, (business_area_category_id))
        row = cursor.fetchone()

        if row:
            return BizCategoriesNameOutPut(
                biz_main_category_name=row["BIZ_MAIN_CATEGORY_NAME"],
                biz_sub_category_name=row["BIZ_SUB_CATEGORY_NAME"],
                biz_detail_category_name=row["BIZ_DETAIL_CATEGORY_NAME"],
            )
        else:
            return None  # 데이터가 없을 경우

    finally:
        if cursor:
            cursor.close()
        connection.close()


def select_rising_menu_by_sub_district_id_rep_id(
    sub_district_id: int, rep_id: int
) -> RisingMenuOutPut:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    try:
        select_query = """
            SELECT 
                MARKET_SIZE, AVERAGE_SALES, AVERAGE_PAYMENT, USAGE_COUNT,
                AVG_PROFIT_PER_MON, AVG_PROFIT_PER_TUE, AVG_PROFIT_PER_WED, AVG_PROFIT_PER_THU, AVG_PROFIT_PER_FRI, AVG_PROFIT_PER_SAT, AVG_PROFIT_PER_SUN,
                AVG_PROFIT_PER_06_09, AVG_PROFIT_PER_09_12, AVG_PROFIT_PER_12_15, AVG_PROFIT_PER_15_18, AVG_PROFIT_PER_18_21, AVG_PROFIT_PER_21_24, AVG_PROFIT_PER_24_06,
                AVG_CLIENT_PER_M_20, AVG_CLIENT_PER_M_30, AVG_CLIENT_PER_M_40, AVG_CLIENT_PER_M_50, AVG_CLIENT_PER_M_60,
                AVG_CLIENT_PER_F_20, AVG_CLIENT_PER_F_30, AVG_CLIENT_PER_F_40, AVG_CLIENT_PER_F_50, AVG_CLIENT_PER_F_60, 
                TOP_MENU_1, TOP_MENU_2, TOP_MENU_3, TOP_MENU_4, TOP_MENU_5
            FROM commercial_district
            WHERE sub_district_id = %s
            AND biz_detail_category_id = %s;
        """

        cursor.execute(select_query, (sub_district_id, rep_id))
        row = cursor.fetchone()

        if row:
            return RisingMenuOutPut(
                market_size=row["MARKET_SIZE"],
                average_sales=row["AVERAGE_SALES"],
                average_payment=row["AVERAGE_PAYMENT"],
                usage_count=row["USAGE_COUNT"],
                avg_profit_per_mon=row["AVG_PROFIT_PER_MON"],
                avg_profit_per_tue=row["AVG_PROFIT_PER_TUE"],
                avg_profit_per_wed=row["AVG_PROFIT_PER_WED"],
                avg_profit_per_thu=row["AVG_PROFIT_PER_THU"],
                avg_profit_per_fri=row["AVG_PROFIT_PER_FRI"],
                avg_profit_per_sat=row["AVG_PROFIT_PER_SAT"],
                avg_profit_per_sun=row["AVG_PROFIT_PER_SUN"],
                avg_profit_per_06_09=row["AVG_PROFIT_PER_06_09"],
                avg_profit_per_09_12=row["AVG_PROFIT_PER_09_12"],
                avg_profit_per_12_15=row["AVG_PROFIT_PER_12_15"],
                avg_profit_per_15_18=row["AVG_PROFIT_PER_15_18"],
                avg_profit_per_18_21=row["AVG_PROFIT_PER_18_21"],
                avg_profit_per_21_24=row["AVG_PROFIT_PER_21_24"],
                avg_profit_per_24_06=row["AVG_PROFIT_PER_24_06"],
                avg_client_per_m_20=row["AVG_CLIENT_PER_M_20"],
                avg_client_per_m_30=row["AVG_CLIENT_PER_M_30"],
                avg_client_per_m_40=row["AVG_CLIENT_PER_M_40"],
                avg_client_per_m_50=row["AVG_CLIENT_PER_M_50"],
                avg_client_per_m_60=row["AVG_CLIENT_PER_M_60"],
                avg_client_per_f_20=row["AVG_CLIENT_PER_F_20"],
                avg_client_per_f_30=row["AVG_CLIENT_PER_F_30"],
                avg_client_per_f_40=row["AVG_CLIENT_PER_F_40"],
                avg_client_per_f_50=row["AVG_CLIENT_PER_F_50"],
                avg_client_per_f_60=row["AVG_CLIENT_PER_F_60"],
                top_menu_1=row["TOP_MENU_1"],
                top_menu_2=row["TOP_MENU_2"],
                top_menu_3=row["TOP_MENU_3"],
                top_menu_4=row["TOP_MENU_4"],
                top_menu_5=row["TOP_MENU_5"],
            )
        else:
            return None  # 데이터가 없을 경우

    finally:
        if cursor:
            cursor.close()
        connection.close()


def select_loc_store_for_content_by_store_business_number(
    store_business_number: str,
) -> LocStoreInfoForContentOutPut:

    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)

    try:
        if connection.open:

            select_query = """
                SELECT 
                STORE_BUSINESS_NUMBER, 
                STORE_NAME,
                ROAD_NAME_ADDRESS
            FROM
                LOCAL_STORE
            WHERE
                STORE_BUSINESS_NUMBER = %s
            ;
            """

            cursor.execute(select_query, (store_business_number,))

            row = cursor.fetchone()

            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"LocStoreInfoForContentOutPut {store_business_number}에 해당하는 매장 정보를 찾을 수 없습니다.",
                )

            result = LocStoreInfoForContentOutPut(
                store_business_number=row.get("STORE_BUSINESS_NUMBER"),
                store_name=row.get("STORE_NAME"),
                road_name_address=row.get("ROAD_NAME_ADDRESS"),
            )

            # logger.info(f"Result for business ID {store_business_id}: {result}")
            return result

    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected Error select_loc_store_for_content_by_store_business_number: {e}"
        )
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)

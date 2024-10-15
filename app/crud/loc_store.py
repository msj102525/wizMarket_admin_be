import logging
from typing import List
import pymysql
from app.db.connect import close_connection, close_cursor, get_db_connection
from app.schemas.loc_info import LocationInfoReportOutput
from app.schemas.loc_store import (
    LocalStoreInfo,
    LocalStoreLatLng,
    LocalStoreSubdistrict,
    LocalStoreCityDistrictSubDistrict,
    BusinessAreaCategoryReportOutput,
    BizDetailCategoryIdOutPut,
    RisingMenuOutPut,
    BizCategoriesNameOutPut
)

# crud/loc_store.py


def parse_quarter(quarter_str):
    year, quarter = quarter_str.split(".")
    return int(year), int(quarter)


def get_filtered_loc_store(filters: dict):

    connection = get_db_connection()
    cursor = None
    total_items = 0  # 총 아이템 개수를 저장할 변수

    try:
        # 총 개수 구하기 위한 쿼리
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SET SESSION MAX_EXECUTION_TIME=10000;")  # 10초로 제한

        count_query = """
            SELECT COUNT(*) as total
            FROM local_store
            JOIN city ON local_store.city_id = city.city_id
            JOIN district ON local_store.district_id = district.district_id
            JOIN sub_district ON local_store.sub_district_id = sub_district.sub_district_id
            WHERE 1=1 and local_year = 2024 and local_quarter = 2
        """
        query_params = []

        # 필터 조건 추가 (총 개수 구하는 쿼리에도 동일한 조건 사용)
        if filters.get("city") is not None:
            count_query += " AND local_store.city_id = %s"
            query_params.append(filters["city"])

        if filters.get("district") is not None:
            count_query += " AND local_store.district_id = %s"
            query_params.append(filters["district"])

        if filters.get("subDistrict") is not None:
            count_query += " AND local_store.sub_district_id = %s"
            query_params.append(filters["subDistrict"])

        if filters.get("mainCategory") is not None:
            count_query += " AND local_store.large_category_code = %s"
            query_params.append(filters["mainCategory"])

        if filters.get("subCategory") is not None:
            count_query += " AND local_store.medium_category_code = %s"
            query_params.append(filters["subCategory"])

        if filters.get("detailCategory") is not None:
            count_query += " AND local_store.small_category_code = %s"
            query_params.append(filters["detailCategory"])

        # 백엔드에서 검색 쿼리 처리
        if filters.get("storeName"):
            if filters.get("matchType") == "=":
                count_query += " AND local_store.store_name = %s"
                query_params.append(filters["storeName"])  # 정확히 일치
            else:
                count_query += " AND local_store.store_name LIKE %s"
                query_params.append(
                    f"%{filters['storeName']}%"  # '%storeName%'로 포함 검색 처리
                )

        # 총 개수 계산 쿼리 실행
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute(count_query, query_params)
        total_items = cursor.fetchone()["total"]  # 총 개수

        # 데이터를 가져오는 쿼리 (페이징 적용)
        data_query = """
            SELECT 
                local_store.store_business_number, local_store.store_name, local_store.branch_name, local_store.road_name_address,
                local_store.large_category_name, local_store.medium_category_name, local_store.small_category_name,
                local_store.industry_name, local_store.building_name, local_store.new_postal_code, local_store.dong_info, local_store.floor_info,
                local_store.unit_info, local_store.local_year, local_store.local_quarter, local_store.CREATED_AT, local_store.UPDATED_AT,
                city.city_name AS city_name, 
                district.district_name AS district_name, 
                sub_district.sub_district_name AS sub_district_name
            FROM local_store
            JOIN city ON local_store.city_id = city.city_id
            JOIN district ON local_store.district_id = district.district_id
            JOIN sub_district ON local_store.sub_district_id = sub_district.sub_district_id
            WHERE 1=1
        """

        # 동일한 필터 조건 적용
        data_query += count_query[
            count_query.find("WHERE 1=1") + len("WHERE 1=1") :
        ]  # 필터 조건 재사용
        data_query += " ORDER BY local_store.store_name"

        # 페이징 처리
        page = filters.get("page", 1)  # 기본값 1
        page_size = filters.get("page_size", 20)  # 기본값 20
        offset = (page - 1) * page_size

        # LIMIT과 OFFSET 추가
        data_query += " LIMIT %s OFFSET %s"
        query_params.append(page_size)
        query_params.append(offset)

        # print(data_query)
        # 데이터 조회 쿼리 실행
        cursor.execute(data_query, query_params)
        result = cursor.fetchall()

        return result, total_items  # 데이터와 총 개수 반환

    finally:
        if cursor:
            cursor.close()
        connection.close()  # 연결 종료


def check_previous_quarter_data_exists(connection, year, quarter):
    """저번 분기의 데이터가 DB에 있는지 확인하는 함수"""

    # SQL 쿼리 작성 (저번 분기의 데이터가 존재하는지 확인)
    query = "SELECT COUNT(*) AS count FROM local_store WHERE local_year = %s AND local_quarter = %s"

    with connection.cursor() as cursor:
        cursor.execute(query, (year, quarter))
        result = cursor.fetchone()

    # count 값이 0이면 데이터가 없는 것
    return result[0] > 0


def insert_data_to_loc_store(connection, data):
    try:
        with connection.cursor() as cursor:
            sql = """
            INSERT INTO local_store (
                CITY_ID, DISTRICT_ID, SUB_DISTRICT_ID,  
                STORE_BUSINESS_NUMBER, store_name, branch_name,
                large_category_code, large_category_name,
                medium_category_code, medium_category_name,
                small_category_code, small_category_name,
                industry_code, industry_name,
                province_code, province_name, district_code,
                district_name, administrative_dong_code, administrative_dong_name,
                legal_dong_code, legal_dong_name,
                lot_number_code, land_category_code, land_category_name,
                lot_main_number, lot_sub_number, lot_address,
                road_name_code, road_name, building_main_number,
                building_sub_number, building_management_number, building_name,
                road_name_address, old_postal_code, new_postal_code,
                dong_info, floor_info, unit_info,
                longitude, latitude, local_year, local_quarter,
                CREATED_AT, UPDATED_AT
            ) VALUES (
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, 
                %s, %s, %s, %s,
                NOW(), NOW()
            )
            """

            # 디버깅을 위해 각 항목을 개별적으로 테스트
            try:
                cursor.execute(
                    sql,
                    (
                        data["CITY_ID"],
                        data["DISTRICT_ID"],
                        data["SUB_DISTRICT_ID"],
                        data["STORE_BUSINESS_NUMBER"],
                        data["store_name"],
                        data["branch_name"],
                        data["large_category_code"],
                        data["large_category_name"],
                        data["medium_category_code"],
                        data["medium_category_name"],
                        data["small_category_code"],
                        data["small_category_name"],
                        data["industry_code"],
                        data["industry_name"],
                        data["province_code"],
                        data["province_name"],
                        data["district_code"],
                        data["district_name"],
                        data["administrative_dong_code"],
                        data["administrative_dong_name"],
                        data["legal_dong_code"],
                        data["legal_dong_name"],
                        data["lot_number_code"],
                        data["land_category_code"],
                        data["land_category_name"],
                        data["lot_main_number"],
                        data["lot_sub_number"],
                        data["lot_address"],
                        data["road_name_code"],
                        data["road_name"],
                        data["building_main_number"],
                        data["building_sub_number"],
                        data["building_management_number"],
                        data["building_name"],
                        data["road_name_address"],
                        data["old_postal_code"],
                        data["new_postal_code"],
                        data["dong_info"],
                        data["floor_info"],
                        data["unit_info"],
                        data["longitude"],
                        data["latitude"],
                        data["local_year"],
                        data["local_quarter"],
                    ),
                )

                connection.commit()

            except Exception as e:
                print(f"Error inserting specific data: {e}")
                raise

    except pymysql.MySQLError as e:
        print(f"Error inserting data into local_store: {e}")
        connection.rollback()
        raise


# 매장번호로 읍면동 id, 읍면동 이름 가져오기
def select_local_store_sub_distirct_id_by_store_business_number(
    store_business_id: str,
) -> LocalStoreSubdistrict:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)

    # print(f"store_business_id: {store_business_id}")

    try:
        if connection.open:

            select_query = """
                SELECT
                    LOCAL_STORE_ID,
                    STORE_BUSINESS_NUMBER,
                    ls.SUB_DISTRICT_ID,
                    sd.SUB_DISTRICT_NAME
                FROM
                    LOCAL_STORE ls
                JOIN SUB_DISTRICT sd ON sd.SUB_DISTRICT_ID = ls.SUB_DISTRICT_ID
                WHERE STORE_BUSINESS_NUMBER = %s
                ;
            """

            # logger.info(f"Executing query: {select_query % tuple(params)}")
            cursor.execute(select_query, (store_business_id,))

            results: LocalStoreSubdistrict = cursor.fetchone()

            return results
    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected Error select_top3_rising_business_by_store_business_number: {e}"
        )
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)

    return results


######### gpt 프롬프트 용 ##############
# 매장번호로 읍면동 id, 읍면동 이름 가져오기
def select_local_store_by_store_business_number(
    store_business_id: str,
) -> LocalStoreCityDistrictSubDistrict:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)

    # print(f"store_business_id: {store_business_id}")

    try:
        if connection.open:

            select_query = """
                SELECT
                    ls.LOCAL_STORE_ID,
                    ls.STORE_BUSINESS_NUMBER,
                    ls.STORE_NAME,
                    c.CITY_NAME,
                    d.DISTRICT_NAME,
                    sd.SUB_DISTRICT_NAME,
                    ls.CITY_ID,
                    ls.DISTRICT_ID,
                    ls.SUB_DISTRICT_ID,
                    ls.LARGE_CATEGORY_NAME,
                    ls.MEDIUM_CATEGORY_NAME,                   
                    ls.SMALL_CATEGORY_NAME,
                    ls.REFERENCE_ID
                FROM
                    local_store ls
                JOIN
                    city c ON ls.city_id = c.city_id
                JOIN
                    district d ON ls.district_id = d.district_id
                JOIN
                    sub_district sd ON ls.sub_district_id = sd.sub_district_id
                WHERE
                    ls.STORE_BUSINESS_NUMBER = %s;
                
            """

            # logger.info(f"Executing query: {select_query % tuple(params)}")
            cursor.execute(select_query, (store_business_id,))

            results: LocalStoreCityDistrictSubDistrict = cursor.fetchone()

            return results
    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected Error select_top3_rising_business_by_store_business_number: {e}"
        )
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)

    return results


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


def get_report_store_info_by_store_business_id(
    store_business_id: str,
) -> LocalStoreSubdistrict:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)

    # print(f"store_business_id: {store_business_id}")

    try:
        if connection.open:

            select_query = """
                SELECT 
                STORE_NAME,
                ROAD_NAME_ADDRESS,
                BUILDING_NAME,
                FLOOR_INFO,
                SMALL_CATEGORY_NAME
            FROM
                LOCAL_STORE
            WHERE
                STORE_BUSINESS_NUMBER = %s
            ;
            """

            # logger.info(f"Executing query: {select_query % tuple(params)}")
            cursor.execute(select_query, (store_business_id,))

            row = cursor.fetchone()

            results = LocalStoreInfo(
                road_name_address=row["ROAD_NAME_ADDRESS"],
                store_name=row["STORE_NAME"],
                building_name=row["BUILDING_NAME"],
                floor_info=row["FLOOR_INFO"],
                small_category_name=row["SMALL_CATEGORY_NAME"],
            )

            return results
    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected Error select_top3_rising_business_by_store_business_number: {e}"
        )
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)

    return results


def get_lat_lng_by_store_business_id(
    store_business_id: str,
) -> LocalStoreLatLng:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)

    # print(f"store_business_id: {store_business_id}")

    try:
        if connection.open:

            select_query = """
                SELECT 
                LONGITUDE,
                LATITUDE
            FROM
                LOCAL_STORE
            WHERE
                STORE_BUSINESS_NUMBER = %s
            ;
            """

            # logger.info(f"Executing query: {select_query % tuple(params)}")
            cursor.execute(select_query, (store_business_id,))

            row = cursor.fetchone()

            results = LocalStoreLatLng(
                longitude=row["LONGITUDE"],
                latitude=row["LATITUDE"],
            )

            return results
    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected Error select_top3_rising_business_by_store_business_number: {e}"
        )
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)

    return results


def get_report_store_info_by_store_business_id(
    store_business_id: str,
) -> LocalStoreSubdistrict:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)

    # print(f"store_business_id: {store_business_id}")

    try:
        if connection.open:

            select_query = """
                SELECT 
                STORE_NAME,
                ROAD_NAME_ADDRESS,
                BUILDING_NAME,
                FLOOR_INFO,
                SMALL_CATEGORY_NAME
            FROM
                LOCAL_STORE
            WHERE
                STORE_BUSINESS_NUMBER = %s
            ;
            """

            # logger.info(f"Executing query: {select_query % tuple(params)}")
            cursor.execute(select_query, (store_business_id,))

            row = cursor.fetchone()

            results = LocalStoreInfo(
                road_name_address=row["ROAD_NAME_ADDRESS"],
                store_name=row["STORE_NAME"],
                building_name=row["BUILDING_NAME"],
                floor_info=row["FLOOR_INFO"],
                small_category_name=row["SMALL_CATEGORY_NAME"],
            )

            return results
    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected Error select_top3_rising_business_by_store_business_number: {e}"
        )
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)

    return results


def get_lat_lng_by_store_business_id(
    store_business_id: str,
) -> LocalStoreLatLng:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)

    # print(f"store_business_id: {store_business_id}")

    try:
        if connection.open:

            select_query = """
                SELECT 
                LONGITUDE,
                LATITUDE
            FROM
                LOCAL_STORE
            WHERE
                STORE_BUSINESS_NUMBER = %s
            ;
            """

            # logger.info(f"Executing query: {select_query % tuple(params)}")
            cursor.execute(select_query, (store_business_id,))

            row = cursor.fetchone()

            results = LocalStoreLatLng(
                longitude=row["LONGITUDE"],
                latitude=row["LATITUDE"],
            )

            return results
    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected Error select_top3_rising_business_by_store_business_number: {e}"
        )
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)

    return results


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


def get_region_id_by_store_business_number(
    store_business_id: str,
) -> LocalStoreLatLng:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)

    # print(f"store_business_id: {store_business_id}")

    try:
        if connection.open:

            select_query = """
                SELECT 
                ls.CITY_ID,
                ls.DISTRICT_ID,
                ls.SUB_DISTRICT_ID,
                reference_id
            FROM
                LOCAL_STORE
            WHERE
                STORE_BUSINESS_NUMBER = %s
            ;
            """

            # logger.info(f"Executing query: {select_query % tuple(params)}")
            cursor.execute(select_query, (store_business_id,))

            row = cursor.fetchone()

            return row
    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
    except Exception as e:
        logger.error(
            f"Unexpected Error select_top3_rising_business_by_store_business_number: {e}"
        )
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)



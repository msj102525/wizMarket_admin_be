from datetime import date
import logging
from typing import List, Optional
from fastapi import HTTPException
import pymysql
from app.schemas.commercial_district import (
    CommercialDistrictInsert,
    CommercialDistrictOutput,
    CommercialStatisticsDataDate,
)
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)

logger = logging.getLogger(__name__)


def select_commercial_district_by_dynamic_query(
    city_id: Optional[int] = None,
    district_id: Optional[int] = None,
    sub_district_id: Optional[int] = None,
    biz_main_category_id: Optional[int] = None,
    biz_sub_category_id: Optional[int] = None,
    biz_detail_category_id: Optional[int] = None,
    market_size_min: Optional[int] = None,
    market_size_max: Optional[int] = None,
    avg_sales_min: Optional[int] = None,
    avg_sales_max: Optional[int] = None,
    operating_cost_min: Optional[int] = None,
    operating_cost_max: Optional[int] = None,
    food_cost_min: Optional[int] = None,
    food_cost_max: Optional[int] = None,
    employee_cost_min: Optional[int] = None,  # 인건비X -> 평균 결제
    employee_cost_max: Optional[int] = None,  # 인건비X -> 평균 결제
    rental_cost_min: Optional[int] = None,
    rental_cost_max: Optional[int] = None,
    avg_profit_min: Optional[int] = None,
    avg_profit_max: Optional[int] = None,
    y_m: Optional[date] = None,
) -> List[CommercialDistrictOutput]:
    connection = get_db_connection()
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    logger = logging.getLogger(__name__)
    results: List[CommercialDistrictOutput] = []

    try:
        if connection.open:
            params = [
                city_id,
                district_id,
                sub_district_id,
                biz_main_category_id,
                biz_sub_category_id,
                biz_detail_category_id,
                market_size_min,
                market_size_max,
                avg_sales_min,
                avg_sales_max,
                operating_cost_min,
                operating_cost_max,
                food_cost_min,
                food_cost_max,
                employee_cost_min,
                employee_cost_max,
                rental_cost_min,
                rental_cost_max,
                avg_profit_min,
                avg_profit_max,
                y_m,
            ]

            select_query = """
                WITH FilteredCD AS (
                    SELECT *
                    FROM COMMERCIAL_DISTRICT CD
                    WHERE 1=1
                        AND CD.CITY_ID = COALESCE(%s, CD.CITY_ID)
                        AND CD.DISTRICT_ID = COALESCE(%s, CD.DISTRICT_ID)
                        AND CD.SUB_DISTRICT_ID = COALESCE(%s, CD.SUB_DISTRICT_ID)
                        AND CD.BIZ_MAIN_CATEGORY_ID = COALESCE(%s, CD.BIZ_MAIN_CATEGORY_ID)
                        AND CD.BIZ_SUB_CATEGORY_ID = COALESCE(%s, CD.BIZ_SUB_CATEGORY_ID)
                        AND CD.BIZ_DETAIL_CATEGORY_ID = COALESCE(%s, CD.BIZ_DETAIL_CATEGORY_ID)
                        AND CD.MARKET_SIZE BETWEEN COALESCE(%s, CD.MARKET_SIZE) AND COALESCE(%s, CD.MARKET_SIZE)
                        AND CD.AVERAGE_SALES BETWEEN COALESCE(%s, CD.AVERAGE_SALES) AND COALESCE(%s, CD.AVERAGE_SALES)
                        AND CD.OPERATING_COST BETWEEN COALESCE(%s, CD.OPERATING_COST) AND COALESCE(%s, CD.OPERATING_COST)
                        AND CD.FOOD_COST BETWEEN COALESCE(%s, CD.FOOD_COST) AND COALESCE(%s, CD.FOOD_COST)
                        AND CD.AVERAGE_PAYMENT BETWEEN COALESCE(%s, CD.AVERAGE_PAYMENT) AND COALESCE(%s, CD.AVERAGE_PAYMENT)
                        AND CD.RENTAL_COST BETWEEN COALESCE(%s, CD.RENTAL_COST) AND COALESCE(%s, CD.RENTAL_COST)
                        AND CD.AVERAGE_PROFIT BETWEEN COALESCE(%s, CD.AVERAGE_PROFIT) AND COALESCE(%s, CD.AVERAGE_PROFIT)
                        AND CD.Y_M = COALESCE(%s, CD.Y_M)
                )
                SELECT
                    CD.*,
                    CI.CITY_NAME,
                    DI.DISTRICT_NAME,
                    SD.SUB_DISTRICT_NAME,
                    BMC.BIZ_MAIN_CATEGORY_NAME,
                    BSC.BIZ_SUB_CATEGORY_NAME,
                    BDC.BIZ_DETAIL_CATEGORY_NAME
                FROM
                    FilteredCD CD
                    JOIN CITY CI ON CD.CITY_ID = CI.CITY_ID
                    JOIN DISTRICT DI ON CD.DISTRICT_ID = DI.DISTRICT_ID
                    JOIN SUB_DISTRICT SD ON CD.SUB_DISTRICT_ID = SD.SUB_DISTRICT_ID
                    JOIN BIZ_MAIN_CATEGORY BMC ON CD.BIZ_MAIN_CATEGORY_ID = BMC.BIZ_MAIN_CATEGORY_ID
                    JOIN BIZ_SUB_CATEGORY BSC ON CD.BIZ_SUB_CATEGORY_ID = BSC.BIZ_SUB_CATEGORY_ID
                    JOIN BIZ_DETAIL_CATEGORY BDC ON CD.BIZ_DETAIL_CATEGORY_ID = BDC.BIZ_DETAIL_CATEGORY_ID
                ORDER BY CD.COMMERCIAL_DISTRICT_ID DESC
            """

            cursor.execute(select_query, params)
            rows = cursor.fetchall()

            for row in rows:
                commercial_district_output = CommercialDistrictOutput(
                    commercial_district_id=row.get("COMMERCIAL_DISTRICT_ID"),
                    city_name=row.get("CITY_NAME"),
                    district_name=row.get("DISTRICT_NAME"),
                    sub_district_name=row.get("SUB_DISTRICT_NAME"),
                    biz_main_category_name=row.get("BIZ_MAIN_CATEGORY_NAME"),
                    biz_sub_category_name=row.get("BIZ_SUB_CATEGORY_NAME"),
                    biz_detail_category_name=row.get("BIZ_DETAIL_CATEGORY_NAME"),
                    national_density=row.get("NATIONAL_DENSITY"),
                    city_density=row.get("CITY_DENSITY"),
                    district_density=row.get("DISTRICT_DENSITY"),
                    sub_district_density=row.get("SUB_DISTRICT_DENSITY"),
                    market_size=row.get("MARKET_SIZE"),
                    average_payment=row.get("AVERAGE_PAYMENT"),
                    usage_count=row.get("USAGE_COUNT"),
                    average_sales=row.get("AVERAGE_SALES"),
                    operating_cost=row.get("OPERATING_COST"),
                    food_cost=row.get("FOOD_COST"),
                    employee_cost=row.get("EMPLOYEE_COST"),
                    rental_cost=row.get("RENTAL_COST"),
                    tax_cost=row.get("TAX_COST"),
                    family_employee_cost=row.get("FAMILY_EMPLOYEE_COST"),
                    ceo_cost=row.get("CEO_COST"),
                    etc_cost=row.get("ETC_COST"),
                    average_profit=row.get("AVERAGE_PROFIT"),
                    avg_profit_per_mon=row.get("AVG_PROFIT_PER_MON"),
                    avg_profit_per_tue=row.get("AVG_PROFIT_PER_TUE"),
                    avg_profit_per_wed=row.get("AVG_PROFIT_PER_WED"),
                    avg_profit_per_thu=row.get("AVG_PROFIT_PER_THU"),
                    avg_profit_per_fri=row.get("AVG_PROFIT_PER_FRI"),
                    avg_profit_per_sat=row.get("AVG_PROFIT_PER_SAT"),
                    avg_profit_per_sun=row.get("AVG_PROFIT_PER_SUN"),
                    avg_profit_per_06_09=row.get("AVG_PROFIT_PER_06_09"),
                    avg_profit_per_09_12=row.get("AVG_PROFIT_PER_09_12"),
                    avg_profit_per_12_15=row.get("AVG_PROFIT_PER_12_15"),
                    avg_profit_per_15_18=row.get("AVG_PROFIT_PER_15_18"),
                    avg_profit_per_18_21=row.get("AVG_PROFIT_PER_18_21"),
                    avg_profit_per_21_24=row.get("AVG_PROFIT_PER_21_24"),
                    avg_profit_per_24_06=row.get("AVG_PROFIT_PER_24_06"),
                    avg_client_per_m_20=row.get("AVG_CLIENT_PER_M_20"),
                    avg_client_per_m_30=row.get("AVG_CLIENT_PER_M_30"),
                    avg_client_per_m_40=row.get("AVG_CLIENT_PER_M_40"),
                    avg_client_per_m_50=row.get("AVG_CLIENT_PER_M_50"),
                    avg_client_per_m_60=row.get("AVG_CLIENT_PER_M_60"),
                    avg_client_per_f_20=row.get("AVG_CLIENT_PER_F_20"),
                    avg_client_per_f_30=row.get("AVG_CLIENT_PER_F_30"),
                    avg_client_per_f_40=row.get("AVG_CLIENT_PER_F_40"),
                    avg_client_per_f_50=row.get("AVG_CLIENT_PER_F_50"),
                    avg_client_per_f_60=row.get("AVG_CLIENT_PER_F_60"),
                    top_menu_1=row.get("TOP_MENU_1"),
                    top_menu_2=row.get("TOP_MENU_2"),
                    top_menu_3=row.get("TOP_MENU_3"),
                    top_menu_4=row.get("TOP_MENU_4"),
                    top_menu_5=row.get("TOP_MENU_5"),
                    created_at=row.get("CREATED_AT"),
                    updated_at=row.get("UPDATED_AT"),
                    y_m=row.get("Y_M"),
                )
                results.append(commercial_district_output)

            return results

    except pymysql.MySQLError as e:
        logger.error(f"MySQL Error: {e}")
        rollback(connection)
    except Exception as e:
        logger.error(f"Unexpected Error: {e}")
        rollback(connection)
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)

    return results


def select_commercial_district_data_date() -> List[CommercialStatisticsDataDate]:

    try:
        with get_db_connection() as connection:
            with connection.cursor(pymysql.cursors.DictCursor) as cursor:
                select_query = """
                    SELECT
                        Y_M
                    FROM
                        COMMERCIAL_DISTRICT
                    GROUP BY Y_M
                    ;
                """

                cursor.execute(select_query)
                rows = cursor.fetchall()

                # logger.info(f"rows: {rows}")

                results = []

                for row in rows:
                    result = CommercialStatisticsDataDate(y_m=row["Y_M"])

                    results.append(result)

                return results

    except pymysql.Error as e:
        logger.error(f"Database error occurred: {str(e)}")
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 오류: {str(e)}")
    except Exception as e:
        logger.error(
            f"Unexpected error occurred in select_commercial_district_data_date: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"내부 서버 오류: {str(e)}")

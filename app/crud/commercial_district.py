import logging
import pymysql
from app.schemas.commercial_district import CommercialDistrictInsert
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)


def insert_commercial_district(data: CommercialDistrictInsert):
    connection = get_db_connection()
    cursor = connection.cursor()
    logger = logging.getLogger(__name__)

    try:
        insert_query = """
        INSERT INTO commercial_district (
            city_id, district_id, sub_district_id, 
            biz_main_category_id, biz_sub_category_id, biz_detail_category_id,
            national_density, city_density, district_density, sub_district_density,
            market_size, average_payment, usage_count,
            average_sales, operating_cost, food_cost, employee_cost, rental_cost, tax_cost, 
            family_employee_cost, ceo_cost, etc_cost, average_profit,
            avg_profit_per_mon, avg_profit_per_tue, avg_profit_per_wed, avg_profit_per_thu, avg_profit_per_fri, avg_profit_per_sat, avg_profit_per_sun,
            avg_profit_per_06_09, avg_profit_per_09_12, avg_profit_per_12_15, avg_profit_per_15_18, avg_profit_per_18_21, avg_profit_per_21_24, avg_profit_per_24_06,
            avg_client_per_m_20, avg_client_per_m_30, avg_client_per_m_40, avg_client_per_m_50, avg_client_per_m_60,
            avg_client_per_f_20, avg_client_per_f_30, avg_client_per_f_40, avg_client_per_f_50, avg_client_per_f_60,
            top_menu_1, top_menu_2, top_menu_3, top_menu_4, top_menu_5
        ) VALUES (
            %(city_id)s, %(district_id)s, %(sub_district_id)s, 
            %(biz_main_category_id)s, %(biz_sub_category_id)s, %(biz_detail_category_id)s,
            %(national_density)s, %(city_density)s, %(district_density)s, %(sub_district_density)s,
            %(market_size)s, %(average_payment)s, %(usage_count)s,
            %(average_sales)s, %(operating_cost)s, %(food_cost)s, %(employee_cost)s, %(rental_cost)s, %(tax_cost)s, 
            %(family_employee_cost)s, %(ceo_cost)s, %(etc_cost)s, %(average_profit)s,
            %(avg_profit_per_mon)s, %(avg_profit_per_tue)s, %(avg_profit_per_wed)s, %(avg_profit_per_thu)s, %(avg_profit_per_fri)s, %(avg_profit_per_sat)s, %(avg_profit_per_sun)s,
            %(avg_profit_per_06_09)s, %(avg_profit_per_09_12)s, %(avg_profit_per_12_15)s, %(avg_profit_per_15_18)s, %(avg_profit_per_18_21)s, %(avg_profit_per_21_24)s, %(avg_profit_per_24_06)s,
            %(avg_client_per_m_20)s, %(avg_client_per_m_30)s, %(avg_client_per_m_40)s, %(avg_client_per_m_50)s, %(avg_client_per_m_60)s,
            %(avg_client_per_f_20)s, %(avg_client_per_f_30)s, %(avg_client_per_f_40)s, %(avg_client_per_f_50)s, %(avg_client_per_f_60)s,
            %(top_menu_1)s, %(top_menu_2)s, %(top_menu_3)s, %(top_menu_4)s, %(top_menu_5)s
        );
        """

        cursor.execute(insert_query, data)
        commit(connection)
        logger.info("Data inserted successfully into commercial_district table.")

    except pymysql.MySQLError as e:
        rollback(connection)
        logger.error(f"Error inserting data: {e}")
    finally:
        close_cursor(cursor)
        close_connection(connection)


# if __name__ == "__main__":

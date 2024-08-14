from pymysql import MySQLError
from typing import List
from app.schemas.rising_business import RisingBusinessCreate, BusinessDetail
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)


def insert_rising_business(data_list: List[RisingBusinessCreate]):
    connection = get_db_connection()
    cursor = None

    try:
        if connection and connection.open:
            cursor = connection.cursor()

            insert_query = """
            INSERT INTO RISING_BUSINESS (city, district, sub_district, business_name, growth_rate)
            VALUES (%s, %s, %s, %s, %s);
            """

            for data in data_list:
                if data.rising_top5:
                    for key, business_detail in data.rising_top5.items():
                        values = (
                            data.location.city,
                            data.location.district,
                            data.location.sub_district,
                            business_detail.business_name,
                            (
                                business_detail.growth_rate
                                if business_detail.growth_rate is not None
                                else 0.00
                            ),
                        )
                        cursor.execute(insert_query, values)
                        print(f"Data inserted for {values}")
                else:
                    values = (
                        data.location.city,
                        data.location.district,
                        data.location.sub_district,
                        None,  # 비즈니스 이름 없음
                        0.00,  # 성장률 0.00
                    )
                    cursor.execute(insert_query, values)
                    print(f"Data inserted for empty rising_top5: {values}")

            commit(connection)

    except MySQLError as e:
        print(f"MySQL Error: {e}")
        rollback(connection)
    except Exception as e:
        print(f"Unexpected Error: {e}")
        rollback(connection)
    finally:
        if cursor:
            close_cursor(cursor)
        if connection:
            close_connection(connection)

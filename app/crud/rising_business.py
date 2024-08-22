import logging
from pymysql import MySQLError
from typing import List
from app.schemas.rising_business import (
    RisingBusiness,
    RisingBusinessInsert,
)
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# data_list = [
#     RisingBusinessInsert(
#         region_id=1950,
#         business_name="세탁소/빨래방",
#         growth_rate=85.0,
#         sub_district_rank=1,
#     ),
#     RisingBusinessInsert(
#         region_id=1950,
#         business_name="여성미용실",
#         growth_rate=20.0,
#         sub_district_rank=2,
#     ),
#     RisingBusinessInsert(
#         region_id=1951, business_name="피자전문", growth_rate=69.7, sub_district_rank=1
#     ),
#     RisingBusinessInsert(
#         region_id=1951, business_name="호프/맥주", growth_rate=57.9, sub_district_rank=2
#     ),
# ]


def insert_rising_business(data_list: List[RisingBusinessInsert]):
    connection = get_db_connection()
    cursor = None
    logger = logging.getLogger(__name__)

    try:
        if connection.open:
            cursor = connection.cursor()

            insert_query = """
            INSERT INTO RISING_BUSINESS (region_id, business_name, growth_rate, sub_district_rank)
            VALUES (%s, %s, %s, %s);
            """

            for data in data_list:
                values = (
                    data.region_id,
                    data.business_name,
                    data.growth_rate if data.growth_rate is not None else None,
                    (
                        data.sub_district_rank
                        if data.sub_district_rank is not None
                        else None
                    ),
                )
                logger.info(f"Executing query: {insert_query % values}")
                cursor.execute(insert_query, values)
                print(f"Data inserted for {values}")

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


def select_all_rising_business_by_sub_district(
    sub_district: str,
) -> List[RisingBusiness]:
    connection = get_db_connection()
    cursor = None
    results = []

    try:
        if connection.open:
            cursor = connection.cursor()
            select_query = """
                SELECT *
                FROM RISING_BUSINESS
                WHERE SUB_DISTRICT LIKE %s;
            """
            cursor.execute(select_query, (sub_district))
            rows = cursor.fetchall()

            for row in rows:
                print(row)
                try:
                    results.append(
                        RisingBusiness(
                            rising_business_id=row[0] if row[0] is not None else None,
                            region_id=row[1] if row[1] is not None else None,
                            business_name=row[2] if row[2] is not None else None,
                            growth_rate=row[3] if row[3] is not None else None,
                            sub_district_rank=row[4] if row[4] is not None else None,
                            created_at=row[5] if row[5] is not None else None,
                            updated_at=row[6] if row[6] is not None else None,
                        )
                    )
                except ValueError as ve:
                    print(f"Value Error: {ve}")

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

    return results


# if __name__ == "__main__":
#     insert_rising_business(data_list)

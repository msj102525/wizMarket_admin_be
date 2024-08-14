from pymysql import MySQLError
from typing import List
from app.schemas.rising_business import (
    RisingBusinessCreate,
    BusinessDetail,
    RisingBusinessOutput,
)
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)
import aiomysql


def insert_rising_business(data_list: List[RisingBusinessCreate]):
    connection = get_db_connection()
    cursor = None

    try:
        if connection.open:
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
                        None,
                        0.00,
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


def select_all_rising_business_by_sub_district(
    sub_district: str,
) -> List[RisingBusinessOutput]:
    connection = get_db_connection()
    cursor = None
    results = []

    try:
        if connection.open:
            cursor = connection.cursor()
            select_query = """
                SELECT id, city, district, sub_district, business_name, growth_rate, created_at, updated_at
                FROM RISING_BUSINESS
                WHERE SUB_DISTRICT LIKE %s;
            """
            cursor.execute(select_query, (sub_district))
            rows = cursor.fetchall()

            for row in rows:
                print(row)
                try:
                    results.append(
                        RisingBusinessOutput(
                            id=row[0],
                            city=str(row[1]),
                            district=str(row[2]),
                            sub_district=str(row[3]),
                            business_name=str(row[4]),
                            growth_rate=float(row[5]) if row[5] is not None else 0.0,
                            created_at=row[6] if row[6] is not None else None,
                            updated_at=row[7] if row[7] is not None else None,
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

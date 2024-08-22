from pymysql import MySQLError
from typing import List
from app.schemas.rising_business import (
    RisingBusiness,
)
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)
import aiomysql

data_list = [
    RisingBusiness(
        REGION_ID=1950,
        BUSINESS_NAME="세탁소/빨래방",
        GROWTH_RATE=85.0,
        SUB_DISTRICT_RANK=1,
    ),
    RisingBusiness(
        REGION_ID=1950,
        BUSINESS_NAME="여성미용실",
        GROWTH_RATE=20.0,
        SUB_DISTRICT_RANK=2,
    ),
    RisingBusiness(
        REGION_ID=1951, BUSINESS_NAME="피자전문", GROWTH_RATE=69.7, SUB_DISTRICT_RANK=1
    ),
    RisingBusiness(
        REGION_ID=1951, BUSINESS_NAME="호프/맥주", GROWTH_RATE=57.9, SUB_DISTRICT_RANK=2
    ),
    RisingBusiness(
        REGION_ID=1951,
        BUSINESS_NAME="아이스크림/빙수",
        GROWTH_RATE=51.7,
        SUB_DISTRICT_RANK=3,
    ),
    RisingBusiness(
        REGION_ID=1951, BUSINESS_NAME="안경점", GROWTH_RATE=37.1, SUB_DISTRICT_RANK=4
    ),
    RisingBusiness(
        REGION_ID=1951,
        BUSINESS_NAME="여성미용실",
        GROWTH_RATE=30.3,
        SUB_DISTRICT_RANK=5,
    ),
    RisingBusiness(
        REGION_ID=1952,
        BUSINESS_NAME="꽃집/꽃배달",
        GROWTH_RATE=68.9,
        SUB_DISTRICT_RANK=1,
    ),
    RisingBusiness(
        REGION_ID=1952, BUSINESS_NAME="잡화점", GROWTH_RATE=61.7, SUB_DISTRICT_RANK=2
    ),
    RisingBusiness(
        REGION_ID=1952,
        BUSINESS_NAME="세탁소/빨래방",
        GROWTH_RATE=27.1,
        SUB_DISTRICT_RANK=3,
    ),
    RisingBusiness(
        REGION_ID=1952, BUSINESS_NAME="편의점", GROWTH_RATE=16.1, SUB_DISTRICT_RANK=4
    ),
    RisingBusiness(
        REGION_ID=1952,
        BUSINESS_NAME="커피전문점",
        GROWTH_RATE=12.7,
        SUB_DISTRICT_RANK=5,
    ),
    RisingBusiness(
        REGION_ID=1953,
        BUSINESS_NAME="발/네일케어",
        GROWTH_RATE=176.2,
        SUB_DISTRICT_RANK=1,
    ),
    RisingBusiness(
        REGION_ID=1953, BUSINESS_NAME="노래방", GROWTH_RATE=66.3, SUB_DISTRICT_RANK=2
    ),
    RisingBusiness(
        REGION_ID=1953, BUSINESS_NAME="요가/단식", GROWTH_RATE=47.5, SUB_DISTRICT_RANK=3
    ),
    RisingBusiness(
        REGION_ID=1953, BUSINESS_NAME="제과점", GROWTH_RATE=44.6, SUB_DISTRICT_RANK=4
    ),
    RisingBusiness(
        REGION_ID=1953,
        BUSINESS_NAME="세탁소/빨래방",
        GROWTH_RATE=43.4,
        SUB_DISTRICT_RANK=5,
    ),
]


def insert_rising_business(data_list: List[RisingBusiness]):
    connection = get_db_connection()
    cursor = None

    try:
        if connection.open:
            cursor = connection.cursor()

            insert_query = """
            INSERT INTO RISING_BUSINESS (region_id, business_name, growth_rate, sub_district_rank)
            VALUES (%s, %s, %s, %s);
            """

            for data in data_list:
                values = (
                    data.REGION_ID,
                    data.BUSINESS_NAME,
                    data.GROWTH_RATE if data.GROWTH_RATE is not None else None,
                    (
                        data.SUB_DISTRICT_RANK
                        if data.SUB_DISTRICT_RANK is not None
                        else None
                    ),
                )
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


# def select_all_rising_business_by_sub_district(
#     sub_district: str,
# ) -> List[RisingBusinessOutput]:
#     connection = get_db_connection()
#     cursor = None
#     results = []

#     try:
#         if connection.open:
#             cursor = connection.cursor()
#             select_query = """
#                 SELECT id, city, district, sub_district, business_name, growth_rate, created_at, updated_at
#                 FROM RISING_BUSINESS
#                 WHERE SUB_DISTRICT LIKE %s;
#             """
#             cursor.execute(select_query, (sub_district))
#             rows = cursor.fetchall()

#             for row in rows:
#                 print(row)
#                 try:
#                     results.append(
#                         RisingBusinessOutput(
#                             id=row[0],
#                             city=str(row[1]),
#                             district=str(row[2]),
#                             sub_district=str(row[3]),
#                             business_name=str(row[4]),
#                             growth_rate=float(row[5]) if row[5] is not None else 0.0,
#                             created_at=row[6] if row[6] is not None else None,
#                             updated_at=row[7] if row[7] is not None else None,
#                         )
#                     )
#                 except ValueError as ve:
#                     print(f"Value Error: {ve}")

#     except MySQLError as e:
#         print(f"MySQL Error: {e}")
#         rollback(connection)
#     except Exception as e:
#         print(f"Unexpected Error: {e}")
#         rollback(connection)
#     finally:
#         if cursor:
#             close_cursor(cursor)
#         if connection:
#             close_connection(connection)

#     return results

if __name__ == "__main__":
    insert_rising_business(data_list)

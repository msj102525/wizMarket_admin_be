import logging
import pymysql
import pandas as pd
import os
from dotenv import load_dotenv
from app.db.connect import (
    get_db_connection,
    close_connection,
    close_cursor,
    commit,
    rollback,
)


def get_or_create_city_id(city: str):
    connection = get_db_connection()
    cursor = None
    try:
        if connection.open:
            cursor = connection.cursor()

            select_sql = """
                SELECT CITY_ID FROM CITY 
                WHERE CITY_NAME = %s 
            """
            cursor.execute(select_sql, (city,))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                insert_sql = """
                    INSERT INTO CITY (CITY_NAME)
                    VALUES (%s)
                    ;
                """
                cursor.execute(insert_sql, (city))
                region_id = cursor.lastrowid

                commit(connection)
                return region_id

    except pymysql.MySQLError as e:
        print(f"Database query failed: {e}")
        rollback(connection)

    finally:
        close_cursor(cursor)
        close_connection(connection)


def get_or_create_distirct_id(city_id: int, distirct: str):
    connection = get_db_connection()
    cursor = None
    try:
        if connection.open:
            cursor = connection.cursor()

            select_sql = """
                SELECT DISTRICT_ID FROM DISTRICT
                WHERE CITY_ID = %s AND DISTRICT_NAME = %s
                ;
            """
            cursor.execute(select_sql, (city_id, distirct))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                insert_sql = """
                    INSERT INTO DISTRICT (CITY_ID, DISTRICT_NAME)
                    VALUES (%s, %s)
                    ;
                """
                cursor.execute(
                    insert_sql,
                    (
                        city_id,
                        distirct,
                    ),
                )
                region_id = cursor.lastrowid

                commit(connection)
                return region_id

    except pymysql.MySQLError as e:
        print(f"Database query failed: {e}")
        rollback(connection)

    finally:
        close_cursor(cursor)
        close_connection(connection)


# def get_or_create_sub_distirct_id(city_id: int, distirct_id: int, sub_district: str):
#     connection = get_db_connection()
#     cursor = None
#     try:
#         if connection.open:
#             cursor = connection.cursor()

#             select_sql = """
#                 SELECT DISTRICT_ID FROM DISTRICT
#                 WHERE CITY_ID = %s AND DISTRICT_NAME = %s
#                 ;
#             """
#             cursor.execute(select_sql, (city_id, distirct_id))
#             result = cursor.fetchone()

#             if result:
#                 return result[0]
#             else:
#                 insert_sql = """
#                     INSERT INTO DISTRICT (CITY_ID, DISTRICT_NAME)
#                     VALUES (%s, %s)
#                     ;
#                 """
#                 cursor.execute(insert_sql, (distirct_id,))
#                 region_id = cursor.lastrowid

#                 commit(connection)
#                 return region_id

#     except pymysql.MySQLError as e:
#         print(f"Database query failed: {e}")
#         rollback(connection)

#     finally:
#         close_cursor(cursor)
#         close_connection(connection)


############################
def insert_data_from_excel():
    load_dotenv()

    root_path = os.getenv("ROOT_PATH")

    file_path = os.path.join(root_path, "app", "data", "regionData", "regionData.xlsx")
    table_name = "region"

    try:
        df = pd.read_excel(file_path, engine="openpyxl")
        print(f"Excel file '{file_path}' read successfully.")

        if "REGION_ID" in df.columns:
            df = df.drop(columns=["REGION_ID"])
            print("REGION_ID column dropped.")

        print(df.head())

    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    connection = get_db_connection()
    if not connection:
        return

    cursor = None
    try:
        cursor = connection.cursor()

        for index, row in df.iterrows():
            placeholders = ", ".join(["%s"] * len(row))
            columns = ", ".join(row.index)
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, tuple(row))

        # 커밋
        commit(connection)
    except pymysql.MySQLError as e:
        print(f"Database error during insertion: {e}")
        rollback(connection)
    except Exception as e:
        print(f"Unexpected error: {e}")
        rollback(connection)
    finally:
        close_cursor(cursor)
        close_connection(connection)


def select_region_id_by_city_sub_district(city: str, sub_district: str):
    connection = get_db_connection()
    cursor = None
    logger = logging.getLogger(__name__)

    try:
        if connection.open:
            cursor = connection.cursor()
            select_query = """
                SELECT REGION_ID
                FROM REGION
                WHERE CITY LIKE %s AND SUB_DISTRICT LIKE %s;
            """
            values = (f"%{city}%", f"%{sub_district}%")
            cursor.execute(select_query, values)
            result = cursor.fetchone()

            logger.info(f"Executing query: {cursor.mogrify(select_query, values)}")

    except pymysql.MySQLError as e:
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

    return result


# 실행
# if __name__ == "__main__":
#     insert_data_from_excel()

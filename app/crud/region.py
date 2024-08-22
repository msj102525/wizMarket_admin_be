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


def get_or_create_region_id(city: str, district: str, sub_district: str):
    connection = get_db_connection()
    cursor = None
    try:
        if connection.open:
            cursor = connection.cursor()

            select_sql = """
                SELECT REGION_ID FROM REGION 
                WHERE CITY = %s AND DISTRICT = %s AND SUB_DISTRICT = %s
            """
            cursor.execute(select_sql, (city, district, sub_district))
            result = cursor.fetchone()

            if result:
                return result[0]
            else:
                insert_sql = """
                    INSERT INTO REGION (CITY, DISTRICT, SUB_DISTRICT)
                    VALUES (%s, %s, %s)
                """
                cursor.execute(insert_sql, (city, district, sub_district))
                region_id = cursor.lastrowid

                commit(connection)
                return region_id

    except pymysql.MySQLError as e:
        print(f"Database query failed: {e}")
        rollback(connection)

    finally:
        close_cursor(cursor)
        close_connection(connection)


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

    try:
        if connection.open:
            cursor = connection.cursor()
            select_query = """
                SELECT *
                FROM RISING_BUSINESS
                WHERE CITY LIKE %s AND SUB_DISTRICT LIKE %s;
            """
            cursor.execute(select_query, (f"%{city}%", f"%{sub_district}%"))
            result = cursor.fetchone()

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

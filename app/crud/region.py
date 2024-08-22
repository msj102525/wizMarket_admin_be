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

load_dotenv()

# ROOT_PATH를 가져옵니다.
root_path = os.getenv("ROOT_PATH")

# ROOT_PATH에 상대 경로를 붙여 file_path를 만듭니다.
file_path = os.path.join(root_path, "app", "data", "regionData", "regionData.xlsx")
table_name = "region"

def insert_data_from_excel(file_path, table_name):
    # 엑셀 파일 읽기
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"Excel file '{file_path}' read successfully.")
        
        # REGION_ID 열 삭제
        if 'REGION_ID' in df.columns:
            df = df.drop(columns=['REGION_ID'])
            print("REGION_ID column dropped.")
        
        print(df.head())  # 수정된 데이터프레임 출력
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # DB 연결
    connection = get_db_connection()
    if not connection:
        return

    cursor = None
    try:
        cursor = connection.cursor()
        
        # 데이터프레임을 반복하면서 데이터를 DB에 삽입
        for index, row in df.iterrows():
            # 예제에서는 모든 열을 일반화된 방식으로 다루기 위해 동적 SQL 생성
            placeholders = ', '.join(['%s'] * len(row))
            columns = ', '.join(row.index)
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

# 실행
# if __name__ == "__main__":
#     insert_data_from_excel(file_path, table_name)
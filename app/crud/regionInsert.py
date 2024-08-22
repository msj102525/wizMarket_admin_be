# insert_excel_to_db.py

import pandas as pd
from app.db.connect import get_db_connection, close_connection, close_cursor, commit, rollback
import pymysql

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

if __name__ == "__main__":
    # 엑셀 파일 경로와 테이블 이름 설정
    file_path = r"C:\workspace\python\wizMarket_back\app\data\regionData\regionData.xlsx"
    table_name = "region"

    # 데이터 삽입 실행
    insert_data_from_excel(file_path, table_name)

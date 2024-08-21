import os
import pandas as pd
import pymysql
import sys
import platform
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from app.db.connect import get_db_connection, close_connection, commit, rollback

# 지정된 폴더 경로
root_dir = r'C:\stroebusinessdata'

# 선택할 열 목록
selected_columns = ['상호명', '지점명', '상권업종대분류명', '상권업종중분류명', '상권업종소분류명', 
                    '표준산업분류명', '시도명', '시군구명', '행정동코드', '행정동명', '법정동코드', 
                    '법정동명', '대지구분명', '지번주소', '건물명', '도로명주소', 
                    '동정보', '층정보', '호정보', 'year_quarter']

# 분기 정보 변환 함수
def convert_quarter_format(year_quarter_str):
    year = year_quarter_str[:4]
    quarter = year_quarter_str[-3]  # 분기 숫자 추출 (예: '1')
    return f"{year}Q{quarter}"

# 데이터 삽입 함수
def insert_data_to_db(connection, data):
    with connection.cursor() as cursor:
        sql = """
        INSERT INTO store_business (
            business_name, branch_name, major_category, middle_category, minor_category,
            standard_industry_code, city, district, administrative_dong_code,
            administrative_dong_name, legal_dong_code, legal_dong_name, land_category,
            lot_number_address, building_name, road_name_address,
            building_unit_info, floor_info, unit_number, year_quarter
        ) VALUES (
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s
        )
        """
        cursor.execute(sql, data)
        print(f"Inserted data: {data}")

# 시스템 종료 함수
def shutdown_system():
    if platform.system() == "Windows":
        os.system("shutdown /s /t 0")
    else:
        os.system("sudo shutdown -h now")

# 모든 하위 폴더를 순회하며 파일 처리
def process_csv_files():
    connection = get_db_connection()
    if not connection:
        print("Database connection could not be established. Exiting...")
        shutdown_system()  # DB 연결이 안될 경우에도 시스템 종료
        return
    
    try:
        for subdir, dirs, files in os.walk(root_dir):
            for file in files:
                if file.endswith('.csv'):
                    file_path = os.path.join(subdir, file)
                    try:
                        folder_name = os.path.basename(subdir)
                        year_quarter_raw = folder_name[-8:]
                        year_quarter = convert_quarter_format(year_quarter_raw)

                        try:
                            df = pd.read_csv(file_path, dtype=str, encoding='utf-8')
                        except UnicodeDecodeError:
                            df = pd.read_csv(file_path, dtype=str, encoding='cp949')

                        df = df.applymap(lambda x: None if pd.isna(x) else x)
                        df['year_quarter'] = year_quarter

                        for _, row in df[selected_columns].iterrows():
                            data = tuple(row[col] for col in selected_columns)
                            insert_data_to_db(connection, data)
        
                    except Exception as e:
                        print(f"오류 발생 파일: {file_path}")
                        print(f"오류 메시지: {e}")
                        rollback(connection)
                        shutdown_system()  # 오류 발생 시 시스템 종료
                        return  # 프로세스를 중단합니다.
        
        commit(connection)
    except Exception as e:
        print(f"Unexpected error during processing: {e}")
        rollback(connection)
    finally:
        close_connection(connection)
        shutdown_system()  # 작업 완료 후 시스템 종료

if __name__ == "__main__":
    process_csv_files()

import pandas as pd
import os
from app.crud.population import *
import re
from dotenv import load_dotenv
from app.schemas.population import Population
from app.schemas.city import City
from app.schemas.district import District
from app.schemas.sub_district import SubDistrict
from app.db.connect import * 
from typing import List


# 첫 로딩 시 전체 시도명 출력
def fetch_cities() -> List[str]:
    return get_all_cities()


# 시도명으로 시도 아이디값 리턴 후 해당하는 시/군/구 리스트 출력
def fetch_districts_for_sido(sido_name: str) -> List[str]:
    city_id = get_city_id_by_name(sido_name)
    if city_id is None:
        raise ValueError("City not found")
    return get_districts_by_city_id(city_id)


# 시/군/구 명으로 시/군/구 아이디값 리턴 후 해당하는 읍/면/동(sub_district) 이름 리스트 출력
def fetch_sub_districts_for_district(district_name: str) -> List[str]:
    district_id = get_district_id_by_name(district_name)
    if district_id is None:
        raise ValueError("District not found")
    return get_sub_districts_by_district_id(district_id) 


# 월별 인구 조회
def fetch_population(city_name: str, district_name: str, sub_district_name: str, start_year_month: str) -> Population:
    ids = get_ids_by_names(city_name, district_name, sub_district_name)
    if ids is None:
        raise ValueError(f"Could not find matching records for the given names: {city_name}, {district_name}, {sub_district_name}")
    
    # 시작년월과 끝년월을 get_population_data 함수에 전달
    population_data = get_population_data(
        ids['city_id'], 
        ids['district_id'], 
        ids['sub_district_id'], 
        start_year_month
    )
    if population_data is None:
        raise ValueError(f"No population data found for the given IDs: {ids}")
    
    return population_data





# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# ROOT_PATH 환경 변수 불러오기
ROOT_PATH = os.getenv("ROOT_PATH")

# CSV 파일이 있는 디렉토리 설정
csv_directory = os.path.join(ROOT_PATH, "app", "data", "populationData")

def load_and_insert_population_data():
    connection = get_db_connection()
    
    # 1. 필요한 데이터를 미리 로드합니다.
    cities = load_all_cities(connection)
    districts = load_all_districts(connection)
    sub_districts = load_all_sub_districts(connection)

    try:
        files = [f for f in os.listdir(csv_directory) if f.endswith(".csv")]
        if files:
            # 파일 목록을 정렬하여 가장 마지막 파일을 선택
            last_file = sorted(files)[-1]
            file_path = os.path.join(csv_directory, last_file)

            # 선택된 마지막 파일만 읽어서 처리
            df = pd.read_csv(file_path, encoding='euc-kr')

            df = df.fillna('세종특별자치시')
            df = df.replace({'': '세종특별자치시', ' ': '세종특별자치시'})

            for index, row in df.iterrows():
                try:
                    city_name = row['시도명']
                    district_name = row['시군구명']
                    sub_district_name = row['읍면동명']

                    # sub_district_name에 '출장소'라는 단어가 포함된 경우, 건너뛰기
                    if '출장소' in sub_district_name:
                        continue

                    # sub_district_name에서 '제'를 제거
                    if isinstance(sub_district_name, str):
                        sub_district_name = re.sub(r'제(\d)', r'\1', sub_district_name)
                            
                    # 특정 패턴의 동명 매핑 작업
                    mappings = {
                        '숭의1.3동': '숭의1,3동',
                        '용현1.4동': '용현1,4동',
                        '도화2.3동': '도화2,3동',
                        '봉명2송정동': '봉명2.송정동',
                        '성화개신죽림동': '성화.개신.죽림동',
                        '용담명암산성동': '용담.명암.산성동',
                        '운천신봉동': '운천.신봉동',
                        '율량사천동': '율량.사천동',
                    }
                    if sub_district_name in mappings:
                        sub_district_name = mappings[sub_district_name]

                    # district_name에 띄어쓰기가 있으면, 첫 번째 단어만 사용
                    if ' ' in district_name:
                        district_name = district_name.split()[0]
                    
                    # 2. 로드된 데이터에서 참조
                    city = cities.get(city_name)
                    district = districts.get((city.city_id, district_name))
                    sub_district = sub_districts.get((district.district_id, sub_district_name))

                    # 행정기관코드와 기준연월
                    admin_code = row['행정기관코드']
                    reference_date = row['기준연월']

                    # 남자와 여자의 인구수를 각각 가져옴
                    male_population = row['남자']
                    female_population = row['여자']

                    # 계(total_population)를 남자와 여자의 합으로 설정
                    total_population = male_population + female_population

                    # 성별 데이터와 gender_id를 처리
                    gender_data = [
                        {'gender_id': 1, 'gender': '남자', 'population': male_population},
                        {'gender_id': 2, 'gender': '여자', 'population': female_population}
                    ]

                    for gender_info in gender_data:
                        gender_id = gender_info['gender_id']
                        gender = gender_info['gender']

                        # 나이별 인구 데이터를 처리
                        age_data = {}
                        for age in range(0, 110):
                            age_data[f'age_{age}'] = row[f'{age}세{gender}']
                        age_data['age_110_over'] = row[f'110세이상 {gender}']

                        # 여기서 population_data 생성 및 DB에 삽입
                        population_data = Population(
                            city_id=city.city_id,
                            district_id=district.district_id,
                            sub_district_id=sub_district.sub_district_id,
                            gender_id=gender_id,
                            admin_code=admin_code,
                            reference_date=reference_date,
                            province_name=city_name,
                            district_name=district_name,
                            subdistrict_name=sub_district_name,
                            total_population=total_population,
                            male_population=male_population if gender_id == 1 else 0,
                            female_population=female_population if gender_id == 2 else 0,
                            **age_data
                        )

                        insert_population_data(connection, population_data)

                except Exception as e:
                    print(f"Error processing row {index} in file {last_file}: {e}")
                    print(f"Row data: {row}")
                    continue

        # 모든 데이터가 성공적으로 삽입된 후에 커밋
        commit(connection)

    except Exception as e:
        print(f"Error during population data insertion: {e}")
    finally:
        close_connection(connection)



# 미리 데이터를 로드하는 함수들
# 데이터 로드 함수들
def load_all_cities(connection):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT city_id, city_name FROM city")
        result = cursor.fetchall()
        return {row['city_name']: City(city_id=row['city_id'], city_name=row['city_name']) for row in result}

def load_all_districts(connection):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT district_id, city_id, district_name FROM district")
        result = cursor.fetchall()
        return {(row['city_id'], row['district_name']): District(district_id=row['district_id'], city_id=row['city_id'], district_name=row['district_name']) for row in result}

def load_all_sub_districts(connection):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("""
            SELECT sd.sub_district_id, sd.district_id, sd.sub_district_name, d.city_id
            FROM sub_district sd
            JOIN district d ON sd.district_id = d.district_id
        """)
        result = cursor.fetchall()

        return {
            (row['district_id'], row['sub_district_name']): SubDistrict(
                sub_district_id=row['sub_district_id'], 
                district_id=row['district_id'], 
                city_id=row['city_id'],  # city_id 추가
                sub_district_name=row['sub_district_name']
            ) 
            for row in result
        }
    

if __name__ == "__main__":
    load_and_insert_population_data()
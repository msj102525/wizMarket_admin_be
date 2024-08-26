import pandas as pd
import os
from app.crud.population import fetch_population_records, fetch_population_by_year_month, insert_population_data
import re
import asyncio
from dotenv import load_dotenv
from app.crud.city import get_or_create_city
from app.crud.district import get_or_create_district
from app.crud.sub_district import get_or_create_sub_district
from app.schemas.population import Population
from app.schemas.city import City
from app.schemas.district import District
from app.schemas.sub_district import SubDistrict
from app.db.connect import *

# async def get_population_data(start_date: int, end_date: int, city: str, district: str, sub_district: str):
#     region_id = get_or_create_region_id(city, district, sub_district)
#     if not region_id:
#         return None
#     return await fetch_population_records(start_date, end_date, region_id)


async def check_population_exists(year_month: int) -> bool:
    records = await fetch_population_by_year_month(year_month)
    return len(records) > 0


# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# ROOT_PATH 환경 변수 불러오기
ROOT_PATH = os.getenv("ROOT_PATH")

# CSV 파일이 있는 디렉토리 설정
csv_directory = os.path.join(ROOT_PATH, "app", "data", "populationData")

async def load_and_insert_population_data():
    connection = None
    cursor = None

    try:
        # DB 연결을 열고, 커서를 생성합니다.
        connection = get_db_connection()
        cursor = connection.cursor()

        for filename in os.listdir(csv_directory):
            if filename.endswith(".csv"):
                file_path = os.path.join(csv_directory, filename)
                df = pd.read_csv(file_path, encoding='euc-kr')

                for index, row in df.iterrows():
                    try:
                        city_name = row['시도명']
                        district_name = row['시군구명']
                        sub_district_name = row['읍면동명']


                        # sub_district_name에 '출장소'라는 단어가 포함된 경우, 건너뛰기
                        if '출장소' in sub_district_name:
                            print(f"Skipping row {index} due to '출장소' in sub_district_name: {sub_district_name}")
                            continue

                        # sub_district_name에서 '제'를 제거
                        if isinstance(sub_district_name, str):
                            sub_district_name = re.sub(r'제(\d)', r'\1', sub_district_name)
                            print(f"Updated sub_district_name for row {index}: {sub_district_name}")

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
                            print(f"Mapped sub_district_name for row {index}: {sub_district_name}")

                        # 동명 합치기 작업
                        merge_mappings = {
                            '복산1동': '복산동',
                            '복산2동': '복산동',
                            '중흥2동': '중흥동',
                            '중흥3동': '중흥동'
                        }
                        if sub_district_name in merge_mappings:
                            sub_district_name = merge_mappings[sub_district_name]
                            print(f"Merged sub_district_name for row {index}: {sub_district_name}")

                        # district_name에 띄어쓰기가 있으면, 마지막 부분만 사용
                        if ' ' in district_name:
                            district_name = district_name.split()[0]  # 첫 번째 단어를 사용
                            print(f"Updated district_name for row {index}: {district_name}")

                        # City, District, SubDistrict 생성 또는 검색
                        city = get_or_create_city(City(name=city_name))
                        district = get_or_create_district(District(name=district_name, city_id=city.city_id))
                        sub_district = get_or_create_sub_district(SubDistrict(name=sub_district_name, district_id=district.district_id, city_id=city.city_id))

                        # 행정기관코드와 기준연월
                        admin_code = row['행정기관코드']
                        reference_date = row['기준연월']

                        # 성별 데이터를 처리
                        for gender_id, gender in enumerate(['남자', '여자'], start=1):
                            total_population = row[gender]
                            if gender_id == 1:
                                male_population = total_population
                                female_population = 0
                            else:
                                male_population = 0
                                female_population = total_population

                            # 나이별 인구 데이터를 처리
                            age_data = {f'age_{age}': row[f'{age}세{gender}'] for age in range(0, 110)}
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
                            male_population=male_population,
                            female_population=female_population,
                            **age_data
                        )

                        # CRUD 레이어에서 데이터 삽입을 처리 (연결과 커서를 전달)
                        await insert_population_data(cursor, population_data)

                    except Exception as e:
                        print(f"Error processing row {index} in file {filename}: {e}")
                        print(f"Row data: {row}")
                        continue

        # 모든 데이터가 성공적으로 삽입된 후에 커밋
        connection.commit

    except Exception as e:
        rollback(connection)
        print(f"Error during population data insertion: {e}")
    finally:
        close_cursor(cursor)
        close_connection(connection)

if __name__ == "__main__":
    asyncio.run(load_and_insert_population_data())
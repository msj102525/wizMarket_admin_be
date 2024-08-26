import pandas as pd
import os
from app.crud.population import fetch_population_records, fetch_population_by_year_month, insert_population_to_db
from app.crud.region import get_or_create_region_id
import asyncio
from dotenv import load_dotenv

async def get_population_data(start_date: int, end_date: int, city: str, district: str, sub_district: str):
    region_id = get_or_create_region_id(city, district, sub_district)
    if not region_id:
        return None
    return await fetch_population_records(start_date, end_date, region_id)


async def check_population_exists(year_month: int) -> bool:
    records = await fetch_population_by_year_month(year_month)
    return len(records) > 0

async def insert_population_data():

    load_dotenv()
    root_path = os.getenv('ROOT_PATH')

    try:
        # 폴더 경로 지정 (프로젝트 루트 기준)
        folder_path = os.path.join(root_path, "app/data/populationData/")

        # 폴더 내 모든 엑셀 파일 처리
        for filename in os.listdir(folder_path):
            if filename.endswith(".csv"):
                file_path = os.path.join(folder_path, filename)

                # CSV 파일 읽기 (인코딩 지정)
                df = pd.read_csv(file_path, encoding='cp949')

                # 3~8열 유지
                base_columns = df.iloc[:, 1:8].copy()

                # 남성 합계 (to09M, to1019M, ..., to9099M, over100M)
                age_ranges_male = {
                    'to09M': (8, 18),
                    'to1019M': (18, 28),
                    'to2029M': (28, 38),
                    'to3039M': (38, 48),
                    'to4049M': (48, 58),
                    'to5059M': (58, 68),
                    'to6069M': (68, 78),
                    'to7079M': (78, 88),
                    'to8089M': (88, 98),
                    'to9099M': (98, 108),
                    'over100M': (108, 119)
                }

                # 여성 합계 (to09F, to1019F, ..., to9099F, over100F)
                age_ranges_female = {
                    'to09F': (119, 129),
                    'to1019F': (129, 139),
                    'to2029F': (139, 149),
                    'to3039F': (149, 159),
                    'to4049F': (159, 169),
                    'to5059F': (169, 179),
                    'to6069F': (179, 189),
                    'to7079F': (189, 199),
                    'to8089F': (199, 209),
                    'to9099F': (209, 219),
                    'over100F': (219, 229)
                }

                # 남성 연령별 합계를 포함한 DataFrame 생성
                male_df = base_columns.copy()
                for col_name, (start_col, end_col) in age_ranges_male.items():
                    male_df[col_name] = df.iloc[:, start_col:end_col].sum(axis=1)

                # 여성 연령별 합계를 포함한 DataFrame 생성
                female_df = base_columns.copy()
                for col_name, (start_col, end_col) in age_ranges_female.items():
                    female_df[col_name] = df.iloc[:, start_col:end_col].sum(axis=1)

                # 남성 DataFrame과 여성 DataFrame의 행을 순차적으로 처리
                for i in range(len(male_df)):
                    await insert_population_to_db(male_df.iloc[i], 2*i + 1)
                    await insert_population_to_db(female_df.iloc[i], 2*i)

    except Exception as e:
        print(f"Error inserting population data: {e}")
        raise


from fastapi import HTTPException
import pandas as pd
import os
from app.crud.population import *
import re
from dotenv import load_dotenv
from app.crud.statistics import (
    select_nationwide_jscore_by_stat_item_id_and_sub_district_id,
    select_state_item_id,
)
from app.schemas.loc_info import LocationInfoReportOutput
from app.schemas.population import Population, PopulationJScoreOutput, PopulationSearch
from app.schemas.city import City
from app.schemas.district import District
from app.schemas.statistics import LocStatisticsOutput, StatisticsJscoreOutput
from app.schemas.sub_district import SubDistrict
from app.db.connect import *
from datetime import datetime, timedelta
from app.crud.population import (
    get_latest_population_data_by_subdistrict_id as crud_get_latest_population_data_by_subdistrict_id,
)

from app.crud.loc_store import (
    select_loc_info_report_data_by_sub_district_id as crud_select_loc_info_report_data_by_sub_district_id,
    select_local_store_sub_distirct_id_by_store_business_number as crud_select_local_store_sub_distirct_id_by_store_business_number,
)


# 상세 조회
async def filter_population_data(filters: dict):
    # print("서비스 전")
    try:
        # select/population.py의 쿼리 함수 호출
        results = get_filtered_population_data(filters)
        return results
    except Exception as e:
        raise Exception(f"Error in filtering population data: {str(e)}")


# 엑셀 다운
async def download_data(filters: dict):
    try:
        results = download_data_ex(filters)
        print("엑셀 다운 로드 후")
        return results
    except Exception as e:
        raise Exception(f"Error in filtering population data: {str(e)}")


# 1. 데이터베이스 조회용 저번 달 ('YYYY-MM-DD' 형식)
def get_previous_month_for_db():
    """현재 날짜 기준으로 저번 달을 'YYYY-MM-DD' 형식으로 반환하는 함수."""
    today = datetime.today()
    first_day_of_this_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_this_month - timedelta(days=1)
    return last_day_of_previous_month.strftime("%Y-%m-%d")  # 'YYYY-MM-DD' 형식


# 2. 파일명 필터링용 저번 달 ('YYYYMMDD' 형식)
def get_previous_month_for_file():
    """현재 날짜 기준으로 저번 달을 'YYYYMMDD' 형식으로 반환하는 함수."""
    today = datetime.today()
    first_day_of_this_month = today.replace(day=1)
    last_day_of_previous_month = first_day_of_this_month - timedelta(days=1)
    return last_day_of_previous_month.strftime("%Y%m%d")  # 'YYYYMMDD' 형식


# .env 파일에서 환경 변수를 로드합니다.
load_dotenv()

# ROOT_PATH 환경 변수 불러오기
ROOT_PATH = os.getenv("ROOT_PATH")

# CSV 파일이 있는 디렉토리 설정
csv_directory = os.path.join(ROOT_PATH, "app", "data", "populationData")


def load_and_insert_population_data():
    connection = get_db_connection()

    # 1. 저번 달 계산 (DB 조회용 및 파일 필터링용)
    previous_month_db = get_previous_month_for_db()  # 'YYYY-MM-DD' 형식
    previous_month_file = get_previous_month_for_file()  # 'YYYYMMDD' 형식

    # 2. 데이터베이스에 저번 달 데이터가 있는지 확인
    exists = check_previous_month_data_exists(connection, previous_month_db)

    if exists:
        print(
            f"저번 달({previous_month_db}) 데이터가 이미 존재합니다. 인서트를 생략합니다."
        )
        return

    # 3. 저번 달 파일 필터링
    try:
        files = [
            f
            for f in os.listdir(csv_directory)
            if previous_month_file in f and f.endswith(".csv")
        ]
        if not files:
            print(f"저번 달({previous_month_file})에 해당하는 파일을 찾을 수 없습니다.")
            return

        for file_name in sorted(files):
            file_path = os.path.join(csv_directory, file_name)

            df = pd.read_csv(file_path, encoding="euc-kr")

            df = df.fillna("세종특별자치시")
            df = df.replace({"": "세종특별자치시", " ": "세종특별자치시"})

            # 1. 필요한 데이터를 미리 로드합니다.
            cities = load_all_cities(connection)
            districts = load_all_districts(connection)
            sub_districts = load_all_sub_districts(connection)

            for index, row in df.iterrows():
                try:
                    city_name = row["시도명"]
                    district_name = row["시군구명"]
                    sub_district_name = row["읍면동명"]

                    # sub_district_name에 '출장소'라는 단어가 포함된 경우, 건너뛰기
                    if "출장소" in sub_district_name:
                        continue

                    # sub_district_name에서 '제'를 제거
                    if isinstance(sub_district_name, str):
                        sub_district_name = re.sub(r"제(\d)", r"\1", sub_district_name)

                    # 특정 패턴의 동명 매핑 작업
                    mappings = {
                        "숭의1.3동": "숭의1,3동",
                        "용현1.4동": "용현1,4동",
                        "도화2.3동": "도화2,3동",
                        "봉명2송정동": "봉명2.송정동",
                        "성화개신죽림동": "성화.개신.죽림동",
                        "용담명암산성동": "용담.명암.산성동",
                        "운천신봉동": "운천.신봉동",
                        "율량사천동": "율량.사천동",
                    }
                    if sub_district_name in mappings:
                        sub_district_name = mappings[sub_district_name]

                    # district_name에 띄어쓰기가 있으면, 첫 번째 단어만 사용
                    if " " in district_name:
                        district_name = district_name.split()[0]

                    # 2. 로드된 데이터에서 참조
                    city = cities.get(city_name)
                    district = districts.get((city.city_id, district_name))
                    sub_district = sub_districts.get(
                        (district.district_id, sub_district_name)
                    )

                    # 행정기관코드와 기준연월
                    admin_code = row["행정기관코드"]
                    reference_date = row["기준연월"]

                    # 남자와 여자의 인구수를 각각 가져옴
                    male_population = row["남자"]
                    female_population = row["여자"]

                    # 계(total_population)를 남자와 여자의 합으로 설정
                    total_population = male_population + female_population

                    # 성별 데이터와 gender_id를 처리
                    gender_data = [
                        {
                            "gender_id": 1,
                            "gender": "남자",
                            "population": male_population,
                        },
                        {
                            "gender_id": 2,
                            "gender": "여자",
                            "population": female_population,
                        },
                    ]

                    for gender_info in gender_data:
                        gender_id = gender_info["gender_id"]
                        gender = gender_info["gender"]

                        # 나이별 인구 데이터를 처리
                        age_data = {}
                        for age in range(0, 110):
                            age_data[f"age_{age}"] = row[f"{age}세{gender}"]
                        age_data["age_110_over"] = row[f"110세이상 {gender}"]

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
                            sub_district_name=sub_district_name,
                            total_population=total_population,
                            male_population=male_population if gender_id == 1 else 0,
                            female_population=(
                                female_population if gender_id == 2 else 0
                            ),
                            **age_data,
                        )

                        insert_population_data(connection, population_data)

                except Exception as e:
                    print(f"Row data: {row}")
                    continue

        # 모든 데이터가 성공적으로 삽입된 후에 커밋
        commit(connection)

    except Exception as e:
        print(f"Error during population data insertion: {e}")
    finally:
        close_connection(connection)

    # 만약 폴더 내의 마지막 파일만 처리하려면 아래의 코드를 사용합니다:
    # 파일 목록을 정렬하여 가장 마지막 파일을 선택하고, 해당 파일만 처리
    # 들여쓰기 주의
    # last_file = sorted(files)[-1]
    # file_path = os.path.join(csv_directory, last_file)
    # df = pd.read_csv(file_path, encoding='euc-kr')
    # 이후 처리 로직은 동일하게 적용됩니다.


# 미리 데이터를 로드하는 함수들
# 데이터 로드 함수들
def load_all_cities(connection):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT city_id, city_name FROM city")
        result = cursor.fetchall()
        return {
            row["city_name"]: City(city_id=row["city_id"], city_name=row["city_name"])
            for row in result
        }


def load_all_districts(connection):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute("SELECT district_id, city_id, district_name FROM district")
        result = cursor.fetchall()
        return {
            (row["city_id"], row["district_name"]): District(
                district_id=row["district_id"],
                city_id=row["city_id"],
                district_name=row["district_name"],
            )
            for row in result
        }


def load_all_sub_districts(connection):
    with connection.cursor(pymysql.cursors.DictCursor) as cursor:
        cursor.execute(
            """
            SELECT sd.sub_district_id, sd.district_id, sd.sub_district_name, d.city_id
            FROM sub_district sd
            JOIN district d ON sd.district_id = d.district_id
        """
        )
        result = cursor.fetchall()

        return {
            (row["district_id"], row["sub_district_name"]): SubDistrict(
                sub_district_id=row["sub_district_id"],
                district_id=row["district_id"],
                city_id=row["city_id"],  # city_id 추가
                sub_district_name=row["sub_district_name"],
            )
            for row in result
        }


if __name__ == "__main__":
    load_and_insert_population_data()


def select_report_population_by_store_business_number(
    store_business_id: str,
) -> PopulationJScoreOutput:
    try:
        sub_district_id: int = (
            crud_select_local_store_sub_distirct_id_by_store_business_number(
                store_business_id
            )
        )

        if sub_district_id is None:
            raise HTTPException(status_code=404, detail="Sub-district ID not found.")

        # 최신 인구 데이터 조회
        population_data = crud_get_latest_population_data_by_subdistrict_id(
            sub_district_id
        )

        # 통계 항목 ID 조회
        resident_stat_item_id: int = select_state_item_id("loc_info", "resident")
        work_pop_stat_item_id: int = select_state_item_id("loc_info", "work_pop")
        house_stat_item_id: int = select_state_item_id("loc_info", "house")
        shop_stat_item_id: int = select_state_item_id("loc_info", "shop")
        income_stat_item_id: int = select_state_item_id("loc_info", "income")

        # J-score 조회 및 반올림 처리
        resident_jscore: float = round(
            select_nationwide_jscore_by_stat_item_id_and_sub_district_id(
                resident_stat_item_id, sub_district_id
            ),
            1,
        )
        work_pop_jscore: float = round(
            select_nationwide_jscore_by_stat_item_id_and_sub_district_id(
                work_pop_stat_item_id, sub_district_id
            ),
            1,
        )
        house_jscore: float = round(
            select_nationwide_jscore_by_stat_item_id_and_sub_district_id(
                house_stat_item_id, sub_district_id
            ),
            1,
        )
        shop_jscore: float = round(
            select_nationwide_jscore_by_stat_item_id_and_sub_district_id(
                shop_stat_item_id, sub_district_id
            ),
            1,
        )
        income_jscore: float = round(
            select_nationwide_jscore_by_stat_item_id_and_sub_district_id(
                income_stat_item_id, sub_district_id
            ),
            1,
        )

        j_score_data = LocStatisticsOutput(
            resident_jscore=resident_jscore,
            work_pop_jscore=work_pop_jscore,
            house_jscore=house_jscore,
            shop_jscore=shop_jscore,
            income_jscore=income_jscore,
        )

        loc_info_data: LocationInfoReportOutput = (
            crud_select_loc_info_report_data_by_sub_district_id(sub_district_id)
        )

        population_j_score_data = PopulationJScoreOutput(
            population_data=population_data,
            j_score_data=j_score_data,
            loc_info_data=loc_info_data,
        )

        return population_j_score_data
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

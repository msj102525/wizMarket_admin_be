import numpy as np
from app.crud.statistics import *



################## 조회 #############################

def select_stat_data(filters_dict):
    result = get_stat_data(filters_dict)
    return result



################# 시/도, 시/군/구 id 값 가져오기 ############################

# 전역 변수 선언
city_ids_cache = None
city_district_pairs_cache =None

def fetch_city():
    global city_ids_cache
    if city_ids_cache is None:
        print("Fetching city_district_pairs from DB...")
        city_ids_cache = get_all_city_ids()  # DB에서 한 번만 가져옴
    return city_ids_cache

def fetch_city_district_pairs():
    """
    city_district_pairs를 전역 변수에 캐싱하여 한 번만 가져오는 함수
    """
    global city_district_pairs_cache
    if city_district_pairs_cache is None:
        print("Fetching city_district_pairs from DB...")
        city_district_pairs_cache = get_all_city_district_pairs()  # DB에서 한 번만 가져옴
    return city_district_pairs_cache

################# stat_item_id 값 가져오기 ########################

stat_item_id_list = None

def fetch_stat_item_id():
    global stat_item_id_list
    if stat_item_id_list is None:
        stat_item_id_list = get_stat_item_id()
    
    print(stat_item_id_list)

    return stat_item_id_list


################## 데이터 통계 값 구하기 ###################
def calculate_statistics(data):
    """
    주어진 데이터에 대해 평균, 중위수, 표준편차, 최대값, 최소값을 계산하는 함수
    """
    if not data or len(data) == 0:
        return {
            "average": None,
            "median": None,
            "stddev": None,
            "max": None,
            "min": None
        }

    avg_value = np.mean(data)
    median_value = np.median(data)
    stddev_value = np.std(data)
    max_value = np.max(data)
    min_value = np.min(data)

    return {
        "average": avg_value,
        "median": median_value,
        "stddev": stddev_value,
        "max": max_value,
        "min": min_value
    }


################### 전국 단위 j_score 계산 후 인서트 #######################
def get_j_score_national(stat_item_id):
    national_data = get_all_city_district_sub_district()

    # data는 city_id, district_id, sub_district_id, count로 구성된 리스트
    data = get_j_score_national_data(national_data)

    # 원하는 컬럼만 추출하여 별도의 리스트 생성
    counts = [item[-1] for item in data]

    # 데이터 기준으로 순위 계산
    ranked_counts = sorted(counts, reverse=True)  # 내림차순으로 정렬
    
    j_score_data_nation = []

    for city_id, district_id, sub_district_id, shop in data:
        if shop > 0:
            # 해당 매장 수의 순위
            rank = ranked_counts.index(shop) + 1
            totals = len(counts)

            # j_score 계산
            j_score = 10 * ((totals + 1 - rank) / totals)
        else:
            j_score = 0  # 매장 수가 0인 경우 j_score도 0

        # j_score_data에 (city_id, district_id, sub_district_id, count, j_score) 형태로 추가
        j_score_data_nation.append((stat_item_id, city_id, district_id, sub_district_id, j_score))

    print(j_score_data_nation)
    # insert_j_score_nation(j_score_data_nation)

    return j_score_data_nation




################### 전국 통계 값 업데이트 후 지역 통계 값 인서트 ####################
def get_city_district_and_national_statistics(stat_item_id):
    """
    전국 통계와 시/군/구별 통계를 계산하는 함수
    """
    # 1. 전국 데이터를 가져와 통계 계산
    national_data = get_national_data()
    national_stats = calculate_statistics(national_data)

    # 2. 모든 시/군/구(city_id, district_id) 쌍을 가져옴
    city_district_pairs = fetch_city_district_pairs()

    # 3. 시/군/구별 통계 계산
    city_district_stats_list = []
    for city_id, district_id in city_district_pairs:
        city_district_data = get_city_district_data(city_id, district_id)
        city_district_stats = calculate_statistics(city_district_data)
        city_district_stats_list.append({
            "city_id": city_id,
            "district_id": district_id,
            "statistics": city_district_stats
        })

    # 전국 단위 통계값 업데이트 
    national_stats = {'stat_item_id': stat_item_id, **national_stats}
    print(national_stats)
    # update_stat_nation(national_stats)

    # 시/군/구 별 통계 값 인서트
    city_district_stats_list = [{'stat_item_id': stat_item_id, **entry} for entry in city_district_stats_list]
    print(city_district_stats_list)
    # insert_stat_region(city_district_stats_list)

    return {
        "national_statistics": national_stats,
        "city_district_statistics": city_district_stats_list
    }




############# 모든 지역 내 시군구 j_score 계산 후 업데이트 ##############
def get_j_score_for_region(stat_item_id):
    """
    특정 지역(city_id) 내 시/군/구 간의 j_score를 계산하는 함수
    """
    # 해당 지역(city_id) 내 모든 district_id와 그 하위의 매장 데이터를 가져옴
    city_district_pairs = fetch_city_district_pairs()

    # 매장 데이터를 담을 리스트
    data = []

    for city_id, district_id in city_district_pairs:
        # 각 city_id와 district_id에 대한 매장 수 합산
        total_count = get_data_for_city_and_district(city_id, district_id)

        # (city_id, district_id, total_count) 형태로 리스트에 추가
        data.append((city_id, district_id, total_count))

    # 매장 수 기준으로 순위 계산 (내림차순)
    counts = [item[2] for item in data]
    ranked_counts = sorted(counts, reverse=True)

    j_score_data_region = []

    for city_id, district_id, count in data:
        if count > 0:
            # 해당 매장 수의 순위
            rank = ranked_counts.index(count) + 1
            totals = len(counts)

            # j_score 계산
            j_score = 10 * ((totals + 1 - rank) / totals)
        else:
            j_score = 0  # 매장 수가 0인 경우 j_score도 0

        # j_score_data에 (city_id, district_id, count, j_score) 형태로 추가
        j_score_data_region.append((stat_item_id, city_id, district_id, None, j_score))

    print(j_score_data_region)
    # update_j_score_data_region(j_score_data_region)

    return j_score_data_region


# 테스트 실행 예시
if __name__ == "__main__":
    get_j_score_national(8)
    get_city_district_and_national_statistics(8)
    get_j_score_for_region(8)
    # fetch_stat_item_id()
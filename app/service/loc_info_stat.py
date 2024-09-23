from app.crud.loc_info_stat import fetch_all_city_ids, fetch_districts_by_city_id, calculate_statistics

def calculate_loc_info_stats():
    # 전체 city_id 가져오기
    cities = fetch_all_city_ids()

    # 전국 통계 계산 (city_id = 0, district_id = 0)
    calculate_statistics(0, 0)
    print("Calculating statistics for 전국")

    for city in cities:
        city_id = city['city_id']
        city_name = city['city_name']

        # 전체 city에 대한 district 통계 (district_id = 0)
        calculate_statistics(city_id, 0)
        print(f"Calculating statistics for 전체 {city_name} districts")

        # 해당 city_id에 속한 district_id 가져오기
        districts = fetch_districts_by_city_id(city_id)
        
        for district in districts:
            district_id = district['district_id']
            district_name = district['district_name']

            calculate_statistics(city_id, district_id)
            print(f"Calculating statistics for {district_name} in {city_name}")


def test_calculate_statistics():
    city_id = 1
    district_id = 3  # 임의로 설정된 district_id
    
    stats = calculate_statistics(city_id, district_id)
    print("통계 결과:")
    print(f"평균: {stats['average']}")
    print(f"중위수: {stats['median']}")
    print(f"표준편차: {stats['std_dev']}")
    print(f"최대값: {stats['max']}")
    print(f"최소값: {stats['min']}")
    print(f"스코어: {stats['ranking_scores']}")

# 테스트 실행
if __name__ == "__main__":
    # calculate_loc_info_stats()
    test_calculate_statistics()
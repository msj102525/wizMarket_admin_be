import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

data_list = []


def setup_driver():
    driver_path = os.path.join(
        os.path.dirname(__file__), "../", "drivers", "chromedriver.exe"
    )

    options = Options()
    options.add_argument("--start-fullscreen")

    prefs = {
        "download.default_directory": os.path.join(
            os.path.dirname(__file__), "downloads"
        ),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)

    # 크롬 드라이버 서비스 설정
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    return driver


commercial_district_url = "https://m.nicebizmap.co.kr/analysis/analysisFree"


driver = setup_driver()


def click_element(wait, by, value):
    element = wait.until(EC.element_to_be_clickable((by, value)))
    text = element.text
    element.click()
    time.sleep(0.7)
    driver.implicitly_wait(10)  # 안전장치
    return text


def read_element(wait, by, value):
    element = wait.until(EC.presence_of_element_located((by, value)))
    text = element.text
    time.sleep(0.3)
    driver.implicitly_wait(5)  # 안전장치
    # print(text)
    return text


def convert_to_float(percent_str):
    return float(percent_str.replace("%", "").strip())


def get_district_count():
    driver = setup_driver()
    try:

        driver.get(commercial_district_url)  # URL 접속
        driver.implicitly_wait(10)

        wait = WebDriverWait(driver, 10)  # 10초 대기

        # 분석 지역을해주세요
        click_element(
            wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
        )

        # 시/도
        city_text = click_element(
            wait,
            By.XPATH,
            '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[1]/a',
        )

        district_ul = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul')
            )
        )
        district_ul_li = district_ul.find_elements(By.TAG_NAME, "li")

        print(f"구 갯수: {len(district_ul_li)}")
        driver.quit()
        loop_search_commercial_district(len(district_ul_li))

    except Exception as e:
        raise Exception(
            f"Failed to fetch data from {commercial_district_url}: {str(e)}"
        )
    finally:
        driver.quit()


def loop_search_commercial_district(district_count):
    print(district_count)
    driver = setup_driver()
    try:
        for idx in range(district_count):
            print(f'idx: {idx}')
            driver.get(commercial_district_url)  # URL 접속
            driver.implicitly_wait(10)

            wait = WebDriverWait(driver, 10)  # 10초 대기

            # 분석 지역을해주세요
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
            )

            # 시/도
            city_text = click_element(
                wait,
                By.XPATH,
                '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[1]/a',
            )

            # 시/군/구
            click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{idx + 1}]/a',
            )

            sub_district_ul = wait.until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        '#basicReport > div.sheet.sheet_01.md_sheet.on > div.sheet_body.pd > div.box.select_bx > div > div.loca_list_bx > ul',
                    )
                )
            )
            sub_district_ul_li_real = sub_district_ul.find_elements(By.TAG_NAME, "li")
            sub_district_ul_li = [1, 2, 3]

            print(f"동 갯수: {len(sub_district_ul_li_real)}")
            # print(f"동 갯수: {len(sub_district_ul_li)}")

            # 읍/면/동
            sub_district_text = click_element(
                wait,
                By.XPATH,
                '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[1]/a',
            )
            for idx2 in range(len(sub_district_ul_li)):
                print(idx, idx2)
                driver.quit()
                search_commercial_district(idx, idx2)

    except Exception as e:
        raise Exception(
            f"Failed to fetch data from {commercial_district_url}: {str(e)}"
        )
    finally:
        driver.quit()


def search_commercial_district(district_idx, sub_district_idx):
    driver = setup_driver()
    print(district_idx, sub_district_idx)
    try:
        start_time = time.time()  # 시작 시간 기록

        driver.get(commercial_district_url)  # URL 접속
        driver.implicitly_wait(10)

        wait = WebDriverWait(driver, 10)  # 10초 대기

        # 페이지 제목 가져오기
        title = driver.title

        # 분석 지역을해주세요
        click_element(
            wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
        )

        # 시/도
        city_text = click_element(
            wait,
            By.XPATH,
            '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[1]/a',
        )

        # 시/군/구
        district_text = click_element(
            wait,
            By.XPATH,
            f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
        )
        time.sleep(1)

        # 읍/면/동
        sub_district_text = click_element(
            wait,
            By.XPATH,
            f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
        )

        print('성공1')

        time.sleep(1)
        # 대분류
        main_category = click_element(
            wait,
            By.XPATH,
            '//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[1]/li[1]/button',
        )

        print('성공2')
        time.sleep(1)
        # 중분류
        sub_category = click_element(
            wait,
            By.XPATH,
            '//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[2]/ul/li[1]/button',
        )

        print('성공3')
        time.sleep(1)
        # 소분류
        detail_category = click_element(
            wait,
            By.XPATH,
            '//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[2]/ul/li[2]/ul/li[1]/button',
        )

        print('성공4')
        time.sleep(1)

        detail_category = detail_category.replace("(확장 분석)", "").strip()


        print(city_text, district_text, sub_district_text, main_category, sub_category, detail_category)

        print('성공5')
        data = search_data(
            wait,
            title,
            city_text,
            district_text,
            sub_district_text,
            main_category,
            sub_category,
            detail_category,
        )

        data_list.append(data)

        end_time = time.time()
        elapsed_time = end_time - start_time

        print(f"Time taken : {elapsed_time}")
        # print(f"Result : {data_list}")
        print(f"Result : {city_text, district_text, sub_district_text}")

        # return data, elapsed_time
    except Exception as e:
        raise Exception(
            f"Failed to fetch data from {commercial_district_url}: {str(e)}"
        )
    finally:
        driver.quit()


def search_data(
    wait,
    title,
    city_text,
    district_text,
    sub_district_text,
    main_category,
    sub_category,
    detail_category,
):
    # 상권분석 보기
    click_element(wait, By.XPATH, '//*[@id="pcBasicReport"]')

    # 분석 텍스트 보기 없애기
    click_element(
        wait,
        By.XPATH,
        '//*[@id="report1"]/div/div[4]/div[1]/div/div/div/div[1]/div[2]/label',
    )

    # 표 전제보기
    click_element(
        wait,
        By.XPATH,
        '//*[@id="report1"]/div/div[4]/div[1]/div/div/div/div[1]/div[1]/label',
    )

    time.sleep(0.5)

    # 밀집도 클릭
    click_element(
        wait,
        By.XPATH,
        '//*[@id="report1"]/div/div[3]/div/ul/li[2]/a',
    )

    # 전국 해당 업종수 밀집도 데이터
    all_detail_category_count = read_element(
        wait,
        By.XPATH,
        '//*[@id="s2"]/div[2]/div[2]/div/div[2]/table/tbody/tr[3]/td[2]',
    )

    # 해당 시, 해당 업종수 밀집도 데이터
    city_detail_category_count = read_element(
        wait,
        By.XPATH,
        '//*[@id="s2"]/div[2]/div[2]/div/div[2]/table/tbody/tr[3]/td[3]',
    )

    # 해당 구, 해당 업종수 밀집도 데이터
    district_detail_category_count = read_element(
        wait,
        By.XPATH,
        '//*[@id="s2"]/div[2]/div[2]/div/div[2]/table/tbody/tr[3]/td[4]',
    )

    # 해당 지역, 해당 업종수 밀집도 데이터
    sub_district_detail_category_count = read_element(
        wait,
        By.XPATH,
        '//*[@id="s2"]/div[2]/div[2]/div/div[2]/table/tbody/tr[3]/td[5]',
    )

    # 시장규모 클릭
    click_element(
        wait,
        By.XPATH,
        '//*[@id="report1"]/div/div[3]/div/ul/li[3]/a',
    )

    # 해당지역 업종 총 시장규모(원) 제일 최신
    sub_district_market_size = read_element(
        wait,
        By.XPATH,
        '//*[@id="s3"]/div[2]/div[2]/div[2]/table/tbody/tr/td[7]',
    )

    # 매출규모 클릭
    click_element(
        wait,
        By.XPATH,
        '//*[@id="report1"]/div/div[3]/div/ul/li[4]/a',
    )

    # 해당지역 업종 점포당 매출규모(원)
    sub_district_total_size = read_element(
        wait,
        By.XPATH,
        '//*[@id="s4"]/div[2]/div[3]/div[2]/table/tbody/tr/td[7]',
    )

    # 결제단가 클릭
    click_element(
        wait,
        By.XPATH,
        '//*[@id="report1"]/div/div[3]/div/ul/li[6]/a',
    )

    # 해당지역 업종 결제단가(원)
    sub_district_average_price = read_element(
        wait,
        By.XPATH,
        '//*[@id="s6"]/div[2]/div[2]/div[2]/table/tbody/tr[2]/td[7]',
    )

    # 해당지역 업종 이용건수(건)
    sub_district_usage_count = read_element(
        wait,
        By.XPATH,
        '//*[@id="s6"]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[7]',
    )

    # 비용/수익통계 클릭
    click_element(
        wait,
        By.XPATH,
        '//*[@id="report1"]/div/div[3]/div/ul/li[7]/a',
    )

    # 해당지역 평균매출(원)
    sub_district_avg_sales = read_element(
        wait,
        By.XPATH,
        '//*[@id="receipt1"]/div/div[2]/ul/li[1]/p[2]/b',
    )

    # 해당지역 평균 영업이익(원)
    sub_district_avg_profit_won = read_element(
        wait,
        By.XPATH,
        '//*[@id="receipt1"]/div/div[2]/ul/li[4]/p[2]/b',
    )

    # 해당지역 평균 영업비용(%)
    sub_district_avg_profit_percent = read_element(
        wait,
        By.XPATH,
        '//*[@id="receipt1"]/div/div[2]/ul/li[2]/p[1]/span',
    )

    # 해당지역 평균 영업이익(%)
    sub_district_avg_profit_percent = read_element(
        wait,
        By.XPATH,
        '//*[@id="receipt1"]/div/div[2]/ul/li[4]/p[1]/span',
    )

    # 매출 비중 클릭
    click_element(
        wait,
        By.XPATH,
        '//*[@id="report1"]/div/div[3]/div/ul/li[8]/a',
    )

    # 해당지역 업종 매출 요일별 (월요일 %)
    sub_district_avg_profit_percent_mon = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[1]/tbody/tr/td[2]',
    )

    # 해당지역 업종 매출 요일별 (화요일 %)
    sub_district_avg_profit_percent_tues = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[1]/tbody/tr/td[3]',
    )

    # 해당지역 업종 매출 요일별 (수요일 %)
    sub_district_avg_profit_percent_wed = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[1]/tbody/tr/td[4]',
    )

    # 해당지역 업종 매출 요일별 (목요일 %)
    sub_district_avg_profit_percent_thurs = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[1]/tbody/tr/td[5]',
    )

    # 해당지역 업종 매출 요일별 (금요일 %)
    sub_district_avg_profit_percent_fri = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[1]/tbody/tr/td[6]',
    )

    # 해당지역 업종 매출 요일별 (토요일 %)
    sub_district_avg_profit_percent_sat = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[1]/tbody/tr/td[7]',
    )

    # 해당지역 업종 매출 요일별 (일요일 %)
    sub_district_avg_profit_percen_sun = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[1]/tbody/tr/td[8]',
    )

    sub_district_avg_profit_percents = {
        "Monday": sub_district_avg_profit_percent_mon,
        "Tuesday": sub_district_avg_profit_percent_tues,
        "Wednesday": sub_district_avg_profit_percent_wed,
        "Thursday": sub_district_avg_profit_percent_thurs,
        "Friday": sub_district_avg_profit_percent_fri,
        "Saturday": sub_district_avg_profit_percent_sat,
        "Sunday": sub_district_avg_profit_percen_sun,
    }

    # 가장 높은 매출 비율을 가진 요일을 찾음
    sub_district_avg_profit_percent_most_day = max(
        sub_district_avg_profit_percents, key=sub_district_avg_profit_percents.get
    )

    sub_district_avg_profit_percent_most_day_value = sub_district_avg_profit_percents[
        sub_district_avg_profit_percent_most_day
    ]

    # 해당지역 업종 매출 시간별 (06 ~ 09  %)
    sub_district_avg_profit_percent_06_09 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[2]/tbody/tr[2]/td[2]',
    )

    # 해당지역 업종 매출 시간별 (09 ~ 12  %)
    sub_district_avg_profit_percent_09_12 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[2]/tbody/tr[2]/td[3]',
    )

    # 해당지역 업종 매출 시간별 (12 ~ 15  %)
    sub_district_avg_profit_percent_12_15 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[2]/tbody/tr[2]/td[4]',
    )

    # 해당지역 업종 매출 시간별 (15 ~ 18  %)
    sub_district_avg_profit_percent_15_18 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[2]/tbody/tr[2]/td[5]',
    )

    # 해당지역 업종 매출 시간별 (18 ~ 21  %)
    sub_district_avg_profit_percent_18_21 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[2]/tbody/tr[2]/td[6]',
    )

    # 해당지역 업종 매출 시간별 (21 ~ 24  %)
    sub_district_avg_profit_percent_21_24 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[2]/tbody/tr[2]/td[7]',
    )

    # 해당지역 업종 매출 시간별 (24 ~ 06  %)
    sub_district_avg_profit_percen_24_06 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s8"]/div[2]/div[2]/div[2]/table[2]/tbody/tr[2]/td[8]',
    )

    # 시간대별 매출 비율을 딕셔너리에 저장
    sub_district_avg_profit_percents_by_time = {
        "06_09": sub_district_avg_profit_percent_06_09,
        "09_12": sub_district_avg_profit_percent_09_12,
        "12_15": sub_district_avg_profit_percent_12_15,
        "15_18": sub_district_avg_profit_percent_15_18,
        "18_21": sub_district_avg_profit_percent_18_21,
        "21_24": sub_district_avg_profit_percent_21_24,
        "24_06": sub_district_avg_profit_percen_24_06,
    }

    # 가장 높은 매출 비율을 가진 시간대를 찾음
    sub_district_avg_profit_percent_most_time = max(
        sub_district_avg_profit_percents_by_time,
        key=sub_district_avg_profit_percents_by_time.get,
    )

    # 가장 높은 매출 비율의 값을 저장
    sub_district_avg_profit_percent_most_time_value = (
        sub_district_avg_profit_percents_by_time[
            sub_district_avg_profit_percent_most_time
        ]
    )

    # 고객 비중 클릭
    click_element(
        wait,
        By.XPATH,
        '//*[@id="report1"]/div/div[3]/div/ul/li[9]/a',
    )

    # 남 20대
    sub_district_avg_client_percent_m_20 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s9"]/div[2]/div[2]/div[2]/table[1]/tbody/tr[1]/td[2]',
    )

    # 남 30대
    sub_district_avg_client_percent_m_30 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s9"]/div[2]/div[2]/div[2]/table[1]/tbody/tr[1]/td[3]',
    )

    # 남 40대
    sub_district_avg_client_percent_m_40 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s9"]/div[2]/div[2]/div[2]/table[1]/tbody/tr[1]/td[4]',
    )

    # 남 50대
    sub_district_avg_client_percent_m_50 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s9"]/div[2]/div[2]/div[2]/table[1]/tbody/tr[1]/td[5]',
    )

    # 남 60대 이상
    sub_district_avg_client_percent_m_60 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s9"]/div[2]/div[2]/div[2]/table[1]/tbody/tr[1]/td[6]',
    )

    # 여 20대
    sub_district_avg_client_percent_f_20 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s9"]/div[2]/div[2]/div[2]/table[1]/tbody/tr[2]/td[2]',
    )

    # 여 30대
    sub_district_avg_client_percent_f_30 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s9"]/div[2]/div[2]/div[2]/table[1]/tbody/tr[2]/td[3]',
    )

    # 여 40대
    sub_district_avg_client_percent_f_40 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s9"]/div[2]/div[2]/div[2]/table[1]/tbody/tr[2]/td[4]',
    )

    # 여 50대
    sub_district_avg_client_percent_f_50 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s9"]/div[2]/div[2]/div[2]/table[1]/tbody/tr[2]/td[5]',
    )

    # 여 60대 이상
    sub_district_avg_client_percent_f_60 = read_element(
        wait,
        By.XPATH,
        '//*[@id="s9"]/div[2]/div[2]/div[2]/table[1]/tbody/tr[2]/td[6]',
    )

    # 남성 비중 리스트
    male_percents = [
        convert_to_float(sub_district_avg_client_percent_m_20),
        convert_to_float(sub_district_avg_client_percent_m_30),
        convert_to_float(sub_district_avg_client_percent_m_40),
        convert_to_float(sub_district_avg_client_percent_m_50),
        convert_to_float(sub_district_avg_client_percent_m_60),
    ]

    # 여성 비중 리스트
    female_percents = [
        convert_to_float(sub_district_avg_client_percent_f_20),
        convert_to_float(sub_district_avg_client_percent_f_30),
        convert_to_float(sub_district_avg_client_percent_f_40),
        convert_to_float(sub_district_avg_client_percent_f_50),
        convert_to_float(sub_district_avg_client_percent_f_60),
    ]

    total_male_percent = sum(male_percents)
    total_female_percent = sum(female_percents)

    if total_male_percent > total_female_percent:
        dominant_gender = "남성"
        dominant_gender_percent = total_male_percent
    else:
        dominant_gender = "여성"
        dominant_gender_percent = total_female_percent

    age_groups = ["20대", "30대", "40대", "50대", "60대"]
    total_percents = [m + f for m, f in zip(male_percents, female_percents)]

    max_age_percent = max(total_percents)
    dominant_age_group = age_groups[total_percents.index(max_age_percent)]

    # 고객 비중 클릭
    click_element(
        wait,
        By.XPATH,
        '//*[@id="report1"]/div/div[3]/div/ul/li[10]/a',
    )

    # 가장 많은 연령대의 유동인구

    most_visitor_age = read_element(
        wait,
        By.XPATH,
        '//*[@id="s10"]/div[1]/p',
    )

    # 주요 메뉴/뜨는 메뉴 클릭
    click_element(
        wait,
        By.XPATH,
        '//*[@id="report1"]/div/div[3]/div/ul/li[11]/a',
    )

    time.sleep(0.2)

    # 뜨는 메뉴 클릭
    click_element(
        wait,
        By.XPATH,
        '//*[@id="s11"]/div[2]/div[2]/div/div[1]/ul/li[2]/button',
    )

    top5_menu_1 = read_element(
        wait,
        By.XPATH,
        '//*[@id="popular_graph"]/div/div[2]/div[2]/table/tbody/tr[1]/td[3]',
    )

    top5_menu_2 = read_element(
        wait,
        By.XPATH,
        '//*[@id="popular_graph"]/div/div[2]/div[2]/table/tbody/tr[2]/td[3]',
    )

    top5_menu_3 = read_element(
        wait,
        By.XPATH,
        '//*[@id="popular_graph"]/div/div[2]/div[2]/table/tbody/tr[3]/td[3]',
    )

    top5_menu_4 = read_element(
        wait,
        By.XPATH,
        '//*[@id="popular_graph"]/div/div[2]/div[2]/table/tbody/tr[4]/td[3]',
    )

    top5_menu_5 = read_element(
        wait,
        By.XPATH,
        '//*[@id="popular_graph"]/div/div[2]/div[2]/table/tbody/tr[5]/td[3]',
    )

    time.sleep(1.5)

    data = {
        "title": title,
        "location": {
            "city": city_text,
            "district": district_text,
            "sub_district": sub_district_text,
        },
        "category": {
            "main": main_category,
            "sub": sub_category,
            "detail": detail_category,
        },
        "density": {
            "national": all_detail_category_count,
            "city": city_detail_category_count,
            "district": district_detail_category_count,
            "sub_district": sub_district_detail_category_count,
        },
        "market_size": sub_district_market_size,
        "average_sales": sub_district_total_size,
        "average_price": sub_district_average_price,
        "usage_count": sub_district_usage_count,
        "average_profit": {
            "amount": sub_district_avg_profit_won,
            "percent": sub_district_avg_profit_percent,
        },
        "sales_by_day": {
            "most_profitable_day": sub_district_avg_profit_percent_most_day,
            "percent": sub_district_avg_profit_percent_most_day_value,
            "details": sub_district_avg_profit_percents,
        },
        "sales_by_time": {
            "most_profitable_time": sub_district_avg_profit_percent_most_time,
            "percent": sub_district_avg_profit_percent_most_time_value,
            "details": sub_district_avg_profit_percents_by_time,
        },
        "client_demographics": {
            "dominant_gender": dominant_gender,
            "dominant_gender_percent": dominant_gender_percent,
            "dominant_age_group": dominant_age_group,
            "age_groups": age_groups,
            "male_percents": male_percents,
            "female_percents": female_percents,
            "most_visitor_age": most_visitor_age,
        },
        "top5_menus": [top5_menu_1, top5_menu_2, top5_menu_3, top5_menu_4, top5_menu_5],
    }

    return data


if __name__ == "__main__":
    get_district_count()
    # loop_search_commercial_district()
    print(data_list)

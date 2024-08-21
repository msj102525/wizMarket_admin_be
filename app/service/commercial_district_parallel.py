from concurrent.futures import ThreadPoolExecutor
import time
import os
from typing import Dict, List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    NoAlertPresentException,
)
from selenium.webdriver.common.alert import Alert
from tqdm import tqdm

from app.crud.commercial_district import insert_commercial_district

commercial_district_url = "https://m.nicebizmap.co.kr/analysis/analysisFree"


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

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def click_element(wait, by, value):
    try:
        element = wait.until(EC.element_to_be_clickable((by, value)))
        text = element.text
        element.click()
        time.sleep(1)
        return text
    except Exception as e:
        print(
            f"Exception occurred: {e} for element located by {by} with value {value}. Skipping to next element."
        )
        return None


def read_element(wait, by, value):
    try:
        element = wait.until(EC.presence_of_element_located((by, value)))
        text = element.text
        time.sleep(0.5)
        return text
    except Exception as e:
        print(
            f"Exception occurred: {e} for element located by {by} with value {value}. Skipping to next element."
        )
        return None


def convert_to_float(percent_str):
    try:
        clean_str = percent_str.replace("%", "").replace(",", "").strip()
        return float(clean_str)
    except ValueError:
        return 0.0


def handle_unexpected_alert(driver):
    try:
        alert = Alert(driver)
        alert_text = alert.text
        print(f"Alert detected: {alert_text}")
        alert.accept()
        return True
    except NoAlertPresentException:
        return False


# def get_city_count(start_idx: int, end_idx: int):
#     driver = setup_driver()
#     print(f"Processing range {start_idx} to {end_idx}")
#     try:
#         driver.get(commercial_district_url)
#         wait = WebDriverWait(driver, 20)
#         driver.implicitly_wait(10)

#         # 분석 지역
#         click_element(
#             wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
#         )

#         city_ul = wait.until(
#             EC.presence_of_element_located(
#                 (By.XPATH, '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul')
#             )
#         )
#         city_ul_li = city_ul.find_elements(By.TAG_NAME, "li")
#         print(f"시/도 갯수: {len(city_ul_li)}")

#         for city_idx in range(start_idx, end_idx):
#             get_district_count(len(city_ul_li))

#     except Exception as e:
#         print(f"Exception occurred: {e}.")
#         return None
#     finally:
#         print(f"시/도 종료!")
#         try:
#         if driver:
#         driver.quit()
#         except Exception as quit_error:
#         print(f"Error closing driver: {str(quit_error)}")


def get_district_count(start_idx: int, end_idx: int):
    driver = setup_driver()
    try:
        for city_idx in tqdm(range(start_idx, end_idx), desc="시/도 Progress"):
            print(f"City idx: {city_idx}")

            driver.get(commercial_district_url)
            wait = WebDriverWait(driver, 20)

            # 분석 지역
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
            )

            city_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
            )

            district_ul = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul',
                    )
                )
            )
            district_ul_li = district_ul.find_elements(By.TAG_NAME, "li")
            print(f"시/군/구 갯수: {len(district_ul_li)}")

            get_sub_district_count(city_idx, len(district_ul_li))
    except Exception as e:
        print(f"Exception occurred: {e}.")
        return None
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def get_sub_district_count(city_idx: int, district_count: int):
    driver = setup_driver()
    try:
        for district_idx in tqdm(range(district_count), "시/군/구 Progress"):
            print(f"District idx: {district_idx}")
            driver.get(commercial_district_url)
            wait = WebDriverWait(driver, 20)

            # 분석 지역
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
            )

            city_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
            )

            district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
            )

            sub_district_ul = wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul',
                    )
                )
            )
            sub_district_ul_li = sub_district_ul.find_elements(By.TAG_NAME, "li")
            print(f"읍/면/동 갯수: {len(sub_district_ul_li)}")

            print(f"시/도 : {city_text}, 시/군/구 : {district_text}")

            get_main_category(city_idx, district_idx, len(sub_district_ul_li))
    except Exception as e:
        print(f"Exception occurred: {e}.")
        return None
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def get_main_category(city_idx: int, district_idx: int, sub_district_count: int):
    driver = setup_driver()
    try:
        for sub_district_idx in tqdm(range(sub_district_count), "읍/면/동 Progress"):
            print(f"Sub District idx: {sub_district_idx}")
            driver.get(commercial_district_url)
            wait = WebDriverWait(driver, 20)

            # 분석 지역
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
            )

            city_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
            )

            district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
            )

            sub_district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
            )

            print(
                f"시/도 : {city_text}, 시/군/구 : {district_text}, 읍/면/동 : {sub_district_text}"
            )

            main_category_ul_1 = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[1]')
                )
            )

            main_category_ul_1_li = main_category_ul_1.find_elements(By.TAG_NAME, "li")
            print(f"대분류1 갯수 : {len(main_category_ul_1_li)}")

            m_c_ul = 1

            get_sub_category(
                city_idx,
                district_idx,
                sub_district_idx,
                len(main_category_ul_1_li),
                m_c_ul,
            )

        for sub_district_idx in tqdm(range(sub_district_count), "읍/면/동 Progress"):
            print(f"idx: {district_idx}")
            driver.get(commercial_district_url)
            wait = WebDriverWait(driver, 20)

            # 분석 지역
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
            )

            city_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
            )

            district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
            )

            sub_district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
            )

            print(
                f"시/도 : {city_text}, 시/군/구 : {district_text}, 읍/면/동 : {sub_district_text}"
            )

            main_category_ul_2 = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[3]')
                )
            )

            main_category_ul_2_li = main_category_ul_2.find_elements(By.TAG_NAME, "li")
            print(f"대분류2 갯수 : {len(main_category_ul_2_li)}")

            m_c_ul = 3

            get_sub_category(
                city_idx,
                district_idx,
                sub_district_idx,
                len(main_category_ul_2_li),
                m_c_ul,
            )

    except Exception as e:
        print(f"Exception occurred: {e}.")
        return None
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def get_sub_category(
    city_idx: int,
    district_idx: int,
    sub_district_idx: int,
    main_category_count: int,
    m_c_ul: int,
):
    driver = setup_driver()
    try:
        for main_category_idx in range(main_category_count):
            print(f"idx: {district_idx}")
            driver.get(commercial_district_url)
            wait = WebDriverWait(driver, 20)

            # 분석 지역
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
            )

            city_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
            )

            district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
            )

            sub_district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
            )

            main_category_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul}]/li[{main_category_idx + 1}]/button',
            )

            print(main_category_text)

            sub_category_li = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#basicReport ul.cate2 > ul")
                )
            )
            sub_category_ul_li_button = sub_category_li.find_elements(
                By.CSS_SELECTOR,
                "#basicReport  ul.cate2 > ul > li > button",
            )
            print(f"중분류 갯수 : {len(sub_category_ul_li_button)}")

            get_detail_category(
                city_idx,
                district_idx,
                sub_district_idx,
                main_category_idx,
                len(sub_category_ul_li_button),
                m_c_ul,
            )

    except Exception as e:
        print(f"Exception occurred: {e}.")
        return None
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def get_detail_category(
    city_idx: int,
    district_idx: int,
    sub_district_idx: int,
    main_category_idx: int,
    sub_category_count: int,
    m_c_ul: int,
):
    driver = setup_driver()
    try:
        for sub_category_idx in range(0, sub_category_count * 2, 2):
            driver.get(commercial_district_url)
            wait = WebDriverWait(driver, 20)

            # 분석 지역
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
            )

            city_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
            )

            district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
            )

            sub_district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
            )

            main_category_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul}]/li[{main_category_idx + 1}]/button',
            )

            sub_category_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul + 1}]/ul/li[{sub_category_idx + 1}]/button',
            )
            print(f"중분류 : {sub_category_text}")
            detail_category_ul = wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "#basicReport ul.cate3")
                )
            )
            detail_category_ul_li_button = detail_category_ul.find_elements(
                By.XPATH,
                f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul + 1}]/ul/li[{sub_category_idx + 2}]/ul/li',
            )
            print(f"소분류 갯수 : {len(detail_category_ul_li_button)}")

            search_commercial_district(
                city_idx,
                district_idx,
                sub_district_idx,
                main_category_idx,
                sub_category_idx,
                len(detail_category_ul_li_button),
                m_c_ul,
            )

    except Exception as e:
        print(f"Exception occurred: {e}.")
        return None
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def search_commercial_district(
    city_idx,
    district_idx,
    sub_district_idx,
    main_category_idx,
    sub_category_idx,
    detail_category_count,
    m_c_ul,
):
    driver = setup_driver()

    try:
        for detail_category_idx in range(detail_category_count):

            start_time = time.time()
            print(
                f"Execution started at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}"
            )

            driver.get(commercial_district_url)
            wait = WebDriverWait(driver, 20)

            print(detail_category_idx)

            # 분석 지역
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
            )

            city_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
            )

            district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
            )

            sub_district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
            )

            main_category_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul}]/li[{main_category_idx + 1}]/button',
            )

            sub_category_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul + 1}]/ul/li[{sub_category_idx + 1}]/button',
            )

            detail_category_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul + 1}]/ul/li[{sub_category_idx + 2}]/ul/li[{detail_category_idx + 1}]/button',
            )

            if detail_category_text:

                detail_category_text = detail_category_text.replace(
                    "(확장 분석)", ""
                ).strip()

                print(detail_category_text)

                #########################################

                # 상권분석 보기
                click_element(wait, By.XPATH, '//*[@id="pcBasicReport"]')

                time.sleep(3)

                # '//*[@id="report1"]' 요소가 나타날 때까지 기다리기
                wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="report1"]/div/div[3]/div/div',
                        )
                    )
                )

                # 분석 텍스트 보기 없애기
                click_element(
                    wait,
                    By.XPATH,
                    '//*[@id="report1"]/div/div[4]/div[1]/div/div/div/div[1]/div[2]/label',
                )

                time.sleep(1)

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

                # 해당지역 업종 이용건수(건)
                sub_district_usage_count = read_element(
                    wait,
                    By.XPATH,
                    '//*[@id="s6"]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td[7]',
                )

                # 해당지역 업종 결제단가(원)
                sub_district_avg_payment_cost = read_element(
                    wait,
                    By.XPATH,
                    '//*[@id="s6"]/div[2]/div[2]/div[2]/table/tbody/tr[2]/td[7]',
                )

                # 비용/수익통계 클릭
                click_element(
                    wait,
                    By.XPATH,
                    '//*[@id="report1"]/div/div[3]/div/ul/li[7]/a',
                )

                # 해당지역 평균매출(원)
                sub_district_total_sales = read_element(
                    wait,
                    By.XPATH,
                    '//*[@id="receipt1"]/div/div[2]/ul/li[1]/p[2]/b',
                )

                # 해당지역 영업비용(원)
                sub_district_operating_cost = read_element(
                    wait,
                    By.XPATH,
                    '//*[@id="receipt1"]/div/div[2]/ul/li[2]/p[2]/b',
                )

                # 식재료비(원)
                sub_district_food_cost = read_element(
                    wait,
                    By.XPATH,
                    '//*[@id="receipt1"]/div/div[2]/ul/li[3]/ul/li[1]/p[2]',
                )

                # 고용인 인건비(원)
                sub_district_employee_cost = read_element(
                    wait,
                    By.XPATH,
                    '//*[@id="receipt1"]/div/div[2]/ul/li[3]/ul/li[2]/p[2]',
                )

                # 임차료(원)
                sub_district_rental_cost = read_element(
                    wait,
                    By.XPATH,
                    '//*[@id="receipt1"]/div/div[2]/ul/li[3]/ul/li[3]/p[2]',
                )

                # 세금(원)
                sub_district_tax_cost = read_element(
                    wait,
                    By.XPATH,
                    '//*[@id="receipt1"]/div/div[2]/ul/li[3]/ul/li[4]/p[2]',
                )

                # 가족 종사자 인건비(원)
                sub_district_family_employee_cost = read_element(
                    wait,
                    By.XPATH,
                    '//*[@id="receipt1"]/div/div[2]/ul/li[3]/ul/li[5]/p[2]',
                )

                # 대표자 인건비(원)
                sub_district_ceo_cost = read_element(
                    wait,
                    By.XPATH,
                    '//*[@id="receipt1"]/div/div[2]/ul/li[3]/ul/li[6]/p[2]',
                )

                # 기타 인건비(원)
                sub_district_etc_cost = read_element(
                    wait,
                    By.XPATH,
                    '//*[@id="receipt1"]/div/div[2]/ul/li[3]/ul/li[7]/p[2]',
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
                    sub_district_avg_profit_percents,
                    key=sub_district_avg_profit_percents.get,
                )

                sub_district_avg_profit_percent_most_day_value = (
                    sub_district_avg_profit_percents[
                        sub_district_avg_profit_percent_most_day
                    ]
                )

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

                try:
                    top5_menu_elements = []

                    wait.until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                '//*[@id="s11"]/div[2]/div[2]',
                            )
                        )
                    )

                    for i in range(5):
                        try:
                            element = wait.until(
                                EC.presence_of_element_located(
                                    (
                                        By.XPATH,
                                        f'//*[@id="popular_graph"]/div/div[2]/div[2]/table/tbody/tr[{i + 1}]/td[3]',
                                    )
                                )
                            )
                            top5_menu_elements.append(element.text)
                        except:
                            top5_menu_elements.append(None)
                except:
                    top5_menu_elements = [None] * 5

                data = {
                    "location": {
                        "city": city_text,
                        "district": district_text,
                        "sub_district": sub_district_text,
                    },
                    "category": {
                        "main": main_category_text,
                        "sub": sub_category_text,
                        "detail": detail_category_text,
                    },
                    "density": {
                        "national": all_detail_category_count,
                        "city": city_detail_category_count,
                        "district": district_detail_category_count,
                        "sub_district": sub_district_detail_category_count,
                    },
                    "market_size": sub_district_market_size,
                    "average_sales": sub_district_total_size,
                    "average_payment_cost": sub_district_avg_payment_cost,
                    "usage_count": sub_district_usage_count,
                    "average_profit": {
                        "sales": sub_district_total_sales,
                        "operating_cost": sub_district_operating_cost,
                        "food": sub_district_food_cost,
                        "employee": sub_district_employee_cost,
                        "rental": sub_district_rental_cost,
                        "tax": sub_district_tax_cost,
                        "family_employee": sub_district_family_employee_cost,
                        "ceo": sub_district_ceo_cost,
                        "etc": sub_district_etc_cost,
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
                        "total_male_percent": total_male_percent,
                        "total_female_percent": total_female_percent,
                        "most_visitor_age": most_visitor_age,
                    },
                    "top5_menus": {
                        "top5_menu_1": (
                            top5_menu_elements[0]
                            if len(top5_menu_elements) > 0
                            else None
                        ),
                        "top5_menu_2": (
                            top5_menu_elements[1]
                            if len(top5_menu_elements) > 1
                            else None
                        ),
                        "top5_menu_3": (
                            top5_menu_elements[2]
                            if len(top5_menu_elements) > 2
                            else None
                        ),
                        "top5_menu_4": (
                            top5_menu_elements[3]
                            if len(top5_menu_elements) > 3
                            else None
                        ),
                        "top5_menu_5": (
                            top5_menu_elements[4]
                            if len(top5_menu_elements) > 4
                            else None
                        ),
                    },
                }

                insert_commercial_district(data)

                end_time = time.time()

                print(
                    f"Execution finished at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}"
                )

                print(f"Total execution time: {end_time - start_time} seconds")

            else:
                print(
                    f"NO DATA : {city_text}, {district_text}, {sub_district_text}, {main_category_text}, {sub_category_text} : index {detail_category_idx}."
                )
                continue

    except Exception as e:
        print(f"Exception occurred: {e}.")
        return None
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def execute_parallel_tasks():
    start_time = time.time()
    print(
        f"Execution started at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}"
    )

    with ThreadPoolExecutor(max_workers=12) as executor:

        futures = [
            # 0 ~ 1 함
            executor.submit(get_district_count, 0, 2),
            executor.submit(get_district_count, 2, 4),
            executor.submit(get_district_count, 4, 6),
            executor.submit(get_district_count, 6, 8),
            executor.submit(get_district_count, 8, 10),
            executor.submit(get_district_count, 10, 12),
            executor.submit(get_district_count, 12, 14),
            executor.submit(get_district_count, 14, 15),
            executor.submit(get_district_count, 15, 16),
            executor.submit(get_district_count, 16, 17),
            # 16번까지 함
        ]

        for future in futures:
            future.result()

    end_time = time.time()
    print(
        f"Execution finished at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}"
    )
    print(f"Total execution time: {end_time - start_time} seconds")


if __name__ == "__main__":
    execute_parallel_tasks()
    print(f"상권분석 END")

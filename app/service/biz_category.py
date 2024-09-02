import re
import time
import os
from typing import List

from fastapi import HTTPException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    NoAlertPresentException,
)
from selenium.webdriver.common.alert import Alert
from tqdm import tqdm

from app.crud.biz_detail_category import get_or_create_biz_detail_category_id
from app.crud.biz_main_category import get_or_create_biz_main_category_id
from app.crud.biz_sub_category import get_or_create_biz_sub_category_id
from app.crud.city import get_or_create_city_id
from app.crud.commercial_district import (
    insert_commercial_district,
    select_all_commercial_district_by_sub_district_id,
)
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    NoAlertPresentException,
    TimeoutException,
)
from app.crud.district import get_district_id, get_or_create_district_id
from app.crud.sub_district import get_or_create_sub_district_id, get_sub_district_id_by
from app.schemas.commercial_district import (
    CommercialDistrictInsert,
    CommercialDistrictOutput,
)

BIZ_MAP_URL = "https://m.nicebizmap.co.kr/analysis/analysisFree"


def setup_driver():
    driver_path = os.path.join(
        os.path.dirname(__file__), "../", "drivers", "chromedriver.exe"
    )

    options = Options()
    options.add_argument("--start-fullscreen")
    options.add_argument("--no-sandbox")  # 샌드박스 비활성화
    options.add_argument("--disable-dev-shm-usage")  # 리소스 절약

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def click_element(wait, by, value):
    try:
        element = wait.until(EC.element_to_be_clickable((by, value)))
        text = element.text
        element.click()
        time.sleep(0.7)
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


def convert_to_int_float(value):
    if isinstance(value, str):
        value = re.sub(r"[^\d.]+", "", value)
        return float(value) if "." in value else int(value)
    return value


def clean_data(int_str):
    def clean_value(value):
        if isinstance(value, str):
            value = re.sub(r"[^\d.]+", "", value)
            return float(value) if value else None
        return value

    return {key: clean_value(value) for key, value in int_str.items()}


def handle_unexpected_alert(driver):
    try:
        alert = Alert(driver)
        alert_text = alert.text
        print(f"Alert detected: {alert_text}")
        alert.accept()
        return True
    except NoAlertPresentException:
        return False


def get_main_category(city_idx, district_idx, sub_district_count):
    driver = setup_driver()
    try:
        # for sub_district_idx in tqdm(range(sub_district_count), "읍/면/동 Progress"):
        #     try:
        #         # print(f"idx: {district_idx}")
        #         driver.get(BIZ_MAP_URL)
        #         wait = WebDriverWait(driver, 60)
        #         driver.implicitly_wait(10)

        #         # time.sleep(3)

        #         # click_element(wait, By.XPATH, '//*[@id="gnb1"]/li[1]/a')

        #         # 분석 지역
        #         click_element(
        #             wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
        #         )

        #         time.sleep(3)

        #         city_text = click_element(
        #             wait,
        #             By.XPATH,
        #             f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
        #         )

        #         time.sleep(3)

        #         district_text = click_element(
        #             wait,
        #             By.XPATH,
        #             f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
        #         )

        #         time.sleep(3)

        #         sub_district_text = click_element(
        #             wait,
        #             By.XPATH,
        #             f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
        #         )

        #         time.sleep(3)

        #         main_category_ul_1 = wait.until(
        #             EC.presence_of_element_located(
        #                 (
        #                     By.XPATH,
        #                     '//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[1]',
        #                 )
        #             )
        #         )

        #         main_category_ul_1_li = main_category_ul_1.find_elements(
        #             By.TAG_NAME, "li"
        #         )
        #         # print(f"대분류1 갯수 : {len(main_category_ul_1_li)}")

        #         m_c_ul = 1

        #         get_sub_category(
        #             city_idx,
        #             district_idx,
        #             sub_district_idx,
        #             len(main_category_ul_1_li),
        #             m_c_ul,
        #         )
        #     except UnexpectedAlertPresentException:
        #         handle_unexpected_alert(wait._driver)
        #     except Exception as e:
        #         print(
        #             f"Exception occurred, 대분류1 반복 err, district_idx:  {district_idx}: {str(e)}"
        #         )
        #         continue
        #     finally:
        #         driver.quit()
        #         driver = setup_driver()

        for sub_district_idx in tqdm(range(sub_district_count), "읍/면/동 Progress"):
            try:
                print(f"idx: {district_idx}")
                driver.get(BIZ_MAP_URL)
                wait = WebDriverWait(driver, 60)
                driver.implicitly_wait(10)

                # time.sleep(3)

                # click_element(wait, By.XPATH, '//*[@id="gnb1"]/li[1]/a')

                # 분석 지역
                click_element(
                    wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
                )

                time.sleep(3)

                city_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
                )

                time.sleep(3)

                district_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
                )

                time.sleep(3)

                sub_district_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
                )

                main_category_ul_2 = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[3]',
                        )
                    )
                )

                main_category_ul_2_li = main_category_ul_2.find_elements(
                    By.TAG_NAME, "li"
                )
                # print(f"대분류2 갯수 : {len(main_category_ul_2_li)}")

                m_c_ul = 3

                get_sub_category(
                    city_idx,
                    district_idx,
                    sub_district_idx,
                    len(main_category_ul_2_li),
                    m_c_ul,
                )
            except UnexpectedAlertPresentException:
                handle_unexpected_alert(wait._driver)
            except Exception as e:
                print(
                    f"Exception occurred: 대분류2 반복 오류, district_idx: {district_idx}: {str(e)}"
                )
                continue
            finally:
                driver.quit()
                driver = setup_driver()
    except Exception as e:
        print(
            f"Exception occurred get_main_category(), sub_district: {sub_district_idx} {e}."
        )
        return None
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def get_sub_category(
    city_idx, district_idx, sub_district_idx, main_category_count, m_c_ul
):
    driver = setup_driver()
    try:
        for main_category_idx in range(main_category_count):
            try:
                # print(f"idx: {district_idx}")
                driver.get(BIZ_MAP_URL)
                wait = WebDriverWait(driver, 60)
                driver.implicitly_wait(10)

                # time.sleep(3)

                # click_element(wait, By.XPATH, '//*[@id="gnb1"]/li[1]/a')

                # 분석 지역
                click_element(
                    wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
                )

                time.sleep(3)

                city_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
                )

                time.sleep(3)

                district_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
                )

                time.sleep(3)

                sub_district_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
                )

                time.sleep(3)

                main_category_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul}]/li[{main_category_idx + 1}]/button',
                )

                sub_category_li = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#basicReport ul.cate2 > ul")
                    )
                )
                sub_category_ul_li_button = sub_category_li.find_elements(
                    By.CSS_SELECTOR,
                    "#basicReport  ul.cate2 > ul > li > button",
                )
                # print(f"중분류 갯수 : {len(sub_category_ul_li_button)}")

                get_detail_category(
                    city_idx,
                    district_idx,
                    sub_district_idx,
                    main_category_idx,
                    len(sub_category_ul_li_button),
                    m_c_ul,
                )
            except UnexpectedAlertPresentException:
                handle_unexpected_alert(wait._driver)
            except Exception as e:
                print(
                    f"Error processing, main_category_idx: {main_category_idx}: {str(e)}"
                )
                continue
            finally:
                driver.quit()
                driver = setup_driver()

    except Exception as e:
        print(
            f"Exception occurred, get_sub_category(), main_category_idx: {main_category_idx} {e}."
        )
        return None
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def get_detail_category(
    city_idx,
    district_idx,
    sub_district_idx,
    main_category_idx,
    sub_category_count,
    m_c_ul,
):
    driver = setup_driver()
    try:
        for sub_category_idx in range(0, sub_category_count * 2, 2):
            try:
                driver.get(BIZ_MAP_URL)
                wait = WebDriverWait(driver, 60)
                driver.implicitly_wait(10)

                # time.sleep(3)

                # click_element(wait, By.XPATH, '//*[@id="gnb1"]/li[1]/a')

                # 분석 지역
                click_element(
                    wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
                )

                time.sleep(3)

                city_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
                )

                time.sleep(3)

                district_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
                )

                time.sleep(3)

                sub_district_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
                )

                time.sleep(3)

                main_category_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul}]/li[{main_category_idx + 1}]/button',
                )

                time.sleep(3)

                sub_category_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul + 1}]/ul/li[{sub_category_idx + 1}]/button',
                )
                # print(f"중분류 : {sub_category_text}")
                detail_category_ul = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "#basicReport ul.cate3")
                    )
                )
                detail_category_ul_li_button = detail_category_ul.find_elements(
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul + 1}]/ul/li[{sub_category_idx + 2}]/ul/li',
                )
                # print(f"소분류 갯수 : {len(detail_category_ul_li_button)}")

                search_commercial_district(
                    city_idx,
                    district_idx,
                    sub_district_idx,
                    main_category_idx,
                    sub_category_idx,
                    len(detail_category_ul_li_button),
                    m_c_ul,
                )
            except UnexpectedAlertPresentException:
                handle_unexpected_alert(wait._driver)
            except Exception as e:
                print(f"Error processing sub_category_idx {sub_category_idx}: {str(e)}")
                continue
            finally:
                driver.quit()
                driver = setup_driver()
    except Exception as e:
        print(
            f"Exception occurred get_detail_category(), sub_category_idx: {sub_category_idx} {e}."
        )
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
            try:

                start_time = time.time()
                print(
                    f"Execution started at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}"
                )

                driver.get(BIZ_MAP_URL)
                wait = WebDriverWait(driver, 40)
                driver.implicitly_wait(10)

                # time.sleep(3)

                # click_element(wait, By.XPATH, '//*[@id="gnb1"]/li[1]/a')

                # 분석 지역
                click_element(
                    wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
                )

                time.sleep(3)

                city_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
                )

                time.sleep(3)

                district_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
                )

                time.sleep(3)

                sub_district_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
                )

                time.sleep(3)

                main_category_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul}]/li[{main_category_idx + 1}]',
                )

                time.sleep(3)

                sub_category_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul + 1}]/ul/li[{sub_category_idx + 1}]',
                )

                time.sleep(3)

                detail_category_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[{m_c_ul + 1}]/ul/li[{sub_category_idx + 2}]/ul/li[{detail_category_idx + 1}]',
                )

                time.sleep(3)

                try:
                    city_id = get_or_create_city_id(city_text)
                    if city_id:
                        district_id = get_or_create_district_id(city_id, district_text)
                        if city_id & district_id:
                            sub_district_id = get_or_create_sub_district_id(
                                city_id, district_id, sub_district_text
                            )
                except Exception as e:
                    print(f"시 구 동 조회 오류 : {e}")

                ###########################

                try:
                    main_category_id = get_or_create_biz_main_category_id(
                        main_category_text
                    )
                    if main_category_id is None:
                        print("Failed to get or create main category ID")
                        continue

                    sub_category_id = get_or_create_biz_sub_category_id(
                        main_category_id, sub_category_text
                    )
                    if sub_category_id is None:
                        print("Failed to get or create sub-category ID")
                        continue

                    if detail_category_text:
                        detail_category_text = detail_category_text.replace(
                            "(확장 분석)", ""
                        ).strip()

                    detail_category_id = get_or_create_biz_detail_category_id(
                        sub_category_id, detail_category_text
                    )
                    if detail_category_id is None:
                        print("Failed to get or create detail category ID")
                        continue

                except Exception as e:
                    print(f"카테고리 조회 오류 : {e}")
                    continue

            except UnexpectedAlertPresentException:
                handle_unexpected_alert(wait._driver)
            except Exception as e:
                print(
                    f"Error processing {city_text}, {district_text}, {sub_district_text}, {main_category_text}, {sub_category_text} : index {detail_category_idx}. {str(e)}"
                )
                continue
            finally:
                driver.quit()
                driver = setup_driver()
    except Exception as e:
        print(
            f"Exception occurred search_commercial_district(), detail_category_idx: {detail_category_idx} {e}."
        )
        return None
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


if __name__ == "__main__":
    get_main_category(0, 0, 1)

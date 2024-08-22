import os
import time

from typing import List

from httpcore import TimeoutException
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

from app.crud.region import get_or_create_region_id
from app.crud.rising_business import insert_rising_business
from app.schemas.rising_business import RisingBusiness

from concurrent.futures import ThreadPoolExecutor

commercial_district_url = os.getenv("RISING_TOP5_URL")


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


commercial_district_url = "https://m.nicebizmap.co.kr/analysis/analysisFree"


def click_element(wait, by, value):
    try:
        element = wait.until(EC.element_to_be_clickable((by, value)))
        text = element.text
        element.click()
        time.sleep(0.7)
        return text
    except TimeoutException:
        print(
            f"TimeoutException occurred for element located by {by} with value {value}. Skipping to next element."
        )
        return None


def read_element(wait, by, value):
    try:
        element = wait.until(EC.presence_of_element_located((by, value)))
        text = element.text
        time.sleep(0.3)
        return text
    except TimeoutException:
        print(
            f"TimeoutException occurred for element located by {by} with value {value}. Skipping to next element."
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


def get_city_count():
    driver = setup_driver()
    try:
        driver.get(commercial_district_url)
        wait = WebDriverWait(driver, 10)
        click_element(wait, By.XPATH, "/html/body/div[5]/div[2]/ul/li[5]/a")
        click_element(wait, By.XPATH, '//*[@id="pc_sheet04"]/div/div[2]/div[2]/ul/li/a')

        city_ul = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul')
            )
        )
        city_ul_li = city_ul.find_elements(By.TAG_NAME, "li")
        print(f"시 갯수: {len(city_ul_li)}")

        get_district_count(len(city_ul_li))

    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def get_district_count(city_count):
    driver = setup_driver()
    try:
        for city_idx in range(city_count):
            try:
                print(f"idx: {city_idx}")
                driver.get(commercial_district_url)
                wait = WebDriverWait(driver, 10)
                click_element(wait, By.XPATH, "/html/body/div[5]/div[2]/ul/li[5]/a")
                click_element(
                    wait, By.XPATH, '//*[@id="pc_sheet04"]/div/div[2]/div[2]/ul/li/a'
                )
                city_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
                )

                district_ul = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul',
                        )
                    )
                )
                district_ul_li = district_ul.find_elements(By.TAG_NAME, "li")
                print(f"구 갯수: {len(district_ul_li)}")

                get_sub_district_count(city_idx, len(district_ul_li))

            except Exception as e:
                print(f"Error processing city index {city_idx}: {str(e)}")
                continue
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def get_sub_district_count(city_idx: int, district_count: int):
    driver = setup_driver()
    try:
        for district_idx in range(district_count):
            try:
                print(f"idx: {district_idx}")
                driver.get(commercial_district_url)
                wait = WebDriverWait(driver, 10)
                click_element(wait, By.XPATH, "/html/body/div[5]/div[2]/ul/li[5]/a")
                click_element(
                    wait, By.XPATH, '//*[@id="pc_sheet04"]/div/div[2]/div[2]/ul/li/a'
                )
                city_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
                )

                district_ul = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul',
                        )
                    )
                )
                district_ul_li = district_ul.find_elements(By.TAG_NAME, "li")
                print(f"구 갯수: {len(district_ul_li)}")

                district_text = click_element(
                    wait,
                    By.XPATH,
                    f'//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
                )

                sub_district_ul = wait.until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul',
                        )
                    )
                )
                sub_district_ul_li = sub_district_ul.find_elements(By.TAG_NAME, "li")
                print(f"동 갯수: {len(sub_district_ul_li)}")

                print(f"시/도: {city_text}, 시/군/구: {district_text}")

                search_rising_businesses_top5(
                    city_idx, district_idx, len(sub_district_ul_li)
                )

            except Exception as e:
                print(f"Error processing district index {district_idx}: {str(e)}")
                continue

    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def search_rising_businesses_top5(
    city_idx: int, district_idx: int, sub_district_count: int
):
    driver = setup_driver()
    try:
        data_list: List[RisingBusiness] = []

        for sub_district_idx in range(sub_district_count):
            start_time = time.time()
            driver.get(commercial_district_url)
            wait = WebDriverWait(driver, 10)
            click_element(wait, By.XPATH, "/html/body/div[5]/div[2]/ul/li[5]/a")
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet04"]/div/div[2]/div[2]/ul/li/a'
            )

            city_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
            )

            district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
            )

            sub_district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
            )

            try:
                region_id = get_or_create_region_id(
                    city_text, district_text, sub_district_text
                )

                print(f"지역ID : {region_id}")

                rising_ul = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="cardBoxTop5"]'))
                )
                rising_ul_li = rising_ul.find_elements(
                    By.CSS_SELECTOR, "#cardBoxTop5 > li"
                )

                for i, li in enumerate(rising_ul_li):
                    li_text = li.text.strip().split("\n")
                    if len(li_text) >= 2:
                        business_name = li_text[1]
                        growth_rate = convert_to_float(li_text[2])

                        data = RisingBusiness(
                            REGION_ID=region_id,
                            BUSINESS_NAME=business_name,
                            GROWTH_RATE=growth_rate,
                            SUB_DISTRICT_RANK=i + 1,
                        )

                        data_list.append(data)
                        print(data)

            except UnexpectedAlertPresentException:
                handle_unexpected_alert(wait._driver)
                data_list.append(
                    RisingBusiness(
                        REGION_ID=region_id,
                        BUSINESS_NAME=None,
                        GROWTH_RATE=None,
                        SUB_DISTRICT_RANK=None,
                    )
                )
            except Exception as e:
                print(f"Loading Error : {str(e)}")
                continue

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Time taken: {elapsed_time} seconds")
            print(
                f"시/도: {city_text}, 시/군/구: {district_text}, 읍/면/동: {sub_district_text}"
            )

        print(data_list)
        insert_rising_business(data_list)
    except Exception as e:
        print(f"Failed to fetch data from {commercial_district_url}: {str(e)}")
    finally:
        driver.quit()


def execute_parallel_tasks():
    start_time = time.time()
    print(
        f"Execution started at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}"
    )

    with ThreadPoolExecutor(max_workers=12) as executor:

        futures = [
            # 0 ~ 1 함
            executor.submit(get_city_count, 0, 2),
            executor.submit(get_city_count, 2, 4),
            executor.submit(get_city_count, 4, 6),
            executor.submit(get_city_count, 6, 8),
            executor.submit(get_city_count, 8, 10),
            executor.submit(get_city_count, 10, 12),
            executor.submit(get_city_count, 12, 14),
            executor.submit(get_city_count, 14, 15),
            executor.submit(get_city_count, 15, 16),
            executor.submit(get_city_count, 16, 17),
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

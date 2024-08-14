import os
import time

from typing import List

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

from app.schemas.rising_business import RisingBusinessCreate, Location, BusinessDetail
import app.crud.rising_business as rb

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


def click_element(wait, by, value):
    try:
        element = wait.until(EC.element_to_be_clickable((by, value)))
        text = element.text
        element.click()
        time.sleep(0.5)
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
        time.sleep(0.3)
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


def get_city_count(start_idx: int, end_idx: int):
    driver = setup_driver()
    print(f"Processing range {start_idx} to {end_idx}")
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

        for city_idx in range(start_idx, end_idx):
            get_district_count(city_idx)

    except Exception as e:
        print(f"Failed to fetch data from {commercial_district_url}: {str(e)}")
    finally:
        driver.quit()


def get_district_count(city_idx):
    driver = setup_driver()
    try:
        driver.get(commercial_district_url)
        wait = WebDriverWait(driver, 10)
        click_element(wait, By.XPATH, "/html/body/div[5]/div[2]/ul/li[5]/a")
        click_element(wait, By.XPATH, '//*[@id="pc_sheet04"]/div/div[2]/div[2]/ul/li/a')
        click_element(
            wait,
            By.XPATH,
            f'//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
        )

        district_ul = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul')
            )
        )
        district_ul_li = district_ul.find_elements(By.TAG_NAME, "li")
        print(f"구 갯수: {len(district_ul_li)}")

        get_sub_district_count(city_idx, len(district_ul_li))

    except Exception as e:
        print(f"Failed to fetch data from {commercial_district_url}: {str(e)}")
    finally:
        driver.quit()


def get_sub_district_count(city_idx, district_count):
    driver = setup_driver()
    try:
        for district_idx in range(district_count):
            # for district_idx in range(1):
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
                    (By.XPATH, '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul')
                )
            )
            district_ul_li = district_ul.find_elements(By.TAG_NAME, "li")

            district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
            )

            sub_district_ul = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul')
                )
            )
            sub_district_ul_li = sub_district_ul.find_elements(By.TAG_NAME, "li")
            print(f"동 갯수: {len(sub_district_ul_li)}")

            search_rising_businesses_top5(
                city_idx, district_idx, len(sub_district_ul_li)
            )

    except Exception as e:
        print(f"Failed to fetch data from {commercial_district_url}: {str(e)}")
    finally:
        driver.quit()


def search_rising_businesses_top5(city_idx, district_idx, sub_district_count):
    driver = setup_driver()
    try:
        data_list: List[RisingBusinessCreate] = []
        for sub_district_idx in range(sub_district_count):
            # for sub_district_idx in range(2):
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
                rising_ul = wait.until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="cardBoxTop5"]'))
                )
                rising_ul_li = rising_ul.find_elements(
                    By.CSS_SELECTOR, "#cardBoxTop5 > li"
                )

                rising_top5 = {}
                for i, li in enumerate(rising_ul_li):
                    li_text = li.text.strip().split("\n")
                    if len(li_text) >= 2:
                        business_name = li_text[1]
                        growth_rate = (
                            convert_to_float(li_text[2]) if len(li_text) == 3 else None
                        )
                        rising_top5[f"business_{i + 1}"] = BusinessDetail(
                            business_name=business_name,
                            growth_rate=growth_rate,
                        )

            except UnexpectedAlertPresentException:
                handle_unexpected_alert(wait._driver)
                rising_top5 = {}
            except Exception as e:
                print(f"Error while fetching top 5 businesses: {str(e)}")
                rising_top5 = {}

            data = RisingBusinessCreate(
                location=Location(
                    city=city_text,
                    district=district_text,
                    sub_district=sub_district_text,
                ),
                rising_top5=rising_top5,
            )

            data_list.append(data)

            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Time taken : {elapsed_time}")
            print(
                f"시/도: {city_text}, 시/군/구: {district_text}, 읍/면/동: {sub_district_text}"
            )
        print(data_list)
        rb.insert_rising_business(data_list)

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

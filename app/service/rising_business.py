from pydantic import BaseModel
from typing import Dict, List, Optional
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from app.schemas.rising_business import RisingBusinessCreate, Location, BusinessDetail
import app.crud.rising_business as rb


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
    element = wait.until(EC.element_to_be_clickable((by, value)))
    text = element.text
    element.click()
    time.sleep(0.7)
    return text


def read_element(wait, by, value):
    element = wait.until(EC.presence_of_element_located((by, value)))
    text = element.text
    time.sleep(0.3)
    return text


def convert_to_float(percent_str):
    try:
        clean_str = percent_str.replace("%", "").replace(",", "").strip()
        return float(clean_str)
    except ValueError:
        return 0.0


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
        # for city_idx in range(city_count):
        for city_idx in range(1):
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
                    (By.XPATH, '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul')
                )
            )
            district_ul_li = district_ul.find_elements(By.TAG_NAME, "li")
            print(f"구 갯수: {len(district_ul_li)}")

            get_sub_district_count(city_idx, len(district_ul_li))

    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def get_sub_district_count(city_idx, district_count):
    driver = setup_driver()
    try:
        # for district_idx in range(district_count):
        for district_idx in range(1):
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
                    (By.XPATH, '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul')
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
                    (By.XPATH, '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul')
                )
            )
            sub_district_ul_li = sub_district_ul.find_elements(By.TAG_NAME, "li")
            print(f"동 갯수: {len(sub_district_ul_li)}")

            print(f"시/도 : {city_text}, 시/군/구 : {district_text}")

            search_rising_businesses_top5(
                city_idx, district_idx, len(sub_district_ul_li)
            )

    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


def search_rising_businesses_top5(city_idx, district_idx, sub_district_count):
    driver = setup_driver()
    try:
        data_list: List[RisingBusinessCreate] = []

        # for sub_district_idx in range(sub_district_count):
        for sub_district_idx in range(6):
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

            rising_ul = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="cardBoxTop5"]'))
            )
            rising_ul_li = rising_ul.find_elements(By.CSS_SELECTOR, "#cardBoxTop5 > li")

            rising_top5 = {}
            for i, li in enumerate(rising_ul_li):
                li_text = li.text.strip().split("\n")
                if len(li_text) >= 2:
                    business_name = li_text[1]  # 업종명
                    growth_rate = (
                        convert_to_float(li_text[2]) if len(li_text) == 3 else None
                    )  # 증가율 변환
                    rising_top5[f"business_{i + 1}"] = BusinessDetail(
                        business_name=business_name,
                        growth_rate=growth_rate,
                    )

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

        rb.insert_rising_business(data_list)

    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


if __name__ == "__main__":
    get_city_count()
    print("성공!")

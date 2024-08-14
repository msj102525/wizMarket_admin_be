import time
import os

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


def get_city_count():
    driver = setup_driver()
    try:
        driver.get(commercial_district_url)
        wait = WebDriverWait(driver, 10)
        driver.implicitly_wait(10)

        # 분석 지역
        click_element(
            wait, By.XPATH, '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
        )

        city_ul = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul')
            )
        )
        city_ul_li = city_ul.find_elements(By.TAG_NAME, "li")
        print(f"시/도 갯수: {len(city_ul_li)}")

        get_district_count(len(city_ul_li))
    except Exception as e:
        print(f"Exception occurred: {e}.")
        return None
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
            print(f"idx: {city_idx}")

            driver.get(commercial_district_url)
            wait = WebDriverWait(driver, 10)

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


def get_sub_district_count(city_idx, district_count):
    driver = setup_driver()
    try:
        for district_idx in range(district_count):
            print(f"idx: {district_idx}")
            driver.get(commercial_district_url)
            wait = WebDriverWait(driver, 10)

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


def get_main_category(city_idx, district_idx, sub_district_count):
    driver = setup_driver()
    try:
        for sub_district_idx in range(sub_district_count):
            print(f"idx: {district_idx}")
            driver.get(commercial_district_url)
            wait = WebDriverWait(driver, 10)

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
                    (By.XPATH, "/html/body/div[10]/div[5]/div[3]/div[2]/div/ul[1]")
                )
            )

            main_category_ul_1_li = main_category_ul_1.find_elements(By.TAG_NAME, "li")
            print(f"대분류1 갯수 : {main_category_ul_1_li}")

            # main_category_ul_2 = wait.until(
            #     EC.presence_of_element_located(
            #         By.XPATH, "//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[3]"
            #     )
            # )

            # main_category_ul_2_li = main_category_ul_2.find_elements(By.TAG_NAME, "li")
            # print(f"대분류2 갯수 : {main_category_ul_2_li}")

            # get_main_category(city_idx, district_idx, len(sub_district_ul_li))

    except Exception as e:
        print(f"Exception occurred: {e}.")
        return None
    finally:
        try:
            if driver:
                driver.quit()
        except Exception as quit_error:
            print(f"Error closing driver: {str(quit_error)}")


if __name__ == "__main__":
    get_city_count()
    print("성공")

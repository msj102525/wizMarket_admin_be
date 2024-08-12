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
    return text


def convert_to_float(percent_str):
    return float(percent_str.replace("%", "").strip())


def get_city_count():
    driver = setup_driver()
    try:

        driver.get(commercial_district_url)  # URL 접속
        driver.implicitly_wait(10)

        wait = WebDriverWait(driver, 10)  # 10초 대기

        # 뜨는 업종
        click_element(wait, By.XPATH, "/html/body/div[5]/div[2]/ul/li[5]/a")

        # 분석 지역을해주세요
        click_element(wait, By.XPATH, '//*[@id="pc_sheet04"]/div/div[2]/div[2]/ul/li/a')

        city_ul = wait.until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul')
            )
        )
        city_ul_li = city_ul.find_elements(By.TAG_NAME, "li")

        print(f"시 갯수: {len(city_ul_li)}")

        driver.quit()
        get_district_count(len(city_ul_li))

    except Exception as e:
        raise Exception(
            f"Failed to fetch data from {commercial_district_url}: {str(e)}"
        )
    finally:
        driver.quit()


def get_district_count(city_count):
    try:
        for city_idx in range(1):
            driver = setup_driver()
            print(f"idx: {city_idx}")
            driver.get(commercial_district_url)  # URL 접속
            driver.implicitly_wait(10)

            wait = WebDriverWait(driver, 10)  # 10초 대기

            # 뜨는 업종
            click_element(wait, By.XPATH, "/html/body/div[5]/div[2]/ul/li[5]/a")

            # 분석 지역을해주세요
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet04"]/div/div[2]/div[2]/ul/li/a'
            )
            # 시/도
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

            driver.quit()

    except Exception as e:
        raise Exception(
            f"Failed to fetch data from {commercial_district_url}: {str(e)}"
        )
    finally:
        driver.quit()


def get_sub_district_count(city_idx, district_count):
    try:
        # for district_idx in range(district_count):
        for district_idx in range(2):
            driver = setup_driver()
            print(f"idx: {district_idx}")
            driver.get(commercial_district_url)  # URL 접속
            driver.implicitly_wait(10)

            wait = WebDriverWait(driver, 10)  # 10초 대기

            # 뜨는 업종
            click_element(wait, By.XPATH, "/html/body/div[5]/div[2]/ul/li[5]/a")

            # 지역 선택
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet04"]/div/div[2]/div[2]/ul/li/a'
            )
            # 시/도
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
                    (
                        By.XPATH,
                        '//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul',
                    )
                )
            )
            sub_district_ul_li = sub_district_ul.find_elements(By.TAG_NAME, "li")
            # sub_district_ul_li = [1, 2, 3]
            print(f"동 갯수: {len(sub_district_ul_li)}")

            print(f"시/도 : {city_text}, 시/군/구 : {district_text}")

            search_rising_businesses_top5(
                city_idx, district_idx, len(sub_district_ul_li)
            )

            driver.quit()

    except Exception as e:
        raise Exception(
            f"Failed to fetch data from {commercial_district_url}: {str(e)}"
        )
    finally:
        driver.quit()


def search_rising_businesses_top5(city_idx, district_idx, sub_district_count):
    print(city_idx, district_idx, sub_district_count)
    try:
        # for sub_district_idx in range(sub_district_count):
        for sub_district_idx in range(2):

            driver = setup_driver()
            start_time = time.time()  # 시작 시간 기록

            driver.get(commercial_district_url)  # URL 접속
            driver.implicitly_wait(10)

            wait = WebDriverWait(driver, 10)  # 10초 대기

            # 뜨는 업종
            click_element(wait, By.XPATH, "/html/body/div[5]/div[2]/ul/li[5]/a")

            # 지역 선택
            click_element(
                wait, By.XPATH, '//*[@id="pc_sheet04"]/div/div[2]/div[2]/ul/li/a'
            )

            # 시/도
            city_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul/li[{city_idx + 1}]/a',
            )

            # 시/군/구
            district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul/li[{district_idx + 1}]/a',
            )

            # 읍/면/동
            sub_district_text = click_element(
                wait,
                By.XPATH,
                f'//*[@id="rising"]/div[2]/div[2]/div[2]/div/div[2]/ul/li[{sub_district_idx + 1}]/a',
            )

            rising_ul = wait.until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="cardBoxTop5"]'))
            )

            rising_ul_li = rising_ul.find_elements(By.CSS_SELECTOR, "#cardBoxTop5 > li")

            data = {
                "location": {
                    "city": city_text,
                    "district": district_text,
                    "sub_district": sub_district_text,
                },
                "rising_top5": {},
            }

            # li 태그 갯수만큼 rising_top5에 데이터 추가
            for i, li in enumerate(rising_ul_li):
                li_text = li.text.strip().split("\n")
                if len(li_text) >= 2:
                    business_name = li_text[1]  # 업종명
                    growth_rate = li_text[2] if len(li_text) == 3 else ""  # 증가율
                    data["rising_top5"][f"business_{i + 1}"] = {
                        "business_name": business_name,
                        "growth_rate": growth_rate,
                    }

            print(data)
            data_list.append(data)  # data_list에 추가

            end_time = time.time()
            elapsed_time = end_time - start_time

            print(f"Time taken : {elapsed_time}")

            print(
                f"시/도: {city_text}, 시/군/구: {district_text}, 읍/면/동: {sub_district_text}"
            )

            driver.quit()

    except Exception as e:
        raise Exception(
            f"Failed to fetch data from {commercial_district_url}: {str(e)}"
        )
    finally:
        driver.quit()


if __name__ == "__main__":
    get_city_count()
    print(data_list)

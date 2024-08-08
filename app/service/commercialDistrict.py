import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os


def setup_driver():
    driver_path = os.path.join(
        os.path.dirname(__file__), "../", "drivers", "chromedriver.exe"
    )

    options = Options()
    options.add_argument("--start-fullscreen")  # 전체 화면 모드로 열기
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


# driver = setup_driver()


def click_element(wait, by, value):
    element = wait.until(EC.visibility_of_element_located((by, value)))
    text = element.text
    element.click()
    time.sleep(0.1)
    # driver.implicitly_wait(5) # 안전장치
    return text


def read_element(wait, by, value):
    element = wait.until(EC.presence_of_element_located((by, value)))
    text = element.text
    time.sleep(0.1)
    # print(text)
    return text


def search_commercial_district():
    driver = setup_driver()
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
            '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[1]/a',
        )

        # 읍/면/동
        sub_district_text = click_element(
            wait,
            By.XPATH,
            '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[1]/a',
        )

        # 대분류
        main_category = click_element(
            wait,
            By.XPATH,
            '//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[1]/li[1]/button',
        )

        # 중분류
        sub_category = click_element(
            wait,
            By.XPATH,
            '//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[2]/ul/li[1]/button',
        )

        # 소분류
        detail_category = click_element(
            wait,
            By.XPATH,
            '//*[@id="basicReport"]/div[5]/div[3]/div[2]/div/ul[2]/ul/li[2]/ul/li[1]/button',
        )

        detail_category = detail_category.replace("(확장 분석)", "").strip()

        # 상권분석 보기
        click_element(wait, By.XPATH, '//*[@id="pcBasicReport"]')

        # 표 전제보기
        click_element(
            wait,
            By.XPATH,
            '//*[@id="report1"]/div/div[4]/div[1]/div/div/div/div[1]/div[1]/label',
        )

        # 분석 텍스트 보기 없애기
        click_element(
            wait,
            By.XPATH,
            '//*[@id="report1"]/div/div[4]/div[1]/div/div/div/div[1]/div[2]/label',
        )

        # 밀집도 클릭
        click_element(
            wait,
            By.XPATH,
            '//*[@id="report1"]/div/div[3]/div/ul/li[2]/a',
        )

        # 밀집도 데이터 표로 보기
        click_element(
            wait,
            By.XPATH,
            '//*[@id="s2"]/div[2]/div[2]/div/div[2]/div/button',
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

        # 시장규모 데이터 표로 보기
        click_element(
            wait,
            By.XPATH,
            '//*[@id="s3"]/div[2]/div[2]/div[2]/div/button',
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

        # 매출규모 데이터 표로 보기
        click_element(
            wait,
            By.XPATH,
            '//*[@id="s4"]/div[2]/div[3]/div[2]/div/button',
        )

        # 해당지역 업종 점포당 매출규모(원)
        sub_district_total_size = read_element(
            wait,
            By.XPATH,
            '//*[@id="s4"]/div[2]/div[3]/div[2]/table/tbody/tr/td[7]',
        )
        

        time.sleep(1.5)

        end_time = time.time()
        elapsed_time = end_time - start_time

        data = {
            "title": title,
            "elapsed_time": elapsed_time,
            "city_text": city_text,
            "district_text": district_text,
            "sub_district_text": sub_district_text,
            "main_category": main_category,
            "sub_category": sub_category,
            "detail_category": detail_category,
            "all_detail_category_count": all_detail_category_count,
            "city_detail_category_count": city_detail_category_count,
            "district_detail_category_count": district_detail_category_count,
            "sub_district_detail_category_count": sub_district_detail_category_count,
            "sub_district_market_size": sub_district_market_size,
            "sub_district_total_size": sub_district_total_size,
        }

        return data
    except Exception as e:
        raise Exception(
            f"Failed to fetch data from {commercial_district_url}: {str(e)}"
        )
    finally:
        driver.quit()


if __name__ == "__main__":
    try:
        result = search_commercial_district()
        print(f"Time taken: {result['elapsed_time']} seconds")
        print(f"Result: {result}")
    except Exception as e:
        print(f"An error occurred: {e}")

# test_crawling.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )

    # # 크롬 드라이버 경로 설정
    # driver_path = os.path.join(os.path.dirname(__file__), '../api', 'drivers', 'chromedriver.exe')

    # # 크롬 옵션 설정
    # options = Options()
    # prefs = {
    #     "download.default_directory": os.path.join(os.path.dirname(__file__), 'downloads'),
    #     "download.prompt_for_download": False,
    #     "download.directory_upgrade": True,
    #     "safebrowsing.enabled": True
    # }
    # options.add_experimental_option("prefs", prefs)

    # # 크롬 드라이버 서비스 설정
    # service = Service(driver_path)
    # driver = webdriver.Chrome(service=service, options=options)

    return driver

commercial_district_url = "https://m.nicebizmap.co.kr/analysis/analysisFree"

def search_commercial_district():
    driver = setup_driver()
    try:
        start_time = time.time()  # 시작 시간 기록

        driver.get(commercial_district_url)
        title = driver.title

        end_time = time.time()  # 종료 시간 기록

        elapsed_time = end_time - start_time
        data = {
            "title": title,
            "elapsed_time": elapsed_time
        }
        return data
    except Exception as e:
        raise Exception(f"Failed to fetch data from {commercial_district_url}: {str(e)}")
    finally:
        driver.quit()

if __name__ == "__main__":
    try:
        result = search_commercial_district()
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}")

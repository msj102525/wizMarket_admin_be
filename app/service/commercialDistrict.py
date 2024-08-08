import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

def setup_driver():
    driver_path = os.path.join(os.path.dirname(__file__), '../', 'drivers', 'chromedriver.exe')

    options = Options()
    options.add_argument("--start-fullscreen")  # 전체 화면 모드로 열기
    prefs = {
        "download.default_directory": os.path.join(os.path.dirname(__file__), 'downloads'),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    # 크롬 드라이버 서비스 설정
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    return driver

commercial_district_url = "https://m.nicebizmap.co.kr/analysis/analysisFree"

def search_commercial_district():
    driver = setup_driver()
    try:
        start_time = time.time()  # 시작 시간 기록

        driver.get(commercial_district_url)  # URL 접속

        wait = WebDriverWait(driver, 10)  # 10초 대기

        # 대기할 요소 정의
        location_xpath = '//*[@id="pc_sheet01"]/div/div[2]/div[2]/ul/li[1]/a'
        
        
        # 첫 번째 요소 대기 및 클릭
        location_element = wait.until(EC.presence_of_element_located((By.XPATH, location_xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", location_element)
        location_element.click()

        # 페이지가 새로 로드될 때까지 대기
        wait.until(EC.staleness_of(location_element))
        location_element = wait.until(EC.presence_of_element_located((By.XPATH, location_xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", location_element)

        city_xpath = '//*[@id="basicReport"]/div[4]/div[2]/div[2]/div/div[2]/ul/li[1]'
        # 다음 단계의 요소 대기 및 클릭
        city_element = wait.until(EC.presence_of_element_located((By.XPATH, city_xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", city_element)
        city_element.click()

        # 페이지가 새로 로드될 때까지 대기
        wait.until(EC.staleness_of(city_element))
        city_element = wait.until(EC.presence_of_element_located((By.XPATH, city_xpath)))
        driver.execute_script("arguments[0].scrollIntoView(true);", city_element)


        # 페이지 제목 가져오기
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
        print(f"Result: {result}")
        print(f"Time taken: {result['elapsed_time']} seconds")
    except Exception as e:
        print(f"An error occurred: {e}")

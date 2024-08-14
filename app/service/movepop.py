from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import time

def crawl_keyword(keyword: str):
    # 드라이버 경로 설정
    driver_path = os.path.join(
        os.path.dirname(__file__), "../", "drivers", "chromedriver.exe"
    )

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # 새 크롬 창을 숨기기 위해 headless 모드 사용
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(driver_path), options=options)

    try:
        driver.get('https://sg.sbiz.or.kr/godo/index.sg')

        # "유동인구" 라디오 버튼 선택
        radio_button = driver.find_element(By.ID, 'icon_list2_2')
        driver.execute_script("arguments[0].click();", radio_button)

        # searchAddress 입력 필드에 키워드 입력
        search_box = driver.find_element(By.ID, 'searchAddress')
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)  # 엔터키 누르기

        last_keyword = keyword.split()[-1]

        # 특정 div가 나타날 때까지 기다리기
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='cell']"))
        )
        div_elements = driver.find_elements(By.XPATH, "//div[@class='cell']")
        for div_element in div_elements:
            span_element = div_element.find_element(By.TAG_NAME, 'span')
            if span_element.text == last_keyword:
                div_content = div_element.get_attribute('innerHTML')
                break

        return div_content

    except Exception as e:
        print(f'Error: {e}')
        raise
    finally:
        driver.quit()

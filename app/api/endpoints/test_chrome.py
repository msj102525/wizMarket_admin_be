from fastapi import APIRouter, Response
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import os

router = APIRouter()

@router.get("/test-chrome", response_class=Response)
async def test_chrome_driver():
    # 크롬 드라이버 경로 설정
    driver_path = os.path.join(os.path.dirname(__file__), '..', 'drivers', 'chromedriver.exe')

    # 크롬 옵션 설정
    options = Options()
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

    try:
        # 크롬 드라이버가 지정된 URL을 열도록 테스트
        url = "https://jumin.mois.go.kr/ageStatMonth.do"
        driver.get(url)

        # 페이지 로드 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sltOrgLvl1"))
        )

        # 드롭다운 메뉴 요소 찾기
        select_element = driver.find_element(By.ID, "sltOrgLvl1")
        print(f"Select element found: {select_element}")

        # 드롭다운 옵션 값 로드 대기
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="sltOrgLvl1"]/option'))
        )

        # 드롭다운 옵션 값 출력
        options = select_element.find_elements(By.TAG_NAME, 'option')
        options_values = [option.get_attribute('value') for option in options]
        print(f"Available options: {options_values}")

        # 특정 옵션 값 선택
        select = Select(select_element)
        select.select_by_value("2600000000")  # value 값으로 선택
        print("Option with value 1100000000 selected")

        # 검색 버튼 클릭 대기
        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        "#content_main > div.content > div.tab_content > div > div.section1 > form > fieldset > div.btn_box > input.btn_search"))
        )
        search_button.click()
        print("Search button clicked")

        # 2초 대기
        time.sleep(2)

        # <div class="section3"> 내부 요소 로드 대기
        section3 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".section3"))
        )

        # <div class="section3"> 내부의 클래스 값이 tbl_type1 인 table 요소 찾기
        table_element = section3.find_element(By.CLASS_NAME, "tbl_type1")

        driver.execute_script("""
                let table = arguments[0];
                let cells = table.querySelectorAll('th, td');
                cells.forEach(cell => {
                    cell.classList.add('border', 'border-gray-300', 'w-40', 'h-12', 'p-2');
                });

                let secondHeader = table.querySelector('thead tr th:nth-child(2)');
                if (secondHeader) {
                    secondHeader.style.width = '160px';
                    secondHeader.style.height = '150px';
                }
            """, table_element)

        table_html = table_element.get_attribute('outerHTML')


        return Response(content=table_html, media_type="text/html")
    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
    finally:
        driver.quit()

# 나중에 이 라우터를 메인 애플리케이션에 포함시키는 것을 잊지 마세요.

from fastapi import APIRouter, Response, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

router = APIRouter()


@router.get("/test-chrome", response_class=Response)
async def test_chrome_driver():
    # 크롬 드라이버 경로 설정
    driver_path = os.path.join(os.path.dirname(__file__), '../../', 'drivers', 'chromedriver.exe')

    # 크롬 드라이버 서비스 설정
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)

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

        results = []

        for value in options_values:
            # 드롭다운 메뉴 요소를 다시 찾기
            select_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "sltOrgLvl1"))
            )
            select = Select(select_element)
            select.select_by_value(value)
            print(f"Option with value {value} selected")

            # 검색 버튼을 다시 찾기
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
            results.append(table_html)



        return Response(content="\n\n".join(results), media_type="text/html")
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.quit()

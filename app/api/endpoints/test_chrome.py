from fastapi import APIRouter, Response, HTTPException
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()


def process_option(value, driver_path):
    # 크롬 드라이버 서비스 설정
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)

    try:
        url = "https://jumin.mois.go.kr/ageStatMonth.do"
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sltOrgLvl1"))
        )

        select_element = driver.find_element(By.ID, "sltOrgLvl1")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="sltOrgLvl1"]/option'))
        )

        select = Select(select_element)
        select.select_by_value(value)

        search_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        "#content_main > div.content > div.tab_content > div > div.section1 > form > fieldset > div.btn_box > input.btn_search"))
        )
        search_button.click()

        time.sleep(2)

        section3 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".section3"))
        )

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
        return table_html
    except Exception as e:
        return f"Error processing value {value}: {str(e)}"
    finally:
        driver.quit()


@router.get("/test-chrome", response_class=Response)
async def test_chrome_driver():
    driver_path = os.path.join(os.path.dirname(__file__), '../../', 'drivers', 'chromedriver.exe')

    service = Service(driver_path)
    driver = webdriver.Chrome(service=service)

    try:
        url = "https://jumin.mois.go.kr/ageStatMonth.do"
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sltOrgLvl1"))
        )

        select_element = driver.find_element(By.ID, "sltOrgLvl1")
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, '//*[@id="sltOrgLvl1"]/option'))
        )

        options = select_element.find_elements(By.TAG_NAME, 'option')
        options_values = [option.get_attribute('value') for option in options]

        with ThreadPoolExecutor(max_workers=len(options_values)) as executor:
            futures = [executor.submit(process_option, value, driver_path) for value in options_values]
            results = [future.result() for future in futures]

        return Response(content="\n\n".join(results), media_type="text/html")
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.quit()

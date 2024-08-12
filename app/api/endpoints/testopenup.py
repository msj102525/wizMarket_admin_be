from fastapi import APIRouter, HTTPException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

router = APIRouter()

@router.post("/testopenup")
async def test_open_up():
    driver_path = os.path.join(
        os.path.dirname(__file__), "../../", "drivers", "chromedriver.exe"
    )

    options = Options()

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

    try:
        # 새 탭에서 URL 열기
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[-1])
        driver.get("https://www.openub.com/")
        time.sleep(5)

        # 검색 입력란을 찾고 클릭
        search_input = driver.find_element(By.ID, "search-address-map")
        search_input.click()
        time.sleep(2)

        # 검색 입력란에 '하노이반점' 텍스트 입력
        search_input.send_keys("하노이반점")
        time.sleep(2)

        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        driver.quit()

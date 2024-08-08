# test_crawling.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    return driver

commercial_district_url = "https://m.nicebizmap.co.kr/analysis/analysisFree"

def search_commercial_district():
    driver = setup_driver()
    try:
        driver.get(commercial_district_url)
        





        title = driver.title
        data = {
            "title": title,
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

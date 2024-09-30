import pymysql
from openpyxl import load_workbook
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import os, time
from tqdm import tqdm
import sys
from app.crud.loc_info import *
import pandas as pd




async def filter_location_info(filters: dict):
    # 필터링 로직: 필요하면 여기서 추가적인 필터 처리를 할 수 있습니다.
    filtered_locations = get_filtered_locations(filters)
    all_corr = get_all_corr()

    # 필요한 항목들로 DataFrame 생성 (SALES와 다른 변수들)
    df_all = pd.DataFrame(all_corr, columns=['SALES', 'SHOP', 'MOVE_POP', 'WORK_POP', 'INCOME', 'SPEND', 'HOUSE', 'RESIDENT'])

    # 전체 상관분석 수행
    all_corr_matrix = df_all.corr()

    # 지역 내 상관 분석
    filter_corr = get_filter_corr(filters)

    # 지역 내 분석 수행
    df_filter = pd.DataFrame(filter_corr)

    filter_corr_matrix = df_filter.groupby('DISTRICT_NAME')[['SALES', 'SHOP', 'MOVE_POP', 'WORK_POP', 'INCOME', 'SPEND', 'HOUSE', 'RESIDENT']].corr()

    filter_corr_matrix = filter_corr_matrix.reset_index().to_dict(orient='records')
    
    # 필요 시 추가적인 비즈니스 로직을 처리할 수 있음
    return filtered_locations, all_corr_matrix, filter_corr_matrix






sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
from app.db.connect import get_db_connection, close_connection


def crawl_keyword(keyword: str, connection, insert_count):
    driver_path = os.path.join(os.path.dirname(__file__), "../", "drivers", "chromedriver.exe")
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(service=Service(driver_path), options=options)

    try:
        driver.get('https://sg.sbiz.or.kr/godo/index.sg')

        # 페이지 로드 완료 확인 코드 추가
        WebDriverWait(driver, 30).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )

        radio_button = driver.find_element(By.ID, 'icon_list2_2')
        driver.execute_script("arguments[0].click();", radio_button)

        search_box = driver.find_element(By.ID, 'searchAddress')
        search_box.send_keys(keyword)
        search_box.send_keys(Keys.RETURN)

        last_keyword = keyword.split()[-1]

        print(f"마지막 동 단위 단어 : {last_keyword}")
        time.sleep(0.3)

        try:
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[@class='cell']"))
            )
            div_elements = driver.find_elements(By.XPATH, "//div[@class='cell']")
            div_content = None
            for div_element in div_elements:
                try:
                    span_element = div_element.find_element(By.TAG_NAME, 'span')
                    if span_element.text == last_keyword:
                        div_content = div_element.get_attribute('innerHTML')
                        break
                except Exception as e:
                    print(f"Error accessing span element: {e}")
        except Exception as e:
            print(f"Timeout or error waiting for div element: {e}")
            div_content = None

        if div_content:
            data = parse_html(div_content)
        else:
            data = {
                'location': None,
                'business': None,
                'person': None,
                'price': None,
                'wrcppl': None,
                'earn': None,
                'cnsmp': None,
                'hhCnt': None,
                'rsdppl': None
            }

        year_month = datetime.now().strftime("%Y%m")

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM movepopdata WHERE keyword = %s", (keyword,))
                if cursor.fetchone():
                    # 이미 존재하는 경우 업데이트
                    sql = """
                       UPDATE movepopdata SET 
                       location=%s, business=%s, person=%s, price=%s, wrcppl=%s, 
                       earn=%s, cnsmp=%s, hhCnt=%s, rsdppl=%s, yearmonth=%s
                       WHERE keyword = %s
                       """
                    cursor.execute(sql, (*data.values(), year_month, keyword))
                    connection.commit()
                    print(f"{insert_count}번째 update 성공")
                else:
                    # 존재하지 않는 경우 삽입
                    insert_record('movepopdata', connection, insert_count, keyword=keyword, yearmonth=year_month,
                                  **data)
                    connection.commit()
        except Exception as e:
            print(f"Error inserting or updating data: {e}")
            connection.rollback()
            raise e

    except Exception as e:
        print(f'Error: {e}')
        raise
    finally:
        driver.quit()


def parse_html(html_content):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    data = {
        'location': soup.find('span').text,
        'business': soup.find('strong', {'data-name': 'business'}).text,
        'person': soup.find('strong', {'data-name': 'person'}).text,
        'price': soup.find('strong', {'data-name': 'price'}).text,
        'wrcppl': soup.find('strong', {'data-name': 'wrcppl'}).text,
        'earn': soup.find('strong', {'data-name': 'earn'}).text,
        'cnsmp': soup.find('strong', {'data-name': 'cnsmp'}).text,
        'hhCnt': soup.find('strong', {'data-name': 'hhCnt'}).text,
        'rsdppl': soup.find('strong', {'data-name': 'rsdppl'}).text
    }
    return data


def insert_record(table_name: str, connection, insert_count, **kwargs):
    try:
        with connection.cursor() as cursor:
            columns = ', '.join(kwargs.keys())
            placeholders = ', '.join(['%s'] * len(kwargs))
            values = tuple(kwargs.values())
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            cursor.execute(sql, values)
        connection.commit()
        print(f"{insert_count}번째 insert 성공")
    except pymysql.IntegrityError as e:
        if e.args[0] == 1062:  # Duplicate entry error code
            print(f"Duplicate entry found for {kwargs}. Skipping...")
        else:
            print(f"Error inserting data: {e}")
            connection.rollback()
            raise e
    except Exception as e:
        print(f"Error inserting data: {e}")
        connection.rollback()
        raise e


def read_keywords_from_excel(file_path):
    workbook = load_workbook(filename=file_path)
    sheet = workbook.active
    keywords = [row[0].value for row in sheet.iter_rows(min_row=1) if row[0].value]
    return keywords


def process_file(file_path):
    connection = get_db_connection()
    insert_count = 0
    try:
        keywords = read_keywords_from_excel(file_path)
        for keyword in tqdm(keywords, desc=f"Processing {os.path.basename(file_path)}"):  # tqdm을 사용하여 진행 상황 표시
            with connection.cursor() as cursor:
                # DB에서 해당 키워드가 있는지, 그리고 earn이 NULL인지 확인
                cursor.execute("SELECT earn FROM movepopdata WHERE keyword = %s", (keyword,))
                result = cursor.fetchone()

                if result:
                    if result[0] is None:  # earn이 NULL인 경우
                        print(f"Keyword {keyword} exists but earn is NULL. Updating data...")
                        crawl_keyword(keyword, connection, insert_count)
                        continue
                    else:
                        print(f"Keyword {keyword} already exists with non-null earn. Skipping...")
                        continue  # earn이 NULL이 아니면 다음 키워드로 넘어감

            # 키워드가 존재하지 않는 경우 새로운 데이터를 삽입
            print(f"Keyword {keyword} does not exist. Inserting data...")
            insert_count += 1
            crawl_keyword(keyword, connection, insert_count)

    finally:
        close_connection(connection)
    print(f"Finished processing {os.path.basename(file_path)}")


def process_keywords_from_excel():
    print("Starting to process keywords from Excel")
    directory = "C:/formovedata"
    excel_files = [os.path.join(directory, f"SplitFile_{i}.xlsx") for i in [3, 4, 5, 6]]
    # excel_files = [os.path.join(directory, f"list.xlsx")]

    with ThreadPoolExecutor(max_workers=4) as executor:
        executor.map(process_file, excel_files)

    print("Finished processing all files")

# if __name__=="__main__":
#     process_keywords_from_excel()
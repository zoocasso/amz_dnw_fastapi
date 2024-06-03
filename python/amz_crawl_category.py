from sqlalchemy import create_engine
import pymysql
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from datetime import datetime
import time

create_date = str(datetime.now()).split(' ')[0].strip()

db_connection_str = 'mysql+pymysql://root:vision9551@127.0.0.1/shop_crawl'
db_connection = create_engine(db_connection_str)
conn = db_connection.connect()

db = pymysql.connect(host='127.0.0.1', user='root', password='vision9551', db='shop_crawl', charset='utf8')
cursor = db.cursor()

"""
    input_list && web driver 설정
"""
URL_ADDRESS = "https://www.amazon.com/"
URL_LIST = open("url_input.txt", "r", encoding="utf-8").read().splitlines()

driver = webdriver.Chrome()
driver.set_window_size(1920, 1080)

"""
    zip코드 입력하는 함수
"""
# ziasin_code (Selenium)
driver.get(URL_ADDRESS)
time.sleep(1)
driver.find_element("id","nav-global-location-popover-link").click()
time.sleep(1)

driver.find_element("id","GLUXZipUpdateInput").send_keys("98101")
driver.find_element("id","GLUXZipUpdate").click()
time.sleep(1)

"""
    zip코드 입력하는 함수
"""
# ziasin_code (Selenium)
driver.get(URL_ADDRESS)
time.sleep(1)
driver.find_element("id","nav-global-location-popover-link").click()
time.sleep(1)

driver.find_element("id","GLUXZipUpdateInput").send_keys("98101")
driver.find_element("id","GLUXZipUpdate").click()
time.sleep(1)

"""
    URL별 크롤링
""" 
for url in URL_LIST:    
    asin_list = list()
    product_idx = 1
    URL_SUFFIX = url.split("https://www.amazon.com/")[1]
    driver.get(URL_ADDRESS + URL_SUFFIX)
    driver.implicitly_wait(10)
    time.sleep(1)

    """
        URL별 asin코드 순열 저장
    """
    while(True):
        # 사이트 스크롤해서 html 불러오기
        for i in [10,5,10/3,10/4,2,10/6,10/7,10/7,10/8,10/8]:
            driver.execute_script(f"window.scrollTo(0,document.body.scrollHeight/{i})")
            time.sleep(1)
        # Selenium && BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # 상품을 지정하는 div를 list형식으로 저장
        contents = soup.find_all('div',{'class':'zg-grid-general-faceout'})

        # 상품의 URL_suffix와 상품의 고유 key값을 dict로 묶어서 list로 저장
        content_URLkey_list = list()
        for index in contents:
            asin = index.find('div',{'class':'p13n-sc-uncoverable-faceout'})['id'].strip()
            asin_dict = dict()
            asin_dict['url'] = url
            asin_dict['product_idx'] = product_idx
            asin_dict['asin'] = asin
            asin_dict['create_date'] = create_date
            asin_list.append(asin_dict)
            product_idx += 1
            
        # 다음페이지로 넘기는 함수
        nextPageURL = soup.find('li',{'class':'a-last'}).find('a')
        if nextPageURL != None:
            URL = URL_ADDRESS + str(nextPageURL['href'].strip())
            driver.get(URL)
            driver.implicitly_wait(10)
            time.sleep(1)
        else:
            print("[COMPLETE]")
            break
    
    asin_df = pd.DataFrame(asin_list)
    asin_df.to_sql(name='amz_category_with_asin',con=db_connection, if_exists='append', index=False)
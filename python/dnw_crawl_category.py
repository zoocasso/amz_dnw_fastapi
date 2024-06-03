from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from datetime import datetime
from bs4 import BeautifulSoup
import pymysql
import time

mydb = pymysql.connect(
    user="root",
    passwd="vision9551",
    host="127.0.0.1",
    db="temp",
)
# 커서 생성
cursor = mydb.cursor()

def checkDictValue_int(dict,key):
    value = dict.get(key)
    if value == None:
        return 0
    else:
        return dict[key]

options = Options()
# options.add_argument("download.default_directory=C:\\Music")
driver = webdriver.Firefox(options=options,executable_path="danawa\geckodriver.exe")
driver.set_window_size(1920, 1080)

URL_ADDRESS = "https://danawa.com/"
# amazon서버 불러오기
driver.get(URL_ADDRESS)

# 마우스를 올려놓는 driver 함수
level1_list = driver.find_elements(By.CSS_SELECTOR,"li.category__list__row")
for index in level1_list:
    ActionChains(driver).move_to_element(index).perform()

time.sleep(0.5)

page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')

category_title_list = list()

category_a_tag_list = soup.select("div.category__4depth li.category__depth__row a")

for list_index in category_a_tag_list:
    title_list = list_index["data-catelist"].split("_")
    category_title_dict = dict()
    category_title_dict["level_1"] = title_list[0]
    category_title_dict["level_2"] = title_list[1]
    category_title_dict["level_3"] = title_list[2]
    category_title_dict["level_4"] = title_list[3]
    category_title_dict["url"] = list_index["href"]
    try:
        category_title_dict["pcategory"] = int(list_index["href"].split("=")[1].split("&")[0])
    except:
        pass
    category_title_list.append(category_title_dict)
    cursor.execute(f"""INSERT INTO `dnw_category` (level1,level2,level3,level4,url,pcategory) VALUES("{category_title_dict["level_1"]}","{category_title_dict["level_2"]}","{category_title_dict["level_3"]}","{category_title_dict["level_4"]}","{category_title_dict["url"]}",{checkDictValue_int(category_title_dict,"pcategory")})""")
    mydb.commit()
driver.close()